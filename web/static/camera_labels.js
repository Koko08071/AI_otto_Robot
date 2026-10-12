(() => {
 const video=document.querySelector('#camera');
 const oldButton=document.querySelector('#camera-toggle');
 const button=oldButton.cloneNode(true);
 oldButton.replaceWith(button);
 const empty=document.querySelector('#camera-empty');
 const container=video.parentElement;
 container.style.position='relative';
 const overlay=document.createElement('div');
 overlay.setAttribute('role','status');
 overlay.id='camera-action-labels';
 Object.assign(overlay.style,{position:'absolute',top:'10px',left:'12px',color:'#46ff66',fontSize:'20px',lineHeight:'1.4',whiteSpace:'pre-line',textShadow:'0 1px 3px #000',maxWidth:'calc(100% - 24px)',overflowWrap:'anywhere',pointerEvents:'none'});
 container.append(overlay);
 const actionStatus=document.createElement('p');
 actionStatus.id='camera-action-status';
 actionStatus.setAttribute('role','status');
 container.after(actionStatus);
 const canvas=document.createElement('canvas');
 let generation=0, token=null;
 async function close() {
  generation++;
  const oldToken=token;
  token=null;
  if(stream)stream.getTracks().forEach(t=>t.stop());
  stream=null; video.srcObject=null; overlay.textContent='';
  actionStatus.textContent='';
  button.textContent='开启'; empty.hidden=false;
  if(oldToken)await api('/api/video/stop',{token:oldToken});
 }
 async function recognize(current) {
  while(current===generation && stream && token) {
   try {
    if(!video.videoWidth){await new Promise(r=>setTimeout(r,100));continue;}
    canvas.width=Math.min(960,video.videoWidth);
    canvas.height=Math.round(video.videoHeight*canvas.width/video.videoWidth);
    canvas.getContext('2d').drawImage(video,0,0,canvas.width,canvas.height);
    const body=await new Promise(resolve=>canvas.toBlob(resolve,'image/jpeg',0.78));
    if(current!==generation || !token)return;
    const response=await fetch('/api/video/frame',{method:'POST',headers:{'Content-Type':'image/jpeg','X-Video-Token':token},body});
    const result=await response.json();
    if(current!==generation)return;
    if(!response.ok)throw Error(result.error||'识别失败');
    if(result.active===false)throw Error('视频会话已结束');
    if(!result.busy){
     overlay.textContent=(result.names||[]).join('\n');
     if(result.message)actionStatus.textContent=result.message;
    }
    await new Promise(r=>setTimeout(r,60));
   } catch(error) {
    if(current!==generation)return;
    await close(); toast('摄像头识别：'+error.message); return;
   }
  }
 }
 button.onclick=async()=>{
  button.disabled=true;
  try {
   if(stream){await close();return;}
   stream=await navigator.mediaDevices.getUserMedia({video:{width:{ideal:1280},height:{ideal:720}},audio:false});
   video.srcObject=stream; empty.hidden=true; button.textContent='关闭';
   await video.play();
   token=(await api('/api/video/start',{})).token;
   const current=++generation;
   stream.getVideoTracks()[0].onended=()=>{if(current===generation)close().catch(error=>toast(error.message));};
   recognize(current);
  } catch(error){await close();toast(error.message);}
  finally{button.disabled=false;}
 };
 window.addEventListener('pagehide',()=>{
  const oldToken=token;
  generation++; token=null;
  if(stream)stream.getTracks().forEach(track=>track.stop());
  if(oldToken)navigator.sendBeacon('/api/video/stop',new Blob([JSON.stringify({token:oldToken})],{type:'application/json'}));
 });
})();
