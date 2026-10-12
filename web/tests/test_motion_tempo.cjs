const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const actions=JSON.parse(fs.readFileSync(path.join(__dirname,'../static/actions.json'),'utf8'));
const composer=fs.readFileSync(path.join(__dirname,'../static/composer.js'),'utf8');
const app=fs.readFileSync(path.join(__dirname,'../static/app.js'),'utf8');

const OPTIONS=['快速','中速','慢速','原速','快速补全','中速补全','慢速补全','原速补全'];

test('catalog exposes 8 tempo variants per family and defaults to 中速补全',()=>{
 const variants=actions.filter(a=>a.tempoPeriodMs);
 assert.equal(variants.length,68*4);
 const defaults=variants.filter(a=>a.isDefaultCatalog);
 assert.equal(defaults.length,34);
 for(const d of defaults){
  assert.equal(d.variantLabel,'中速补全');
  assert.equal(d.tempoPeriodMs,500);
  assert.equal(d.isComplete,true);
 }
 const families=new Set(variants.map(a=>a.familyId));
 assert.equal(families.size,34);
 for(const fam of families){
  const labels=variants.filter(a=>a.familyId===fam).map(a=>a.variantLabel).sort();
  assert.deepEqual(labels,[...OPTIONS].sort());
 }
});

test('原速 matches backup 1000ms walk period',()=>{
 const walk=actions.find(a=>a.id==='walk_p1000');
 assert.equal(walk.tempoPeriodMs,1000);
 assert.equal(walk.variantLabel,'原速');
 assert.equal(walk.program.segments[0].period,1000);
 assert.equal(walk.program.segments[0].duration,4000);
});

test('composer and home UI wire default + eight-option switching',()=>{
 for(const src of [composer,app]){
  assert.match(src,/DEFAULT_MOTION_VARIANT='中速补全'/);
  assert.match(src,/MOTION_VARIANT_OPTIONS=\['快速','中速','慢速','原速','快速补全','中速补全','慢速补全','原速补全'\]/);
 }
 assert.match(composer,/isDefaultCatalog/);
 assert.match(composer,/switchClipMotionVariant/);
 assert.match(composer,/buildTempoSelect/);
 assert.match(composer,/has-tempo/);
 assert.match(composer,/clip-tempo/);
 assert.match(app,/tempo-select/);
 assert.match(app,/resolvePreviewAction/);
});
