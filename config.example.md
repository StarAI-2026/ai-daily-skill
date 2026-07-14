# AI日报 Skill 用户配置（示例）

> **首次使用**：复制本文件为 `config.md`，把所有 `{占位符}` 对应的「你的值」改成你本机路径。  
> 所有路径在执行时由 Agent 读取本文件替换。  
> **不要**把含真实密钥的 `config.md` / `.env` 提交到公开仓库。

## 路径配置

请把以下路径改为你本机的实际值：

| 变量 | 你的值 | 说明 |
|------|--------|------|
| `{OUTPUT_ROOT}` | `C:\path\to\AI日报配图` | AI日报的输出根目录（按日期 `yyyy-MM-dd` 建子目录存封面/配图） |
| `{OUTPUT_ROOT_GITHUB}` | `C:\path\to\GitHub日报配图` | GitHub日报的输出根目录 |
| `{EDGE_PATH}` | `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe` | Edge 浏览器路径 |
| `{EDGE_PROFILE}` | `C:\path\to\EdgeProfile` | Edge 独立 Profile 目录（豆包登录态） |
| `{NODE_MODULES}` | `C:\Users\你的用户名\AppData\Roaming\npm\node_modules` | 全局 npm node_modules 路径 |
| `{DOUBAO_BATCH}` | `C:\path\to\doubao_batch.js` | 批量生图脚本路径 |
| `{DOUBAO_GEN}` | `C:\path\to\doubao_gen.js` | 单图补生成脚本路径（仅应急） |
| `{PUBLISH_TOOL}` | `C:\path\to\publish_article.js` | 发布工具脚本路径 |
| `{CLEANUP_TOOL}` | `C:\path\to\ai-daily-skill\scripts\cleanup.js` | 日期目录清理脚本（建议用 skill 自带） |
| `{WECHAT_DIR}` | `C:\path\to\baoyu-post-to-wechat` | 微信发布脚本所在目录（内含 `.env`） |
| `{GZH_SKILL_DIR}` | `C:\path\to\gzh-design-skill` | gzh-design-skill 安装目录（可选排版） |

### 首次路径引导清单

1. 在资源管理器中创建两个空文件夹（名称自定），分别作为 AI / GitHub 输出根目录  
2. 把上面 `{OUTPUT_ROOT}` / `{OUTPUT_ROOT_GITHUB}` 改成这两个路径  
3. 确保目录可写；定时任务会写入 `{OUTPUT_ROOT}\yyyy-MM-dd\`  
4. 运行一次：`node scripts/cleanup.js --dry-run` 确认能读到路径且无误删  

## 目录保留策略（cleanup.js）

| 项 | 值 |
|----|-----|
| 扫描对象 | 每个 `OUTPUT_ROOT` **独立** |
| 计入规则 | 仅 `YYYY-MM-DD` 纯日期文件夹；`*-backup*` 等不计入 |
| 今天 | **永不删除** |
| 触发 | 某根目录历史日期夹 ≥ **14** |
| 动作 | 删除最早的，**只保留最新 7 个** |
| 调用时机 | 每次发布成功并 verify 之后强制执行 `node {CLEANUP_TOOL}` |

## 风格配置

### 封面风格

**COVER_STYLE**: `dark-ink`

可选：`dark-ink` / `minimalist-tech` / `cyber-neon` / `magazine-editorial`

### 配图风格

**CHAPTER_STYLE**: `acid-brutalist`

可选：`acid-brutalist` / `flat-illustration` / `isometric-tech` / `watercolor-soft`

## 信息源配置

**FIRST_RUN**: `true`

> 首次交互可设 `true` 展示信息源提示；**定时/无人值守必须为 `false`**。

**AI_DAILY_SOURCE**: `A`  
**GITHUB_DAILY_SOURCE**: `A`  
**CUSTOM_KEYWORDS**: `""`

### 热度轨（平台热议 · 选题主轴）

| 配置键 | 示例值 | 说明 |
|--------|--------|------|
| `HEAT_TRACK` | `true` | 是否启用 |
| `HEAT_PLATFORMS` | `xiaohongshu,bilibili,douyin,x` | 可删减平台 |
| `HEAT_KEYWORDS` | `AI,GPT,大模型,Agent,Claude` | 搜索词 |
| `HEAT_TOP_PER_PLATFORM` | `3` | 每平台最多条数 |
| `HEAT_MAX_TOTAL` | `8` | 合并上限 |
| `HEAT_REQUIRE_VERIFY` | `true` | 进正文前核实 |

**HEAT_TRACK**: `true`  
**HEAT_PLATFORMS**: `xiaohongshu,bilibili,douyin,x`  
**HEAT_KEYWORDS**: `AI,GPT,大模型,Agent,Claude,OpenAI`  
**HEAT_TOP_PER_PLATFORM**: `3`  
**HEAT_MAX_TOTAL**: `8`  
**HEAT_REQUIRE_VERIFY**: `true`

## GitHub 周榜抓取配置

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `TRENDING_BACKEND` | `html_fallback` | `html_fallback` / `ossinsight` / `github_api` |
| `TRENDING_POOL_SIZE` | `20` | 候选池大小 |
| `TRENDING_VERIFY_INTERVAL` | `2` | 重抓间隔天数 |

## 微信发布配置

在 `{WECHAT_DIR}/.env`：

```
WECHAT_APP_ID=你的appid
WECHAT_APP_SECRET=你的secret
```

## 排版配置（可选）

| 变量 | 你的值 | 说明 |
|------|--------|------|
| `{GZH_SKILL_DIR}` | `C:\path\to\gzh-design-skill` | 排版 skill 目录 |
| `TYPESER` | `false` | `true` 启用精致排版 |
| `GZH_THEME` | `moyu-green` | 主题名 |
