#!/usr/bin/env node
/**
 * 日报日期目录清理（开源版，路径从 config.md 读取）
 *
 * 规则（每个输出根目录独立）：
 * - 只处理纯日期文件夹：YYYY-MM-DD（backup 等名不参与）
 * - 今天的目录永远保留，不参与计数与删除
 * - 某根目录内「历史日期夹」数量 >= THRESHOLD(14) 时：
 *   删除最早的若干个，只保留最新 KEEP(7) 个
 *
 * 用法:
 *   node cleanup.js
 *   node cleanup.js --config-md <path-to-config.md>
 *   node cleanup.js --dry-run
 *   node cleanup.js --roots "C:\path\AI,C:\path\GitHub"
 *   CLEANUP_DRY_RUN=1 node cleanup.js
 */
'use strict';

const fs = require('fs');
const path = require('path');

const THRESHOLD = 14;
const KEEP = 7;

function localDateYmd() {
  return new Date().toLocaleDateString('sv-SE');
}

function isDateDir(name) {
  return /^\d{4}-\d{2}-\d{2}$/.test(name);
}

function parseArgs(argv) {
  const out = { configMd: null, dryRun: false, roots: null, help: false };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--dry-run') out.dryRun = true;
    else if (a === '--config-md' && argv[i + 1]) out.configMd = path.resolve(argv[++i]);
    else if (a === '--roots' && argv[i + 1]) {
      out.roots = argv[++i]
        .split(/[,;]/)
        .map((s) => s.trim())
        .filter(Boolean)
        .map((s) => path.resolve(s));
    } else if (a === '--help' || a === '-h') out.help = true;
  }
  if (process.env.CLEANUP_DRY_RUN === '1' || process.env.CLEANUP_DRY_RUN === 'true') {
    out.dryRun = true;
  }
  return out;
}

function defaultConfigMd() {
  return path.resolve(__dirname, '..', 'config.md');
}

function parseConfigPaths(configPath) {
  if (!fs.existsSync(configPath)) {
    throw new Error('config.md 不存在: ' + configPath);
  }
  const text = fs.readFileSync(configPath, 'utf8');
  const map = {};
  const re = /\|\s*`\{([^}]+)\}`\s*\|\s*`([^`]*)`\s*\|/g;
  let m;
  while ((m = re.exec(text)) !== null) {
    map[m[1]] = m[2].trim();
  }
  return map;
}

function resolveRoots(args) {
  if (args.roots && args.roots.length) {
    return { roots: args.roots, configPath: args.configMd || defaultConfigMd() };
  }
  const configPath = args.configMd || defaultConfigMd();
  const cfg = parseConfigPaths(configPath);
  const roots = [];
  if (cfg.OUTPUT_ROOT) roots.push(path.resolve(cfg.OUTPUT_ROOT));
  if (cfg.OUTPUT_ROOT_GITHUB) roots.push(path.resolve(cfg.OUTPUT_ROOT_GITHUB));
  if (roots.length === 0) {
    throw new Error(
      '未找到 OUTPUT_ROOT / OUTPUT_ROOT_GITHUB。请编辑 config.md 填写输出目录，或使用 --roots "path1,path2"'
    );
  }
  return { roots, configPath };
}

function listHistoricalDateDirs(base, today) {
  if (!fs.existsSync(base)) return null;
  const entries = fs.readdirSync(base, { withFileTypes: true });
  return entries
    .filter((e) => e.isDirectory() && isDateDir(e.name) && e.name !== today)
    .map((e) => e.name)
    .sort();
}

function cleanupRoot(base, today) {
  const dateDirs = listHistoricalDateDirs(base, today);
  if (dateDirs === null) {
    return { base, missing: true, count: 0, toDelete: [], kept: [], triggered: false };
  }
  const count = dateDirs.length;
  if (count < THRESHOLD) {
    return { base, missing: false, triggered: false, count, toDelete: [], kept: dateDirs };
  }
  const drop = Math.max(0, count - KEEP);
  return {
    base,
    missing: false,
    triggered: true,
    count,
    toDelete: dateDirs.slice(0, drop),
    kept: dateDirs.slice(drop),
  };
}

function main() {
  const args = parseArgs(process.argv);
  if (args.help) {
    console.log(
      'Usage: node cleanup.js [--config-md path] [--roots a,b] [--dry-run]\n' +
        'Policy: per OUTPUT_ROOT, if historical YYYY-MM-DD dirs >= ' +
        THRESHOLD +
        ', keep newest ' +
        KEEP +
        ", delete older.\nToday's dir is never deleted."
    );
    process.exit(0);
  }

  let roots;
  let configPath;
  try {
    ({ roots, configPath } = resolveRoots(args));
  } catch (e) {
    console.error('[cleanup] ERROR: ' + e.message);
    process.exit(1);
  }

  const today = localDateYmd();
  const dryRun = !!args.dryRun;
  console.log(
    '[cleanup] today=' +
      today +
      ' threshold=' +
      THRESHOLD +
      ' keep=' +
      KEEP +
      ' dryRun=' +
      dryRun +
      ' config=' +
      configPath
  );

  let anyTrigger = false;
  let totalDeleted = 0;

  for (const base of roots) {
    const result = cleanupRoot(base, today);
    if (result.missing) {
      console.log('  skip (missing): ' + base);
      continue;
    }
    if (!result.triggered) {
      console.log(
        '  ok (no cleanup): ' + base + ' historical=' + result.count + ' < ' + THRESHOLD
      );
      continue;
    }
    anyTrigger = true;
    console.log(
      '  TRIGGER: ' +
        base +
        ' historical=' +
        result.count +
        ' → delete ' +
        result.toDelete.length +
        ', keep ' +
        result.kept.length
    );
    for (const name of result.toDelete) {
      const full = path.join(base, name);
      if (dryRun) {
        console.log('    [dry-run] would delete ' + name);
        totalDeleted += 1;
        continue;
      }
      try {
        fs.rmSync(full, { recursive: true, force: true });
        console.log('    deleted ' + name);
        totalDeleted += 1;
      } catch (e) {
        console.log('    FAIL ' + name + ': ' + e.message);
      }
    }
    if (result.kept.length) {
      console.log('    kept: ' + result.kept.join(', '));
    }
  }

  if (!anyTrigger) {
    console.log(
      '[cleanup] done — no root reached ' + THRESHOLD + ' historical date folders'
    );
  } else {
    console.log(
      '[cleanup] done — ' +
        (dryRun ? 'would delete' : 'deleted') +
        ' ' +
        totalDeleted +
        ' folder(s); today ' +
        today +
        ' always kept'
    );
  }
}

main();
