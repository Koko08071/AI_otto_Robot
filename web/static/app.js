'use strict';
const $=s=>document.querySelector(s);
const axes=[['ll','左腿',39],['rl','右腿',17],['lf','左脚',38],['rf','右脚',18]];
let status={connected:false},catalog={actions:[],expressions:[]},originals=[],editing=null,stream=null,polling=false,connecting=false;
const MOTION_VARIANT_OPTIONS=['快速','中速','慢速','原速','快速补全','中速补全','慢速补全','原速补全'];
const DEFAULT_MOTION_VARIANT='中速补全';
const familyVariantChoice=new Map();
let toastTimer;
function toast(text){if($('#editor').open)$('#editor-state').textContent=text;$('#toast').textContent=text;$('#toast').hidden=false;clearTimeout(toastTimer);toastTimer=setTimeout(()=>$('#toast').hidden=true,5000);$('#last-command').textContent=text;}
async function api(path,body){const r=await fetch(path,body===undefined?{}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});const data=await r.json();if(!r.ok)throw Error(data.error||`HTTP ${r.status}`);return data;}
function on(selector,fn){$(selector).addEventListener('click',async event=>{try{await fn(event);}catch(e){toast(e.message);}});}
function requireConnection(){if(!status.connected)throw Error('请先连接机器人');}
function paintStatus(next){status=next;$('#connection-state').textContent=next.connected?'● 已连接':'○ 未连接';$('#connection-state').classList.toggle('online',!!next.connected);$('#connect').textContent=next.connected?'断开连接':'连接机器人';$('#active').textContent=next.connected?(next.active==='idle'?'就绪':next.active||'就绪'):'待连接';$('#device-info').textContent=next.connected?`${next.board} · ${next.port}`:(next.error||'等待连接');$('#route').textContent=`网页 → 本机服务 → ${next.mode==='ble'?'蓝牙':'Wi-Fi'} → 机器人`;$('#output').textContent=next.servo_enabled?'关闭舵机':'启用舵机';$('#pwm-status').textContent=next.connected?(next.servo_enabled?'PWM 已启用 · 状态为指令角度，无位置传感器反馈':'PWM 已关闭'):'等待设备状态';document.querySelectorAll('.face-card').forEach(b=>b.classList.toggle('selected',b.dataset.id===next.expression));paintRunButtons();}
async function refresh(){if(polling||connecting)return;polling=true;try{paintStatus(await api('/api/status'));}catch(e){$('#connection-state').textContent='本机服务不可达';}finally{polling=false;}}
function setupAxes(){for(const [id,label,pin]of axes){const node=document.createElement('div');node.className='axis';node.innerHTML=`<div class="axis-top"><label for="angle-${id}">${label}<small>GPIO ${pin}</small></label><input id="angle-${id}" type="number" min="0" max="180" step="1" value="${id==='lf'?100:90}" aria-label="${label}角度"></div><input id="range-${id}" type="range" min="0" max="180" value="${id==='lf'?100:90}" aria-label="${label}角度滑块">`;$('#axes').append(node);$(`#angle-${id}`).oninput=e=>$(`#range-${id}`).value=e.target.value;$(`#range-${id}`).oninput=e=>$(`#angle-${id}`).value=e.target.value;}}
function resolvePreviewAction(familyId){const want=familyVariantChoice.get(familyId)||DEFAULT_MOTION_VARIANT;return catalog.actions.find(a=>a.familyId===familyId&&a.variantLabel===want)||catalog.actions.find(a=>a.familyId===familyId&&a.isDefaultCatalog)||null;}
function renderActions(){
 const grid=$('#actions');grid.replaceChildren();let group='';
 const families=[
  ...catalog.actions.filter(a=>!a.isDefaultCatalog&&!a.tempoPeriodMs&&a.source!=='OttoDIY/OttoDIYLib'),
  ...catalog.actions.filter(a=>a.isDefaultCatalog)
 ];
 families.forEach((def,i)=>{
  const action=def.isDefaultCatalog?(resolvePreviewAction(def.familyId)||def):def;
  if(action.group!==group){group=action.group;const h=document.createElement('p');h.className='group-title';h.textContent=group;grid.append(h);}
  const card=document.createElement('article');card.className='action-card';
  const edit=document.createElement('button');edit.className='action-edit';edit.setAttribute('aria-label',`编辑${action.familyLabel||action.label}`);
  const duration=action.program.segments.reduce((sum,s)=>sum+s.duration,0);
  edit.innerHTML=`<span class="card-index">${String(i+1).padStart(2,'0')} / ${action.edited?'已编辑':'OTTO'} · ${action.variantLabel||DEFAULT_MOTION_VARIANT}</span><strong></strong><span class="card-bottom"><span>${(duration/1000).toFixed(1)} s · ${action.program.segments.length} 条指令</span><span>编辑 ↗</span></span>`;
  edit.querySelector('strong').textContent=action.familyLabel||action.label;edit.onclick=()=>openEditor(action);card.append(edit);
  const tempo=document.createElement('label');tempo.className='tempo-picker';tempo.innerHTML='<span>预览节奏</span>';
  const select=document.createElement('select');select.className='tempo-select';select.setAttribute('aria-label',`${action.familyLabel||action.label}节奏版本`);
  if(!def.isDefaultCatalog)select.hidden=true;
  for(const label of MOTION_VARIANT_OPTIONS){
   const opt=document.createElement('option');opt.value=label;opt.textContent=label;
   if(!catalog.actions.some(a=>a.familyId===def.familyId&&a.variantLabel===label))opt.disabled=true;
   if(label===(action.variantLabel||DEFAULT_MOTION_VARIANT))opt.selected=true;
   select.append(opt);
  }
  select.onchange=()=>{familyVariantChoice.set(def.familyId,select.value);renderActions();};
  tempo.append(select);card.append(tempo);
  const controls=document.createElement('div');controls.className='action-controls';
  for(const repeat of [false,true]){const b=document.createElement('button');b.dataset.action=action.id;b.dataset.repeat=String(repeat);b.onclick=()=>runProgram(action.program,repeat).catch(e=>toast(e.message));controls.append(b);}
  card.append(controls);grid.append(card);
 });$('#action-count').textContent=families.length;paintRunButtons();filterCatalog();
}
let commandBusy=false;
function paintRunButtons(){
 document.querySelectorAll('[data-action][data-repeat]').forEach(b=>{
  const running=status.connected&&status.active===b.dataset.action&&!!status.repeat===(b.dataset.repeat==='true');
  b.textContent=running?'停止':b.dataset.repeat==='true'?'持续运行':'运行一遍';b.classList.toggle('running',running);b.disabled=commandBusy;
 });
}
async function runProgram(p,repeat){
 requireConnection();if(commandBusy)return;commandBusy=true;paintRunButtons();
 try{
  if(status.active===p.name&&!!status.repeat===repeat){await api('/api/stop',{});toast('动作已停止');}
  else{await api('/api/validate',{...p,repeat});await api('/api/output',{enabled:true});await api('/api/play',{...p,repeat});toast(repeat?'正在持续运行':'正在运行一遍');}
  paintStatus(await api('/api/status'));
 }finally{commandBusy=false;paintRunButtons();}
}
function renderExpressions(){const grid=$('#expressions');grid.replaceChildren();let group='';catalog.expressions.forEach(face=>{if(face.group!==group){group=face.group;const h=document.createElement('p');h.className='group-title';h.textContent=group;grid.append(h);}const b=document.createElement('button');b.className='face-card';b.dataset.id=face.id;b.title=face.source;b.setAttribute('aria-label',`播放${face.label}`);if(face.preview){const img=document.createElement('img');img.src=face.preview;img.alt=face.label+'官方动画';img.loading='lazy';b.append(img);}else{const tile=document.createElement('div');tile.className='fixture';tile.textContent=face.source.endsWith('.aaf')?'AAF':'EAF';b.append(tile);}const label=document.createElement('strong');label.textContent=face.label;const id=document.createElement('small');id.textContent=face.id;b.append(label,id);b.onclick=async()=>{try{requireConnection();await api('/api/face',{expression:face.id});toast(`已发送官方动画：${face.label}`);await refresh();}catch(e){toast(e.message);}};grid.append(b);});$('#face-count').textContent=catalog.expressions.length;}
function summary(){try{const p=JSON.parse($('#program-json').value);const t=p.segments.reduce((n,s)=>n+Number(s.duration),0);$('#program-summary').textContent=`${p.segments.length} 条指令 · ${(t/1000).toFixed(2)} 秒 · ${new TextEncoder().encode(JSON.stringify(p)).length} 字节`;}catch(e){$('#program-summary').textContent='正在编辑 JSON…';}}
function openEditor(action){editing=action;$('#editor-title').textContent=action.label;$('#editor-source').textContent=`${action.source} · ${action.call} · 机器人自身左右`;$('#program-json').value=JSON.stringify(action.program,null,2);$('#editor-error').textContent='';$('#editor-state').textContent='';summary();for(const [id,repeat] of [['play-program',false],['loop-program',true]]){$('#'+id).dataset.action=action.id;$('#'+id).dataset.repeat=String(repeat);}paintRunButtons();$('#editor').showModal();}
function program(){const value=JSON.parse($('#program-json').value);if(value.name!==editing.id)throw Error(`保留动作标识 name: "${editing.id}"，可自由编辑 segments 内的指令`);return value;}
async function editorAction(fn){try{$('#editor-error').textContent='';await fn();}catch(e){$('#editor-error').textContent=e.message;}}
$('#program-json').addEventListener('input',summary);
on('#reset-program',()=>{const original=originals.find(a=>a.id===editing.id);$('#program-json').value=JSON.stringify(original.program,null,2);$('#editor-error').textContent='';summary();});
on('#validate-program',()=>editorAction(async()=>{const r=await api('/api/validate',program());$('#editor-error').textContent='';toast(`校验通过 · ${(r.duration/1000).toFixed(2)} 秒 · 协议 ${r.bytes} 字节`);}));
on('#save-program',()=>editorAction(async()=>{const r=await api('/api/behavior',program());editing.program=r.program;editing.edited=true;renderActions();toast('动作修改已保存到本机');}));
on('#play-program',()=>editorAction(()=>runProgram(program(),false)));
on('#loop-program',()=>editorAction(()=>runProgram(program(),true)));
on('#connect',async()=>{if(connecting)return;connecting=true;$('#connect').disabled=true;$('#connection-state').textContent=status.connected?'正在断开…':'正在连接…';try{const next=status.connected?await api('/api/disconnect',{}):await api('/api/connect',{mode:$('#transport').value});paintStatus(next);toast(next.connected?'机器人已连接':'已断开连接');}finally{connecting=false;$('#connect').disabled=false;}});
on('#stop',async()=>{requireConnection();await api('/api/stop',{});toast('已停止当前动作，保持指令姿态');await refresh();});
on('#editor-stop',async()=>{requireConnection();await api('/api/stop',{});toast('动作已停止');await refresh();});
on('#output',async()=>{requireConnection();await api('/api/output',{enabled:!status.servo_enabled});await refresh();});
on('#home',async()=>{requireConnection();await api('/api/output',{enabled:true});await api('/api/home',{});toast('正在返回站姿');});
on('#send-pose',async()=>{requireConnection();const pose=Object.fromEntries(axes.map(([id])=>[id,Number($(`#angle-${id}`).value)]));const duration=Number($('#pose-duration').value);await api('/api/output',{enabled:true});await api('/api/servo',{pose,duration});toast('四轴姿态已发送');});
on('#camera-toggle',async()=>{if(stream){stream.getTracks().forEach(t=>t.stop());stream=null;$('#camera').srcObject=null;$('#camera-toggle').textContent='开启';$('#camera-empty').hidden=false;return;}stream=await navigator.mediaDevices.getUserMedia({video:true,audio:false});$('#camera').srcObject=stream;$('#camera-empty').hidden=true;$('#camera-toggle').textContent='关闭';});
function filterCatalog(){
 const query=$('#catalog-search').value.trim().toLocaleLowerCase();
 for(const [gridSelector,cardSelector] of [['#actions','.action-card'],['#expressions','.face-card']]){
  const grid=$(gridSelector);
  for(const card of grid.querySelectorAll(cardSelector))card.hidden=!!query&&!card.textContent.toLocaleLowerCase().includes(query);
  for(const heading of grid.querySelectorAll('.group-title')){
   let item=heading.nextElementSibling,visible=false;
   while(item&&!item.classList.contains('group-title')){
    if(item.matches(cardSelector)&&!item.hidden)visible=true;
    item=item.nextElementSibling;
   }
   heading.hidden=!visible;
  }
  let empty=grid.querySelector('.empty-state');
  if(!empty){empty=document.createElement('p');empty.className='empty-state';empty.textContent='没有匹配的内容';grid.append(empty);}
  empty.hidden=!!grid.querySelector(`${cardSelector}:not([hidden])`);
 }
}
$('#catalog-search').oninput=filterCatalog;
document.querySelectorAll('.tab').forEach(tab=>tab.onclick=()=>{document.querySelectorAll('.tab').forEach(t=>t.classList.toggle('active',t===tab));$('#actions-view').hidden=tab.dataset.tab!=='actions';$('#expressions-view').hidden=tab.dataset.tab!=='expressions';$('#catalog-search').value='';$('#catalog-search').placeholder=tab.dataset.tab==='actions'?'搜索动作':'搜索表情';filterCatalog();});
$('#transport').addEventListener('change',()=>{if(status.connected)toast('切换通信方式前，请先断开当前连接');});
setupAxes();
(async()=>{try{catalog=await api('/api/catalog');originals=structuredClone(catalog.actions);renderActions();renderExpressions();await refresh();setInterval(refresh,3000);}catch(e){toast(e.message);}})();
