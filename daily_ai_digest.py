#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""每日 AI 科技热点日报 - 增强版"""
import subprocess
import json
import os
import re
from datetime import datetime
from collections import OrderedDict

# -------------------------- 配置项 --------------------------
# 扩展搜索Query，覆盖更多内容领域
QUERIES = [
    {"name": "今日头条", "query": "AI 大模型 重大发布 2026", "count": 2},
    {"name": "GitHub热门", "query": "GitHub Trending AI 开源项目 2026", "count": 3},
    {"name": "大模型更新", "query": "GPT Claude Gemini Qwen 大模型 更新 2026", "count": 2},
    {"name": "AI工具上新", "query": "AI 效率工具 开源 发布 2026", "count": 2},
    {"name": "AI绘画进展", "query": "AI绘画 Sora DALL-E 3 ComfyUI 新功能 2026", "count": 2},
    {"name": "AI编程突破", "query": "AI编程 Copilot Cursor OpenClaw 新特性 2026", "count": 2},
    {"name": "行业动态", "query": "AI 行业政策 融资 商业化 2026", "count": 2},
    {"name": "研究突破", "query": "AI 论文 研究突破 新技术 2026", "count": 2},
]

# 内容分类标签
TAGS = {
    "大模型": ["大模型", "GPT", "Claude", "Gemini", "Qwen", "Llama"],
    "开源工具": ["GitHub", "开源", "工具", "脚本", "插件"],
    "AI绘画": ["AI绘画", "Sora", "DALL-E", "ComfyUI", "Midjourney"],
    "AI编程": ["AI编程", "Copilot", "Cursor", "OpenClaw"],
    "行业资讯": ["融资", "政策", "商业化", "行业"],
    "研究突破": ["论文", "研究", "技术突破"],
}

# 输出目录配置
OUTPUT_DIR = "D:/OpenClaw/GitHub日报配图"
DATE_STR = datetime.now().strftime("%Y-%m-%d")
SAVE_DIR = os.path.join(OUTPUT_DIR, DATE_STR)
os.makedirs(SAVE_DIR, exist_ok=True)

# -------------------------- 核心功能 --------------------------
def search_content(query, count=3):
    """搜索内容"""
    try:
        cmd = [
            "python", "C:/Users/23736/.claude/skills/bendishousuo/scripts/bendishousuo.py",
            "-q", query, "-n", str(count), "-f", "raw"
        ]
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        data = json.loads(out.stdout)
        return data.get("results", [])
    except Exception as e:
        print(f"搜索失败 [{query}]: {str(e)}")
        return []

def deduplicate_results(results):
    """内容去重"""
    seen_titles = set()
    unique_results = []
    for item in results:
        title = item.get("title", "").strip()
        if not title or title in seen_titles:
            continue
        # 标题相似度过滤
        duplicate = False
        for seen in seen_titles:
            if len(set(title) & set(seen)) / len(set(title)) > 0.7:
                duplicate = True
                break
        if duplicate:
            continue
        seen_titles.add(title)
        unique_results.append(item)
    return unique_results

def get_tags_for_content(title, snippet):
    """给内容打标签"""
    content = f"{title} {snippet}".lower()
    tags = []
    for tag, keywords in TAGS.items():
        for kw in keywords:
            if kw.lower() in content:
                tags.append(f"#{tag}")
                break
    return " ".join(tags[:2]) if tags else ""

def generate_titles():
    """生成3个不同风格的标题供选择"""
    date = datetime.now().strftime("%m月%d日")
    return [
        f"{date} AI日报 | 今日科技热点都在这里了",
        f"{date} 科技前沿 | 8个你不能错过的AI新动态",
        f"AI科技周报[{date}] | 大模型更新/开源工具/行业资讯一网打尽"
    ]

def main():
    print(f"🚀 开始生成 {DATE_STR} GitHub日报...")
    
    # 1. 抓取所有内容
    all_results = OrderedDict()
    total_items = 0
    for q in QUERIES:
        print(f"🔍 正在搜索: {q['name']}")
        results = search_content(q['query'], q['count'])
        unique_results = deduplicate_results(results)
        all_results[q['name']] = unique_results
        total_items += len(unique_results)
    
    print(f"✅ 共抓取到 {total_items} 条内容")
    
    # 2. 生成日报内容
    titles = generate_titles()
    report = f"""---
title: {titles[0]}
alternate_titles:
  - {titles[1]}
  - {titles[2]}
date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
---

# 🤖 {titles[0]}

每日精选AI行业动态、开源工具、技术突破，帮你5分钟掌握科技前沿。

---
"""
    
    # 按分类输出内容
    for category, items in all_results.items():
        if not items:
            continue
        # 分类标题
        category_icons = {
            "今日头条": "🔥",
            "GitHub热门": "⭐",
            "大模型更新": "🤖",
            "AI工具上新": "🛠️",
            "AI绘画进展": "🎨",
            "AI编程突破": "💻",
            "行业动态": "📰",
            "研究突破": "🔬",
        }
        icon = category_icons.get(category, "📌")
        report += f"\n## {icon} {category}\n\n"
        
        for item in items[:2]:  # 每个分类最多显示2条，保证总量
            title = item.get("title", "").strip()
            snippet = item.get("snippet", "").strip()
            url = item.get("url", "")
            tags = get_tags_for_content(title, snippet)
            
            # 清理内容
            snippet = re.sub(r'\s+', ' ', snippet)[:200] + "..." if len(snippet) > 200 else snippet
            
            report += f"### {title}\n"
            if tags:
                report += f"{tags}\n\n"
            report += f"> {snippet}\n"
            if url:
                report += f"\n🔗 [查看详情]({url})\n"
            report += "\n"
    
    # 添加底部内容
    report += """---

## 💡 今日互动

你最想试用上面哪个项目？欢迎在评论区留言~

如果觉得内容有用，欢迎点赞转发，让更多朋友看到科技的力量。
"""
    
    # 3. 保存内容
    article_path = os.path.join(SAVE_DIR, "article.md")
    with open(article_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"✅ 日报生成完成，已保存到: {article_path}")
    print(f"📝 可选标题：")
    for i, t in enumerate(titles, 1):
        print(f"  {i}. {t}")
    
    # 3.5 调用增强工具生成配套资源
    print("\n⚡ 生成配套资源...")
    subprocess.run([
        "python", "D:/OpenClaw/github_daily_enhancer.py", DATE_STR
    ], capture_output=True, text=True)
    
    # 4. 自动触发后续流程（图片生成+发布）
    print("\n🚀 开始触发图片生成流程...")
    try:
        env = os.environ.copy()
        env['NODE_PATH'] = "C:/Users/23736/AppData/Roaming/npm/node_modules"
        subprocess.run([
            "node", "D:/OpenClaw/doubao_batch.js",
            "--config", f"{SAVE_DIR}/_batch_config.json",
            "--output", SAVE_DIR
        ], env=env, timeout=300)
        
        print("🖼️ 图片生成完成，开始发布到公众号...")
        subprocess.run([
            "node", "D:/OpenClaw/workspace/skills/daily-folder-cleanup/publish_article.js",
            f"{SAVE_DIR}/article.md",
            f"{SAVE_DIR}/cover.png",
            "github"
        ], env=env, timeout=120)
        
        print("✅ 全流程执行完成！")
    except Exception as e:
        print(f"❌ 后续流程执行失败: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()
