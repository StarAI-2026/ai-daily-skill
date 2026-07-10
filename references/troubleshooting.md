# 故障排除手册

当全自动发布工作流执行失败时，对照此文档快速排查与解决。

| 问题现象 | 根本原因分析 | 修复方案 / 规避措施 |
| :--- | :--- | :--- |
| **API 请求返回 403 错误** | 微信或 AI HOT API 服务器拦截了无 User-Agent 标头的请求。 | 必须在请求 Headers 中补充类似 `User-Agent: Mozilla/5.0 aihot-skill/0.2.0`。 |
| **新闻数据中文乱码** | PowerShell `Invoke-RestMethod` 编码解析机制缺陷，导致抓取的 UTF-8 中文出现乱码。 | 必须使用 Node.js 脚本来执行 API 请求，并保存为 JSON。 |
| **Edge 调试端口 9222 无法连接** | Edge 浏览器没有启用远程调试端口，或者端口被占用。 | 执行 `taskkill /im msedge.exe /f` 关闭浏览器，然后用调试参数 `msedge.exe --remote-debugging-port=9222 --remote-allow-origins=*` 重启。 |
| **豆包（doubao.com）提示登录** | Playwright CDP 连接成功，但由于用户在 Edge 中未登录或 Cookie 失效，导致弹出登录框。 | 提醒用户在 Edge 中手动登录 `https://www.doubao.com/chat` 确保能正常聊天，不要在脚本中注入凭证。 |
| **生图任务超时** | 豆包生图在服务器端排队严重，或网络响应过慢，超出脚本预设的等待时间。 | 适当增加 `doubao_batch.js` 的等待超时阈值（如设为 120s）。若依然失败，可考虑使用 `doubao_gen.js` 对失败的图片单独补生成。 |
| **生图只有 384x216 大小** | 获取的是豆包页面预览图，并非高清原图。 | 必须在 `doubao_batch.js` 脚本中触发“下载原图”的点击事件，获取完整质量的大图（~5MB）。 |
| **微信发布失败：标题过长** | 微信接口对文章标题有严格的字节数限制（最大 64 字节）。 | 缩短文章的 `title` 字段（建议在 20 个汉字以内）。 |
| **微信发布失败：图片缺失** | 文章 Markdown 中引用的配图文件名与实际生成的 PNG 文件不匹配。 | 确认引用路径大小写敏感，且文件确实存在于发布目录下。只能引用 `_image_manifest.json` 中标记为 `success` 或 `skipped` 的图片。 |
