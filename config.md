# AI日报 Skill 用户配置

> 首次使用前，请填写以下配置项。所有 `{占位符}` 会在执行时按此文件的值替换。

## 路径配置

请把以下路径改为你本机的实际值：

| 变量 | 你的值 | 说明 |
|------|--------|------|
| `{OUTPUT_ROOT}` | `D:\OpenClaw\AI日报配图` | AI日报的输出根目录（按日期建子目录） |
| `{OUTPUT_ROOT_GITHUB}` | `D:\OpenClaw\GitHub日报配图` | GitHub日报的输出根目录 |
| `{EDGE_PATH}` | `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe` | Edge 浏览器路径 |
| `{EDGE_PROFILE}` | `D:\OpenClaw\EdgeProfile` | Edge 独立 Profile 目录路径 |
| `{NODE_MODULES}` | `C:\Users\23736\AppData\Roaming\npm\node_modules` | 全局 npm node_modules 路径 |
| `{DOUBAO_BATCH}` | `D:\OpenClaw\doubao_batch.js` | 批量生图脚本路径 |
| `{DOUBAO_GEN}` | `D:\OpenClaw\doubao_gen.js` | 单图补生成脚本路径 |
| `{PUBLISH_TOOL}` | `D:\OpenClaw\workspace\skills\daily-folder-cleanup\publish_article.js` | 发布工具脚本路径 |
| `{CLEANUP_TOOL}` | `D:\OpenClaw\ai-daily-skill\scripts\cleanup.js` | 日期目录清理（≥14 保留最新 7；读本文件 OUTPUT_ROOT） |
| `{WECHAT_DIR}` | `D:\OpenClaw\workspace\skills\baoyu-post-to-wechat` | 微信发布脚本所在目录 |

## 风格配置

从 `styles/cover/` 中选一个封面风格，从 `styles/chapter/` 中选一个配图风格。
填写文件名（不含路径，不含扩展名）：

### 封面风格

**COVER_STYLE**: `dark-ink`

可选值：

| 文件名 | 风格名 | 特点 |
|--------|--------|------|
| `dark-ink` | 暗黑泼墨 | 电影黑场质感，右侧人物辅助，左侧大字标题，高冲击力 |
| `minimalist-tech` | 极简科技 | 干净留白，几何线条，无人物，专业克制 |
| `cyber-neon` | 赛博霓虹 | 高饱和霓虹光效，未来感，年轻潮流 |
| `magazine-editorial` | 杂志编辑风 | 色块拼接，大字排版，平面设计感 |

### 配图风格

**CHAPTER_STYLE**: `acid-brutalist`

可选值：

| 文件名 | 风格名 | 特点 |
|--------|--------|------|
| `acid-brutalist` | 酸性野兽派 | 粗野厚涂色块拼贴，撕裂锯齿边缘，高对比度 |
| `flat-illustration` | 扁平插画 | 简洁扁平，色彩明快，矢量风格 |
| `isometric-tech` | 等距科技 | 30度等距投影，3D几何模块，发光线条 |
| `watercolor-soft` | 水彩柔和 | 水彩手绘，柔和色调，艺术感 |

> **提示**：封面和配图风格可以自由组合，不要求同系列。
> 例如：封面选 `cyber-neon` + 配图选 `isometric-tech` 也是合法的。
>
> 如果你想创建自己的风格，复制 `styles/cover/` 或 `styles/chapter/` 下的任意一个文件，
> 改个名字，修改内容，然后在上方填入你的风格文件名即可。

## 信息源配置

**FIRST_RUN**: `false`

> 定时任务 / 无人值守场景必须为 `false`。为 `true` 时仅在**交互会话**中可展示一次信息源提示；**禁止**阻塞等待用户回复。

不修改则使用默认值（A），直接可用。

### AI 日报信息源

**AI_DAILY_SOURCE**: `A`

可选值：
- `A` = 使用默认（aihot.virxact.com 公开 API 自动抓取）- 最快，无需登录（**一手轨 / 核实底稿**）
- `B` = 网页搜索 - 搜特定关键词
- `C` = 手动输入 - 在对话中直接贴热点列表
- `D` = 自定义 API / 命令 - 提供自己的数据源 URL 或命令

> **双轨（默认）**：热度轨（平台热议）选题 + 一手轨（本项 A）核实。详见下方「热度轨」。

### 热度轨（平台热议 · 选题主轴）

控制是否从抖音 / 小红书 / B 站 / X 等抓「正在火的话题」。规范见 `references/heat-track.md`。

| 配置键 | 你的值 | 说明 |
|--------|--------|------|
| `HEAT_TRACK` | `true` | 是否启用热度轨（`true`/`false`）。定时任务建议 `true` |
| `HEAT_PLATFORMS` | `xiaohongshu,bilibili,douyin,x` | 平台：小红书/B站/抖音/X，逗号分隔；可删减 |
| `HEAT_KEYWORDS` | `AI,GPT,大模型,Agent,Claude,OpenAI` | 搜索关键词，逗号分隔 |
| `HEAT_TOP_PER_PLATFORM` | `3` | 每平台最多收录几条 |
| `HEAT_MAX_TOTAL` | `8` | 合并去重后最多几条进 bundle |
| `HEAT_REQUIRE_VERIFY` | `true` | `true`：进「今日热议」正文前必须核实（confirmed/partial） |

**HEAT_TRACK**: `true`  
**HEAT_PLATFORMS**: `xiaohongshu,bilibili,douyin,x`  
**HEAT_KEYWORDS**: `AI,GPT,大模型,Agent,Claude,OpenAI`  
**HEAT_TOP_PER_PLATFORM**: `3`  
**HEAT_MAX_TOTAL**: `8`  
**HEAT_REQUIRE_VERIFY**: `true`

### GitHub 日报信息源

**GITHUB_DAILY_SOURCE**: `A`

可选值：
- `A` = 使用默认（GitHub Trending + Search API）
- `B` = 手动输入 - 在对话中直接贴项目列表
- `C` = 自行描述 - 描述要搜索的项目类别范围（如“只看 Agent 框架、编程工具相关”）

### 自定义关键词

**CUSTOM_KEYWORDS**: `""`

留空则使用默认搜索范围。如需聚焦特定方向，填写关键词，如 `"model release,coding tools,chinese ai"`。

> **提示**：也可以在对话指令中临时指定信息源，如“用网页搜索发今天的日报”，会覆盖此配置。

## GitHub 周榜抓取配置（fetch_weekly_trending.py）

控制 GitHub 日报的数据源与过滤口径。详见 `scripts/fetch_weekly_trending.py` 头部注释。

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `TRENDING_BACKEND` | `html_fallback` | 周榜数据源：`html_fallback`(爬 github.com/trending?since=weekly，已验证) / `ossinsight`(OSS Insight API，端点待确认) / `github_api`(GitHub 官方 REST，需 GITHUB_TOKEN) |
| `TRENDING_POOL_SIZE` | `20` | 每周候选池大小（Top N by 本周新增 Star） |
| `TRENDING_VERIFY_INTERVAL` | `2` | 抓取-校验节奏间隔天数：每 N 天重新抓一次并 diff，期间沿用旧池 |
| `AI_TOPICS_WHITELIST` | （脚本内置默认） | 来源策展：GitHub topics 白名单，逗号分隔。定义"什么是 AI"的边界 |
| `TRUSTED_ORGS` | （脚本内置默认） | 来源策展：可信组织 owner 名单，逗号分隔（如 huggingface,langchain-ai,microsoft...） |

> **"随时变动 API"**：切换数据源只需改 `TRENDING_BACKEND`，无需改代码。OSS Insight 当前端点 404，待确认正确端点后可一键启用；aihot 交叉验证信号始终开启（公开 API，无需 Key）。
> **编辑口径**：想调整"什么算 AI 项目"，改 `AI_TOPICS_WHITELIST` / `TRUSTED_ORGS` 即可，这是人工定义的边界，不靠关键词正则。

## 微信发布配置

微信 API 凭证（app_id / app_secret）通过外部脚本的 `.env` 文件配置，**不在本 skill 内存储**。
请确保 `{WECHAT_DIR}` 目录下有 `.env` 文件，包含：

```
WECHAT_APP_ID=你的appid
WECHAT_APP_SECRET=你的secret
```

## 排版配置（gzh-design-skill 精致排版）

控制 Step 4.1.5 是否启用 gzh-design-skill 排版替代 md-to-wechat 基础渲染。

| 变量 | 你的值 | 说明 |
|------|--------|------|
| `{GZH_SKILL_DIR}` | `D:\OpenClaw\workspace\skills\gzh-design-skill` | gzh-design-skill 安装目录（提供组件库与校验脚本） |
| `TYPESER` | `true` | 是否启用精致排版：`true` 生成 article.html 用 gzh-design 排版；`false` 回退 md-to-wechat 基础渲染 |
| `GZH_THEME` | `moyu-green` | 排版主题：moyu-green(摸鱼绿)/red-white(红白)/graphite(石墨极简)/zen(留白禅意)/ticket(摸鱼票据)/olive(橄榄手记) |

> **说明**：`TYPESER` 为 `true` 且 gzh-design-skill 已安装时，发布工具会自动优先用生成的 `article.html`；设为 `false` 或不安装时，流程完全回退到原有 md-to-wechat 渲染，不影响现有发布。
>
> **高级**：可基于你的封面风格（如 `dark-ink` 暗黑泼墨）用 gzh-design-skill 的主题生成器现造一套匹配的正文排版主题，存为 `{GZH_SKILL_DIR}/references/theme-starai-daily.md` 并在 `theme-index.md` 登记，然后 `GZH_THEME` 填 `starai-daily`，实现封面+正文视觉品牌统一。
