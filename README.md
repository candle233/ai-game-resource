# AI Game Resource Library

Eagle 素材库：游戏 AI 生成素材集合（提示词卡片 / 音乐 / 音效 / 概念图 / 3D 道具）。

## 在 Eagle 中打开

1. `git clone https://github.com/candle233/ai-game-resource.git`
2. 打开 Eagle → 菜单「导入 → 导入库」或直接把整个文件夹拖入 Eagle，选择「从现有文件夹打开」即可。
   - 该文件夹本身就是一个 Eagle 库（含 `metadata.json` + `images/`），Eagle 会把它识别为库。
3. 之后在多台设备上同步时，先 `git pull` 再打开 Eagle；编辑后在 Eagle 关闭时 `git add -A && git commit -m "sync" && git push`。

## 多端同步约定

- **先 pull 后开库，关库后再 push**：避免 `metadata.json` / `mtime.json` 冲突。
- **不要手动编辑** `metadata.json` / `mtime.json` / `tags.json`，让 Eagle 自己管理。
- 素材本体在 `images/<id>.info/`，每项一个文件夹，含源文件与 `metadata.json`。
- `backup/`（Eagle 自动备份）、`.mimosa/`、`vector-db/`（AI 横向搜索索引）不入库，clone 后首次使用会自动重建。
- 如遇 `metadata.json` 冲突：Eagle 通常以单行压缩 JSON 存储，建议**任选一侧整份保留**，在 Eagle 里核对缺失项。

## 目录结构

```
ai-game-resource/
├── metadata.json      # Eagle 库结构（文件夹树、智能文件夹、标签组）
├── images/            # 素材项，每项 <id>.info/ 文件夹
├── tags.json          # 标签
├── mtime.json         # Eagle 内部修改时间索引
└── saved-filters.json # 保存的筛选
```

## 许可

素材为 AI 生成/程序合成的原型占位资源，仅供学习与原型开发使用。
