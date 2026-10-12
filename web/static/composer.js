'use strict';
const $=selector=>document.querySelector(selector);
const TRACKS=[['motion','四轴动作'],['expression','屏幕表情'],['audio','机器人声音'],['music','电脑音乐']];
const eyeSvg=closed=>closed
 ? '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 3l18 18M9.8 5.4A11 11 0 0 1 12 5c4.5 0 8.4 2.8 10 7a10.9 10.9 0 0 1-3.2 4.4M6.4 6.5A11.4 11.4 0 0 0 2 12c1.6 4.2 5.5 7 10 7 1.1 0 2.2-.2 3.2-.5"/><path d="M10 10a3 3 0 0 0 4 4"/></svg>'
 : '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M2 12c1.6-4.2 5.5-7 10-7s8.4 2.8 10 7c-1.6 4.2-5.5 7-10 7S3.6 16.2 2 12Z"/><circle cx="12" cy="12" r="3"/></svg>';
const freshTracks=()=>TRACKS.map(([kind])=>({id:kind,kind,muted:false,clips:[]}));
let composition={id:null,revision:null,name:'未命名组合',trigger:'',tracks:freshTracks()};
let resources={actions:[],expressions:[],audio:[]},saved=[],kind='motion',selected=new Set(),clipboard=[],clipboardAfter=0;
const MOTION_VARIANT_OPTIONS=['快速','中速','慢速','原速','快速补全','中速补全','慢速补全','原速补全'];
const DEFAULT_MOTION_VARIANT='中速补全';
const familyVariantChoice=new Map();

let dirty=true,zoom=88,playhead=0,playing=false,playStart=0,playAudio=new Map(),history=[],future=[],menuStart=0,noticeTimer,shownFace=null;
const thumbnailTimers=new Map();
const thumbnailObserver=new IntersectionObserver(entries=>{for(const entry of entries){const video=entry.target;if(entry.isIntersecting){video.dataset.visible='1';video.play().catch(()=>{});}else{video.dataset.visible='';clearTimeout(thumbnailTimers.get(video));thumbnailTimers.delete(video);video.pause();if(video.readyState)video.currentTime=0;}}},{root:$('#resource-list'),threshold:.25});
const byId=id=>composition.tracks.flatMap(t=>t.clips).find(c=>c.id===id);
const trackOf=id=>composition.tracks.find(t=>t.clips.some(c=>c.id===id));
const track=kind=>composition.tracks.find(t=>t.kind===kind);
const seconds=ms=>(ms/1000).toFixed(2);
const safeId=()=>crypto.randomUUID();
function notify(message,error=false){const n=$('#notice');n.textContent=message;n.classList.toggle('error',error);n.hidden=false;clearTimeout(noticeTimer);noticeTimer=setTimeout(()=>n.hidden=true,4500);}
async function request(path,body){const response=await fetch(path,body===undefined?{}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});let data=await response.json();if(!response.ok)throw Error(data.error||`HTTP ${response.status}`);return data;}
function motionVariantsFor(familyId){return MOTION_VARIANT_OPTIONS.map(label=>{const item=resources.actions.find(a=>a.familyId===familyId&&a.variantLabel===label);return item?{label,item}:null;}).filter(Boolean);}
function resolveMotionVariant(familyId,variantLabel){const want=variantLabel||familyVariantChoice.get(familyId)||DEFAULT_MOTION_VARIANT;return resources.actions.find(a=>a.familyId===familyId&&a.variantLabel===want)||resources.actions.find(a=>a.familyId===familyId&&a.isDefaultCatalog)||null;}
function buildTempoSelect(familyId, currentLabel, onChange){
 const select=document.createElement('select');select.className='tempo-select';
 select.setAttribute('aria-label','节奏版本');
 const current=currentLabel||DEFAULT_MOTION_VARIANT;
 for(const v of motionVariantsFor(familyId)){
  const opt=document.createElement('option');opt.value=v.label;opt.textContent=v.label;
  if(v.label===current)opt.selected=true;select.append(opt);
 }
 select.onclick=e=>e.stopPropagation();
 select.onmousedown=e=>e.stopPropagation();
 select.ondragstart=e=>{e.preventDefault();e.stopPropagation();};
 select.onchange=e=>{e.stopPropagation();onChange(select.value);};
 return select;
}
function resourceRows(type){if(type==='expression')return resources.expressions;if(type!=='motion')return resources.audio;if($('#show-original').checked)return resources.actions;const defaults=resources.actions.filter(a=>a.isDefaultCatalog);return defaults.map(def=>resolveMotionVariant(def.familyId)||def).filter(Boolean);}
function switchClipMotionVariant(clip,variantLabel){const current=resources.actions.find(a=>a.id===clip.resourceId);const fam=current?.familyId||clip.resourceSnapshot?.familyId;if(!fam){notify('此片段没有可切换的节奏版本',true);return;}const item=resolveMotionVariant(fam,variantLabel);if(!item){notify('找不到节奏版本：'+variantLabel,true);return;}const dur=durationOf(item,'motion');edit(()=>{clip.resourceId=item.id;clip.durationMs=dur;clip.resourceSnapshot=snapshot(item,'motion');clip.startMs=fitClips([{kind:'motion',startMs:0,durationMs:dur}],clip.startMs,[clip.id]);});familyVariantChoice.set(fam,variantLabel);}
function resource(kind,id){return resourceRows(kind).find(x=>x.id===id)||({'motion':resources.actions,'expression':resources.expressions,'audio':resources.audio,'music':resources.audio}[kind]||[]).find(x=>x.id===id);}
function durationOf(item,kind){if(kind==='motion')return item.program?.segments?.reduce((n,s)=>n+s.duration,0)||0;return item.durationMs||1000;}
function expressionPhases(itemOrSnap){const s=itemOrSnap||{};const intro=Number(s.introMs)||0,loop=Number(s.loopMs)||Math.max(1,Number(s.durationMs)||1000),outro=Number(s.outroMs)||0;return{introMs:intro,loopMs:loop,outroMs:outro,supportsRepeat:s.supportsRepeat!==false&&loop>0};}
function expressionDuration(itemOrSnap,loopCount){const p=expressionPhases(itemOrSnap);const n=Math.max(1,Math.min(99,Number(loopCount)||1));return p.introMs+p.loopMs*n+p.outroMs;}
function clipLoopCount(clip){return Math.max(1,Math.min(99,Number(clip?.loopCount)||1));}
function setExpressionLoopCount(clip,next){const item=resources.expressions.find(x=>x.id===clip.resourceId)||clip.resourceSnapshot||{};const n=Math.max(1,Math.min(99,next|0));const dur=expressionDuration(item,n);edit(()=>{clip.loopCount=n;clip.durationMs=dur;if(clip.resourceSnapshot){clip.resourceSnapshot.durationMs=dur;clip.resourceSnapshot.loopCount=n;}clip.startMs=fitClips([{kind:'expression',startMs:0,durationMs:dur}],clip.startMs,[clip.id]);});}
function snapshot(item,kind){let snap={label:item.label,revision:item.revision||1,kind,durationMs:durationOf(item,kind),source:item.source||''};if(kind==='motion'){snap.program=structuredClone(item.program);if(item.familyId)snap.familyId=item.familyId;if(item.familyLabel)snap.familyLabel=item.familyLabel;if(item.variantLabel)snap.variantLabel=item.variantLabel;}if(kind==='expression'){snap.preview=item.preview||null;snap.introMs=item.introMs||0;snap.loopMs=item.loopMs||item.durationMs||1000;snap.outroMs=item.outroMs||0;snap.hasLoopRange=!!item.hasLoopRange;snap.hasStopFrame=!!item.hasStopFrame;snap.supportsRepeat=item.supportsRepeat!==false;}if(['audio','music'].includes(kind)){snap.url=item.url;snap.mime=item.mime;snap.sha256=item.sha256;}return snap;}
function clipLabel(c){return c.resourceSnapshot?.label||resource(trackOf(c.id)?.kind,c.resourceId)?.label||c.resourceId;}
function markDirty(){dirty=true;$('#save-state').textContent='未保存';$('#save-state').classList.add('dirty');renderSaved();}
function remember(){history.push(structuredClone(composition.tracks));if(history.length>60)history.shift();future=[];}
function edit(operation){remember();operation();markDirty();renderTimeline();renderInspector();renderPreview();}
function undo(){if(!history.length)return;future.push(structuredClone(composition.tracks));composition.tracks=history.pop();selected.clear();markDirty();renderTimeline();renderInspector();renderPreview();}
function redo(){if(!future.length)return;history.push(structuredClone(composition.tracks));composition.tracks=future.pop();selected.clear();markDirty();renderTimeline();renderInspector();renderPreview();}
function totalMs(){return Math.max(0,...composition.tracks.flatMap(t=>t.clips.map(c=>c.startMs+c.durationMs)));}
function renderSaved(){const host=$('#composition-list');host.replaceChildren();if(!saved.length){const p=document.createElement('p');p.className='library-help';p.textContent='还没有保存的组合';host.append(p);}for(const item of saved){const row=document.createElement('div');row.className='saved-row';const b=document.createElement('button');b.className='saved-item'+(composition.id===item.id?' current':'');const title=document.createElement('strong');title.textContent=item.name;const meta=document.createElement('small');meta.textContent=`版本 ${item.revision} · ${item.clipCount} 片段 · ${seconds(item.durationMs)} 秒${item.trigger?' · 🎙 '+item.trigger:''}`;b.append(title,meta);b.onclick=()=>openComposition(item.id).catch(e=>notify(e.message,true));const del=document.createElement('button');del.className='saved-delete';del.textContent='删除';del.title='删除组合 '+item.name;del.onclick=()=>deleteSaved(item);row.append(b,del);host.append(row);}}
async function deleteSaved(item){if(!confirm(`确定删除输出组合“${item.name}”？`))return;await request('/api/compositions/'+item.id+'/delete',{});if(composition.id===item.id){stopPreview();composition={id:null,revision:null,name:'未命名组合',trigger:'',tracks:freshTracks()};$('#name').value=composition.name;$('#voice-trigger').value='';selected.clear();history=[];future=[];markDirty();renderTimeline();renderInspector();renderPreview();}await loadSaved();notify('已删除组合');}
function renderResources(){
 const host=$('#resource-list');thumbnailObserver.disconnect();
 for(const [video,timer] of thumbnailTimers){clearTimeout(timer);video.pause();}
 thumbnailTimers.clear();host.replaceChildren();
 const search=$('#resource-search').value.trim().toLocaleLowerCase();
 const rows=resourceRows(kind).filter(x=>(x.label+' '+(x.familyLabel||'')+' '+x.id).toLocaleLowerCase().includes(search));
 if(!rows.length){const p=document.createElement('p');p.className='library-help';p.textContent=kind==='audio'?'暂无声音。上传文件或输入文字合成。':'没有匹配的资源';host.append(p);return;}
 for(const item of rows){
  const card=document.createElement((kind==='audio'||kind==='motion')?'div':'button');
  card.className='resource-item '+kind;card.draggable=true;
  card.title='拖到轨道，或点击加入播放头所在位置';
  if(kind==='expression'&&item.thumbnailVideo){
   const video=document.createElement('video');video.className='resource-thumb';video.src=item.thumbnailVideo;
   video.muted=true;video.playsInline=true;video.preload='metadata';video.draggable=false;
   video.setAttribute('aria-hidden','true');
   video.onended=()=>{if(video.dataset.visible!=='1')return;const timer=setTimeout(()=>{
    thumbnailTimers.delete(video);if(video.dataset.visible==='1'&&video.isConnected){video.currentTime=0;video.play().catch(()=>{});}
   },800);thumbnailTimers.set(video,timer);};
   card.classList.add('has-thumbnail');card.append(video);thumbnailObserver.observe(video);
  }
  const copy=document.createElement('span');copy.className='resource-copy';
  const title=document.createElement('strong');title.textContent=kind==='motion'&&item.familyLabel?item.familyLabel:item.label;
  const detail=document.createElement('small');detail.textContent=`${seconds(durationOf(item,kind))} 秒${item.durationEstimated?' · 时长待核对':''} · ${item.origin==='tts'?'语音合成':item.id}${kind==='expression'&&item.onDevice===false?' · 未打入机身包':''}`;
  copy.append(title,detail);card.append(copy);
  if(kind==='motion'&&item.familyId){
   card.classList.add('has-tempo');
   card.title='拖到轨道，或点击加入播放头；下拉可切换节奏版本';
   const picker=document.createElement('label');picker.className='tempo-picker';
   picker.append(buildTempoSelect(item.familyId,item.variantLabel||DEFAULT_MOTION_VARIANT,label=>{familyVariantChoice.set(item.familyId,label);renderResources();}));
   card.append(picker);
  }
  card.ondragstart=e=>{if(e.target.closest&&e.target.closest('select')){e.preventDefault();return;}e.dataTransfer.effectAllowed='copy';e.dataTransfer.setData('application/x-otto-resource',JSON.stringify({id:item.id,kind}));};
  card.onclick=e=>{if(e.target.closest&&e.target.closest('select,label.tempo-picker'))return;addClip(kind,item,playhead);};
  if(kind==='audio'){
   const actions=document.createElement('div');actions.className='audio-card-actions';
   for(const [label,handler] of [['试听',()=>previewAudio(item)],['机器人播放',()=>playOnRobot(item)],['修改',()=>openAudioDialog(item)],['删除',()=>removeAudio(item)]]){
    const button=document.createElement('button');button.textContent=label;button.onclick=e=>{e.stopPropagation();handler();};actions.append(button);
   }
   card.append(actions);
  }
  host.append(card);
 }
}
function overlaps(target,kind){return track(kind).clips.some(other=>other.id!==target.id&&target.startMs<other.startMs+other.durationMs&&other.startMs<target.startMs+target.durationMs);}
function fitClips(members,requested,ignored=[]){
 const ids=new Set(ignored),min=-Math.min(...members.map(x=>x.startMs));
 const occupied=members.flatMap(item=>track(item.kind).clips.filter(other=>!ids.has(other.id)).map(other=>({item,other})));
 const candidates=[Math.max(min,Math.round(requested))];
 for(const {item,other} of occupied)candidates.push(other.startMs+other.durationMs-item.startMs,other.startMs-item.durationMs-item.startMs);
 const valid=delta=>delta>=min&&occupied.every(({item,other})=>item.startMs+delta+item.durationMs<=other.startMs||item.startMs+delta>=other.startMs+other.durationMs);
 const options=candidates.filter(valid).sort((a,b)=>Math.abs(a-requested)-Math.abs(b-requested));
 const snap=candidates.slice(1).filter(valid).sort((a,b)=>Math.abs(a-requested)-Math.abs(b-requested)).find(value=>Math.abs(value-requested)<=120);
 return snap??options[0]??Math.max(min,Math.round(requested));
}
function phaseStrip(clip){const kind=trackOf(clip.id)?.kind;if(kind==='expression'){const snap=clip.resourceSnapshot||resources.expressions.find(x=>x.id===clip.resourceId)||{};const p=expressionPhases(snap);const n=clipLoopCount(clip);if(!(p.introMs||p.outroMs||n>1)){/* still show when has loop range */ if(!snap.hasLoopRange&&!snap.hasStopFrame&&n===1)return null;}const strip=document.createElement('div');strip.className='phase-strip expression';const parts=[['起',p.introMs]];for(let i=0;i<n;i++)parts.push([i===0?'循环':`循环×${i+1}`,p.loopMs]);parts.push(['回',p.outroMs]);const total=Math.max(1,parts.reduce((s,[,d])=>s+d,0));for(const [text,duration] of parts){if(!duration)continue;const part=document.createElement('span');part.textContent=text;if(text.startsWith('循环')&&text!=='循环')part.className='loop-extra';part.style.width=100*duration/total+'%';strip.append(part);}return strip;}const complete=clip.resourceSnapshot?.program&&(clip.resourceSnapshot?.variantLabel?.endsWith('补全')||clip.resourceId.includes('_complete'));if(!complete)return null;const segments=clip.resourceSnapshot.program.segments;if(segments.length<3)return null;const approach=segments[0].duration+(segments[1]?.type==='move'&&segments[2]?.type==='oscillate'?segments[1].duration:0),back=segments.at(-1).duration,body=Math.max(1,clip.durationMs-approach-back);const strip=document.createElement('div');strip.className='phase-strip';for(const [text,duration] of [['准备',approach],['主体',body],['回归',back]]){const part=document.createElement('span');part.textContent=text;part.style.width=100*duration/clip.durationMs+'%';strip.append(part);}return strip;}
function renderTimeline(){const target=$('#timeline-content');target.replaceChildren();const width=Math.max(15,Math.ceil(totalMs()/1000)+2)*zoom;
 for(const [trackKind,labelText] of [['ruler','时间'],...TRACKS]){const row=document.createElement('div');row.className=trackKind==='ruler'?'ruler-row':'track-row';const label=document.createElement('div');label.className='track-label';if(trackKind==='ruler'){label.textContent='秒 / 播放头';}else{const t=track(trackKind);label.classList.toggle('muted',t.muted);const title=document.createElement('span');title.textContent=labelText;const eye=document.createElement('button');eye.className='eye';eye.innerHTML=eyeSvg(t.muted);eye.title=t.muted?'启用整条轨道':'屏蔽整条轨道';eye.setAttribute('aria-label',eye.title);eye.onclick=()=>edit(()=>t.muted=!t.muted);label.append(title,eye);label.oncontextmenu=e=>{e.preventDefault();showTrackMenu(e,trackKind,playhead);};}
 row.append(label);const lane=document.createElement('div');lane.className='lane';lane.style.width=width+'px';lane.style.backgroundSize=zoom+'px 100%';if(trackKind==='ruler'){for(let n=0;n<=width/zoom;n++){const tick=document.createElement('span');tick.className='tick';tick.style.left=n*zoom+'px';tick.textContent=n+'s';lane.append(tick);}lane.onclick=e=>{playhead=positionAt(e,lane);renderTimeline();renderPreview();};}else{
 const t=track(trackKind);lane.classList.toggle('muted',t.muted);lane.ondragover=e=>{e.preventDefault();lane.classList.add('drag-over');};lane.ondragleave=()=>lane.classList.remove('drag-over');lane.ondrop=e=>{e.preventDefault();lane.classList.remove('drag-over');handleDrop(e,trackKind,lane);};lane.oncontextmenu=e=>{if(e.target.closest('.clip'))return;e.preventDefault();showTrackMenu(e,trackKind,positionAt(e,lane));};
 if(!t.clips.length){const hint=document.createElement('div');hint.className='empty-hint';hint.textContent=['audio','music'].includes(trackKind)?'拖入声音，或右键上传声音':'拖入资源，或在空白处点右键';lane.append(hint);}
 for(const c of t.clips){const item=document.createElement('div');item.className='clip '+trackKind;item.classList.toggle('selected',selected.has(c.id));item.classList.toggle('muted',t.muted||c.muted);item.classList.toggle('conflict',overlaps(c,trackKind));item.style.left=c.startMs/1000*zoom+'px';item.style.width=Math.max(1,c.durationMs/1000*zoom)+'px';item.draggable=true;item.title=`${clipLabel(c)} · ${seconds(c.durationMs)} 秒${overlaps(c,trackKind)?' · 与另一个动作重叠':''}`;
 const name=document.createElement('span');name.className='clip-name';
 const motionRes=trackKind==='motion'?resources.actions.find(a=>a.id===c.resourceId):null;
 const fam=motionRes?.familyId||c.resourceSnapshot?.familyId;
 const famLabel=motionRes?.familyLabel||c.resourceSnapshot?.familyLabel;
 name.textContent=trackKind==='motion'&&famLabel?famLabel:clipLabel(c);
 const meta=document.createElement('span');meta.className='clip-meta';meta.textContent=seconds(c.durationMs)+'s';item.append(name,meta);
 if(trackKind==='motion'&&fam){
  item.classList.add('has-tempo');
  const picker=document.createElement('label');picker.className='clip-tempo';
  const cur=motionRes?.variantLabel||c.resourceSnapshot?.variantLabel||DEFAULT_MOTION_VARIANT;
  picker.append(buildTempoSelect(fam,cur,label=>switchClipMotionVariant(c,label)));
  item.append(picker);
 }
 const strip=phaseStrip(c);if(strip)item.append(strip);
 const eye=document.createElement('button');eye.className='clip-eye';eye.innerHTML=eyeSvg(c.muted);eye.title=c.muted?'取消屏蔽片段':'屏蔽片段';eye.setAttribute('aria-label',eye.title+' '+clipLabel(c));eye.onclick=e=>{e.stopPropagation();edit(()=>c.muted=!c.muted);};item.append(eye);
 item.onclick=e=>{if(e.target.closest&&e.target.closest('select,label.clip-tempo'))return;e.stopPropagation();if(e.shiftKey)selected.add(c.id);else selected=new Set([c.id]);renderTimeline();renderInspector();renderPreview();};item.oncontextmenu=e=>{e.preventDefault();e.stopPropagation();if(!selected.has(c.id))selected=new Set([c.id]);renderInspector();showClipMenu(e,c);};item.ondragstart=e=>{if(e.target.closest&&e.target.closest('select')){e.preventDefault();return;}if(!selected.has(c.id))selected=new Set([c.id]);e.dataTransfer.effectAllowed='move';e.dataTransfer.setData('application/x-otto-clips',JSON.stringify({ids:[...selected],anchor:c.id,grabOffsetPx:e.clientX-item.getBoundingClientRect().left}));};lane.append(item);}
 }const playLine=document.createElement('div');playLine.className='playhead';playLine.style.left=playhead/1000*zoom+'px';lane.append(playLine);row.append(lane);target.append(row);}
 $('#undo').disabled=!history.length;$('#redo').disabled=!future.length;}
function positionAt(e,lane,grabOffsetPx=0){return Math.round(Math.max(0,(e.clientX-lane.getBoundingClientRect().left-grabOffsetPx)*1000/zoom)/10)*10;}
function addClip(trackKind,item,startMs){if(!item)return;const duration=durationOf(item,trackKind);if(!duration){notify('资源未提供时长，请先补充目录元数据',true);return;}const id=safeId(),clip={id,resourceId:item.id,startMs:0,durationMs:duration,muted:false,resourceSnapshot:snapshot(item,trackKind)};if(trackKind==='expression'){clip.loopCount=1;clip.resourceSnapshot.loopCount=1;}clip.startMs=fitClips([{kind:trackKind,startMs:0,durationMs:duration}],startMs);edit(()=>track(trackKind).clips.push(clip));selected=new Set([id]);renderTimeline();renderInspector();}
function handleDrop(e,trackKind,lane){const resourceData=e.dataTransfer.getData('application/x-otto-resource');const group=e.dataTransfer.getData('application/x-otto-clips');try{if(resourceData){const d=JSON.parse(resourceData);if(d.kind!==trackKind&&!(d.kind==='audio'&&trackKind==='music')){notify('请把资源拖到对应轨道',true);return;}addClip(trackKind,resource(trackKind,d.id),positionAt(e,lane));return;}if(group){const d=JSON.parse(group),anchor=byId(d.anchor);if(!anchor||trackOf(anchor.id)?.kind!==trackKind){notify('请放到同类轨道',true);return;}const target=positionAt(e,lane,d.grabOffsetPx||0),members=d.ids.map(byId).filter(Boolean);const delta=fitClips(members.map(c=>({kind:trackOf(c.id).kind,startMs:c.startMs,durationMs:c.durationMs})),target-anchor.startMs,d.ids);if(delta)edit(()=>members.forEach(c=>c.startMs+=delta));}}catch(error){notify(error.message,true);}}
function renderInspector(){const clips=[...selected].map(byId).filter(Boolean);$('#selection-count').textContent=clips.length?`${clips.length} 个已选`:'';$('#inspector-empty').hidden=!!clips.length;$('#inspector-content').hidden=!clips.length;if(!clips.length)return;const c=clips[0],kind=trackOf(c.id)?.kind;$('#inspector-name').textContent=clips.length===1?clipLabel(c):`已选择 ${clips.length} 个片段`;$('#clip-start').disabled=clips.length!==1;$('#clip-duration').disabled=clips.length!==1||kind==='motion';$('#clip-start').value=(c.startMs/1000).toFixed(3);$('#clip-duration').value=(c.durationMs/1000).toFixed(3);$('#clip-note').textContent=clips.length>1?'复制、屏蔽和移除会作用于全部选中片段。':kind==='motion'?'动作包含准备、主体和回归；时长由完整指令决定。请在控制台编辑动作资源。':['audio','music'].includes(kind)?'可修改片段占用时长；实际播放会在此时长结束时停播。':'表情含起／循环／回。点「重复＋」多播一轮循环段；「减少重复」可减回。占用时长随循环自动更新。';
const loopBox=$('#expr-loop-controls');
if(loopBox){
  const canLoop=clips.length===1&&kind==='expression';
  loopBox.hidden=!canLoop;
  if(canLoop){
    const n=clipLoopCount(c);
    const snap=c.resourceSnapshot||{};
    const p=expressionPhases(snap);
    $('#expr-loop-label').textContent=`循环 ×${n} · 起${(p.introMs/1000).toFixed(2)}s + 循环${(p.loopMs/1000).toFixed(2)}s×${n} + 回${(p.outroMs/1000).toFixed(2)}s`;
    $('#expr-loop-remove').disabled=n<=1;
    $('#clip-duration').disabled=true;
  }
}
$('#mute-selection').textContent=clips.every(x=>x.muted)?'取消屏蔽':'屏蔽';}
function renderPreview(){const current=composition.tracks.flatMap(t=>t.muted?[]:t.clips.filter(c=>!c.muted&&playhead>=c.startMs&&playhead<c.startMs+c.durationMs).map(c=>({track:t,clip:c})));$('#timecode').textContent=String(Math.floor(playhead/60000)).padStart(2,'0')+':'+seconds(playhead%60000).padStart(5,'0');$('#preview-active').textContent=current.map(({clip})=>clipLabel(clip)).join(' ＋ ')||'统一站姿 / 保持画面';const face=current.find(x=>x.track.kind==='expression');const key=face?.clip.id||null;if(key===shownFace)return;shownFace=key;const host=$('#preview-face');host.replaceChildren();if(face?.clip.resourceSnapshot?.preview){const img=document.createElement('img');img.src=face.clip.resourceSnapshot.preview;img.alt=clipLabel(face.clip)+' 官方预览';host.append(img);}else{const span=document.createElement('span');span.textContent=face?clipLabel(face.clip):'选择表情片段后显示官方预览';host.append(span);}}
function hideMenu(){$('#menu').hidden=true;$('#menu').replaceChildren();}
function showMenu(e,rows){const menu=$('#menu');menu.replaceChildren();for(const row of rows){if(row===null){menu.append(document.createElement('hr'));continue;}if(row.heading){const h=document.createElement('div');h.className='menu-label';h.textContent=row.heading;menu.append(h);continue;}const b=document.createElement('button');b.setAttribute('role','menuitem');b.textContent=row.label;b.onclick=()=>{hideMenu();row.action();};menu.append(b);}menu.hidden=false;menu.style.left=Math.min(e.clientX,innerWidth-260)+'px';menu.style.top=Math.min(e.clientY,innerHeight-370)+'px';}
function showTrackMenu(e,trackKind,start){menuStart=start;const rows=[];if(['audio','music'].includes(trackKind)){rows.push({label:'上传声音文件…',action:()=>{uploadToTrack=trackKind;$('#audio-file').click();}});if(trackKind==='audio')rows.push({label:'合成语音…',action:()=>openAudioDialog()});}if(clipboard.length)rows.push({label:'粘贴已复制的片段',action:()=>pasteClips(start)});if(rows.length)rows.push(null);rows.push({heading:'添加'+({motion:'动作',expression:'表情',audio:'机器人声音',music:'电脑音乐'}[trackKind])});for(const item of resourceRows(trackKind)){rows.push({label:`${item.label} · ${seconds(durationOf(item,trackKind))} 秒`,action:()=>addClip(trackKind,item,start)});}showMenu(e,rows);}
function showClipMenu(e,clip){const rows=[{heading:clipLabel(clip)},{label:'复制',action:copySelected},{label:'粘贴到所选片段之后',action:()=>pasteClips()},{label:clip.muted?'取消屏蔽':'屏蔽片段',action:muteSelected},{label:'移除',action:removeSelected}];const kind=trackOf(clip.id)?.kind;if(kind==='motion'){const current=resources.actions.find(a=>a.id===clip.resourceId);const fam=current?.familyId||clip.resourceSnapshot?.familyId;const currentLabel=current?.variantLabel||clip.resourceSnapshot?.variantLabel||'';if(fam){rows.push(null,{heading:'节奏版本'});for(const v of motionVariantsFor(fam)){rows.push({label:(v.label===currentLabel?'✓ ':'')+v.label,action:()=>switchClipMotionVariant(clip,v.label)});}}}if(kind==='expression'){const n=clipLoopCount(clip);rows.push(null,{heading:'表情循环'},{label:`重复＋（当前 ×${n}）`,action:()=>setExpressionLoopCount(clip,n+1)});if(n>1)rows.push({label:'减少重复',action:()=>setExpressionLoopCount(clip,n-1)});}showMenu(e,rows);}
function copySelected(){clipboard=[...selected].map(id=>{const c=byId(id),t=trackOf(id);return c&&t?{kind:t.kind,clip:structuredClone(c)}:null;}).filter(Boolean);if(clipboard.length){clipboardAfter=Math.max(...clipboard.map(x=>x.clip.startMs+x.clip.durationMs));notify(`已复制 ${clipboard.length} 个片段`);}}
function pasteClips(at=clipboardAfter){if(!clipboard.length)return;const base=Math.min(...clipboard.map(x=>x.clip.startMs));const ids=[];let end=at;const members=clipboard.map(({kind,clip})=>({kind,startMs:clip.startMs-base,durationMs:clip.durationMs})),delta=fitClips(members,at);edit(()=>{for(const {kind,clip} of clipboard){const next=structuredClone(clip);next.id=safeId();next.startMs=delta+clip.startMs-base;track(kind).clips.push(next);ids.push(next.id);end=Math.max(end,next.startMs+next.durationMs);}});clipboardAfter=end;selected=new Set(ids);renderTimeline();renderInspector();notify(`已粘贴 ${ids.length} 个片段`);}
function muteSelected(){const clips=[...selected].map(byId).filter(Boolean);if(!clips.length)return;const value=!clips.every(c=>c.muted);edit(()=>clips.forEach(c=>c.muted=value));}
function removeSelected(){if(!selected.size)return;edit(()=>{for(const t of composition.tracks)t.clips=t.clips.filter(c=>!selected.has(c.id));});selected.clear();renderTimeline();renderInspector();}
function stopPreview(){playing=false;for(const audio of playAudio.values())audio.pause();playAudio.clear();$('#preview-play').textContent='▶ 预览';}
function frame(){if(!playing)return;playhead=Math.max(0,performance.now()-playStart);if(playhead>=totalMs()){playhead=totalMs();stopPreview();}document.querySelectorAll('.playhead').forEach(x=>x.style.left=playhead/1000*zoom+'px');renderPreview();for(const t of composition.tracks.filter(x=>['audio','music'].includes(x.kind)&&!x.muted))for(const c of t.clips){const active=!c.muted&&playhead>=c.startMs&&playhead<c.startMs+c.durationMs;let sound=playAudio.get(c.id);if(active&&!sound&&c.resourceSnapshot?.url){sound=new Audio(c.resourceSnapshot.url);sound.currentTime=(playhead-c.startMs)/1000;sound.play().catch(()=>notify('浏览器未允许音频预览，请点击预览后重试',true));playAudio.set(c.id,sound);}if(!active&&sound){sound.pause();playAudio.delete(c.id);}}if(playing)requestAnimationFrame(frame);}
let editingAudio=null,uploadToTrack=false,replaceAudio=null,previewingAudio=null;
function previewAudio(item){if(previewingAudio){previewingAudio.pause();previewingAudio=null;}
 previewingAudio=new Audio(item.url);previewingAudio.play().catch(()=>notify('浏览器无法播放此声音',true));}
async function playOnRobot(item){
 notify('正在通过 Wi-Fi 发送到机器人扬声器…');
 try{await request('/api/audio/play',{filename:item.url.split('/').at(-1)});notify(`机器人已播放：${item.label}`);}
 catch(error){notify(error.message,true);}
}
async function uploadAudio(file){
 if(!file)return;
 const query=new URLSearchParams({name:file.name});
 if(replaceAudio){query.set('id',replaceAudio.id);query.set('label',$('#audio-name').value.trim()||replaceAudio.label);}
 const response=await fetch('/api/audio/upload?'+query,{method:'POST',headers:{'Content-Type':file.type||'application/octet-stream'},body:file});
 const data=await response.json();if(!response.ok)throw Error(data.error||'声音上传失败');
 const index=resources.audio.findIndex(x=>x.id===data.id);if(index<0)resources.audio.push(data);else resources.audio[index]=data;
 renderResources();
 if(uploadToTrack)addClip(uploadToTrack,data,menuStart);
 notify(replaceAudio?`已更新：${data.label}`:`已导入：${data.label}`);
 uploadToTrack=false;replaceAudio=null;$('#audio-dialog').close();
}
function openAudioDialog(item=null){
 editingAudio=item;$('#audio-dialog-title').textContent=item?'修改声音资源':'合成机器人语音';
 $('#audio-name').value=item?.label||'';$('#audio-text').value=item?.text||'';
 const isUpload=item&&item.origin!=='tts';
 $('#audio-text-label').hidden=!!isUpload;$('#audio-replace').hidden=!isUpload;
 $('#audio-save').textContent=isUpload?'保存名称':item?'重新合成并保存':'生成并加入资源库';
 $('#audio-dialog').showModal();(isUpload?$('#audio-name'):$('#audio-text')).focus();
}
async function removeAudio(item){
 if(!confirm(`从资源库删除“${item.label}”？已保存组合仍保留此声音版本。`))return;
 await request('/api/audio/'+item.id,{action:'delete'});
 resources.audio=resources.audio.filter(x=>x.id!==item.id);renderResources();notify('已从声音资源库删除');
}
async function saveAudioDialog(){
 const name=$('#audio-name').value.trim(),text=$('#audio-text').value.trim();
 if(!name)throw Error('请给声音命名');
 let item;
 if(editingAudio?.origin!=='tts'&&editingAudio){item=await request('/api/audio/'+editingAudio.id,{action:'rename',label:name});}
 else{if(!text)throw Error('请输入要说的话');item=await request('/api/audio/synthesize',{id:editingAudio?.id,label:name,text});}
 const index=resources.audio.findIndex(x=>x.id===item.id);if(index<0)resources.audio.push(item);else resources.audio[index]=item;
 renderResources();$('#audio-dialog').close();notify(`已保存声音：${item.label}`);
}
async function loadResources(){resources=await request('/api/resources');renderResources();renderTimeline();notify('资源库已刷新');}
async function loadSaved(){saved=await request('/api/compositions');renderSaved();}
async function openComposition(id){if(dirty&&composition.tracks.some(t=>t.clips.length)&&!confirm('当前修改还未保存。要放弃并打开另一个组合吗？'))return;stopPreview();composition=await request('/api/compositions/'+id);for(const [kind] of TRACKS)if(!track(kind))composition.tracks.push({id:kind,kind,muted:false,clips:[]});selected.clear();history=[];future=[];playhead=0;dirty=false;$('#name').value=composition.name;$('#voice-trigger').value=composition.trigger||'';$('#save-state').textContent=`已保存 · 版本 ${composition.revision}`;$('#save-state').classList.remove('dirty');renderSaved();renderTimeline();renderInspector();renderPreview();}
async function saveComposition(silent=false){composition.name=$('#name').value.trim();composition.trigger=$('#voice-trigger').value.trim();if(!composition.name){notify('请先给组合命名',true);$('#name').focus();return null;}if(!dirty&&composition.id){if(!silent)notify('组合已是最新保存版本');return composition.id;}try{const savedItem=await request('/api/compositions',composition);composition=savedItem;dirty=false;$('#save-state').textContent=`已保存 · 版本 ${composition.revision}`;$('#save-state').classList.remove('dirty');await loadSaved();if(!silent)notify(`已保存：${composition.name}`);return composition.id;}catch(e){notify(e.message,true);return null;}}
function newComposition(){if(dirty&&composition.tracks.some(t=>t.clips.length)&&!confirm('当前修改还未保存。要新建组合吗？'))return;stopPreview();composition={id:null,revision:null,name:'未命名组合',trigger:'',tracks:freshTracks()};selected.clear();history=[];future=[];playhead=0;$('#name').value=composition.name;$('#voice-trigger').value='';markDirty();renderTimeline();renderInspector();renderPreview();$('#name').select();}
$('#name').oninput=()=>{composition.name=$('#name').value;markDirty();};$('#voice-trigger').oninput=()=>{composition.trigger=$('#voice-trigger').value;markDirty();};$('#save-composition').onclick=()=>saveComposition();$('#new-composition').onclick=newComposition;$('#reload-compositions').onclick=()=>loadSaved().catch(e=>notify(e.message,true));$('#reload-resources').onclick=()=>loadResources().catch(e=>notify(e.message,true));$('#resource-search').oninput=renderResources;$('#show-original').onchange=renderResources;document.querySelectorAll('#resource-tabs button').forEach(b=>b.onclick=()=>{kind=b.dataset.kind;document.querySelectorAll('#resource-tabs button').forEach(x=>x.classList.toggle('active',x===b));$('#show-original').parentElement.hidden=kind!=='motion';$('#audio-tools').hidden=kind!=='audio';renderResources();});$('#zoom').oninput=e=>{zoom=Number(e.target.value);renderTimeline();};$('#undo').onclick=undo;$('#redo').onclick=redo;$('#copy-selection').onclick=copySelected;$('#mute-selection').onclick=muteSelected;$('#remove-selection').onclick=removeSelected;
$('#expr-loop-add').onclick=()=>{const c=byId([...selected][0]);if(!c||trackOf(c.id)?.kind!=='expression')return;setExpressionLoopCount(c,clipLoopCount(c)+1);};
$('#expr-loop-remove').onclick=()=>{const c=byId([...selected][0]);if(!c||trackOf(c.id)?.kind!=='expression')return;setExpressionLoopCount(c,clipLoopCount(c)-1);};$('#clip-start').onchange=e=>{const c=byId([...selected][0]);if(!c)return;const n=Number(e.target.value);if(!Number.isFinite(n)||n<0)return notify('开始时间必须为非负数',true);edit(()=>c.startMs=fitClips([{kind:trackOf(c.id).kind,startMs:0,durationMs:c.durationMs}],Math.round(n*1000),[c.id]));};$('#clip-duration').onchange=e=>{const c=byId([...selected][0]);if(!c||trackOf(c.id).kind==='motion')return;const n=Math.round(Number(e.target.value)*1000);if(!Number.isFinite(n)||n<1)return notify('时长至少为 1 毫秒',true);edit(()=>{c.durationMs=n;c.startMs=fitClips([{kind:trackOf(c.id).kind,startMs:0,durationMs:n}],c.startMs,[c.id]);});};$('#preview-play').onclick=()=>{if(playing){stopPreview();return;}if(!totalMs())return notify('先添加片段，再预览');if(playhead>=totalMs())playhead=0;playing=true;playStart=performance.now()-playhead;$('#preview-play').textContent='Ⅱ 暂停';frame();};$('#preview-stop').onclick=()=>{stopPreview();playhead=0;renderTimeline();renderPreview();};$('#audio-upload').onclick=()=>{replaceAudio=null;uploadToTrack=false;$('#audio-file').click();};$('#audio-synthesize').onclick=()=>openAudioDialog();$('#audio-replace').onclick=()=>{replaceAudio=editingAudio;uploadToTrack=false;$('#audio-file').click();};$('#audio-form').onsubmit=e=>{if(e.submitter?.value!=='save')return;e.preventDefault();saveAudioDialog().catch(x=>notify(x.message,true));};$('#audio-file').onchange=e=>{const file=e.target.files[0];if(file)uploadAudio(file).catch(x=>notify(x.message,true));else{replaceAudio=null;uploadToTrack=false;}e.target.value='';};
document.addEventListener('click',e=>{if(!e.target.closest('#menu'))hideMenu();});document.addEventListener('contextmenu',e=>{if(!e.target.closest('#menu')&&!e.target.closest('.lane')&&!e.target.closest('.track-label')&&!e.target.closest('.resource-item'))hideMenu();});document.addEventListener('keydown',e=>{const editable=e.target.closest('input,textarea,[contenteditable="true"]');if(e.key==='Escape'){hideMenu();return;}if(editable)return;if(selected.size&&!e.metaKey&&!e.ctrlKey&&['ArrowLeft','ArrowRight'].includes(e.key)){e.preventDefault();const clips=[...selected].map(byId).filter(Boolean);const step=e.altKey?1:e.shiftKey?100:10;const delta=(e.key==='ArrowRight'?1:-1)*step;const shift=fitClips(clips.map(c=>({kind:trackOf(c.id).kind,startMs:c.startMs,durationMs:c.durationMs})),delta,[...selected]);if(shift)edit(()=>clips.forEach(c=>c.startMs+=shift));return;}if(!(e.metaKey||e.ctrlKey))return;const key=e.key.toLowerCase();if(key==='c'&&selected.size){e.preventDefault();copySelected();}else if(key==='v'&&clipboard.length){e.preventDefault();pasteClips();}else if(key==='z'){e.preventDefault();e.shiftKey?redo():undo();}});

const VOICE_CHUNK_BYTES=65536,VOICE_CHUNK_SAMPLES=VOICE_CHUNK_BYTES/2;
const VOICE_SOURCE_LABEL={browser:'网页',robot:'机器人',computer:'本机 FFmpeg'};
let browserMic=null;

function syncMicHelp(source){
 const help=$('#mic-permission-help');
 if(!help)return;
 help.hidden=source==='robot';
 help.textContent=source==='browser'
  ?'优先用网页麦克风：点击开启后浏览器会请求本机麦权限（地址栏左侧可改）。'
  :source==='computer'
  ?'本机 FFmpeg 麦克风需在 macOS「系统设置 → 隐私与安全性 → 麦克风」允许运行本服务的应用（终端 / Cursor）。'
  :'机器人麦克风经 Wi-Fi 采集，不占用电脑麦克风权限。';
}

async function stopBrowserMic(){
 if(!browserMic)return;
 try{browserMic.processor.onaudioprocess=null;}catch(_){ }
 try{browserMic.processor.disconnect();}catch(_){ }
 try{browserMic.source.disconnect();}catch(_){ }
 try{browserMic.mute.disconnect();}catch(_){ }
 try{await browserMic.ctx.close();}catch(_){ }
 browserMic.stream.getTracks().forEach(t=>t.stop());
 browserMic=null;
}

async function startBrowserMic(){
 await stopBrowserMic();
 if(!navigator.mediaDevices?.getUserMedia)throw Error('当前浏览器不支持网页麦克风');
 const stream=await navigator.mediaDevices.getUserMedia({audio:{channelCount:1,echoCancellation:true,noiseSuppression:true,autoGainControl:true},video:false});
 const ctx=new(window.AudioContext||window.webkitAudioContext)();
 if(ctx.state==='suspended')await ctx.resume();
 const source=ctx.createMediaStreamSource(stream);
 const processor=ctx.createScriptProcessor(4096,1,1);
 const mute=ctx.createGain();mute.gain.value=0;
 let pending=new Int16Array(0);
 let posting=false;
 const queue=[];
 const flush=async()=>{
  if(posting||!queue.length||!browserMic)return;
  posting=true;
  try{
   while(queue.length&&browserMic){
    const body=queue.shift();
    const response=await fetch('/api/voice/chunk',{method:'POST',headers:{'Content-Type':'application/octet-stream'},body});
    const data=await response.json();
    if(!response.ok)throw Error(data.error||`HTTP ${response.status}`);
   }
  }catch(e){notify(e.message,true);await stopBrowserMic();try{await request('/api/voice',{action:'stop'});}catch(_){ }await refreshVoice();}
  finally{posting=false;if(queue.length)flush();}
 };
 processor.onaudioprocess=e=>{
  if(!browserMic)return;
  const input=e.inputBuffer.getChannelData(0);
  const ratio=ctx.sampleRate/16000;
  const outLen=Math.floor(input.length/ratio);
  if(outLen<1)return;
  const next=new Int16Array(pending.length+outLen);
  next.set(pending,0);
  for(let i=0;i<outLen;i++){
   const sample=Math.max(-1,Math.min(1,input[Math.floor(i*ratio)]||0));
   next[pending.length+i]=sample<0?sample*0x8000:sample*0x7fff;
  }
  let offset=0;
  while(next.length-offset>=VOICE_CHUNK_SAMPLES){
   const chunk=new Int16Array(VOICE_CHUNK_SAMPLES);
   chunk.set(next.subarray(offset,offset+VOICE_CHUNK_SAMPLES));
   queue.push(chunk.buffer);
   offset+=VOICE_CHUNK_SAMPLES;
  }
  pending=next.subarray(offset);
  flush();
 };
 source.connect(processor);processor.connect(mute);mute.connect(ctx.destination);
 browserMic={stream,ctx,source,processor,mute};
}

function sourceLabel(source){return VOICE_SOURCE_LABEL[source]||source||'网页';}

async function refreshVoice(){try{const [voice,run]=await Promise.all([request('/api/voice'),request('/api/compositions/run')]);$('#voice-toggle').textContent=voice.listening?'停止监听':'开启监听';$('#voice-toggle').classList.toggle('active',voice.listening);const source=voice.source||'browser';if(document.activeElement!==$('#voice-source'))$('#voice-source').value=source;syncMicHelp($('#voice-source').value||source);if(!voice.listening||source!=='browser')await stopBrowserMic();const phase={loading:'正在加载模型',wake:'等待“小黄小黄”',command:'已唤醒，正在识别指令'};$('#voice-status').textContent=voice.error?'识别出错：'+voice.error:voice.listening?`${phase[voice.phase]||'正在监听'} · ${sourceLabel(source)}麦克风${voice.lastText?' · 听到：'+voice.lastText:''}${voice.lastTrigger?' · 上次触发：'+voice.lastTrigger:''}`:'监听未开启';$('#robot-run').disabled=run.running;$('#robot-stop').disabled=!run.running;if(run.error)$('#voice-status').textContent+=' · 执行失败：'+run.error;}catch(e){$('#voice-status').textContent=e.message;}}

async function setVoiceListening(wantStart){
 const source=$('#voice-source').value||'browser';
 if(!wantStart){await stopBrowserMic();await request('/api/voice',{action:'stop'});return;}
 try{
  await request('/api/voice',{action:'start',source});
 }catch(e){
  await stopBrowserMic();
  throw e;
 }
 if(source==='browser'){
  try{await startBrowserMic();}
  catch(e){await stopBrowserMic();try{await request('/api/voice',{action:'stop'});}catch(_){ }
   throw Error('网页麦克风无法开启：'+e.message+'。可改选「本机 FFmpeg 麦克风」或「机器人麦克风」。');}
 }
}

$('#voice-toggle').onclick=async()=>{try{await setVoiceListening(!$('#voice-toggle').classList.contains('active'));await refreshVoice();}catch(e){notify(e.message,true);await refreshVoice();}};
$('#voice-source').onchange=async()=>{syncMicHelp($('#voice-source').value);if(!$('#voice-toggle').classList.contains('active'))return;try{await stopBrowserMic();await setVoiceListening(true);await refreshVoice();}catch(e){notify(e.message,true);await refreshVoice();}};
$('#robot-run').onclick=async()=>{const id=await saveComposition(true);if(!id)return;try{await request('/api/compositions/run',{id});await refreshVoice();notify('已保存，机器人正在执行组合');}catch(e){notify(e.message,true);}};
$('#robot-stop').onclick=async()=>{try{await request('/api/compositions/stop',{});await refreshVoice();}catch(e){notify(e.message,true);}};
window.addEventListener('beforeunload',()=>{stopBrowserMic();});
syncMicHelp($('#voice-source').value||'browser');
setInterval(()=>refreshVoice(),1500);
(async()=>{try{await Promise.all([loadResources(),loadSaved()]);renderTimeline();renderInspector();renderPreview();await refreshVoice();}catch(e){notify(e.message,true);}})();
