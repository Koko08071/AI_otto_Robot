const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const source=fs.readFileSync(require('node:path').join(__dirname,'../static/app.js'),'utf8');
function harness(){
 const calls=[],buttons=[false,true].map(repeat=>({dataset:{action:'walk',repeat:String(repeat)},classList:{toggle(k,v){this[k]=v;}}}));
 const device={connected:true,active:'idle',repeat:false};
 const context=vm.createContext({document:{querySelectorAll:()=>buttons},status:{...device},requireConnection(){},toast(){},
  async api(path,body){calls.push({path,body});if(path==='/api/play'){device.active=body.name;device.repeat=body.repeat;}if(path==='/api/stop')device.active='idle';return {...device};}});
 vm.runInContext(source.slice(source.indexOf('let commandBusy='),source.indexOf('function renderExpressions()'))+'\nfunction paintStatus(s){status=s;paintRunButtons();}',context);
 return {context,calls,buttons};
}
test('continuous button becomes stop and second click stops',async()=>{
 const h=harness();await vm.runInContext("runProgram({name:'walk',segments:[]},true)",h.context);
 assert.equal(h.calls.find(x=>x.path==='/api/play').body.repeat,true);
 assert.equal(h.buttons[1].textContent,'停止');assert.equal(h.buttons[1].classList.running,true);
 assert.equal(h.buttons[0].textContent,'运行一遍');
 await vm.runInContext("runProgram({name:'walk',segments:[]},true)",h.context);
 assert.equal(h.calls.at(-2).path,'/api/stop');assert.equal(h.buttons[1].textContent,'持续运行');
});
test('once button restores when device reports completion',async()=>{
 const h=harness();await vm.runInContext("runProgram({name:'walk',segments:[]},false)",h.context);
 assert.equal(h.buttons[0].textContent,'停止');assert.equal(h.calls.find(x=>x.path==='/api/play').body.repeat,false);
 vm.runInContext("paintStatus({connected:true,active:'idle',repeat:false})",h.context);
 assert.equal(h.buttons[0].textContent,'运行一遍');assert.equal(h.buttons[0].classList.running,false);
});
test('switching mode starts the selected mode',async()=>{
 const h=harness();await vm.runInContext("runProgram({name:'walk',segments:[]},true)",h.context);
 await vm.runInContext("runProgram({name:'walk',segments:[]},false)",h.context);
 assert.equal(h.calls.filter(x=>x.path==='/api/play').at(-1).body.repeat,false);
 assert.equal(h.buttons[0].textContent,'停止');assert.equal(h.buttons[1].textContent,'持续运行');
});
