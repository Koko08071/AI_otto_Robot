"""Local composition and resource storage; independent of the robot transport."""
from __future__ import annotations
import hashlib
import json
import os
import re
import shutil
import subprocess
import threading
import uuid
import wave
import sys
from audio_tools import ffmpeg
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STATIC = ROOT/'static'
LIBRARY = ROOT/'library'
COMPOSITIONS = LIBRARY/'compositions'
AUDIO = LIBRARY/'audio'
BEHAVIORS = ROOT/'behaviors'
_LOCK = threading.RLock()
_ID = re.compile(r'^[a-f0-9-]{36}$')
_KINDS = {'motion','expression','audio','music'}

class StoreError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status=status

def _read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))

def resource_catalog():
    def path_for(env, default):
        candidate=Path(os.environ.get(env, str(default))).expanduser()
        if not candidate.is_file(): raise StoreError(f'资源目录不存在：{candidate}',503)
        return candidate
    actions=_read_json(path_for('OTTO_ACTION_CATALOG',STATIC/'actions.json'))
    expressions=_read_json(path_for('OTTO_EXPRESSION_CATALOG',STATIC/'expressions.json'))
    if not isinstance(actions,list) or not isinstance(expressions,list): raise StoreError('资源目录必须是数组',503)
    for kind,entries in [('动作',actions),('表情',expressions)]:
        ids=set()
        for entry in entries:
            if not isinstance(entry,dict) or not isinstance(entry.get('id'),str) or not isinstance(entry.get('label'),str):
                raise StoreError(f'{kind}资源缺少 id 或 label',503)
            if entry['id'] in ids:raise StoreError(f'{kind}资源 ID 重复：{entry["id"]}',503)
            ids.add(entry['id'])
    for action in actions:
        edited=BEHAVIORS/(action['id']+'.json')
        if edited.is_file():
            action['program']=_read_json(edited)
            action['edited']=True
        segments=action.get('program',{}).get('segments')
        if not isinstance(segments,list) or not segments or any(
            not isinstance(s,dict) or isinstance(s.get('duration'),bool)
            or not isinstance(s.get('duration'),int) or s['duration']<1 for s in segments
        ):raise StoreError(f'动作 {action["id"]} 缺少有效的 program.segments 时长',503)
    for expression in expressions:
        duration=expression.get('durationMs')
        if isinstance(duration,bool) or not isinstance(duration,int) or duration<1:
            raise StoreError(f'表情 {expression["id"]} 缺少正整数 durationMs',503)
    audio=[]
    if AUDIO.is_dir():
        for p in AUDIO.glob('*.json'):
            try:
                item=_read_json(p)
                if not item.get('deleted'):audio.append(item)
            except (OSError,ValueError):continue
    audio.sort(key=lambda item:item['label'].casefold())
    return dict(actions=actions,expressions=expressions,audio=audio)

def _summary(item):
    return {key:item[key] for key in ('id','name','revision','updatedAt','durationMs','clipCount')}|{'trigger':item.get('trigger','')}

def list_compositions():
    if not COMPOSITIONS.is_dir():return []
    items=[]
    for p in COMPOSITIONS.glob('*.json'):
        try:items.append(_summary(_read_json(p)))
        except (OSError,ValueError,KeyError):continue
    return sorted(items,key=lambda item:item['updatedAt'],reverse=True)

def voice_phrases(value):
    return [part.strip() for part in re.split(r'[,，、;；\n]+',value) if part.strip()]

def match_voice_trigger(transcript, items):
    from opencc import OpenCC
    converter=OpenCC('t2s')
    def normalized(value):return ''.join(c for c in converter.convert(value).casefold() if c.isalnum())
    heard=normalized(transcript)
    candidates=sorted(((phrase,item) for item in items for phrase in voice_phrases(item.get('trigger',''))),
                      key=lambda pair:len(normalized(pair[0])),reverse=True)
    return next((item for phrase,item in candidates if normalized(phrase) in heard),None)

def get_composition(identifier):
    if not _ID.fullmatch(identifier):raise StoreError('组合 ID 无效',404)
    p=COMPOSITIONS/(identifier+'.json')
    if not p.is_file():raise StoreError('组合不存在',404)
    return _read_json(p)

def delete_composition(identifier):
    with _LOCK:
        path=COMPOSITIONS/(identifier+'.json')
        get_composition(identifier)
        path.unlink()
        return {'id':identifier,'deleted':True}

def _nonnegative_int(value,label):
    if isinstance(value,bool) or not isinstance(value,int) or value<0:raise StoreError(f'{label} 必须为非负整数毫秒')
    return value

def validate_composition(value):
    if not isinstance(value,dict) or not isinstance(value.get('name'),str) or not value['name'].strip():
        raise StoreError('请给组合命名')
    tracks=value.get('tracks')
    trigger=value.get('trigger','')
    if not isinstance(trigger,str) or len(trigger)>400:raise StoreError('语音触发词总长度至多 400 字')
    phrases=voice_phrases(trigger)
    if any(len(phrase)>40 for phrase in phrases):raise StoreError('每个语音触发词至多 40 字')
    if any(not any(char.isalnum() for char in phrase) for phrase in phrases):raise StoreError('语音触发词必须包含文字或数字')
    if len({phrase.casefold() for phrase in phrases})!=len(phrases):raise StoreError('同一组合的语音触发词不能重复')
    if not isinstance(tracks,list):raise StoreError('tracks 必须为数组')
    seen_tracks=set();seen_clips=set();normalized=[];end=0;count=0
    for track in tracks:
        if not isinstance(track,dict) or track.get('kind') not in _KINDS:raise StoreError('轨道类型无效')
        kind=track['kind'];key=track.get('id')
        if not isinstance(key,str) or not key or key in seen_tracks:raise StoreError('轨道 ID 无效或重复')
        seen_tracks.add(key)
        muted=track.get('muted',False)
        if not isinstance(muted,bool) or not isinstance(track.get('clips'),list):raise StoreError('轨道内容无效')
        clips=[]
        for clip in track['clips']:
            if not isinstance(clip,dict):raise StoreError('片段必须是对象')
            cid=clip.get('id');resource=clip.get('resourceId')
            if not isinstance(cid,str) or not cid or cid in seen_clips:raise StoreError('片段 ID 无效或重复')
            if not isinstance(resource,str) or not resource:raise StoreError('片段资源 ID 无效')
            seen_clips.add(cid)
            start=_nonnegative_int(clip.get('startMs'),'开始时间')
            duration=_nonnegative_int(clip.get('durationMs'),'时长')
            if not duration:raise StoreError('片段时长必须大于 0')
            if start+duration>4294967295:raise StoreError('组合时长超出毫秒时间线范围')
            muted_clip=clip.get('muted',False)
            if not isinstance(muted_clip,bool):raise StoreError('片段屏蔽状态无效')
            snapshot=clip.get('resourceSnapshot',{})
            if not isinstance(snapshot,dict):raise StoreError('资源快照无效')
            loop_count=clip.get('loopCount', 1)
            if loop_count is None: loop_count = 1
            if not isinstance(loop_count, int) or isinstance(loop_count, bool) or loop_count < 1 or loop_count > 99:
                raise StoreError('表情循环次数须为 1–99 的整数')
            if kind != 'expression' and loop_count != 1:
                raise StoreError('只有表情片段可设置循环次数')
            entry=dict(id=cid,resourceId=resource,startMs=start,durationMs=duration,muted=muted_clip,resourceSnapshot=snapshot)
            if kind == 'expression':
                entry['loopCount'] = loop_count
            clips.append(entry)
            end=max(end,start+duration);count+=1
        ordered=sorted(clips,key=lambda clip:clip['startMs'])
        if any(a['startMs']+a['durationMs']>b['startMs'] for a,b in zip(ordered,ordered[1:])):
            raise StoreError(f'{kind} 轨道上的片段不能重叠')
        normalized.append(dict(id=key,kind=kind,muted=muted,clips=clips))
    return dict(name=value['name'].strip(),trigger='，'.join(phrases),tracks=normalized,durationMs=end,clipCount=count)

def save_composition(value):
    valid=validate_composition(value)
    with _LOCK:
        identifier=value.get('id');old=None
        if identifier is not None:
            old=get_composition(identifier)
            if value.get('revision')!=old['revision']:raise StoreError('此组合已有较新版本，请重新打开后再保存',409)
        else:identifier=str(uuid.uuid4())
        if valid['trigger']:
            from opencc import OpenCC
            converter=OpenCC('t2s')
            clean=lambda text:''.join(c for c in converter.convert(text).casefold() if c.isalnum())
            incoming={clean(phrase) for phrase in voice_phrases(valid['trigger'])}
            for item in list_compositions():
                existing={clean(phrase) for phrase in voice_phrases(item.get('trigger',''))}
                if item['id']!=identifier and incoming & existing:
                    raise StoreError('这个语音关键词已分配给另一个组合')
        now=datetime.now(timezone.utc).isoformat()
        item=dict(schemaVersion=1,id=identifier,name=valid['name'],trigger=valid['trigger'],revision=old['revision']+1 if old else 1,
                  createdAt=old['createdAt'] if old else now,updatedAt=now,durationMs=valid['durationMs'],
                  clipCount=valid['clipCount'],tracks=valid['tracks'])
        COMPOSITIONS.mkdir(parents=True,exist_ok=True)
        target=COMPOSITIONS/(identifier+'.json');tmp=COMPOSITIONS/(identifier+'.'+uuid.uuid4().hex+'.tmp')
        tmp.write_text(json.dumps(item,ensure_ascii=False,indent=2),encoding='utf-8');tmp.replace(target)
        return item

def _audio_meta(identifier):
    if not _ID.fullmatch(identifier):raise StoreError('声音资源不存在',404)
    path=AUDIO/(identifier+'.json')
    if not path.is_file():raise StoreError('声音资源不存在',404)
    return _read_json(path)

def _write_audio_meta(item):
    target=AUDIO/(item['id']+'.json');tmp=target.with_suffix('.tmp')
    tmp.write_text(json.dumps(item,ensure_ascii=False,indent=2),encoding='utf-8')
    tmp.replace(target)

def _convert_audio(source,identifier,label,origin,old=None,text=None):
    executable=ffmpeg()
    target=AUDIO/(identifier+'-'+uuid.uuid4().hex+'.wav')
    command=[executable,'-nostdin','-hide_banner','-loglevel','error','-y','-i',str(source),'-map','0:a:0','-vn']
    if origin=='tts':command+=['-af','highpass=f=180,lowpass=f=3600,tremolo=f=9:d=0.12,acompressor=threshold=0.04:ratio=4:attack=4:release=80:makeup=6,alimiter=limit=0.94:level=0']
    command+=['-ac','1','-ar','24000','-c:a','pcm_s16le',str(target)]
    result=subprocess.run(command,
                          capture_output=True,text=True,timeout=120)
    if result.returncode or not target.is_file():
        target.unlink(missing_ok=True)
        raise StoreError('文件没有可用音轨，或格式无法转换')
    with wave.open(str(target),'rb') as wav:
        duration=max(1,round(wav.getnframes()*1000/wav.getframerate()))
    item=dict(id=identifier,label=label.strip(),kind='audio',mime='audio/wav',durationMs=duration,
              url='/api/audio/'+target.name,sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
              revision=old['revision']+1 if old else 1,origin=origin,sourceName=label)
    if text is not None:item['text']=text;item['voice']='Eddy zh-CN · robotic EQ'
    _write_audio_meta(item)
    return item

def save_audio(stream,length,filename,mime,identifier=None,label=None):
    suffix=Path(filename).suffix.lower()
    if suffix not in {'.mp4','.m4a','.mp3','.wav','.aac','.ogg','.opus','.flac','.webm','.aif','.aiff'}:
        raise StoreError('支持 MP4、M4A、MP3、WAV、AAC、OGG、FLAC、WebM、AIFF')
    if length<1:raise StoreError('文件为空')
    AUDIO.mkdir(parents=True,exist_ok=True)
    source=AUDIO/(uuid.uuid4().hex+suffix)
    try:
        with source.open('wb') as out:
            remaining=length
            while remaining:
                chunk=stream.read(min(1024*1024,remaining))
                if not chunk:raise StoreError('声音上传中断')
                out.write(chunk);remaining-=len(chunk)
        with _LOCK:
            old=_audio_meta(identifier) if identifier else None
            if old and old.get('deleted'):raise StoreError('声音资源已删除',404)
            name=(label or (old['label'] if old else Path(filename).stem)).strip()
            if not name:raise StoreError('请给声音命名')
            return _convert_audio(source,identifier or str(uuid.uuid4()),name,'upload',old)
    finally:source.unlink(missing_ok=True)

def synthesize_audio(text,label,identifier=None):
    if not isinstance(text,str) or not text.strip() or len(text)>2000:raise StoreError('请输入 1–2000 字的语音文本')
    if sys.platform!='win32' and not shutil.which('say'):raise StoreError('此平台暂不支持离线语音合成，请上传音频',503)
    AUDIO.mkdir(parents=True,exist_ok=True)
    source=AUDIO/(uuid.uuid4().hex+('.wav' if sys.platform=='win32' else '.aiff'))
    try:
        if sys.platform=='win32':
            request=source.with_suffix('.json')
            request.write_text(json.dumps({'text':text.strip(),'output':str(source.resolve())}),encoding='utf-8')
            try:
                result=subprocess.run(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(ROOT.parent/'tools/windows_tts.ps1'),str(request.resolve())],capture_output=True,text=True,timeout=120)
            finally:request.unlink(missing_ok=True)
        else:
            result=subprocess.run(['say','-v','Eddy (中文（中国大陆）)','-r','190','-o',str(source),text.strip()],capture_output=True,text=True,timeout=120)
        if result.returncode or not source.is_file():raise StoreError('语音合成失败：'+result.stderr.strip())
        with _LOCK:
            old=_audio_meta(identifier) if identifier else None
            if old and old.get('deleted'):raise StoreError('声音资源已删除',404)
            name=(label or (old['label'] if old else text[:20])).strip()
            if not name:raise StoreError('请给声音命名')
            return _convert_audio(source,identifier or str(uuid.uuid4()),name,'tts',old,text.strip())
    finally:source.unlink(missing_ok=True)

def update_audio(identifier,label):
    if not isinstance(label,str) or not label.strip():raise StoreError('请给声音命名')
    with _LOCK:
        item=_audio_meta(identifier)
        if item.get('deleted'):raise StoreError('声音资源已删除',404)
        item['label']=label.strip();item['revision']+=1
        _write_audio_meta(item)
        return item

def delete_audio(identifier):
    with _LOCK:
        item=_audio_meta(identifier)
        item['deleted']=True
        _write_audio_meta(item)
        return {'id':identifier,'deleted':True}

def audio_file(name):
    if not re.fullmatch(r'[a-f0-9-]{36}(?:-[a-f0-9]{32})?\.[a-z0-9]{1,8}',name):raise StoreError('音频不存在',404)
    path=AUDIO/name
    if not path.is_file():raise StoreError('音频不存在',404)
    return path
