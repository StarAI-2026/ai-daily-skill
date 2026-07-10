#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""GitHub日报增强功能工具集"""
import os
import json
from datetime import datetime

def generate_batch_config(save_dir, content_categories):
    """生成图片批量配置，每个分类对应不同风格的配图"""
    style_config = {
        "今日头条": "科技感十足的新闻封面，深色背景，蓝色光效，未来感",
        "GitHub热门": "简约扁平化风格，GitHub元素，代码图标，明亮配色",
        "大模型更新": "科技风，大脑/神经网络元素，蓝紫色渐变背景",
        "AI工具上新": "清新简约风格，工具图标，明亮轻快配色",
        "AI绘画进展": "艺术感，画笔/调色板元素，多彩渐变背景",
        "AI编程突破": "代码风格，键盘/编辑器元素，深色背景亮色代码",
        "行业动态": "商务新闻风格，简洁专业，蓝色系配色",
        "研究突破": "学术风格，实验室/论文元素，简约专业",
        "封面": "大气科技感日报封面，包含'GitHub日报'字样，AI元素，未来感，适合公众号封面尺寸"
    }
    
    batch_config = []
    # 封面
    batch_config.append({
        "name": "cover",
        "prompt": style_config["cover"] + f"，日期：{datetime.now().strftime('%Y年%m月%d日')}"
    })
    
    # 每个分类的配图
    for category in content_categories:
        if category in style_config:
            batch_config.append({
                "name": category.replace(" ", "_"),
                "prompt": style_config[category]
            })
    
    # 保存配置
    config_path = os.path.join(save_dir, "_batch_config.json")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(batch_config, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 图片配置文件已生成: {config_path}")
    return config_path

def generate_short_content(article_path, save_dir):
    """生成短文案，适合朋友圈/小红书发布"""
    with open(article_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 提取标题和核心亮点
    import re
    title_match = re.search(r'title: (.*?)\n', content)
    title = title_match.group(1) if title_match else "今日AI日报"
    
    # 提取前3条亮点
    highlights = re.findall(r'### (.*?)\n', content)[:3]
    
    short_text = f"""{title}

今日科技亮点：
"""
    for i, h in enumerate(highlights, 1):
        short_text += f"{i}. {h}\n"
    
    short_text += "\n全文在公众号，欢迎关注获取每日AI前沿~\n#AI #科技 #开源 #程序员"
    
    # 保存
    short_path = os.path.join(save_dir, "short_content.txt")
    with open(short_path, "w", encoding="utf-8") as f:
        f.write(short_text)
    
    print(f"✅ 短文案已生成: {short_path}")
    return short_text

def save_to_archive(save_dir, date_str):
    """保存到历史存档"""
    archive_dir = "D:/OpenClaw/日报存档"
    os.makedirs(archive_dir, exist_ok=True)
    
    archive_path = os.path.join(archive_dir, f"{date_str}_GitHub日报.md")
    import shutil
    shutil.copy(os.path.join(save_dir, "article.md"), archive_path)
    
    # 更新存档索引
    index_path = os.path.join(archive_dir, "index.json")
    index = []
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            index = json.load(f)
    
    index.insert(0, {
        "date": date_str,
        "path": archive_path,
        "title": open(os.path.join(save_dir, "article.md"), "r", encoding="utf-8").readline().replace("#", "").strip()
    })
    
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已存档到历史记录: {archive_path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 2:
        date_str = sys.argv[1]
    else:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    save_dir = f"D:/OpenClaw/GitHub日报配图/{date_str}"
    if not os.path.exists(save_dir):
        print(f"❌ 目录不存在: {save_dir}")
        exit(1)
    
    # 生成图片配置
    categories = ["今日头条", "GitHub热门", "大模型更新", "AI工具上新", "AI绘画进展", "AI编程突破", "行业动态", "研究突破"]
    generate_batch_config(save_dir, categories)
    
    # 生成短文案
    generate_short_content(os.path.join(save_dir, "article.md"), save_dir)
    
    # 存档
    save_to_archive(save_dir, date_str)
