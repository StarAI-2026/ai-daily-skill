#!/usr/bin/env node
/**
 * 初始化热度轨计划与 heat_track.json 骨架
 *
 * 用法:
 *   node init_heat_track.js <日期目录>
 *   node init_heat_track.js <日期目录> --config-md <path>
 */
'use strict';

const fs = require('fs');
const path = require('path');

function localDateYmd() {
  return new Date().toLocaleDateString('sv-SE');
}

function parseConfigMd(configPath) {
  const text = fs.readFileSync(configPath, 'utf8');
  const out = {};
  // **KEY**: `value`  or **KEY**: value
  const re = /\*\*([A-Z0-9_]+)\*\*\s*:\s*`?([^`\n]+?)`?\s*$/gm;
  let m;
  while ((m = re.exec(text)) !== null) {
    out[m[1]] = m[2].trim();
  }
  return out;
}

function parseList(s, fallback) {
  if (!s || s === '""' || s === "''") return fallback;
  return s
    .split(/[,，]/)
    .map((x) => x.trim())
    .filter(Boolean);
}

function parseBool(s, def) {
  if (s == null || s === '') return def;
  const v = String(s).trim().toLowerCase();
  if (['true', '1', 'yes', 'on'].includes(v)) return true;
  if (['false', '0', 'no', 'off'].includes(v)) return false;
  return def;
}

function parseIntSafe(s, def) {
  const n = parseInt(String(s || ''), 10);
  return Number.isFinite(n) && n > 0 ? n : def;
}

function main() {
  const args = process.argv.slice(2);
  let outDir = null;
  let configMd = path.resolve(__dirname, '..', 'config.md');
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--config-md' && args[i + 1]) {
      configMd = path.resolve(args[++i]);
    } else if (!args[i].startsWith('-')) {
      outDir = path.resolve(args[i]);
    }
  }
  if (!outDir) {
    console.error('用法: node init_heat_track.js <日期目录> [--config-md path]');
    process.exit(1);
  }
  if (!fs.existsSync(configMd)) {
    console.error('config.md 不存在:', configMd);
    process.exit(1);
  }

  const cfg = parseConfigMd(configMd);
  const enabled = parseBool(cfg.HEAT_TRACK, true);
  const platforms = parseList(cfg.HEAT_PLATFORMS, [
    'xiaohongshu',
    'bilibili',
    'douyin',
    'x',
  ]);
  const keywords = parseList(cfg.HEAT_KEYWORDS, [
    'AI',
    'GPT',
    'Claude',
    '豆包',
    '千问',
    'Agent',
    'Codex',
    '实测',
    '下线',
    '封号',
    'AI视频',
    '智能体',
  ]);
  const topPer = parseIntSafe(cfg.HEAT_TOP_PER_PLATFORM, 3);
  const maxTotal = parseIntSafe(cfg.HEAT_MAX_TOTAL, 8);
  const requireVerify = parseBool(cfg.HEAT_REQUIRE_VERIFY, true);

  fs.mkdirSync(outDir, { recursive: true });

  const plan = {
    schema: 'heat_track_plan/v1',
    localDate: localDateYmd(),
    enabled,
    platforms,
    keywords,
    top_per_platform: topPer,
    max_total: maxTotal,
    require_verify: requireVerify,
    heat_quality: {
      goal: '普通人会刷到、会讨论的高热 AI 话题；禁止只堆单一细类',
      checklist: [
        '普通人在不在乎（会截图转发吗）',
        '平台上是不是很多人在聊',
        '和「我今天用 AI」有没有关系',
      ],
      diversity:
        '前 5～8 条尽量覆盖 ≥3 种形态：产品突变/权益与可用/全网实测/工具入口/安全避坑/内容玩法/情绪社会等',
      anti_patterns: [
        '整期只写额度/会员/计费',
        '整期只写冷门开源发版',
        '把 aihot 列表原样当热榜',
      ],
      note: '某类样例（如额度重置）只用于校准「什么叫热」，不是唯一栏目',
    },
    search_queries: platforms.flatMap((p) =>
      keywords.slice(0, 8).map((k) => ({
        platform: p,
        query: k,
        hint:
          p === 'xiaohongshu'
            ? `小红书搜索「${k}」按热度看笔记；再补「实测/下线/避坑」等讨论向`
            : p === 'bilibili'
              ? `B站搜索「${k}」综合/热门；优先高播放讨论视频而非纯教程课`
              : p === 'douyin'
                ? `抖音搜索「${k}」看高赞话题`
                : p === 'x'
                  ? `X/Twitter search ${k} AI`
                  : `搜索 ${p} ${k}`,
      }))
    ),
    instructions_file: 'references/heat-track.md',
    output_file: 'heat_track.json',
  };

  const planPath = path.join(outDir, 'heat_track_plan.json');
  fs.writeFileSync(planPath, JSON.stringify(plan, null, 2), 'utf8');

  const skeletonPath = path.join(outDir, 'heat_track.json');
  if (!fs.existsSync(skeletonPath)) {
    const skeleton = {
      schema: 'heat_track/v1',
      localDate: localDateYmd(),
      enabled,
      platforms_requested: platforms,
      platforms_failed: [],
      topics: [],
      notes: enabled
        ? 'Agent：按 heat_track_plan.json 检索后填写 topics[]'
        : 'HEAT_TRACK=false，可跳过热度轨',
    };
    fs.writeFileSync(skeletonPath, JSON.stringify(skeleton, null, 2), 'utf8');
  }

  console.log('wrote', planPath);
  console.log('heat_track', skeletonPath);
  console.log('enabled', enabled);
  console.log('platforms', platforms.join(','));
  console.log('keywords', keywords.join(','));
  console.log('queries', plan.search_queries.length);
  if (!enabled) {
    console.log('HEAT_TRACK=false — agent may skip platform search');
  }
}

main();
