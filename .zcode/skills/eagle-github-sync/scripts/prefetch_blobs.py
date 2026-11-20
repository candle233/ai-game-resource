#!/usr/bin/env python3
"""Prefetch missing blobs for a commit in a partial clone, in small resilient batches.

In a partial clone (blob:none), `git merge` / `git checkout` lazily downloads every
missing blob at once. For a large asset library this builds a huge pack that stalls
or disconnects mid-transfer, and retries keep requesting the same big batch.

Fetching in small batches first keeps each request small, makes retries cheap, and
lets `git merge` finish entirely from the local object store.

Usage:
    python -I prefetch_blobs.py <repo_path> <commit> [options]

Example:
    python -I prefetch_blobs.py "D:\\Game materials.library" a0065681743db5f44a7b1c6d7c209dff1100d33e

Exit codes:
    0  all blobs for <commit> are present locally
    1  some blobs still missing after all rounds (safe to re-run; resumes)
    2  bad arguments / git not available
"""

import argparse
import random
import subprocess
import sys
import time


def git(repo, args, input_text=None, timeout=120):
    return subprocess.run(
        ["git", "-C", repo] + args,
        input=input_text,
        capture_output=True,
        text=True,
        errors="replace",
        timeout=timeout,
    )


def missing_blobs(repo, commit):
    """Return (sorted list of blob hashes in <commit> tree missing locally, total blob count)."""
    cat = git(repo, ["cat-file", "--batch-all-objects", "--batch-check=%(objectname)"])
    local = set(cat.stdout.split())

    ls = git(repo, ["ls-tree", "-r", commit])
    if ls.returncode != 0:
        raise RuntimeError("git ls-tree failed: %s" % ls.stderr.strip())

    target = set()
    for line in ls.stdout.splitlines():
        parts = line.split(None, 3)
        if len(parts) >= 3 and parts[1] == "blob":
            target.add(parts[2])
    return sorted(target - local), len(target)


def fetch_batch(repo, hashes, timeout):
    """Ask git to lazy-fetch these blobs from the promisor remote in one small request."""
    try:
        result = git(repo, ["cat-file", "--batch"],
                     input_text="\n".join(hashes) + "\n", timeout=timeout)
        out = result.stdout
        still = [h for h in hashes if ("%s missing" % h) in out]
        return still, "ok"
    except subprocess.TimeoutExpired:
        return list(hashes), "TIMEOUT"
    except Exception as exc:
        return list(hashes), "ERR:%s" % type(exc).__name__


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("repo", help="path to the Eagle repository")
    parser.add_argument("commit", help="commit-ish whose tree blobs must be present")
    parser.add_argument("--batch-size", type=int, default=100,
                        help="blobs per request (default: 100)")
    parser.add_argument("--timeout", type=int, default=400,
                        help="per-batch timeout in seconds (default: 400)")
    parser.add_argument("--rounds", type=int, default=8,
                        help="max retry rounds (default: 8)")
    args = parser.parse_args()

    try:
        missing, total = missing_blobs(args.repo, args.commit)
    except Exception as exc:
        print("ERROR: %s" % exc, file=sys.stderr)
        return 2

    print("target blobs: %d, missing: %d" % (total, len(missing)), flush=True)
    if not missing:
        print("nothing to prefetch", flush=True)
        return 0

    for rnd in range(1, args.rounds + 1):
        # Re-check each round: pack indexes may lag, and earlier batches may have landed.
        remaining, _ = missing_blobs(args.repo, args.commit)
        if not remaining:
            break
        random.shuffle(remaining)
        batches = [remaining[i:i + args.batch_size]
                   for i in range(0, len(remaining), args.batch_size)]
        print("ROUND %d: %d batches, %d blobs" % (rnd, len(batches), len(remaining)),
              flush=True)

        still_all = []
        for idx, batch in enumerate(batches, 1):
            still, status = fetch_batch(args.repo, batch, args.timeout)
            still_all.extend(still)
            got = len(batch) - len(still)
            if got or status != "ok" or idx % 10 == 0:
                print("  R%d b%d/%d: got %d still %d %s" %
                      (rnd, idx, len(batches), got, len(still), status), flush=True)
            time.sleep(0.3)

        print("ROUND %d done: remaining %d" % (rnd, len(still_all)), flush=True)
        if still_all and rnd < args.rounds:
            time.sleep(2)

    missing, _ = missing_blobs(args.repo, args.commit)
    print("FINAL missing: %d" % len(missing), flush=True)
    if missing:
        print("Sample:", missing[:20], flush=True)
        print("Re-run this script; it resumes from current progress.", flush=True)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
