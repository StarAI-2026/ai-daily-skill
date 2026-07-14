---
name: ai-daily
description: "AI日报/GitHub开源日报全自动发布。触发词：发布日报/写日报/StarAI日报/生成日报/公众号日报/发布GitHub日报/StarAI开源日报/GitHub热门项目/定时任务/cron/自动发布。执行4步：抓取->批量生图->写文章+排版->publish_article.js 发布并返回media_id。独立skill；定时任务零交互。"
version: 2.6.1
author: StarAI
license: MIT
metadata:
  openclaw:
    requires:
      anyBins:
        - bun
        - npx
        - node
---

# AI日报 - 全自动发布工作流

将 AI 资讯转化为 B站科技UP主风格文章，配自定义风格的封面图和章节配图，发布到微信公众号。

**独立技能**：所有逻辑自包含，不依赖其他 skill 配合。4 步完成从新闻到发布。
**风格可自定义**：封面和配图风格可在 `config.md` 中自由选择或自定义。
**可开源**：所有环境相关路径/凭证均参数化，不含任何硬编码敏感信息。

## 语言

使用用户的语言回复。技术术语（路径、参数名）保持英文。

---

## 首次使用前必读

1. **复制配置**：若只有 `config.example.md`，先复制为 `config.md`
2. **创建输出文件夹**（必做）：在本机新建两个目录（名称自定），分别填入 `config.md` 的 `{OUTPUT_ROOT}`（AI 日报）与 `{OUTPUT_ROOT_GITHUB}`（GitHub 日报）。封面/配图会按 **`{OUTPUT_ROOT}\yyyy-MM-dd\`** 落盘
3. **填写其余路径**：`DOUBAO_BATCH`、`PUBLISH_TOOL`、`CLEANUP_TOOL`（默认 `scripts/cleanup.js`）、`EDGE_PROFILE` 等
4. **选择风格**：在 `config.md` 中从 `styles/cover/` 和 `styles/chapter/` 各选一个风格，或自定义
5. **配置微信凭证**：在微信发布脚本目录下创建 `.env` 文件，填入 `WECHAT_APP_ID` 和 `WECHAT_APP_SECRET`
6. **安装依赖**：确保 node、bun、npx 可用
7. **自检清理配置**：`node scripts/cleanup.js --dry-run`（应打印两个 OUTPUT 路径且不误删）

## 用户配置（从 config.md 读取）

执行前**必须先读取 `config.md`**，获取以下信息：
- 所有 `{占位符}` 路径的实际值
  - `{OUTPUT_ROOT}` / `{OUTPUT_ROOT_GITHUB}`：AI/GitHub 日报输出根目录
  - `{EDGE_PATH}`：Edge 浏览器可执行文件路径
  - `{EDGE_PROFILE}`：Edge 独立 Profile 目录路径
  - `{NODE_MODULES}`：全局 npm node_modules 路径
  - `{DOUBAO_BATCH}`：批量生图脚本路径
  - `{DOUBAO_GEN}`：单图补生成脚本路径
  - `{PUBLISH_TOOL}`：发布工具脚本路径
  - `{CLEANUP_TOOL}`：目录清理脚本路径
  - `{WECHAT_DIR}`：微信发布脚本所在目录
  - `{GZH_SKILL_DIR}`：gzh-design-skill 安装目录（排版组件库 + 校验/内嵌脚本）
- `COVER_STYLE`：封面风格文件名（对应 `styles/cover/{COVER_STYLE}.md`）
- `CHAPTER_STYLE`：配图风格文件名（对应 `styles/chapter/{CHAPTER_STYLE}.md`）
- `TYPESER`：是否启用 gzh-design-skill 精致排版（`true`/`false`）
- `GZH_THEME`：排版主题名（如 `moyu-green`）
- `TRENDING_BACKEND`：GitHub 周榜数据源（`html_fallback` 默认主后端 / `ossinsight` / `github_api`），可随时改后端，无需改代码
- `TRENDING_POOL_SIZE`：每周候选池大小（默认 20）
- `TRENDING_VERIFY_INTERVAL`：抓取-校验节奏间隔天数（默认 2，即每 2 天重新抓一次并 diff）
  - `AI_TOPICS_WHITELIST` / `TRUSTED_ORGS`：来源策展白名单（定义"什么是 AI"的边界，改这两个即改编辑口径）
  - **热度轨**：`HEAT_TRACK` / `HEAT_PLATFORMS` / `HEAT_KEYWORDS` / `HEAT_TOP_PER_PLATFORM` / `HEAT_MAX_TOTAL` / `HEAT_REQUIRE_VERIFY`（平台热议选题，见 `references/heat-track.md`）

## 双轨选题（AI 日报默认）

| 轨道 | 作用 | 数据文件 |
|------|------|----------|
| **热度轨（主）** | 抖音/小红书/B站/X 等正在火的话题 → 定「今天写啥」 | `heat_track.json` |
| **一手轨（辅）** | aihot 等 → 核实事实、补条目 | `raw_daily.json` |
| **合并** | 写作唯一优先读本文件 | `daily_bundle.json` |

- `HEAT_TRACK=false` 时跳过平台检索，行为与旧版「仅 aihot」接近  
- 禁止把未核实热搜写成官方发布；`rumor` 最多 1 条且文案必须「网传/待观察」

## 日报类型（两种模式，默认 AI 日报）

| 配置项 | AI 日报 | GitHub 日报 |
|--------|---------|------------|
| 触发词 | 发布日报 / StarAI日报 / 生成日报 | 发布GitHub日报 / StarAI开源日报 |
| 输出根目录 | `{OUTPUT_ROOT}` | `{OUTPUT_ROOT_GITHUB}` |
| 文章模板 | `references/article-prompt-ai.md` | `references/article-prompt-github.md` |
| 固定开头 | 「欢迎来到StarAI日报，请查收今日AI圈热门动态。」 | 「欢迎来到StarAI开源日报，本周 GitHub 热门 AI 项目已更新，请查收。」 |

## References（本 skill 自带，按需读取）

| 文件 | 何时读取 |
|------|----------|
| `config.md` | **每次执行前必读**，获取路径和风格配置 |
| `references/heat-track.md` | AI 日报 Step 1 热度轨：平台检索与核实 |
| `styles/cover/{COVER_STYLE}.md` | Step 2 生成封面提示词时 |
| `styles/chapter/{CHAPTER_STYLE}.md` | Step 3 生成章节配图提示词时 |
| `references/article-prompt-ai.md` | Step 4 生成 AI 日报文章时 |
| `references/article-prompt-github.md` | Step 4 生成 GitHub 日报文章时 |
| `references/title-generator.md` | Step 4 生成文章标题时 |
| `references/copywriting-guide.md` | Step 4 优化标题和导语时 |
| `references/troubleshooting.md` | 遇到问题时查阅 |
| `scripts/validate_gzh_html.py` | Step 4 发布前校验 HTML 合规性时自动调用 |
| `scripts/typeset_gzh.py` | Step 4.1.5 排版转换器：article.md → 摸鱼绿 article.html（纯片段，全内联+span leaf） |
| `scripts/fetch_weekly_trending.py` | GitHub 日报 Step 1：多后端周榜抓取 + 抓取校验节奏 + AI 过滤（topics/组织白名单 + aihot 交叉验证），输出 raw_weekly.json |
| `{GZH_SKILL_DIR}/references/theme-index.md` | Step 4.1.5 排版时确认主题（TYPESER=true 才需读） |
| `{GZH_SKILL_DIR}/references/theme-{GZH_THEME}.md` | Step 4.1.5 排版时读主题专属组件库 |
| `{GZH_SKILL_DIR}/references/common-components.md` | Step 4.1.5 排版时读通用组件库 |
| `{GZH_SKILL_DIR}/scripts/validate_gzh_html.py` | Step 4.1.5 排版后校验产物合规性 |
| `{GZH_SKILL_DIR}/scripts/embed_images_for_copy.py` | Step 4.1.5 可选：生成含图片版预览页供手动复制 |

---

## 5 条铁律

1. **端到端流程**：4 步必须全部执行。用户说"发布日报"/定时任务触发 = 必须发布到微信公众号草稿箱。
2. **禁止把文章正文贴到对话/飞书回复里**：文章保存为 `article.md`，通过发布工具上传。
3. **禁止询问用户"是否要发布"**：触发即确认发布。
4. **用批量脚本一次性生图**：禁止逐张循环，必须一次性 `doubao_batch.js`。
5. **完成后返回 media_id**：无 media_id = 失败，禁止报成功。
6. **豆包同一对话框生图**：封面+章节图必须在**同一个豆包会话**里连续生成；禁止每张图新开对话/新标签/反复打开 create-image。

## 无人值守 / 定时任务模式（强制）

当触发来源为 **cron / 定时任务 / 自动发布**，或指令含「禁止询问」「无人值守」时：

1. **禁止向用户提问**（信息源、是否发布、风格选择全部跳过）
2. 信息源固定读 `config.md`：`AI_DAILY_SOURCE` / `GITHUB_DAILY_SOURCE`（默认 A）；忽略 `FIRST_RUN`
3. 生图**整次任务只允许 1～2 次** `{DOUBAO_BATCH}`（同一对话框，batch 内部不关再开）
4. **绝对禁止**：循环 `doubao_gen`、删除 `_doubao_chat_url.txt`、每次失败就重新 create-image、改 batch 源码
5. 部分失败：最多再跑 **1 次** batch（skip 成功图 + 读会话 URL 续聊）；仍失败则停止并报错
6. 必须执行：`node {PUBLISH_TOOL} ...` + `verify_publish.js`；成功标准仅 media_id
7. 对外成功模板：标题 + 本地时间 + media_id + 草稿箱链接；中间工具失败但 verify 成功仍报成功
8. **禁止**使用已删除的 `starai-daily` / `starai-github-daily` / `starai-daily-publish` 路径

### 完成定义（缺一不可）

| 检查项 | AI 日报 | GitHub 日报 |
|--------|---------|-------------|
| 数据文件 | `raw_daily.json` | `raw_weekly.json` |
| 封面 | `cover.png` | `cover.png` |
| 文章 | `article.md` | `article.md` |
| 排版（TYPESER=true） | `article.html` | `article.html` |
| 发布凭证 | `publish_result.json` 含 media_id | 同左 |
| counter | `last_ai_publish_date` 为今日 | `last_github_publish_date` 为今日 |


## 绝对禁止（会导致 cron 假成功 / 失败）

1. **禁止**用 PowerShell `Get-Content` / `ConvertFrom-Json` / `Invoke-RestMethod` 读写 JSON 或抓 aihot
2. **禁止**只用分析报告结束任务（飞书发 analysis_*.md 不算完成）
3. **禁止**在没有 `publish_result.json` + `media_id` 时说「发布成功」
4. **禁止** `toISOString().slice(0,10)` 当目录日期；用本地日期或 `scripts/fetch_ai_daily.js`
5. JSON/API **只用 Node.js**：`node scripts/fetch_ai_daily.js "{目录}"`

6. **禁止** `Get-Process msedge` / `Stop-Process -Name msedge` / `taskkill /im msedge.exe`
   （会杀用户浏览器 → Playwright 页关闭 → 生图全失败 → cron 报错）
7. 浏览器**只**由 `doubao_batch.js` / `doubao_gen.js` 管理；脚本内部只会结束 **EdgeProfile** 相关进程，agent 不要自己管浏览器
8. **禁止**对每张图单独 `node doubao_gen.js`（每跑一次会关浏览器再开 = 新会话）；多图/补图统一 **一条** `doubao_batch.js`
9. **禁止**在豆包页面「生成完关浏览器再开」；整次任务生图进程内必须保持同一对话框
10. **禁止** `Remove-Item` / 删除 / 清空 `_doubao_chat_url.txt`（定时日志已证实：删锚点会导致反复 create-image 刷历史）
11. **禁止**修改 `doubao_batch.js` / `doubao_gen.js` 源码来“绕过”
12. **整次任务 `doubao_batch` 最多执行 2 次**（第 2 次仅补失败图且必须带已有会话 URL）；禁止 3 次以上反复开关 Edge

## 发布后强制验收

```powershell
node D:\OpenClaw\ai-daily-skill\scripts\verify_publish.js "{日期目录}"
```

exit code != 0 = **整次任务失败**。

## 生图脚本说明

### 同一对话框铁律（用户硬性要求）

| 正确 | 错误 |
|------|------|
| 一次 `doubao_batch.js`，同一会话连续输入多条提示词 | 每张图跑一次 `doubao_gen.js` |
| 失败后**再跑同一 batch**（skip 已成功 + 读 `_doubao_chat_url.txt` 续聊） | 生成完关窗口，再开 create-image 新会话 |
| 会话锚点：`{日期目录}/_doubao_chat_url.txt` | 历史对话刷屏 |

**批量生图脚本（`{DOUBAO_BATCH}`）自己管理浏览器**：`launchPersistentContext` + EdgeProfile，**不需要 9222**。整批只进入**一个**豆包对话。

agent 不需要做任何浏览器准备工作。写好 `_batch_config.json` 后只执行一次 batch。

**如果 EdgeProfile 未登录**（脚本会报错提示），需要手动登录一次：
`Start-Process "{EDGE_PATH}" -ArgumentList "--user-data-dir={EDGE_PROFILE}", "https://www.doubao.com/chat"`

批量脚本默认读取 `ai-daily-skill/config.md`，也可用 `--config-md <路径>`。

`{DOUBAO_GEN}` **仅**在 batch 无法修复的极端情况补 **1** 张，且必须与 batch 共用输出目录（自动读 `_doubao_chat_url.txt` 续聊）。

---

## 4 步工作流

### Step 1: 找新闻（信息源决策）

**判断逻辑**（按优先级）：

1. **定时/无人值守** → 直接用 `config.md` 的 `AI_DAILY_SOURCE`（默认 A），**禁止询问**
2. 用户指令已指定信息源 → 按指令执行
3. 仅当**交互会话**且 `FIRST_RUN=true` 时，可提示一次信息源选项，但**不得阻塞**：立即用默认 A 继续

#### 1A. 检查指令中是否已指定信息源

如果用户的触发指令中已经明确说了信息源方式或搜索内容，**直接跳过询问，按指令中指定的方式执行**。识别规则：

- 提到 API 名称或 URL（如 aihot、aihot.virxact.com）-> 方式 A（公开 API）
- 提到网页搜索、web search、GitHub Trending -> 方式 B（网页搜索）
- 直接贴了新闻/事件文本 -> 方式 C（手动输入）
- 提到用我的 API、用这个命令 -> 方式 D（自定义）
- 指令里带了主题/关键词/领域 -> 作为搜索范围

#### 1B. 交互会话且 FIRST_RUN=true（可选提示，不阻塞）

可展示信息源选项供下次生效，**本次仍立即用 config 默认值执行**。定时任务永不走此分支。

#### 1C. 执行抓取（AI 日报 = 一手轨 + 热度轨）

```powershell
$date = Get-Date -Format "yyyy-MM-dd"
$dir = "{OUTPUT_ROOT}\$date"
New-Item -ItemType Directory -Force -Path $dir | Out-Null
```

**1C-1 一手轨（核实底稿，默认方式 A）**

```powershell
node scripts/fetch_ai_daily.js "$dir"
# 输出: raw_daily.json
```

方式 B/C/D：按用户选择抓取，仍须整理为可核对的 JSON 放进日期目录。

**1C-2 热度轨（选题主轴，`HEAT_TRACK=true` 时强制）**

```powershell
node scripts/init_heat_track.js "$dir"
# 输出: heat_track_plan.json + heat_track.json 骨架
```

然后 **Agent 必须**（读 `references/heat-track.md`）：

1. 按 `heat_track_plan.json` 的 `search_queries` / 平台列表检索  
   - 优先：网页搜索、浏览器、agent-reach 等真实检索  
   - 关键词：`HEAT_KEYWORDS`；平台：`HEAT_PLATFORMS`  
2. 把话题写入 `heat_track.json` 的 `topics[]`（含平台、热度信号、链接、核实）  
3. 用 `raw_daily.json` + 搜索做事实核实，填 `verify.status`  
4. 某平台失败 → 记入 `platforms_failed`，改用 web 搜索补；仍不够 → 可从 aihot 降级条目并标 `source_type: "fallback_aihot"`（**文中禁止伪装成平台热议**）

**1C-3 合并（写作前强制）**

```powershell
node scripts/merge_daily_bundle.js "$dir"
# 输出: daily_bundle.json
```

**AI 日报 Step 1 产出清单**：

| 文件 | 必须 |
|------|------|
| `raw_daily.json` | 是（一手轨） |
| `heat_track.json` | `HEAT_TRACK=true` 时是 |
| `daily_bundle.json` | 是（写作主输入） |

写作时 **优先读 `daily_bundle.json`**，不要只读 aihot。

#### 1E. GitHub 日报：固定走周榜抓取（不走热度轨双轨）

GitHub 日报的数据源固定为 **GitHub 周榜（按本周新增 Star 排名）**，无需询问用户信息源，直接运行抓取脚本：

```powershell
python scripts/fetch_weekly_trending.py "{日期目录}" --force
```

脚本自动完成：多后端抓取（默认 `html_fallback`）→ aihot 公开 API 交叉验证 → AI 过滤（GitHub topics 白名单 + 可信组织名单）→ 抓取-校验节奏（每 `TRENDING_VERIFY_INTERVAL` 天重抓并 diff，无变化沿用旧池）→ 输出 `{日期目录}/raw_weekly.json`（本周候选池，含 `weekly_stars` / `total_stars` / `ai_relevant`）。

**输出物**：`{日期目录}/raw_weekly.json`

> 后端可随时切换：改 `config.md` 的 `TRENDING_BACKEND` 即可在 `html_fallback` / `ossinsight` / `github_api` 间切换，无需改代码（"随时变动 API"）。

**输出物**：`{日期目录}/raw_daily.json` 或 `raw_topics.json`

---

### Step 2: 生成封面

#### 2.1 生图脚本自管理浏览器

批量生图脚本会自己启动和管理 Edge 浏览器，**agent 不需要检查端口或手动启动 Edge**。

#### 2.2 生成封面提示词

1. **读取 `config.md`** 获取 `COVER_STYLE` 的值
2. **读取 `styles/cover/{COVER_STYLE}.md`** 获取封面风格指令
3. 从 Step 1 的数据中提取核心事件、用户价值、风险/提示
4. 按风格指令中的规则生成标题、从随机池抽取参数
5. 组装成完整的中文生图 prompt
6. 文件名固定为 `cover`，type 为 `"cover"`

#### 2.3 写入封面配置

```json
{
  "name": "cover",
  "event": "封面 - [文章主标题]",
  "type": "cover",
  "prompt": "[按封面风格文件生成的完整中文提示词]"
}
```

---

### Step 3: 每个事件生成配图

#### 3.1 生成章节配图提示词

1. **读取 `config.md`** 获取 `CHAPTER_STYLE` 的值
2. **读取 `styles/chapter/{CHAPTER_STYLE}.md`** 获取配图风格规范
3. 为文章里的每个深度项目生成章节配图提示词（AI 日报约 6-7 个；**GitHub 日报只给 2-3 个本周之星深拆项目各配一张，不按 Top 10 全配**）
4. 按风格文件中的 Prompt 模板填充占位符
5. 文件命名：`{主题关键词}.png`

#### 3.2 写入完整批量配置

将封面 + 所有章节配图合并写入 `_batch_config.json`。

#### 3.3 执行批量生图（同一对话框，只跑这一条命令）

```powershell
$env:NODE_PATH = "{NODE_MODULES}"
node {DOUBAO_BATCH} --config "{日期目录}\_batch_config.json" --output "{日期目录}"
```

> 脚本会在输出目录写入 `_doubao_chat_url.txt`。部分失败时**不要**改用多次 `doubao_gen`；再次执行上面同一命令即可（已成功文件 skip，失败项在同一会话续聊）。

#### 3.4 验证图片清单

> **豆包生图机制**：每次提示词约 4 张候选，脚本取最大一张；正常 3–8 MB，&lt;500KB 视为失败。

**验证要求**：
- 所有图片 status 为 success 或 skipped
- 每张 size_mb &gt;= 0.5
- 数量 = 封面 1 + 章节 N

读取 `_image_manifest.json`。失败则**只重跑 batch**，禁止循环 `doubao_gen.js`。

---

### Step 4: 写文章 + 发布到公众号

#### 4.1 写文章

1. **读取** 对应的文章模板（`references/article-prompt-ai.md` 或 `article-prompt-github.md`）
2. 将 Step 1 数据替换模板中的占位符，生成文章
3. **读取** `references/title-generator.md` 生成候选标题
4. **读取** `references/copywriting-guide.md` 优化标题和导语
5. 保存为 `{日期目录}/article.md`

**文章 frontmatter**：title（不超过20字）、author、description（120字以内）

**标题铁律**：不超过 20 字，一条标题只聚焦一个新闻点，最后 3-5 字制造悬念，禁用"炸了""重磅"等失效词。

**去 AI 味铁律**：禁用"值得注意的是""综上所述"，禁用 emoji，禁用话题标签。

**写作风格**：B站科技UP主风格，口语化连接词，中国化比喻，短句为主，全文 3000-5000 字。

**图片引用规则**：先读取 `_image_manifest.json`，按清单中的 filename 引用图片，只引用 `status: "success"` 的图片。

#### 4.1.5 排版（gzh-design-skill 精致排版）【可选，由 config.md 的 TYPESER 控制】

> 此步骤将 md-to-wechat 的"基础渲染"升级为 gzh-design-skill 的"精致排版"（封面卡 + 目录 + 引言卡 + 章节编号 + 关键词下划线 + 三连 CTA）。产物为纯片段 `article.html`，直接喂给发布工具（wechat-api.ts 原生支持 .html 输入，会自动上传 HTML 里的图片）。

**触发条件**：`config.md` 中 `TYPESER` 为 `true` 且 `{GZH_SKILL_DIR}` 指向的 gzh-design-skill 已安装。否则跳过本步骤，直接用 `article.md` 发布（回退到 md-to-wechat 基础渲染）。

**执行步骤**：

1. **读取主题索引**：读 `{GZH_SKILL_DIR}/references/theme-index.md`，确认 `config.md` 中 `GZH_THEME` 对应的主题（默认 `moyu-green` 摸鱼绿）。AI 日报属"盘点/工具清单"类，默认即摸鱼绿。
2. **读取组件库**：读 `{GZH_SKILL_DIR}/references/theme-{GZH_THEME}.md`（主题专属组件库）+ `{GZH_SKILL_DIR}/references/common-components.md`（通用组件库）。
3. **排版生成纯片段 `article.html`**：调用本 skill 自带转换器（已严格按摸鱼绿组件库实现，避免每次手敲）：
   ```bash
   python scripts/typeset_gzh.py "{日期目录}/article.md" "{日期目录}/article.html" --date YYYY.MM.DD --brand "StarAI开源日报"
   ```
   转换器自动产出：封面卡 + 横向目录 + 引言卡 + PART 0X 章节编号 + 关键词绿色加粗/下划线 + 结尾三连 CTA，并**必须**满足以下硬约束：
   - **纯片段结构**：从 `<section style="...">` 开始，禁止包含 `<html>/<head>/<body>`、toolbar、复制按钮、`<script>`（那些是预览页的事，发布工具会原样提取 body 内容，混入 UI 元素会污染文章）。
   - **全内联样式**：所有样式写在 `style=""` 属性内，禁止 `<style>/<class>/<div class>/grid/position:fixed` 等公众号禁用的写法。
   - **span leaf 包裹**：每个文字节点用 `<span leaf="">文字</span>` 包裹（公众号编辑器兼容性要求）。
   - **图片相对路径**：沿用 article.md 的图片文件名（如 `apple_openai.png`、`cover.png`），生成 `<img src="apple_openai.png" style="...">`，禁止改文件名、禁止用绝对路径。
   - **必备组件**：封面卡（含日期/标题/摘要）、横向目录导航、开头引言卡、PART 01–08 章节编号、每段 1–3 个关键词下划线、结尾三连 CTA（点赞/在看/转发）。**今日速览胶囊为条件渲染**：仅当文章含「今日速览」段落（AI 日报）才输出；GitHub 日报用【本周 GitHub 热榜 Top 10】排名榜（有序列表组件）承担速览职能，不渲染今日速览胶囊。
   - **中文全角**：正文标点自动全角，代码块内原样保留。
4. **合规校验**（路径必须加引号，禁止把 `\` 吃掉）：
   ```powershell
   python "D:\OpenClaw\ai-daily-skill\scripts\validate_gzh_html.py" "{日期目录}\article.html"
   ```
   或：`python "{GZH_SKILL_DIR}\scripts\validate_gzh_html.py" "{日期目录}\article.html"`  
   **0 ERROR 才继续**；有 ERROR 则修复后重试。也可跳过本步，交给 `publish_article.js` 内置校验。
5. **生成含图片版预览页（手动复制用，可选）**：若用户可能手动复制粘贴，调用 `{GZH_SKILL_DIR}/scripts/embed_images_for_copy.py` 把图片 base64 内嵌，生成 `{日期目录}/article_排版_预览(含图片).html`，供用户点"复制到公众号"按钮手动粘贴（自动 API 发布不需要此文件）。

**排版检查清单**（生成后逐项核对）：
- [ ] 封面卡存在且信息正确
- [ ] 目录导航列出所有章节
- [ ] 引言卡存在（GitHub 日报无今日速览胶囊，以 Top 10 榜单代替）
- [ ] 每个章节有 PART 0X 编号
- [ ] 每段有下划线关键词
- [ ] 结尾三连 CTA 存在
- [ ] 所有图片 src 为相对路径且文件存在
- [ ] 无 `<style>/<class>/grid/position:fixed`
- [ ] validate_gzh_html.py 输出 0 ERROR

#### 4.2 发布到微信公众号

发布工具会自动执行 HTML 合规校验（dry-run 预检 -> validate_gzh_html.py -> 正式发布）。如需跳过校验强制发布，加 `--skip-validate` 参数。

```powershell
node {PUBLISH_TOOL} "{日期目录}\article.md" "{日期目录}\cover.png" "news"
```

> **排版接入说明**：若 Step 4.1.5 已生成 `article.html`，发布工具会**自动优先使用 `article.html`**（跳过 md-to-wechat 基础渲染），并把 HTML 里的相对路径图片（如 `apple_openai.png`）上传到微信。命令参数不变，仍传 `article.md` 作为主参数（工具内部判断 article.html 是否存在）。若 `article.html` 不存在，回退到 `article.md` + md-to-wechat 渲染。

GitHub 日报将第三个参数改为 `"github"`。

**安全注意**：微信 API 凭证通过外部 .env 文件读取，不写入本 skill。

#### 4.3 强制验收（verify）

1. **强制验收**：`node scripts/verify_publish.js "{日期目录}"`（或 skill 安装路径下的同脚本）
2. **唯一成功标准**：`verify_publish` exit 0 且 `publish_result.json` 含 `media_id`
3. 中间步骤（如单独跑 validate_gzh）失败但最终 publish+verify 成功 → **必须报成功**，禁止把中间错误当最终失败
4. **禁止**返回文章正文

#### 4.4 清理旧日期目录（verify 成功后强制）

**每次发布且 verify 通过后必须执行**（定时 cron 同样强制；失败只记日志，不推翻发布成功）：

```powershell
node {CLEANUP_TOOL}
# 等价：node scripts/cleanup.js
# 预览不删：node scripts/cleanup.js --dry-run
```

**保留策略（写死，勿改口径）**：

| 项 | 规则 |
|----|------|
| 范围 | `{OUTPUT_ROOT}` 与 `{OUTPUT_ROOT_GITHUB}` **各自独立**扫描 |
| 计入 | 仅纯日期夹 `YYYY-MM-DD`；`*-backup*` 等不计入 |
| 今天 | **永不删除**，且不计入「历史数量」 |
| 触发 | 某根目录历史日期夹数量 **≥ 14** |
| 动作 | 删除最早的，**只保留最新 7 个**历史日期夹 |
| 路径来源 | `cleanup.js` 读 `config.md` 的 `OUTPUT_ROOT` / `OUTPUT_ROOT_GITHUB`（可用 `--roots` 覆盖） |

#### 4.5 向用户报告（成功/失败模板强制）

**成功时必须按下面格式回复（缺一不可）**：

```text
✅ StarAI {AI日报|GitHub开源日报} 发布成功
标题：{title}
发布时间：{localDate} {HH:mm}（本地）
media_id：{media_id}
草稿箱：https://mp.weixin.qq.com
查看路径：内容管理 → 草稿箱 → 用标题搜索
```

**失败时**：

```text
❌ StarAI {模式} 发布失败
原因：{一句话}
已完成：{步骤列表}
目录：{日期目录}
```

> HTML 校验优先用：`python "D:\OpenClaw\ai-daily-skill\scripts\validate_gzh_html.py" "article.html"`  
> 路径必须带引号与反斜杠；`publish_article.js` 内已含校验，**可不单独再跑** validate。

---

## 测试模式（不真实发布）

```powershell
cd {WECHAT_DIR}
bun scripts/wechat-api.ts "{日期目录}\article.md" --theme modern --color blue --author "Star_Ai" --summary "测试摘要" --cover "{日期目录}\cover.png" --no-cite --dry-run
```

---

## 风格自定义指南

### 方式一：选择内置风格

1. 浏览 `styles/cover/` 和 `styles/chapter/` 目录下的 .md 文件
2. 打开每个文件看风格特点和适用场景
3. 在 `config.md` 中填写 `COVER_STYLE` 和 `CHAPTER_STYLE`

### 方式二：手动创建自定义风格

1. 复制 `styles/cover/` 或 `styles/chapter/` 下的任意一个文件
2. 改个名字（如 `my-style.md`）
3. 修改文件内容中的风格规则（配色、字体、背景、装饰等）
4. 在 `config.md` 中填入你的风格文件名（不含扩展名）

### 方式三：AI 生成风格（推荐）

用一句话描述你想要的风格，让 AI 自动生成一套风格文件：

> "帮我生成一套赛博朋克风格的封面风格，主色用霓虹紫，要有故障艺术效果"

AI 会：
1. 根据你的描述生成完整的风格文件（包含配色方案、装饰元素池、Prompt 模板）
2. 保存到 `styles/cover/` 或 `styles/chapter/` 目录
3. 自动在 `config.md` 中更新对应的风格字段

**风格描述参考**：
- 配色方向：主色 + 辅色 + 背景色（如"主色用薄荷绿，辅色用暖橙，白色背景"）
- 视觉风格：极简/杂志/手绘/科技/赛博/水彩/油画/扁平
- 氛围感：干净/活泼/沉稳/未来感/温暖
- 参考品牌：像 Apple 官网/像小米海报/像抖音风格

### 风格文件结构

每个风格文件应包含：
- 基础固定规则（画面比例、整体氛围）
- 标题生成规则（字体、色彩方案）
- 背景/装饰元素随机池
- Prompt 模板或组装规则
- 最终校验规则

---

## 故障排除

详细故障排除见 `references/troubleshooting.md`。

## CHANGELOG

### v2.6.1 (2026-07-14)
- **热度质量**：`heat-track.md` §1.5 明确「够热」三问 + 多形态样例（额度等只是校准样例，禁止锁死单一细类）
- 选题多样性：前 5～8 条尽量 ≥3 种热度形态；禁止整期额度专题或整期冷门开源
- `init_heat_track.js` 的 plan 写入 `heat_quality` 供 Agent 对照；关键词增加实测/下线/产品名等讨论向种子

### v2.6.0 (2026-07-14)
- **热度轨**：AI 日报以抖音/小红书/B站/X 等平台热议为选题主轴；aihot 等为一手核实轨
- 新增 `references/heat-track.md`、`scripts/init_heat_track.js`、`scripts/merge_daily_bundle.js`
- `config.md`：`HEAT_TRACK` / `HEAT_PLATFORMS` / `HEAT_KEYWORDS` 等
- 文章模板增加强制 **【今日热议】**；写作主输入改为 `daily_bundle.json`
- 平台失败可降级 aihot，但禁止伪装成平台热搜

### v2.5.2 (2026-07-14)
- **目录清理收进 skill**：`scripts/cleanup.js` 从 `config.md` 读 `OUTPUT_ROOT` / `OUTPUT_ROOT_GITHUB`
- **保留策略**：每个输出根目录独立；历史 `YYYY-MM-DD` ≥14 时只保留最新 7 个；今天永不删；backup 名不计入
- **流程强制**：verify 成功后必须执行 cleanup（失败不推翻发布成功）
- **开源首次引导**：`config.example.md`；首次必读要求自建输出文件夹 + `cleanup --dry-run` 自检
- `fetch_ai_daily.js` 省略参数时读 config 的 OUTPUT_ROOT，不再硬编码本机盘符

### v2.5.1 (2026-07-13)
- **成功通知模板**：标题 + 本地发布时间 + media_id + 草稿箱链接；最终以 verify_publish 为准，中间工具失败不算整单失败
- validate 路径必须加引号：`python "D:\OpenClaw\ai-daily-skill\scripts\validate_gzh_html.py" "..."`（避免 `\` 被吞）
- **同一对话框生图**：batch/gen 保存并复用 `_doubao_chat_url.txt`；禁止循环 doubao_gen 新开会话
- 禁止 agent 执行 Get-Process/Stop-Process/taskkill msedge（会导致生图页被关）
- 修 cron 假成功：强制 `verify_publish.js`；禁止 PowerShell 解析 JSON
- 新增 `scripts/fetch_ai_daily.js`（本地日期 + Node 抓 aihot）
- 分析报告不得作为最终产出

### v2.5.0 (2026-07-13)
- **无人值守模式**：定时/cron 禁止询问；信息源固定 config；完成定义含 `publish_result.json`
- 废弃并移除 `starai-daily` / `starai-github-daily` / `starai-daily-publish` 旧路径；唯一入口 `ai-daily-skill`（junction：`.openclaw/skills/ai-daily`）
- 触发词增加：定时任务 / cron / 自动发布
- OpenClaw cron 双 job：GitHub 22:00、AI 23:30（Asia/Shanghai）

### v2.4.0 (2026-07-13)
- GitHub 日报结构最终定型（v3）：Top 20 候选池（`fetch_weekly_trending.py` 每 2 天刷新）→ 文章只列【本周 GitHub 热榜 Top 10】排名榜（一行一项目，含本周新增⭐）→ 仅对 2-3 个【本周之星】做 HomeRail 式深度拆解（带配图）→ 结尾。每日只深拆 2-3 个，读 `published_projects.json` 优先选本周未发过的项目，避免重复与信息过载
- 移除【其余热门·中深度解读】段：未被选为本周之星的项目只在 Top 10 榜单中一句话一览，不再另开段落
- GitHub 日报不再含「今日速览」胶囊：Top 10 榜单一览已承担速览职能，typeset_gzh.py 对 GitHub 文章自动跳过今日速览渲染（条件渲染），与 AI 日报（有今日速览）区分
- article-prompt-github.md 同步定稿：开场白去掉今日速览、固定开头改为周榜口径、写作对标 HomeRail 范文（钩子/一句话记住/打个比方/痛点/普通人怎么用/适合谁/说句实话）、全文 3000-5000 字
- SKILL.md 排版说明（Step 4.1.5）同步：今日速览胶囊标注为条件渲染，GitHub 日报以 Top 10 榜单代替；固定开头口径改为周榜

### v2.1.0 (2026-07-12)
- 集成 HTML 合规校验：发布前自动用 validate_gzh_html.py 检查 HTML 兼容性
- 文章模板增加引言卡、关键词标记、章节编号、中文标点规范
- 风格自定义增加 AI 生成风格选项（方式三）
- publish_article.js 增加 dry-run 预检 + HTML 校验步骤
- 校验脚本来源：gzh-design-skill (AGPL-3.0, isjiamu)

### v2.2.0 (2026-07-12)
- 接入 gzh-design-skill 精致排版：新增 Step 4.1.5，TYPESER=true 时用其组件库把 article.md 排成 article.html（封面卡/目录/引言卡/PART 编号/关键词下划线/三连 CTA），替代 md-to-wechat 基础渲染
- **新增 `scripts/typeset_gzh.py` 转换器**：把 article.md 自动排成摸鱼绿纯片段 article.html（封面卡+目录+引言卡+今日速览胶囊+PART 章节+关键词绿色加粗+三连 CTA），全内联样式+span leaf 包裹，validate_gzh_html.py 校验 0 ERROR
- publish_article.js 改造：优先读 article.html 发布（wechat-api.ts 原生支持 .html 输入并自动上传文中图片），否则回退 article.md
- 新增含图片版预览页生成（embed_images_for_copy.py，base64 内嵌）供手动复制粘贴
- config.md 新增排版配置段：GZH_SKILL_DIR / TYPESER / GZH_THEME

### v2.3.0 (2026-07-13)
- GitHub 日报数据源重构为「周榜 Top 10 by 本周新增 Star」：新增 `scripts/fetch_weekly_trending.py` 多后端可切换数据层（html_fallback 默认 / ossinsight / github_api / aihot 交叉验证）
- 抓取-校验节奏状态机：Day1 建池 → Day2/3 复用 → 每 TRENDING_VERIFY_INTERVAL 天重抓 diff，低频（≈3次/周）化解日报+周榜矛盾
- AI 过滤改"来源策展"思路（逆向 aihot 方法论）：GitHub topics 白名单 + 可信组织名单定义"什么是 AI"，aihot 公开 API 作交叉验证信号，LLM 编辑门（写文章阶段）剔除玩具/demo/跑题，不再靠脆弱关键词正则
- article-prompt-github.md 重写为周榜结构：新增【本周 GitHub 热榜 Top 10】排名榜 + 【本周之星】2-3 个对标 HomeRail 深度拆解（标注本周新增⭐）；当时另含【其余热门】中深度解读段（该段已在 v2.4.0 移除，改由 Top 10 榜单一句话一览替代），每个项目展示本周新增⭐
- typeset_gzh.py 新增有序列表（排名榜）渲染组件，兼容 Top 10 榜单
- 发布链路不变（publish_article.js 优先 article.html），仍受公众号 IP 白名单外部门约束

### v2.0.0 (2026-07-10)
- 风格系统：封面和配图风格参数化，用户可在 config.md 中选择或自定义
- 内置 4 套封面风格 + 4 套配图风格
- 新增 config.md 用户配置文件
- 新增风格自定义指南

### v1.1.0 (2026-07-10)
- 信息源改为向用户主动询问
- 所有本地路径参数化
- 加 license: MIT

### v1.0.0 (2026-07-10)
- 基于 starai-daily-publish v3.0.0 重新构建为独立 skill
- 精简为 4 步工作流
