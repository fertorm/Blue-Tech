#!/usr/bin/env node
/**
 * pre-commit-secrets.js — Secret Pattern Scanner
 *
 * PreToolUse hook that fires on git commit and git push commands.
 * Scans staged files for known secret patterns and blocks the operation
 * if any are found (exit code 2).
 *
 * Patterns detected:
 *   AIzaSy...  — Google API keys
 *   sk-...     — OpenAI / Stripe secret keys
 *   AKIA...    — AWS access key IDs
 *   ghp_...    — GitHub personal access tokens
 *   xoxb-...   — Slack bot tokens
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const SECRET_PATTERNS = [
  { name: 'Google API Key',              regex: /AIzaSy[0-9A-Za-z_-]{33}/ },
  { name: 'OpenAI / Generic Secret Key', regex: /sk-[0-9A-Za-z]{32,}/ },
  { name: 'AWS Access Key ID',           regex: /AKIA[0-9A-Z]{16}/ },
  { name: 'GitHub Personal Token',       regex: /ghp_[0-9A-Za-z]{36}/ },
  { name: 'Slack Bot Token',             regex: /xoxb-[0-9A-Za-z-]{40,}/ },
];

// Files excluded from scanning (test fixtures, ignore lists, this script itself)
const EXCLUDED_SUFFIXES = [
  '.gitignore', '.npmignore', 'pre-commit-secrets.js',
  '.test.js', '.spec.js', '_test.py', 'test_', '.example',
];

function isExcluded(filePath) {
  const base = path.basename(filePath);
  return EXCLUDED_SUFFIXES.some(suffix =>
    base.endsWith(suffix) || base.startsWith('test_')
  );
}

function getStagedFiles() {
  try {
    const output = execSync('git diff --cached --name-only', {
      encoding: 'utf8',
      stdio: ['pipe', 'pipe', 'pipe'],
    });
    return output.trim().split('\n').filter(Boolean);
  } catch {
    return [];
  }
}

function scanFile(filePath) {
  try {
    if (!fs.existsSync(filePath)) return [];
    const stat = fs.statSync(filePath);
    if (stat.size > 1_000_000) return []; // Skip files > 1 MB
    const content = fs.readFileSync(filePath, 'utf8');
    const findings = [];
    for (const { name, regex } of SECRET_PATTERNS) {
      if (regex.test(content)) {
        findings.push(name);
      }
    }
    return findings;
  } catch {
    return [];
  }
}

function main() {
  let inputData = '';
  process.stdin.on('data', chunk => { inputData += chunk; });
  process.stdin.on('end', () => {
    let toolInput = {};
    try {
      toolInput = JSON.parse(inputData);
    } catch {
      process.stdout.write(inputData);
      process.exit(0);
    }

    const command = toolInput.tool_input?.command || '';

    // Only run on git commit or git push
    if (!/git\s+(commit|push)/.test(command)) {
      process.stdout.write(inputData);
      process.exit(0);
    }

    const stagedFiles = getStagedFiles();
    if (stagedFiles.length === 0) {
      process.stdout.write(inputData);
      process.exit(0);
    }

    const violations = [];
    for (const file of stagedFiles) {
      if (isExcluded(file)) continue;
      const findings = scanFile(file);
      if (findings.length > 0) {
        violations.push({ file, patterns: findings });
      }
    }

    if (violations.length > 0) {
      console.error('[Hook] BLOCKED: Potential secrets detected in staged files!');
      console.error('[Hook] ─────────────────────────────────────────────────────');
      for (const { file, patterns } of violations) {
        console.error(`[Hook]   FILE: ${file}`);
        for (const p of patterns) {
          console.error(`[Hook]     → ${p}`);
        }
      }
      console.error('[Hook] ─────────────────────────────────────────────────────');
      console.error('[Hook] Remove secrets, use environment variables, then retry.');
      console.error('[Hook] To bypass (NOT recommended): git commit --no-verify');
      process.exit(2);
    }

    process.stdout.write(inputData);
    process.exit(0);
  });
}

main();
