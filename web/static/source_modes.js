// Browser camera frames share the robot scheduler with voice-triggered compositions.
(() => {
 const source = document.querySelector('#voice-source');
 const toggle = document.querySelector('#voice-toggle');
 source.replaceChildren(...[['browser','网页麦克风'],['video','视频'],['both','网页麦克风和视频']].map(([value,text]) => {
  const option=document.createElement('option'); option.value=value; option.textContent=text; return option;
 }));
 source.setAttribute('aria-label','识别数据源');
 const panel=document.createElement('section');
 panel.className='camera-input'; panel.hidden=true;
 panel.innerHTML='<div class="camera-picture"><video autoplay muted playsinline></video><div class="camera-labels" role="status"></div></div><span class="camera-status" role="status">视频未开启</span>';
 document.querySelector('.voicebar').after(panel);
 const video=panel.querySelector('video'), labels=panel.querySelector('.camera-labels'), status=panel.querySelector('.camera-status');
 let stream=null, token=null, epoch=0, running=false, changing=false;
 const canvas=document.createElement('canvas');
 const help=document.querySelector('#mic-permission-help');
 help.textContent='';

 async function stopVideo() {
  epoch++;
  const oldToken=token; token=null;
  if(stream)stream.getTracks().forEach(track=>track.stop());
  stream=null; video.srcObject=null; labels.textContent=''; panel.hidden=true;
  if(oldToken)await request('/api/video/stop',{token:oldToken});
 }
 async function frames(generation) {
  while(generation===epoch && token) {
   try {
    if(!video.videoWidth){await new Promise(r=>setTimeout(r,100));continue;}
    canvas.width=Math.min(960,video.videoWidth);
    canvas.height=Math.round(video.videoHeight*canvas.width/video.videoWidth);
    canvas.getContext('2d').drawImage(video,0,0,canvas.width,canvas.height);
    const jpeg=await new Promise(resolve=>canvas.toBlob(resolve,'image/jpeg',0.78));
    if(generation!==epoch || !token)return;
    const response=await fetch('/api/video/frame',{method:'POST',headers:{'Content-Type':'image/jpeg','X-Video-Token':token},body:jpeg});
    const result=await response.json();
    if(generation!==epoch)return;
    if(!response.ok)throw Error(result.error||'视频识别失败');
    if(result.active===false)throw Error('视频会话已关闭');
    if(!result.busy){labels.textContent=(result.names||[]).join('\n');status.textContent=result.message||'视频识别中';}
    await new Promise(r=>setTimeout(r,60));
   } catch(error) {
    if(generation!==epoch)return;
    notify(error.message,true);
    await disable();
    return;
   }
  }
 }
 async function startVideo() {
  stream=await navigator.mediaDevices.getUserMedia({video:{width:{ideal:1280},height:{ideal:720}},audio:false});
  video.srcObject=stream; panel.hidden=false; status.textContent='正在加载识别模型';
  await video.play();
  const result=await request('/api/video/start',{}); token=result.token;
  const generation=++epoch;
  stream.getVideoTracks()[0].onended=()=>{if(generation===epoch)disable().catch(e=>notify(e.message,true));};
  frames(generation);
 }
 async function disable() {
  running=false;
  const results=await Promise.allSettled([stopVideo(),stopBrowserMic(),request('/api/voice',{action:'stop'})]);
  toggle.classList.remove('active'); toggle.textContent='开启识别';
  const failed=results.find(x=>x.status==='rejected');
  if(failed)notify(failed.reason.message,true);
 }
 async function enable() {
  try {
   if(source.value!=='video') {
    await startBrowserMic();
    await request('/api/voice',{action:'start',source:'browser'});
   }
   if(source.value!=='browser')await startVideo();
   running=true; toggle.classList.add('active'); toggle.textContent='关闭识别';
  } catch(error) {await disable();throw error;}
 }
 async function change(operation) {
  if(changing)return;
  changing=true; source.disabled=true; toggle.disabled=true;
  try{await operation();}catch(error){notify(error.message,true);}
  finally{changing=false;source.disabled=false;toggle.disabled=false;}
 }
 toggle.onclick=()=>change(()=>running?disable():enable());
 source.onchange=()=>change(async()=>{if(running){await disable();await enable();}});
 // Existing polling calls this function by name; retain voice and runner status.
 refreshVoice=async()=>{
  try {
   const [voice,run]=await Promise.all([request('/api/voice'),request('/api/compositions/run')]);
   const phase={loading:'正在加载语音模型',wake:'等待“小黄小黄”',command:'正在识别语音'};
   document.querySelector('#voice-status').textContent=voice.error?'语音：'+voice.error:voice.listening?(phase[voice.phase]||'语音监听中')+(voice.lastText?' · '+voice.lastText:''):'麦克风未开启';
   document.querySelector('#robot-run').disabled=run.running;
   document.querySelector('#robot-stop').disabled=false;
   if(run.error)document.querySelector('#voice-status').textContent+=' · '+run.error;
   if(running && source.value!=='video' && !voice.listening && !changing)await disable();
  }catch(error){document.querySelector('#voice-status').textContent=error.message;}
 };
 document.querySelector('#robot-stop').onclick=async()=>{
  await disable();
  try{await request('/api/compositions/stop',{});await request('/api/stop',{});await refreshVoice();}
  catch(error){notify(error.message,true);}
 };
 window.addEventListener('pagehide',()=>{
  epoch++;
  if(stream)stream.getTracks().forEach(t=>t.stop());
  if(token)navigator.sendBeacon('/api/video/stop',new Blob([JSON.stringify({token})],{type:'application/json'}));
  if(running && source.value!=='video')navigator.sendBeacon('/api/voice',new Blob([JSON.stringify({action:'stop'})],{type:'application/json'}));
 });
 toggle.textContent='开启识别';
})();
