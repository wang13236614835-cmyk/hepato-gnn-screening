// Static contract checks for the restored original offline check-in pages.
// Browser smoke testing is separate; the original pages intentionally use their
// own DOM/event model and are not executed inside a fake DOM here.
const fs = require('fs');
const path = require('path');
const assert = require('assert');

const root = path.resolve(__dirname, '..');
const members = [
  ['王启龙', 'semester_flow_leader_v1'],
  ['宁显泷', 'semester_flow_ningxl_v1'],
  ['衣思淼', 'semester_flow_yisimiao_v1'],
  ['代维斯丹', 'semester_flow_daiweisd_v1'],
  ['王散曼', 'semester_flow_wangsanman_v1'],
];
const tabs = ['🧭 我的工作台', '🔬 全线流程', '📍 本周看板', '🗓 学期总览', '📋 周卡片·打卡', '📚 学习资源', '✅ 打卡台账', '💾 数据管理'];
let checks = 0;

for (const [name, key] of members) {
  const file = path.join(root, name, `打卡_${name}.html`);
  assert.ok(fs.existsSync(file), `${file} exists`); checks++;
  const html = fs.readFileSync(file, 'utf8');
  assert.ok(html.includes('<nav id="nav">'), `${name}: original nav`); checks++;
  for (const tab of tabs) { assert.ok(html.includes(tab), `${name}: ${tab}`); checks++; }
  assert.ok(html.includes(`const SKEY = "${key}";`), `${name}: legacy storage key`); checks++;
  assert.ok(html.includes('localStorage'), `${name}: localStorage persistence`); checks++;
  for (const fn of ['function load(', 'function save(', 'function exp(', 'function imp(']) {
    assert.ok(html.includes(fn), `${name}: ${fn}`); checks++;
  }
  assert.ok(html.includes('confirm('), `${name}: checkbox confirmation`); checks++;
  assert.ok(html.includes('current-review-banner'), `${name}: current review banner`); checks++;
  assert.ok(!html.includes('plan-data'), `${name}: no replacement v2 plan dependency`); checks++;
}

console.log(JSON.stringify({
  passed: true,
  members: members.length,
  checks,
  scope: 'Original tabs, legacy localStorage keys, persistence/import-export, confirmation, review banner, no v2 template dependency'
}));
