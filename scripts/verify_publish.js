#!/usr/bin/env node
/**
 * 发布完成硬门禁：目录必须有 publish_result.json 且 ok+media_id
 * 用法: node verify_publish.js <日期目录>
 * exit 0 成功 / 1 失败（供 cron/agent 判定，禁止假成功）
 */
const fs = require('fs');
const path = require('path');

const dir = process.argv[2];
if (!dir) {
  console.error('用法: node verify_publish.js <日期目录>');
  process.exit(1);
}

const resultPath = path.join(dir, 'publish_result.json');
const checks = {
  dir: fs.existsSync(dir),
  publish_result: fs.existsSync(resultPath),
  article_md: fs.existsSync(path.join(dir, 'article.md')),
  cover: fs.existsSync(path.join(dir, 'cover.png')),
};

if (!checks.dir) {
  console.error('FAIL: 目录不存在', dir);
  process.exit(1);
}
if (!checks.article_md) console.error('WARN: 缺 article.md');
if (!checks.cover) console.error('WARN: 缺 cover.png');

if (!checks.publish_result) {
  console.error('FAIL: 缺 publish_result.json — 视为未发布（禁止假成功）');
  process.exit(1);
}

let data;
try {
  data = JSON.parse(fs.readFileSync(resultPath, 'utf8'));
} catch (e) {
  console.error('FAIL: publish_result.json 解析失败', e.message);
  process.exit(1);
}

if (!data.ok) {
  console.error('FAIL: publish_result.ok != true', JSON.stringify(data));
  process.exit(1);
}
if (!data.media_id || String(data.media_id).length < 8) {
  console.error('FAIL: 无有效 media_id', JSON.stringify(data));
  process.exit(1);
}

console.log('VERIFY_OK');
console.log('title:', data.title || '');
console.log('media_id:', data.media_id);
console.log('type:', data.type || '');
console.log('localDate:', data.localDate || '');
process.exit(0);
