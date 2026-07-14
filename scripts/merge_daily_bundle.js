#!/usr/bin/env node
/**
 * 合并一手轨(raw_daily) + 热度轨(heat_track) → daily_bundle.json
 *
 * 用法:
 *   node merge_daily_bundle.js <日期目录>
 */
'use strict';

const fs = require('fs');
const path = require('path');

function readJson(p, optional) {
  if (!fs.existsSync(p)) {
    if (optional) return null;
    throw new Error('缺少文件: ' + p);
  }
  return JSON.parse(fs.readFileSync(p, 'utf8'));
}

function main() {
  const outDir = process.argv[2] && path.resolve(process.argv[2]);
  if (!outDir) {
    console.error('用法: node merge_daily_bundle.js <日期目录>');
    process.exit(1);
  }

  const rawPath = path.join(outDir, 'raw_daily.json');
  const heatPath = path.join(outDir, 'heat_track.json');
  const raw = readJson(rawPath, true);
  const heat = readJson(heatPath, true) || {
    schema: 'heat_track/v1',
    topics: [],
    platforms_failed: [],
    notes: 'missing heat_track.json',
  };

  const topics = Array.isArray(heat.topics) ? heat.topics : [];
  const usable = topics.filter((t) => {
    if (t.use_in_article === false) return false;
    const st = (t.verify && t.verify.status) || 'unknown';
    if (st === 'unknown' && t.source_type === 'fallback_aihot') return true;
    if (st === 'rumor') return true;
    if (st === 'confirmed' || st === 'partial') return true;
    // 未填 verify 但有平台信号：仍进入 bundle，写作时降权
    if (t.platforms && t.platforms.length && t.title) return true;
    return false;
  });

  const heatLead = usable.filter((t) => {
    const st = (t.verify && t.verify.status) || '';
    return st === 'confirmed' || st === 'partial' || (t.heat_signal && t.title);
  });

  const bundle = {
    schema: 'daily_bundle/v1',
    localDate:
      heat.localDate ||
      (raw && raw.date) ||
      new Date().toLocaleDateString('sv-SE'),
    tracks: {
      primary_heat: {
        topic_count: topics.length,
        usable_count: usable.length,
        lead_count: heatLead.length,
        platforms_failed: heat.platforms_failed || [],
      },
      secondary_facts: {
        has_raw_daily: !!raw,
        sections: raw && Array.isArray(raw.sections) ? raw.sections.length : 0,
      },
    },
    // 写作优先顺序
    editorial_priority: [
      '1. 用 heat_track 可用话题做【今日热议】与选题主轴',
      '2. 用 raw_daily 核实事实、补次要条目与数据',
      '3. rumor 最多 1 条且必须写「网传/待观察」',
      '4. 禁止伪造平台热度数字',
    ],
    heat_topics: usable,
    heat_all: topics,
    raw_daily: raw,
  };

  const outFile = path.join(outDir, 'daily_bundle.json');
  fs.writeFileSync(outFile, JSON.stringify(bundle, null, 2), 'utf8');
  console.log('wrote', outFile);
  console.log(
    'heat_topics',
    topics.length,
    'usable',
    usable.length,
    'lead',
    heatLead.length
  );
  console.log('has_raw_daily', !!raw);
  if (usable.length === 0) {
    console.log(
      'WARN: no usable heat topics — article should still note heat-track gap'
    );
  }
}

try {
  main();
} catch (e) {
  console.error(e.message || e);
  process.exit(1);
}
