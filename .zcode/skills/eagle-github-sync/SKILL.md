---
name: eagle-github-sync
description: 从 GitHub 快速同步 Eagle 素材库（partial clone / blob:none 仓库）。当用户说"同步 Eagle""拉一下素材""素材库更新了""git pull 卡住了""合并素材""sync eagle library"，或遇到 checkout 卡在固定进度、curl 18 / early EOF、mtime.json / metadata.json 冲突时使用。优先用 ls-remote 查新、小批量预取 blob、再合并，避免大 pack 断流。
---

# Eagle 素材库 GitHub 同步

把远程的 Eagle 素材库更新拉到本地，并让 Eagle 能直接打开。适用于仓库本体即 Eagle 库（`metadata.json` + `mtime.json` + `images/<id>.info/`）、素材是数千个二进制文件的场景。

操作本地 Eagle 库内容（搜索/打标签/整理）请用 `eagle` skill；本 skill 只负责 git 同步。

## 核心原则

这类仓库通常是 **partial clone**（`remote.origin.partialclonefilter = blob:none`）：本地只有提交和树对象，素材文件按需下载。

直接 `git merge` / `git checkout` 会在 checkout 阶段一次性懒加载全部缺失 blob，打包成几十 MB 的 pack。网络一断就卡在固定进度（典型 52%），报 `curl 18 transfer closed` / `early EOF`，且重试还是请求同一批、反复卡同一处。

**正确做法：先小批量补齐缺失 blob 到对象库，再合并。** 这样 checkout 全程走本地，秒级完成，不依赖网络稳定性。

## 同步流程

把 `<repo>` 换成仓库路径（本环境默认是 `D:\Game materials.library`；不确定就先 `git -C <repo> rev-parse --show-toplevel`）。

### 1. 先看远程有没有新提交

```bash
git -C "<repo>" rev-parse HEAD
git -C "<repo>" ls-remote origin refs/heads/main
```

两个 hash 相同就直接结束并告知用户"已是最新"。`ls-remote` 不下载对象、速度快，优先用它，不要用 `git fetch --all` 来"看看有没有更新"。

### 2. 只抓提交元数据（不抓 blob）

```bash
git -C "<repo>" fetch origin main --filter=blob:none --no-tags
```

这一步很快。完成后 `origin/main` 指向新提交。若历史极长可加 `--depth=50`。

### 3. 处理本地工作区的 Eagle 托管文件

```bash
git -C "<repo>" status -sb
```

- 干净 → 跳过。
- 只有 `mtime.json` / `metadata.json` 被改 → 这是 Eagle 后台写入的中间态，stash 起来：
  ```bash
  git -C "<repo>" stash push -m "pre-eagle-sync" -- mtime.json metadata.json
  ```
- 有其他用户文件被改 → 先问用户，不要擅自 stash 或 checkout。

### 4. 小批量预取缺失 blob（关键步骤）

用本 skill 自带的脚本，目标 commit 取 `origin/main`：

```bash
python -I "<skill目录>/scripts/prefetch_blobs.py" "<repo>" $(git -C "<repo>" rev-parse origin/main)
```

Windows CMD 里没有 `$(...)`，先取出 hash 再传入：

```cmd
git -C "<repo>" rev-parse origin/main
python -I "<skill目录>\scripts\prefetch_blobs.py" "<repo>" <上一步输出的hash>
```

脚本每批默认 100 个 blob、单批超时 400 秒、失败自动重试多轮，直到 `final missing: 0` 才返回 0。看到 `final missing: 0` 再继续；否则重复运行脚本（它会自动从当前进度续传）。

### 5. 快进合并

```bash
git -C "<repo>" merge --ff-only origin/main
```

这次不应出现 `Updating files` 的长进度条；若出现且卡住，说明第 4 步没补完，回到第 4 步。

### 6. 恢复 stash 并解决冲突

```bash
git -C "<repo>" stash pop
```

若 `mtime.json` / `metadata.json` 冲突：先比对两边条目数，**保留完整的一份**（Eagle 常把 `mtime.json` 写成半截，条目数远小于 item 数；远程快照通常完整，但一定要比对）：

```bash
git -C "<repo>" show :2:mtime.json   # ours = 合并后的远程版本
git -C "<repo>" show :3:mtime.json   # theirs = stash 的本地版本
# 确认远程完整后：
git -C "<repo>" checkout --ours mtime.json
git -C "<repo>" add mtime.json
git -C "<repo>" stash drop
```

本地用户文件冲突时让用户决定，不要自动选边。

### 7. 收尾验证

```bash
git -C "<repo>" status -sb          # 应为 ## main...origin/main，无改动
git -C "<repo>" log -1 --oneline
git -C "<repo>" stash list          # 应为空
```

告知用户同步结果。之后如需在 Eagle 里核对，用 `eagle` skill。

## 故障处理

- **checkout 又卡在固定进度**：中断后先 `git status -sb`；若工作区半更新且本来是干净的，`git reset --hard HEAD` 恢复（有本地改动先 stash），然后重新执行第 4 步。`index.lock` 残留时，确认没有 git 进程（`tasklist | findstr git`）再删 `.git/index.lock`。
- **再次出现 `curl 18 / early EOF`**：说明 blob 没补够，重跑预取脚本；不要靠反复 `git merge` 硬试。
- **临时网络配置**：如需调整，`http.postBuffer`、降低 `http.maxRequests`、启用 HTTP/1.1 有帮助；但**不要设 `http.lowSpeedLimit=0`**，那会让挂起的连接无限等待、永远不超时失败。同步结束后把这些临时配置 `--unset` 掉。
- **凭据**：公开仓库无需凭据。私有仓库用 git credential helper 或环境变量注入 token，不要把 token 写进仓库、脚本或示例。

## 脚本

- `scripts/prefetch_blobs.py` — 小批量补齐目标 commit 缺失的 blob，带超时容错和多轮重试。

脚本放在系统临时目录运行即可，不要写进素材库仓库（避免污染 Eagle 库）。
