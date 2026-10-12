const assert = require('assert');
const fs = require('fs');
const path = require('path');
const exprs = JSON.parse(fs.readFileSync(path.join(__dirname, '../static/expressions.json'), 'utf8'));
const laugh = exprs.find(e => e.id === 'laugh_05s_10');
assert.ok(laugh.hasLoopRange);
assert.strictEqual(laugh.introMs + laugh.loopMs + laugh.outroMs, laugh.durationMs);
function expressionDuration(e, n) {
  return e.introMs + e.loopMs * n + e.outroMs;
}
assert.strictEqual(expressionDuration(laugh, 1), laugh.durationMs);
assert.strictEqual(expressionDuration(laugh, 3), laugh.introMs + laugh.loopMs * 3 + laugh.outroMs);
const shy = exprs.find(e => e.id === 'shy_20s_40s');
assert.ok(shy.loopMs === 4000);
const js = fs.readFileSync(path.join(__dirname, '../static/composer.js'), 'utf8');
assert.ok(js.includes('setExpressionLoopCount'));
assert.ok(js.includes('重复＋'));
assert.ok(js.includes('expressionPhases'));
console.log('expression loop tests ok');
const music = exprs.find(e => e.id === 'music_25s');
assert.ok(music, 'music_25s missing');
assert.ok(music.hasLoopRange);
assert.strictEqual(music.label, '弹钢琴');
const dog = exprs.find(e => e.id === 'dog_act');
assert.ok(dog && dog.label === '变小狗');
const cat = exprs.find(e => e.id === 'cat_act');
assert.ok(cat && cat.label === '变小猫');
console.log('custom emo expressions ok');
