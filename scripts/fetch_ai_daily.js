#!/usr/bin/env node
/**
 * 抓取 aihot 公开日报 API，写入本地目录 raw_daily.json
 * 使用本地时区日期，禁止 PowerShell ConvertFrom-Json
 *
 * 用法:
 *   node fetch_ai_daily.js <输出目录>
 *   输出目录应由 Agent 按 config.md 的 {OUTPUT_ROOT}\yyyy-MM-dd 传入
 *   省略目录时：尝试读 ../config.md 的 OUTPUT_ROOT + 本地今天；仍失败则报错退出
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

function readOutputRootFromConfig() {
  const configPath = path.resolve(__dirname, '..', 'config.md');
  if (!fs.existsSync(configPath)) return null;
  const text = fs.readFileSync(configPath, 'utf8');
  const m = text.match(/\|\s*`\{OUTPUT_ROOT\}`\s*\|\s*`([^`]*)`\s*\|/);
  return m && m[1] ? m[1].trim() : null;
}

const date = localDateYmd();
let outDir;
if (process.argv[2]) {
  outDir = path.resolve(process.argv[2]);
} else {
  const root = readOutputRootFromConfig();
  if (!root) {
    console.error(
      '用法: node fetch_ai_daily.js <输出目录>\n或先在 config.md 填写 {OUTPUT_ROOT}'
    );
    process.exit(1);
  }
  outDir = path.resolve(root, date);
}
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
