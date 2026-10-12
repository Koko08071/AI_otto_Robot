const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../static/composer.js'),'utf8');
const algorithm=source.slice(source.indexOf('function fitClips('),source.indexOf('function phaseStrip('));
function fit(tracks){return new Function('track',algorithm+'return fitClips;')(kind=>tracks[kind]);}
test('nearby clips snap together; occupied space is never chosen',()=>{
 const place=fit({audio:{clips:[{id:'a',startMs:0,durationMs:1000},{id:'b',startMs:2000,durationMs:1000}]}});
 const item=[{kind:'audio',startMs:0,durationMs:700}];
 assert.equal(place(item,1050),1000);
 assert.equal(place(item,850),1000);
 assert.equal(place(item,1450),1300);
});
test('moving a selected clip ignores itself and stops at its neighbor',()=>{
 const place=fit({motion:{clips:[{id:'a',startMs:0,durationMs:1000},{id:'b',startMs:1500,durationMs:1000}]}});
 assert.equal(place([{kind:'motion',startMs:0,durationMs:1000}],600,['a']),500);
});
