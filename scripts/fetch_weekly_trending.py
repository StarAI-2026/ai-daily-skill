#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_weekly_trending.py — GitHub 周榜热门项目抓取（多后端可切换 + 抓取校验节奏）

设计原则（来自与用户的方案确认）：
1. 多后端可切换（"随时变动 API"）：
   - html_fallback : 爬 github.com/trending?since=weekly（已验证可用，默认主后端）
   - ossinsight    : OSS Insight API（当前端点 404，预留，配 OSSINSIGHT_URL 后可一键启用）
   - github_api    : GitHub 官方 REST（需 GITHUB_TOKEN，按 star 排序的近似榜）
   - aihot         : 非主后端，仅作"质量交叉验证信号"（调用 aihot 公开 API，借其编辑筛选）
2. 过滤（定义权交给白名单 + aihot 编辑，不靠关键词正则）：
   ① 来源策展：GitHub topics 白名单 + 可信组织名单
   ③ aihot 交叉验证：trending repo 若也出现在 aihot selected → aihot_confirmed=True（强信号）
   （② LLM 编辑门在写文章阶段由 Agent 执行，不在本脚本）
3. 抓取-校验节奏状态机（Day1建池→Day2/3复用→Day4再抓diff→之后每2天校验）：
   - 距上次抓取 >= VERIFY_INTERVAL 天 或 --force → 重新抓取并与旧池 diff
   - 无变化则沿用旧池；有变化则刷新
4. 输出：{日期目录}/raw_weekly.json（候选池）+ 持久化状态文件

用法：
  python fetch_weekly_trending.py <输出日期目录> [--force] [--backend html_fallback]
"""
import sys
import os
import re
import json
import argparse
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta

# ===================== 可配置项（也可走环境变量覆盖） =====================
DEFAULT_BACKEND = os.getenv("TRENDING_BACKEND", "html_fallback")
POOL_SIZE = int(os.getenv("TRENDING_POOL_SIZE", "20"))
VERIFY_INTERVAL = int(os.getenv("TRENDING_VERIFY_INTERVAL", "2"))  # 每 2 天校验一次
STATE_FILE = os.getenv("TRENDING_STATE_FILE",
                       os.path.join(os.path.dirname(os.path.abspath(__file__)), ".trending_state.json"))
OSSINSIGHT_URL = os.getenv("OSSINSIGHT_URL", "")      # 例如 https://api.ossinsight.io/v1/...
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

# ① 来源策展：GitHub topics 白名单（结构化元数据，非自由文本正则）
AI_TOPICS_WHITELIST = set(os.getenv("AI_TOPICS_WHITELIST", "").split(",")) if os.getenv("AI_TOPICS_WHITELIST") else {
    "machine-learning", "deep-learning", "ml", "llm", "large-language-models",
    "agent", "agents", "ai-agents", "ai-agent", "rag", "retrieval-augmented-generation",
    "generative-ai", "genai", "diffusion-models", "diffusion", "nlp", "natural-language-processing",
    "computer-vision", "cv", "mlops", "llm-agent", "llm-agents", "mcp", "model-context-protocol",
    "ai", "artificial-intelligence", "neural-network", "transformer", "pytorch", "tensorflow",
    "stable-diffusion", "embedding", "embeddings", "finetuning", "fine-tuning", "prompt-engineering",
    "chatbot", "conversational-ai", "llmops", "speech-recognition", "text-to-speech", "text-generation",
    "image-generation", "multimodal", "vector-database", "knowledge-graph", "reinforcement-learning",
}
# ① 来源策展：可信组织名单（owner 小写匹配）
TRUSTED_ORGS = set(os.getenv("TRUSTED_ORGS", "").split(",")) if os.getenv("TRUSTED_ORGS") else {
    "huggingface", "langchain-ai", "microsoft", "anthropic", "openai", "facebookresearch",
    "google-research", "google", "nvidia", "meta-llama", "llamaindex", "gradio-app",
    "vllm-project", "ollama", "exla", "pytorch", "tensorflow", "deepseek-ai", "qwenlm",
    "modelscope", "bytedance", "tencent", "tencentcloud", "alibaba", "baichuan-inc",
    "sgl-project", "vllm", "guidance-ai", "embedchain", "run-llama", "x-ai", "cohere",
}

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
AIHOT_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"


def _http_get(url, headers=None, timeout=25):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


# ===================== 后端 1：html_fallback（默认主后端） =====================
def fetch_html_weekly():
    """爬 github.com/trending?since=weekly，解析仓库、描述、语言、topics、本周新增star、总star。"""
    url = "https://github.com/trending?since=weekly"
    html = _http_get(url, {"User-Agent": UA})
    repos = []
    # 每个仓库在一个 <article class="Box-row"> 块内
    blocks = re.split(r'<article class="Box-row">', html)[1:]
    for b in blocks:
        # 跳过赞助位
        if "TRENDING_REPO_SPONSOR" in b:
            continue
        # owner/repo：h2 内 <a> 属性顺序不定，href 前可能有 data-* 
        m = re.search(r'<h2[^>]*>\s*<a [^>]*href="/([^"]+)/([^"]+)"', b)
        if not m:
            m = re.search(r'href="/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)"', b)
            if not m:
                continue
        owner, repo = m.group(1), m.group(2)
        if owner == "sponsors":
            continue
        full = f"{owner}/{repo}"
        # 描述：<p class="col-9 color-fg-muted ...">
        dm = re.search(r'<p class="col-9 color-fg-muted[^"]*">\s*(.*?)\s*</p>', b, re.S)
        desc = re.sub(r'<[^>]+>', '', dm.group(1)).strip() if dm else ""
        # 语言
        lm = re.search(r'<span itemprop="programmingLanguage">([^<]+)</span>', b)
        lang = lm.group(1).strip() if lm else ""
        # topics
        topics = re.findall(r'href="/topics/([^"]+)"', b)
        # 总 star：stargazers 链接 </svg> 之后的数字（避免抓到 SVG 坐标）
        sm = re.search(r'href="/[^"]+/stargazers".*?</svg>\s*([\d,]+)', b, re.S)
        total_stars = int(sm.group(1).replace(",", "")) if sm else 0
        # 本周新增 star
        wm = re.search(r'([\d,]+)\s*stars this week', b)
        weekly_stars = int(wm.group(1).replace(",", "")) if wm else 0
        repos.append({
            "full_name": full, "owner": owner, "repo": repo,
            "desc": desc, "lang": lang, "topics": topics,
            "weekly_stars": weekly_stars, "total_stars": total_stars,
            "url": f"https://github.com/{full}",
        })
    return repos


# ===================== 后端 2：ossinsight（预留，端点待确认） =====================
def fetch_ossinsight():
    if not OSSINSIGHT_URL:
        print("[ossinsight] 未配置 OSSINSIGHT_URL，跳过")
        return []
    try:
        data = _http_get(OSSINSIGHT_URL, {"User-Agent": UA})
        # 解析逻辑随真实端点而定，此处仅占位
        print("[ossinsight] 端点已配置但解析未实现，返回空（请按真实响应补充解析）")
        return []
    except Exception as e:
        print(f"[ossinsight] 请求失败: {e}")
        return []


# ===================== 后端 3：github_api（需 token，近似榜） =====================
def fetch_github_api():
    if not GITHUB_TOKEN:
        print("[github_api] 未配置 GITHUB_TOKEN，跳过")
        return []
    try:
        since = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
        url = f"https://api.github.com/search/repositories?q=stars:%3E1000+pushed:%3E{since}&sort=stars&order=desc&per_page=50"
        headers = {"User-Agent": UA, "Authorization": f"Bearer {GITHUB_TOKEN}",
                   "Accept": "application/vnd.github+json"}
        data = json.loads(_http_get(url, headers))
        repos = []
        for it in data.get("items", []):
            repos.append({
                "full_name": it["full_name"], "owner": it["owner"]["login"], "repo": it["name"],
                "desc": it.get("description") or "", "lang": it.get("language") or "",
                "topics": it.get("topics", []), "weekly_stars": 0, "total_stars": it["stargazers_count"],
                "url": it["html_url"],
            })
        return repos
    except Exception as e:
        print(f"[github_api] 请求失败: {e}")
        return []


# ===================== aihot 交叉验证信号 =====================
def fetch_aihot_confirmed_repos():
    """调用 aihot 公开 API 的 selected 条目，提取其中的 github.com/owner/repo 作为已编辑确认集合。"""
    try:
        url = "https://aihot.virxact.com/api/public/items?mode=selected&take=50"
        data = json.loads(_http_get(url, {"User-Agent": AIHOT_UA}))
        confirmed = set()
        for it in data.get("items", []):
            u = it.get("url", "")
            m = re.search(r'github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)', u)
            if m:
                confirmed.add(f"{m.group(1)}/{m.group(2)}")
        print(f"[aihot] selected 中识别出 {len(confirmed)} 个 github repo 作为交叉验证信号")
        return confirmed
    except Exception as e:
        print(f"[aihot] 请求失败（非致命，跳过交叉验证）: {e}")
        return set()


# ===================== 过滤 + 排序 =====================
def apply_filter(repos, aihot_confirmed):
    for r in repos:
        r["aihot_confirmed"] = r["full_name"].lower() in aihot_confirmed
        topics_l = {t.lower() for t in r["topics"]}
        r["topic_hit"] = bool(topics_l & AI_TOPICS_WHITELIST)
        r["org_hit"] = r["owner"].lower() in TRUSTED_ORGS
        r["ai_relevant"] = r["topic_hit"] or r["org_hit"] or r["aihot_confirmed"]
    # 按本周新增 Star 纯降序排（真实周榜排名）；ai_relevant 仅作标记，供写文章时选深度拆解参考
    repos.sort(key=lambda r: -(r["weekly_stars"] or r["total_stars"]))
    return repos


def build_pool(repos):
    """取 Top POOL_SIZE（repos 已在 apply_filter 中按 weekly_stars 降序排好，
    即真实周榜排名）；rank 按此真实顺序赋值。

    注意：不再做 AI-first 重排——重排会破坏周榜排名（高星非白名单项目被挤到后面）。
    “是不是真 AI / 是不是玩具”由写文章阶段的 LLM 编辑门 + aihot 信号裁决，
    而不是在取池阶段用关键字/白名单重排。
    """
    pool = repos[:POOL_SIZE]
    for i, r in enumerate(pool, 1):
        r["rank"] = i
    return pool


# ===================== 状态机：抓取-校验节奏 =====================
def load_state():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def save_state(pool):
    state = {
        "last_crawl": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "pool": pool,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def pool_signature(pool):
    return {r["full_name"]: r["weekly_stars"] for r in pool}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir", help="输出日期目录")
    ap.add_argument("--force", action="store_true", help="强制重新抓取（忽略节奏）")
    ap.add_argument("--backend", default=DEFAULT_BACKEND)
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    state = load_state()
    days_since = None
    if state and state.get("last_crawl"):
        try:
            last = datetime.strptime(state["last_crawl"], "%Y-%m-%d")
            days_since = (datetime.now() - last).days
        except Exception:
            days_since = None

    need_crawl = args.force or (days_since is None) or (days_since >= VERIFY_INTERVAL)
    print(f"[节奏] last_crawl={state.get('last_crawl') if state else None} days_since={days_since} need_crawl={need_crawl}")

    if not need_crawl and state:
        print("[节奏] 沿用旧池（未到校验日）")
        pool = state["pool"]
    else:
        # 1) 主后端抓取
        if args.backend == "ossinsight":
            raw = fetch_ossinsight()
        elif args.backend == "github_api":
            raw = fetch_github_api()
        else:
            raw = fetch_html_weekly()
        print(f"[抓取] 主后端 {args.backend} 返回 {len(raw)} 个仓库")
        if not raw:
            print("[抓取] 主后端为空，回退 html_fallback")
            raw = fetch_html_weekly()
        # 2) aihot 交叉验证
        aihot_confirmed = fetch_aihot_confirmed_repos()
        # 3) 过滤 + 排序 + 取池
        filtered = apply_filter(raw, aihot_confirmed)
        pool = build_pool(filtered)
        # diff 提示
        if state:
            old = pool_signature(state["pool"])
            new = pool_signature(pool)
            added = [k for k in new if k not in old]
            changed = [k for k in new if k in old and new[k] != old[k]]
            print(f"[diff] 新增 {len(added)} 个，star 变化 {len(changed)} 个")
        save_state(pool)

    # 输出 raw_weekly.json
    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "backend": args.backend,
        "pool_size": len(pool),
        "repos": pool,
    }
    out_path = os.path.join(args.out_dir, "raw_weekly.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"[输出] {out_path} ({len(pool)} 个)")

    # 控制台摘要
    print("\n===== 本周 GitHub 热榜候选池 Top 10 =====")
    for r in pool[:10]:
        tag = "AI" if r["ai_relevant"] else "  "
        aih = "✓aihot" if r["aihot_confirmed"] else ""
        print(f"#{r['rank']:>2} [{tag}] {r['full_name']}  +{r['weekly_stars']}⭐(周)  总{r['total_stars']}  {aih}")
        print(f"     {r['desc'][:60]}")


if __name__ == "__main__":
    main()
