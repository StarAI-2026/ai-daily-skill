---
name: ai-daily
description: "AI日报全自动发布。当用户说'发布日报'/'写日报'/'StarAI日报'/'生成日报'/'公众号日报'/'发布GitHub日报'/'StarAI开源日报'/'GitHub热门项目'时自动执行4步：抓取新闻数据→批量生成封面+章节配图→写文章→发布到微信公众号并返回media_id。独立skill，全部逻辑自包含，不依赖其他skill。配置已参数化，可直接开源。"
version: 1.1.0
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

将 AI 资讯转化为 B站科技UP主风格文章，配豆包生成的封面图和章节配图，发布到微信公众号。

**独立技能**：所有逻辑自包含，不依赖其他 skill 配合。4 步完成从新闻到发布。
**可开源**：所有环境相关路径/凭证均参数化，不含任何硬编码敏感信息。

## 语言

使用用户的语言回复。技术术语（路径、参数名）保持英文。

---

## 用户配置（首次使用前请修改为本机实际值）

本 skill 不含任何硬编码本地路径。以下变量在执行时会按此处的值替换。开源前请把下方示例值换成你自己的路径并删除示例中的真实凭证。

| 变量 | 示例值（当前测试机） | 说明 |
|------|----------------------|------|
| `{OUTPUT_ROOT}` | `D:\OpenClaw\AI日报配图` | AI日报的输出根目录，按日期建子目录 |
| `{OUTPUT_ROOT_GITHUB}` | `D:\OpenClaw\GitHub日报配图` | GitHub日报的输出根目录 |
| `{EDGE_PATH}` | `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe` | 本机 Edge 可执行文件路径 |
| `{NODE_MODULES}` | `C:\Users\23736\AppData\Roaming\npm\node_modules` | 全局 npm node_modules 路径 |
| `{DOUBAO_BATCH}` | `D:\OpenClaw\doubao_batch.js` | 批量生图脚本 |
| `{DOUBAO_GEN}` | `D:\OpenClaw\doubao_gen.js` | 单图补生成脚本 |
| `{PUBLISH_TOOL}` | `D:\OpenClaw\workspace\skills\daily-folder-cleanup\publish_article.js` | 发布工具脚本 |
| `{CLEANUP_TOOL}` | `D:\OpenClaw\workspace\skills\daily-folder-cleanup\cleanup.js` | 目录清理脚本 |
| `{WECHAT_DIR}` | `D:\OpenClaw\workspace\skills\baoyu-post-to-wechat` | 微信发布脚本所在目录 |
| `{WECHAT_SCRIPT}` | `{WECHAT_DIR}\scripts\wechat-api.ts` | 微信草稿发布脚本（支持 --dry-run） |

> **开源注意**：以上脚本（doubao_batch.js / publish_article.js / wechat-api.ts 等）不在本 skill 仓库内，属于外部工具依赖。开源时应在 README 中列出这些工具的获取方式，或者把它们一并打包进 skill。

## 日报类型（两种模式，默认 AI 日报）

| 配置项 | AI 日报 | GitHub 日报 |
|--------|---------|------------|
| 触发词 | 发布日报 / StarAI日报 / 生成日报 | 发布GitHub日报 / StarAI开源日报 |
| 输出根目录 | `{OUTPUT_ROOT}` | `{OUTPUT_ROOT_GITHUB}` |
| 文章模板 | `references/article-prompt-ai.md` | `references/article-prompt-github.md` |
| 固定开头 | 「欢迎来到StarAI日报，请查收今日AI圈热门动态。」 | 「欢迎来到StarAI开源日报，请查收今日GitHub热门AI项目。」 |
| 日报气泡 | `StarAI日报，今日AI资讯` | `GitHub 日报，今日AI项目热点` |

## References（本 skill 自带，按需读取）

| 文件 | 何时读取 |
|------|----------|
| `references/cover-prompt.md` | Step 2 生成封面提示词时 |
| `references/chapter-image-spec.md` | Step 3 生成章节配图提示词时 |
| `references/article-prompt-ai.md` | Step 4 生成 AI 日报文章时 |
| `references/article-prompt-github.md` | Step 4 生成 GitHub 日报文章时 |
| `references/title-generator.md` | Step 4 生成文章标题时 |
| `references/copywriting-guide.md` | Step 4 优化标题和导语时 |
| `references/troubleshooting.md` | 遇到问题时查阅 |

---

## 5 条铁律（触发本技能时必须遵守）

1. **端到端流程**：4 步必须全部执行。用户说"发布日报"就是要发布到微信公众号，不是只生成文章。
2. **禁止把文章正文贴到对话回复里**：文章保存为 `article.md` 文件，通过发布工具上传。对话回复只返回 media_id 和发布报告。
3. **禁止询问用户"是否要发布"**：用户说"发布日报"就已确认发布意图。信息源询问（Step 1）不是发布确认。
4. **用批量脚本一次性生图**：禁止逐张循环（浏览器反复开关），必须一次性批量生成。
5. **完成后返回 media_id**：发布成功后返回 media_id + 草稿箱链接。

## 失败模式自检（每次执行前过一遍）

- ❌ 把文章正文作为对话回复 = 失败
- ❌ 只生成图片不发布 = 失败
- ❌ 询问用户"是否要发布" = 失败
- ❌ 描述发布流程但不执行命令 = 失败
- ❌ 用单图脚本循环生成每张图片 = 失败
- ✅ 调用发布工具返回 media_id = 成功
- ✅ 用批量脚本一次生成所有图片 = 成功

---

## 生图脚本说明

**批量生图脚本（{DOUBAO_BATCH}）自己管理浏览器**：它用 `launchPersistentContext` 启动独立的 EdgeProfile，**不需要检查或手动启动 9222 调试端口**。

agent 不需要做任何浏览器准备工作。直接写好 `_batch_config.json` 然后执行批量生图命令即可。脚本会自动：
- 检查 EdgeProfile 登录态（Cookies 文件是否存在且 > 10KB）
- 关闭已运行的 EdgeProfile Edge 进程
- 用 `launchPersistentContext` 启动新的 Edge 实例
- 打开豆包图像生成页并在同一对话中连续生成所有图片

**如果 EdgeProfile 未登录**（脚本会报错提示），需要手动登录一次：
`Start-Process {EDGE_PATH} -ArgumentList --user-data-dir=D:\\OpenClaw\\EdgeProfile, https://www.doubao.com/chat`
登录 doubao.com 后关闭 Edge，之后再跑生图命令即可。

---

## 4 步工作流

### Step 1: 找新闻（信息源决策）

**判断逻辑**：先检查用户指令中是否已包含信息源描述，有则跳过询问直接执行，无则向用户询问。

#### 1A. 检查指令中是否已指定信息源

如果用户的触发指令中已经明确说了信息源方式或搜索内容，**直接跳过询问，按指令中指定的方式执行**。识别规则：

- 提到 API 名称或 URL（如 aihot、aihot.virxact.com、/api/public/daily）-> 方式 A（公开 API）
- 提到网页搜索、web search、GitHub Trending、搜一下 -> 方式 B（网页搜索）
- 直接贴了新闻/事件文本 -> 方式 C（手动输入）
- 提到用我的 API、用这个命令、跑这个 URL -> 方式 D（自定义）
- 指令里带了主题/关键词/领域（如只看模型发布、编程工具相关）-> 作为 Q2 的答案

**示例**：
- 用 aihot 公开 API 抓取今天的数据，发布今天的 StarAI 日报 -> 方式 A，Q2 用默认
- 发布今天的 StarAI 日报，信息源用公开 API，搜索今天 AI 圈热门新闻 -> 方式 A，Q2 已指定
- 发布 GitHub 日报，用网页搜索搜今日 AI 开源项目 -> 方式 B，Q2 已指定

#### 1B. 指令中未指定信息源时，向用户询问

如果用户只说了发布日报而没说信息源，用 request_user_input 工具或自然语言询问两个问题：

**Q1：信息获取方式**
- A. 公开 API（如 aihot.virxact.com/api/public/daily）- 自动抓取，无需登录
- B. 网页搜索（web_search / WebFetch）- 通用，可搜任意关键词
- C. 手动输入热点列表 - 用户直接贴新闻/事件文本
- D. 自定义 API/命令 - 用户提供自己的数据源 URL 或命令

**Q2：搜索什么信息**（自由文本）
- 询问用户想覆盖的主题/关键词/领域/时间范围
- AI 日报默认示例：今天 AI 圈的热门新闻、模型发布、工具更新
- GitHub 日报默认示例：今日 GitHub 上与 AI/LLM/agent/编程工具相关的热门项目
- 用户可以指定更聚焦的范围，如：只看中国 AI 公司的动态 / 只看编程工具相关

#### 1C. 执行抓取

**方式 A：公开 API**

```powershell
# 1. 创建当日目录
$date = Get-Date -Format "yyyy-MM-dd"
$dir = "{OUTPUT_ROOT}\$date"   # GitHub日报用 {OUTPUT_ROOT_GITHUB}
New-Item -ItemType Directory -Force -Path $dir | Out-Null

# 2. 抓取数据（必须用 Node.js，PowerShell 会中文乱码）
node -e "const https=require('https');const fs=require('fs');https.get({hostname:'aihot.virxact.com',path:'/api/public/daily',headers:{'User-Agent':'Mozilla/5.0 aihot-skill/0.2.0'}},r=>{let d='';r.on('data',c=>d+=c);r.on('end',()=>{fs.writeFileSync(process.argv[1]+'/raw_daily.json',d);console.log('data len:'+d.length);const j=JSON.parse(d);console.log('Date:'+j.date);console.log('Sections:'+j.sections.map(s=>s.label+':'+s.items.length).join(', '));})}).on('error',e=>console.error(e.message));" "$($dir -replace '\\','/')"
```

**方式 B：网页搜索**

使用 web_search 工具按用户给的关键词搜索，然后用 WebFetch 抓取具体页面内容。整理筛选后保存为 `{dir}/raw_topics.json`，结构同下。

**方式 C：手动输入**

读取用户贴入的热点/事件文本，整理为统一 JSON 结构保存为 `{dir}/raw_topics.json`。

**方式 D：自定义 API/命令**

按用户提供的 URL 或命令执行，保存原始响应到 `{dir}/raw_daily.json` 或 `raw_topics.json`。

**统一数据结构**（方式 B/C/D 整理时应遵循）：

```json
{
  "date": "2026-07-10",
  "sections": [
    { "label": "头条", "items": [{ "title": "...", "summary": "...", "url": "..." }] }
  ]
}
```

**目录清理（可选）**：创建新目录后调用清理脚本（仅在目录总数达 14 个时才真正删除最早的 7 个）：

```powershell
node {CLEANUP_TOOL}
```

若清理脚本不存在则跳过，不阻塞流程。

**输出物**：`{日期目录}/raw_daily.json` 或 `raw_topics.json`

---

### Step 2: 生成封面

#### 2.1 生图脚本自管理浏览器

批量生图脚本（`{DOUBAO_BATCH}`）会自己启动和管理 Edge 浏览器（用独立的 EdgeProfile），**agent 不需要检查端口或手动启动 Edge**。直接进入 2.2 生成提示词即可。

#### 2.2 生成封面提示词

1. **读取** `references/cover-prompt.md` 获取完整的暗黑泼墨标题封面生成指令
2. 从 Step 1 的数据中提取核心事件、用户价值、风险/提示
3. 按指令中的标题生成规则生成 3 组标题（主标题+副标题+强调词），随机选 1 组
4. 从指令中的各随机池（背景样式、人物全维度、文字视觉、装饰元素）独立抽取参数
5. 根据日报类型选择右上角固定气泡文案（AI日报 / GitHub日报）
6. 组装成完整的中文生图 prompt，按指令中的校验规则自检
7. 文件名固定为 `cover`，type 为 `"cover"`

**封面风格**：暗黑泼墨标题（右人物辅助 + 左标题核心，电影黑场质感）。**章节配图不能用此风格，必须用酸性野兽派。两种风格不可混用。**

#### 2.3 写入封面配置

封面图的配置先单独准备好（Step 3 会和章节配图一起写入完整批量配置并一次性生成）：

```json
{
  "name": "cover",
  "event": "封面 - [文章主标题]",
  "type": "cover",
  "prompt": "[按 cover-prompt.md 生成的完整中文提示词]"
}
```

---

### Step 3: 每个事件生成配图

#### 3.1 生成章节配图提示词

1. **读取** `references/chapter-image-spec.md` 获取酸性野兽派章节配图规范
2. 为**每个事件**（包括「今日之星」「重点推荐」「值得关注」所有板块）生成章节配图提示词：
   - 根据 4 种内容图类型选择之一（事件/过程、人物/产品、数据/对比、场景/概念）
   - 按 chapter-image-spec.md 中的 Prompt 模板填充占位符
   - 文件命名：`{主题关键词}.png`（如 `grok45.png`、`gpt_live.png`）

**酸性野兽派风格核心语汇**（仅用于章节配图）：
- 背景：粗野厚涂色块拼贴、撕裂锯齿边缘、马克笔涂鸦笔触
- 核心主体：图像主导（流程图/概念图/数据图），文字仅 1-2 个关键词点睛
- 装饰元素简化为 2 种：半色调圆点贴纸 + 错版印刷重影
- 配色与封面同色系但降低饱和度 30%
- **画面中不出现任何人物**

#### 3.2 写入完整批量配置

将封面 + 所有章节配图合并写入 `_batch_config.json`：

```json
[
  {
    "name": "cover",
    "event": "封面 - [文章主标题]",
    "type": "cover",
    "prompt": "[封面提示词]"
  },
  {
    "name": "grok45",
    "event": "Grok 4.5 发布",
    "type": "chapter",
    "prompt": "[章节配图提示词1]"
  },
  {
    "name": "gpt_live",
    "event": "OpenAI GPT-Live 语音模型",
    "type": "chapter",
    "prompt": "[章节配图提示词2]"
  }
]
```

#### 3.3 执行批量生图

```powershell
$env:NODE_PATH = "{NODE_MODULES}"

# 批量生图（启动一次浏览器，在同一豆包对话中生成所有图片）
node {DOUBAO_BATCH} --config "{日期目录}\_batch_config.json" --output "{日期目录}"
```

脚本行为：
- 启动 Edge 浏览器一次（已登录豆包）
- 在同一豆包对话中连续输入每个提示词
- 每张图保存为 `{name}.png`
- 断点续传：已存在的文件自动跳过
- 完成后自动生成 `_image_manifest.json` 清单

#### 3.4 验证图片清单

> **豆包生图机制**：豆包每次提示词会生成4张候选图，脚本自动收集所有4张请求的响应体，选择最大的一张保存。正常原图大小为 3-8 MB，低于 500 KB 的视为缩略图，脚本会自动跳过。

**验证要求**：
- 所有图片状态为 success
- 每张图片 size_mb >= 0.5（即 >= 500 KB）
- 配图数量 = 事件总数（每个事件一张配图 + 1张封面）
- 如有图片 < 0.5 MB 或状态为 failed，必须用单图脚本补生成

读取 `_image_manifest.json` 确认所有图片状态：

```json
{
  "date": "2026-07-10",
  "total": 7,
  "images": [
    { "filename": "cover.png", "type": "cover", "status": "success", "size_mb": 6.5 },
    { "filename": "grok45.png", "type": "chapter", "status": "success", "size_mb": 6.9 }
  ]
}
```

如有失败的图片，用单图脚本补生成：

```powershell
node {DOUBAO_GEN} --prompt "[失败图片的提示词]" --output "{日期目录}"
# 然后重命名生成的文件为正确的文件名
```

---

### Step 4: 写文章 + 发布到公众号

#### 4.1 写文章

1. **读取** 对应日期类型的文章模板（`references/article-prompt-ai.md` 或 `references/article-prompt-github.md`）
2. 将 Step 1 数据 + 深度分析结果替换模板中的占位符，生成文章
3. **读取** `references/title-generator.md` 生成 5 条候选标题
4. **读取** `references/copywriting-guide.md` 优化标题和导语（AIDA 评分选最佳标题）
5. 保存为 `{日期目录}/article.md`

**文章 frontmatter**：

```yaml
---
title: [不超过20字，只讲一件事，悬念结尾]
author: Star_Ai
description: [120字以内的摘要]
---
```

**标题铁律**：
- 不超过 20 个字（微信信息流完整显示）
- 一条标题只聚焦一个新闻点
- 最后 3-5 字制造悬念
- 禁用"炸了""重磅""变天了""火力全开"等失效词

**去 AI 味铁律**：
- 禁用"值得注意的是""综上所述""让我们来看看"
- 禁用 emoji（语音播报读不出）
- 禁用"写在最后"作为结尾标题
- 禁用话题标签（#xxx）

**写作风格**：
- B站科技UP主风格，像聊天一样写
- 口语化连接词："那说实话呢""就是说""说白了""讲真"
- 中国化比喻（小米、华为、比亚迪、大疆等中国品牌）
- 短句为主，每句不超过 25 字
- 全文 3000-5000 字

**图片引用规则**：
- **先读取 `_image_manifest.json` 清单**，按清单中的 filename 引用图片
- 引用路径与清单中的 filename 完全一致（大小写敏感）
- 封面图引用放在文章最前面：`![封面](cover.png)`
- 只引用 `status: "success"` 或 `status: "skipped"` 的图片
- 引用格式：`![描述](grok45.png)`

#### 4.2 发布到微信公众号

**这一步必须实际执行发布命令，不能只描述流程，不能询问用户，不能把文章内容贴到对话里。**

调用发布工具：

```powershell
node {PUBLISH_TOOL} "{日期目录}\article.md" "{日期目录}\cover.png" "news"
```

GitHub 日报将第三个参数改为 `"github"`。

工具行为：
- 自动读取 frontmatter（title、description）
- 自动执行 `bun scripts/wechat-api.ts` 发布命令
- 自动解析并返回 media_id
- 成功后自动更新 counter.json

**绝对禁止**：
- ❌ 调发布工具之后再次写一份 bun 命令
- ❌ 把文章内容作为对话回复发给用户
- ❌ 描述发布流程但不调用工具
- ❌ 询问用户"是否要发布"

**如果调工具失败**：
- 重试一次
- 仍然失败则把失败信息告诉用户（包含具体错误），但不输出文章正文到对话

**CVE 安全注意**（开源相关）：
- 微信 API 凭证（app_id / app_secret）通过外部脚本的环境变量或 .env 文件读取，**不写入本 skill**
- 本 skill 不存任何凭证，开源仓库不应包含 .env 文件

#### 4.3 清理旧目录

发布成功后立即清理：

```powershell
node {CLEANUP_TOOL}
```

清理规则：监控两个输出目录，累计达 14 个日期目录时删除最早的 7 个，保留最近的 7 个。今天的目录永远保留。未达阈值时静默执行。若脚本不存在则跳过。

#### 4.4 向用户报告

发布成功后返回验证报告（不返回文章正文）：

```
AI日报发布完成

发布信息：
  日期: [YYYY-MM-DD]
  标题: [文章标题]
  作者: Star_Ai
  字数: [N] 字
  封面: cover.png ([大小] MB)
  章节配图: [N] 张

文件位置：
  文章: [日期目录]\article.md
  配图: [日期目录]\*.png

微信公众号：
  media_id: [media_id]
  草稿箱: https://mp.weixin.qq.com (内容管理 → 草稿箱)

下一步：在微信公众号后台确认无误后，手动点击"发布"
```

---

## 测试模式（不真实发布）

如需验证发布流程但不实际推送到微信，使用 wechat-api.ts 的 --dry-run 参数：

```powershell
cd {WECHAT_DIR}
bun scripts/wechat-api.ts "{日期目录}\article.md" --theme modern --color blue --author "Star_Ai" --summary "测试摘要" --cover "{日期目录}\cover.png" --no-cite --dry-run
```

--dry-run 模式只解析和渲染文章，不调用微信 API，不产生草稿。

---

## 使用示例

### 完整自动化执行

用户说："发布今天的 StarAI 日报"

执行流程：
1. 询问用户信息源（方式+关键词）→ 按选择抓取 → `raw_daily.json` + 创建日期目录
2. 读取 cover-prompt.md 生成封面提示词
3. 读取 chapter-image-spec.md 为每个热点生成配图提示词 → 合并写入 _batch_config.json → 批量脚本一次性生成 → 验证 _image_manifest.json
4. 读取 article-prompt-ai.md 写 article.md → 调发布工具 → 返回 media_id

### GitHub 日报执行

用户说："发布 GitHub 日报"

同上流程，数据源按用户选择的方式抓取 GitHub 相关内容，输出目录改为 `{OUTPUT_ROOT_GITHUB}`。

### 仅生成文章不发布

用户说："生成今天的日报文章，先不要发布"

执行 Step 1-4.1，跳过 4.2-4.4。

### 仅发布已有文章

用户说："发布昨天生成好的日报"

跳过 Step 1-3，直接执行 Step 4.2-4.4，指定 article.md 路径。

---

## 故障排除

详细故障排除见 `references/troubleshooting.md`。常见问题：

| 问题 | 解决方案 |
|------|----------|
| API 返回 403 | 必须带浏览器 User-Agent |
| 数据中文乱码 | 必须用 Node.js 而非 PowerShell 的 Invoke-RestMethod |
| EdgeProfile 未登录 | 手动用 EdgeProfile 启动 Edge 登录 doubao.com 一次 |
| 豆包未登录 | 在 Edge 中手动登录 doubao.com |
| 配图生成超时 | 等待更长时间（最多 120 秒），或跳过配图 |
| 图片是缩略图 | 走"下载原图"流程获取原图 |
| 标题超 64 字节 | 缩短标题（约 20 个中文字符） |
| 图片文件不存在 | 文章引用了未生成的图片，需补生成或删除引用 |
| API 凭证缺失 | 在外部 wechat-api.ts 的 .env 中配置，不在本 skill 内 |

---

## 开源指南

本 skill 可直接开源到 GitHub。注意事项：

1. **不提交凭证**：`.env`、`app_secret`、`access_token` 等一律加入 .gitignore
2. **参数化路径**：所有环境相关的路径用 `{OUTPUT_ROOT}` 等占位符，已在上方"用户配置"段落列出
3. **外部脚本依赖**：`doubao_batch.js`、`publish_article.js`、`wechat-api.ts` 等不在本 skill 仓库内，README 中需说明获取方式，或把它们一并打包进 skill
4. **License**：MIT（已在 frontmatter 标明）

## 迭代指南

本 skill 设计为可持续迭代。更新方式：

1. **修改提示词模板**：直接编辑 `references/` 下对应的 .md 文件
2. **修改文章风格**：编辑 `references/article-prompt-ai.md` 或 `article-prompt-github.md`
3. **修改封面设计规则**：编辑 `references/cover-prompt.md`
4. **修改配图规范**：编辑 `references/chapter-image-spec.md`
5. **修改流程逻辑**：编辑本 SKILL.md
6. 每次修改后在下方 CHANGELOG 记录变更

## CHANGELOG

### v1.1.0 (2026-07-10)
- 信息源改为向用户主动询问（方式+搜索什么信息）
- 所有本地路径参数化为 {占位符}，可安全开源到 GitHub
- frontmatter 加 license: MIT
- 增加开源指南段落

### v1.0.0 (2026-07-10)
- 基于 starai-daily-publish v3.0.0 重新构建为独立 skill
- 从外部 skill 依赖改为全部内联 references
- 精简为 4 步工作流（找新闻 → 生成封面 → 生成配图 → 发文章+发布）
- 安装到 `~/.codex/skills/ai-daily/`
- 所有依赖脚本路径已验证可执行
