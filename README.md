# AI日报 Skill (ai-daily)

将 AI 资讯 / GitHub 开源热榜自动转化为 B站科技UP主风格文章，配自定义风格的封面图和章节配图，发布到微信公众号草稿箱。

**当前版本：v2.5.1**

## 特点

- **4 步全自动**：抓取 → 批量生图 → 写文章(+排版) → 发布到公众号
- **双模式**：AI 日报（aihot 公开 API）+ GitHub 开源日报（周榜 Top10 + 本周之星）
- **风格可自定义**：内置 4 套封面 + 4 套配图风格，可自由组合或自定义
- **同一对话框生图**：`doubao_batch` 在同一豆包会话连续生图；会话 URL 写入 `_doubao_chat_url.txt` 支持续聊
- **发布硬门禁**：`publish_result.json` + `verify_publish.js`，避免「只写分析就当成功」
- **可开源**：路径与凭证参数化；微信 `app_id/secret` 放在发布脚本 `.env`，不进 skill

## 快速开始

### 1. 安装

```bash
git clone https://github.com/StarAI-2026/ai-daily-skill.git
# OpenClaw 示例：放到 skills 目录或 junction
# Claude / Codex：按各工具 skills 路径安装
```

### 2. 配置

编辑 `config.md`：

- 填写本机路径：`OUTPUT_ROOT`、`DOUBAO_BATCH`、`PUBLISH_TOOL` 等
- 选择 `COVER_STYLE` / `CHAPTER_STYLE`
- 设置 `TYPESER` / `GZH_THEME`（精致排版，可选）

微信凭证写在发布工具目录的 `.env`（`WECHAT_APP_ID` / `WECHAT_APP_SECRET`），不要写进本仓库。

### 3. 依赖

- Node.js（抓取、生图脚本、发布）
- Python 3（周榜抓取、typeset、HTML 校验）
- bun（微信发布脚本）
- 本机配置好的 `doubao_batch.js` + EdgeProfile 豆包登录

### 4. 使用

自然语言触发示例：

- `发布日报` / `StarAI日报` → AI 日报
- `发布GitHub日报` / `StarAI开源日报` → GitHub 周榜日报

定时任务（OpenClaw cron）请使用无人值守文案：禁止询问、只跑 `doubao_batch`、最后 `verify_publish.js`。

## 目录结构

```
ai-daily-skill/
├── SKILL.md                 # 主技能（v2.5.1）
├── config.md                # 用户配置（路径 / 风格 / 排版）
├── LICENSE                  # MIT
├── README.md
├── references/              # 文章模板、标题、文案、故障排除
├── styles/
│   ├── cover/               # 封面风格
│   └── chapter/             # 章节配图风格
└── scripts/
    ├── fetch_ai_daily.js          # AI 日报抓取（本地日期）
    ├── fetch_weekly_trending.py   # GitHub 周榜多后端抓取
    ├── typeset_gzh.py             # 摸鱼绿等 gzh 排版
    ├── validate_gzh_html.py       # 公众号 HTML 合规校验
    └── verify_publish.js          # 发布完成硬门禁
```

## 4 步流程（摘要）

1. **抓取**：`fetch_ai_daily.js` 或 `fetch_weekly_trending.py`
2. **生图**：写 `_batch_config.json` → **一次** `doubao_batch.js`（同一豆包对话框）
3. **写文章**：`article.md`；可选 `typeset_gzh.py` → `article.html`
4. **发布**：`publish_article.js` → `verify_publish.js`（必须有 media_id）

成功通知建议包含：标题、本地发布时间、media_id、草稿箱链接 https://mp.weixin.qq.com

## 铁律（节选）

- 禁止循环 `doubao_gen.js` 为每张图新开豆包会话
- 禁止 PowerShell `ConvertFrom-Json` 抓/读 JSON（用 Node）
- 禁止 `Stop-Process msedge` / `taskkill msedge` 杀浏览器
- 无 `publish_result.json` + media_id = 未成功

## License

MIT
