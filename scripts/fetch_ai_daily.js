#!/usr/bin/env node
/**
 * 抓取 aihot 公开日报 API，写入本地目录 raw_daily.json
 * 使用本地时区日期，禁止 PowerShell ConvertFrom-Json
 *
 * 用法:
 *   node fetch_ai_daily.js [输出目录]
 *   省略目录时默认: D:\OpenClaw\AI日报配图\{本地今天}
 */
const https = require('https');
const fs = require('fs');
const path = require('path');

function localDateYmd() {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

const date = localDateYmd();
const outDir = path.resolve(
  process.argv[2] || path.join('D:', 'OpenClaw', 'AI日报配图', date)
);
const outFile = path.join(outDir, 'raw_daily.json');

fs.mkdirSync(outDir, { recursive: true });

const opts = {
  hostname: 'aihot.virxact.com',
  path: '/api/public/daily',
  headers: { 'User-Agent': 'Mozilla/5.0 aihot-skill/0.2.0' },
};

https
  .get(opts, (res) => {
    let d = '';
    res.on('data', (c) => (d += c));
    res.on('end', () => {
      if (res.statusCode && res.statusCode >= 400) {
        console.error(`HTTP ${res.statusCode}`);
        console.error(d.slice(0, 300));
        process.exit(1);
      }
      let j;
      try {
        j = JSON.parse(d);
      } catch (e) {
        console.error('JSON parse failed:', e.message);
        process.exit(1);
      }
      fs.writeFileSync(outFile, d, 'utf8');
      console.log('wrote', outFile);
      console.log('bytes', Buffer.byteLength(d, 'utf8'));
      console.log('apiDate', j.date || '(none)');
      console.log('localDirDate', date);
      if (Array.isArray(j.sections)) {
        console.log(
          'sections',
          j.sections.map((s) => `${s.label}:${(s.items || []).length}`).join(', ')
        );
      }
      process.exit(0);
    });
  })
  .on('error', (e) => {
    console.error(e.message);
    process.exit(1);
  });
