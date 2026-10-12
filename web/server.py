"""Local Otto console: HTTP browser UI -> BLE or Wi-Fi -> ESP32-S3."""
from __future__ import annotations
import json
import math
import mimetypes
import os
import re
import shutil
import subprocess
import threading
import time
import urllib.error
import urllib.request
import wave
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, unquote, parse_qs
import sys
sys.path.append(str(Path(__file__).resolve().parents[1] / 'gesture_recognition'))
from robot_config import DEVICE_URL, TARGET_ID, setting
from ble_link import BleTransport
from composer_store import StoreError, resource_catalog, list_compositions, get_composition, save_composition, delete_composition, save_audio, synthesize_audio, update_audio, delete_audio, audio_file, match_voice_trigger
from voice_trigger import CHUNK_BYTES, VoiceListener
from video_input import VideoInput, StudioMotion

ROOT = Path(__file__).resolve().parent
STATIC = ROOT/'static'
DATA = ROOT/'behaviors'
CHANNELS = ('ll','rl','lf','rf')
STAND = dict(zip(CHANNELS,(90,90,100,90)))
NAME_RE = re.compile(r'^[a-z][a-z0-9_]{0,39}$')
MAX_BODY = 65536

class RequestError(Exception):
    def __init__(self,message,status=400):
        super().__init__(message); self.status=status

def number(value,low,high,label,integer=False):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or not low<=value<=high or (integer and value!=int(value)):
        raise RequestError(f'{label} 必须为 {low}–{high} 范围内的'+('整数' if integer else '数值'))
    return value

def vector(value,label,low=0,high=180):
    if not isinstance(value,list) or len(value)!=4:
        raise RequestError(f'{label} 必须是四项数组：[左腿,右腿,左脚,右脚]')
    return [number(x,low,high,label) for x in value]

def validate_angles(value):
    if not isinstance(value,dict) or set(value)!=set(CHANNELS):
        raise RequestError('姿态必须包含 ll、rl、lf、rf')
    return {k:number(value[k],0,180,k) for k in CHANNELS}

def validate_program(raw):
    if not isinstance(raw,dict) or not isinstance(raw.get('name'),str) or not NAME_RE.fullmatch(raw['name']):
        raise RequestError('name 必须是小写字母开头、至多 40 位的字母数字下划线名称')
    segments=raw.get('segments')
    if not isinstance(segments,list) or not segments:
        raise RequestError('segments 需要至少一条指令')
    normalized=[]; total=0
    for s in segments:
        if not isinstance(s,dict): raise RequestError('指令必须为对象')
        kind=s.get('type'); duration=number(s.get('duration'),1,4294967295,'duration',True)
        item=dict(type=kind,duration=duration); total+=duration
        if kind=='move': item['pose']=vector(s.get('pose'),'pose')
        elif kind=='oscillate':
            item['period']=number(s.get('period'),1,4294967295,'period',True)
            item['amplitude']=vector(s.get('amplitude'),'amplitude',-180,180)
            item['offset']=vector(s.get('offset'),'offset',-180,180)
            item['phase']=vector(s.get('phase'),'phase',-360000,360000)
            for a,o in zip(item['amplitude'],item['offset']):
                if 90+o-abs(a)<0 or 90+o+abs(a)>180: raise RequestError('振荡轨迹超出舵机 0–180° 范围，请调整幅度或偏移')
        elif kind=='output':
            if not isinstance(s.get('enabled'),bool): raise RequestError('enabled 必须为布尔值')
            item['enabled']=s['enabled']
        elif kind!='hold': raise RequestError('指令类型应为 move / oscillate / hold / output')
        normalized.append(item)
    number(total,1,4294967295,'总时长',True)
    result=dict(name=raw['name'],segments=normalized)
    for key in ('repeat','reset_phase_on_repeat'):
        if key in raw:
            if not isinstance(raw[key],bool): raise RequestError(key+' 必须为布尔值')
            result[key]=raw[key]
    # Includes BLE envelope capacity, even when the current transport is Wi-Fi.
    size=len(json.dumps(dict(id=2147483647,path='/api/play',body=result),separators=(',',':')).encode())+1
    if size>MAX_BODY: raise RequestError('动作超过固件 65536 字节协议缓冲区')
    return result,total,size

class RobotLink:
    def __init__(self):
        self.mode='ble'; self.ble=BleTransport(); self.lock=threading.RLock()
        self.url=DEVICE_URL
        self.urls=[self.url]
        self.connected=False; self.last_pose=dict(STAND); self.last_error=None
    def request(self,path,body=None):
        try:
            if self.mode=='ble':
                reply=self.ble.request(path,body)
                if reply['status']!=200: raise RequestError(reply['result'].get('error','机器人拒绝请求'),reply['status'])
                return reply['result']
            data=json.dumps(body).encode() if body is not None else None
            req=urllib.request.Request(self.url+path,data=data,headers={'Content-Type':'application/json'})
            with urllib.request.urlopen(req,timeout=4) as response: return json.loads(response.read())
        except RequestError: raise
        except urllib.error.HTTPError as exc:
            raise RequestError(json.loads(exc.read()).get('error',str(exc)),exc.code) from exc
        except Exception as exc:
            self.connected=False
            self.last_error=f'{"蓝牙" if self.mode=="ble" else "Wi-Fi"}通信失败：{str(exc) or type(exc).__name__}'
            print(self.last_error,flush=True)
            raise RequestError(self.last_error,503) from exc
    def status(self):
        with self.lock:
            device={};error=self.last_error
            was_connected=self.connected
            if was_connected:
                try:
                    device=self.request('/api/status')
                    self.last_pose=dict(zip(CHANNELS,device['pose']))
                except RequestError as exc: error=str(exc)
                if not device and self.mode=='ble':
                    try:
                        self.ble.reconnect()
                        self.connected=True
                        device=self.request('/api/status')
                        self.last_pose=dict(zip(CHANNELS,device['pose']))
                        self.last_error=None
                        error=None
                        print('蓝牙已自动重连',flush=True)
                    except Exception as exc:
                        self.connected=False
                        error=f'蓝牙自动重连失败：{str(exc) or type(exc).__name__}'
            return dict(device,connected=self.connected,mode=self.mode,pose=self.last_pose,error=error,
                        port='Otto-0E70 · BLE' if self.mode=='ble' else self.url)
    def connect(self,mode):
        if mode not in ('ble','wifi'): raise RequestError('未知通信方式')
        with self.lock:
            if self.connected: self.disconnect()
            self.mode=mode
            try:
                if mode=='ble':self.ble.connect()
                for url in self.urls if mode=='wifi' else [self.url]:
                    self.url=url
                    try:info=self.request('/api/status')
                    except RequestError:
                        if mode=='wifi':continue
                        raise
                    if info.get('device_id','').replace(':','').lower()!=TARGET_ID:
                        if mode=='ble':self.ble.disconnect()
                        if mode=='wifi':continue
                        raise RequestError('目标机器人身份不匹配',409)
                    self.connected=True; self.last_error=None
                    return self.status()
                raise RequestError('没有找到身份匹配的 Otto Wi-Fi 设备',503)
            except RequestError: raise
            except Exception as exc: raise RequestError(str(exc) or type(exc).__name__,503) from exc
    def disconnect(self):
        with self.lock:
            try:
                if self.connected:self.request('/api/stop',{})
            finally:
                self.connected=False
                if self.mode=='ble':self.ble.disconnect()
            return self.status()
    def command(self,path,body):
        with self.lock:
            if not self.connected: raise RequestError('请先连接机器人',409)
            return self.request(path,body)
    def play_audio(self,filename,duration_ms=None):
        file=audio_file(filename)
        with wave.open(str(file),'rb') as wav:
            if (wav.getnchannels(),wav.getsampwidth(),wav.getframerate())!=(1,2,24000):
                raise RequestError('声音文件需要 24 kHz 单声道 16-bit WAV')
            pcm=wav.readframes(wav.getnframes())
            if duration_ms is not None:pcm=pcm[:min(len(pcm),int(duration_ms*48))]
        try:
            with urllib.request.urlopen(self.url+'/api/status',timeout=4) as response:
                status=json.load(response)
            if status.get('device_id','').replace(':','').lower()!=TARGET_ID:
                raise RequestError('Wi-Fi 地址不是这台 Otto 机器人',409)
            if not status.get('audio_available'):
                raise RequestError('机器人固件尚未提供扬声器播放，请先刷入音频固件',409)
            from array import array
            samples=array('h');samples.frombytes(pcm)
            for index,value in enumerate(samples):samples[index]=max(-32768,min(32767,value*2))
            pcm=samples.tobytes()
            address=urlparse(self.url)
            audio_url=address._replace(netloc=f'{address.hostname}:81').geturl()+'/api/audio/pcm'
            req=urllib.request.Request(audio_url,data=pcm,headers={'Content-Type':'application/octet-stream'})
            with urllib.request.urlopen(req,timeout=max(15,len(pcm)/48000+10)) as response:
                return json.load(response)
        except RequestError:raise
        except Exception as exc:raise RequestError('机器人 Wi-Fi 扬声器通信失败：'+str(exc),503) from exc

LINK=RobotLink()

class CompositionRunner:
    def __init__(self):
        self.lock=threading.RLock();self.cancel=threading.Event();self.players=[];self.robot_required=False;self.state={'running':False,'error':None,'compositionId':None,'source':None,'startedAt':None,'runCount':0}
    def start(self,identifier,source='button'):
        item=get_composition(identifier)
        if not item['clipCount']:raise RequestError('组合没有片段',409)
        with self.lock:
            if self.state['running']:raise RequestError('已有组合正在运行',409)
            self.robot_required=any(t['kind']!='music' and not t['muted'] and any(not c['muted'] for c in t['clips']) for t in item['tracks'])
            if self.robot_required and (not LINK.connected or LINK.mode!='wifi'):LINK.connect('wifi')
            if self.robot_required:
                status=LINK.status()
                if status.get('moving') or status.get('active') not in (None,'idle'):
                    raise RequestError('机器人正在执行动作，请稍后重试',409)
            self.cancel=threading.Event()
            self.players=[]
            self.state={'running':True,'error':None,'compositionId':identifier,'source':source,'startedAt':time.time(),'runCount':self.state['runCount']+1}
            threading.Thread(target=self._run,args=(item,self.cancel),daemon=True).start()
            return dict(self.state)
    def _run(self,item,cancel):
        # Group clips by startMs. Robot PCM must be fully uploaded before playback
        # starts; rebase the timeline clock to that instant so motions/music land
        # on the same beat as the speaker instead of racing ahead during upload.
        by_time={}
        for track in item['tracks']:
            if track.get('muted'): continue
            for clip in track['clips']:
                if clip.get('muted'): continue
                start_ms=int(clip['startMs'])
                by_time.setdefault(start_ms, []).append((track['kind'], clip))
                if track['kind']=='expression':
                    snap=clip.get('resourceSnapshot') or {}
                    dur=int(clip.get('durationMs') or snap.get('durationMs') or 0)
                    if dur>0:
                        by_time.setdefault(start_ms+dur, []).append(('expression_end', clip))
        other_order={'expression_end':-1,'expression':0,'motion':1,'music':2}
        start=time.monotonic()
        try:
            for at in sorted(by_time):
                if cancel.wait(max(0,start+at/1000-time.monotonic())):break
                group=by_time[at]
                audio_clips=[clip for kind,clip in group if kind=='audio']
                if audio_clips:
                    for clip in audio_clips:
                        if cancel.is_set():break
                        filename=clip['resourceSnapshot']['url'].rsplit('/',1)[-1]
                        LINK.play_audio(filename,clip['durationMs'])
                    # play_audio returns when the robot accepted PCM and began playing.
                    start=time.monotonic()-at/1000.0
                for kind,clip in sorted(((k,c) for k,c in group if k!='audio'), key=lambda item: other_order.get(item[0],9)):
                    if cancel.is_set():break
                    snap=clip['resourceSnapshot']
                    if kind=='motion':
                        LINK.command('/api/output',{'enabled':True})
                        LINK.command('/api/play',snap['program'])
                    elif kind=='expression':
                        loops=max(1,min(99,int(clip.get('loopCount') or snap.get('loopCount') or 1)))
                        LINK.command('/api/face',{'expression':clip['resourceId'],'loopCount':loops})
                    elif kind=='expression_end':
                        LINK.command('/api/face',{'expression':'smile_static','loopCount':1})
                    elif kind=='music':
                        filename=snap['url'].rsplit('/',1)[-1]
                        player=subprocess.Popen(['afplay','-t',str(clip['durationMs']/1000),str(audio_file(filename))],
                                                stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                        with self.lock:self.players.append(player)
            if not cancel.is_set():cancel.wait(max(0,start+item['durationMs']/1000-time.monotonic()))
        except Exception as exc:
            with self.lock:self.state['error']=str(exc)
        finally:
            with self.lock:
                for player in self.players:
                    if player.poll() is None:player.terminate()
                self.players=[]
            if self.robot_required and LINK.connected:
                try:LINK.command('/api/output',{'enabled':False})
                except RequestError:pass
            with self.lock:self.state['running']=False
    def _play_audio(self,filename,duration_ms):
        try:LINK.play_audio(filename,duration_ms)
        except Exception as exc:
            with self.lock:self.state['error']=str(exc)
    def stop(self):
        self.cancel.set()
        with self.lock:
            for player in self.players:
                if player.poll() is None:player.terminate()
            self.players=[]
        if self.robot_required and LINK.connected:LINK.command('/api/stop',{})
        if self.robot_required and LINK.connected:LINK.command('/api/output',{'enabled':False})
        with self.lock:self.state['running']=False
        return dict(self.state)
    def status(self):
        with self.lock:return dict(self.state)

RUNNER=CompositionRunner()
VOICE=VoiceListener(LINK,RUNNER,list_compositions,match_voice_trigger)
VIDEO=VideoInput(StudioMotion(LINK,RUNNER,get_composition))

class Handler(BaseHTTPRequestHandler):
    def reply(self,result,status=200):
        payload=json.dumps(result,ensure_ascii=False,allow_nan=False).encode()
        self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Content-Length',str(len(payload)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(payload)
    def body(self,max_size=MAX_BODY):
        try:
            size=int(self.headers.get('Content-Length','0'))
            if size<1 or (max_size is not None and size>max_size):raise ValueError()
            value=json.loads(self.rfile.read(size))
            if not isinstance(value,dict):raise ValueError()
            return value
        except (ValueError,UnicodeDecodeError):raise RequestError('请求需要 JSON 对象')
    def handle_request(self,method):
        port=self.server.server_port
        if self.headers.get('Host') not in (f'127.0.0.1:{port}',f'localhost:{port}'):raise RequestError('只接受本机地址',403)
        path=unquote(urlparse(self.path).path)
        if method=='GET':
            if path=='/api/status':return self.reply(LINK.status())
            if path=='/api/resources':return self.reply(resource_catalog())
            if path=='/api/compositions':return self.reply(list_compositions())
            if path=='/api/compositions/run':return self.reply(RUNNER.status())
            if path=='/api/voice':return self.reply(VOICE.status())
            if path.startswith('/api/compositions/'):
                return self.reply(get_composition(path.removeprefix('/api/compositions/')))
            if path.startswith('/api/audio/'):
                file=audio_file(path.removeprefix('/api/audio/'))
                self.send_response(200)
                self.send_header('Content-Type',mimetypes.guess_type(file.name)[0] or 'application/octet-stream')
                self.send_header('Content-Length',str(file.stat().st_size))
                self.end_headers()
                with file.open('rb') as source:shutil.copyfileobj(source,self.wfile)
                return
            if path=='/api/catalog':
                resources=resource_catalog()
                return self.reply(dict(actions=resources['actions'],expressions=resources['expressions']))
            file=(STATIC/('index.html' if path=='/' else path.lstrip('/'))).resolve()
            if not file.is_relative_to(STATIC) or not file.is_file():raise RequestError('路径不存在',404)
            payload=file.read_bytes();self.send_response(200)
            self.send_header('Content-Type',mimetypes.guess_type(str(file))[0] or 'application/octet-stream')
            self.send_header('Content-Length',str(len(payload)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(payload);return
        if self.headers.get('Origin') not in (None,'http://'+self.headers.get('Host','')):raise RequestError('只接受本机页面请求',403)
        if path=='/api/video/start':
            self.body()
            return self.reply(VIDEO.start())
        if path=='/api/video/stop':return self.reply(VIDEO.stop(self.body().get('token')))
        if path in ('/api/video/frame','/api/video/preview'):
            try:length=int(self.headers.get('Content-Length','0'))
            except ValueError:length=0
            if not 1<=length<=1500000:raise RequestError('视频帧大小无效')
            jpeg=self.rfile.read(length)
            if path=='/api/video/preview':return self.reply(VIDEO.preview(jpeg))
            return self.reply(VIDEO.frame(self.headers.get('X-Video-Token'),jpeg))
        if path=='/api/audio/upload':
            try:
                query=parse_qs(urlparse(self.path).query)
                length=int(self.headers.get('Content-Length','0'))
                if length<1:raise ValueError()
            except ValueError:raise RequestError('声音文件无效')
            return self.reply(save_audio(self.rfile,length,query.get('name',['audio'])[0],
                                         self.headers.get('Content-Type','').split(';')[0],
                                         query.get('id',[None])[0],query.get('label',[None])[0]),201)
        if path=='/api/audio/synthesize':
            body=self.body()
            return self.reply(synthesize_audio(body.get('text'),body.get('label'),body.get('id')),201)
        if path=='/api/audio/play':
            body=self.body()
            return self.reply(LINK.play_audio(body.get('filename','')))
        if path.startswith('/api/audio/'):
            identifier=path.removeprefix('/api/audio/')
            body=self.body()
            if body.get('action')=='rename':return self.reply(update_audio(identifier,body.get('label')))
            if body.get('action')=='delete':return self.reply(delete_audio(identifier))
            raise RequestError('声音操作无效')
        if path=='/api/compositions':return self.reply(save_composition(self.body(None)))
        if path.startswith('/api/compositions/') and path.endswith('/delete'):
            return self.reply(delete_composition(path.removeprefix('/api/compositions/').removesuffix('/delete')))
        if path=='/api/compositions/run':return self.reply(RUNNER.start(self.body().get('id','')))
        if path=='/api/compositions/stop':return self.reply(RUNNER.stop())
        if path=='/api/voice/chunk':
            try:length=int(self.headers.get('Content-Length','0'))
            except ValueError:length=0
            if length!=CHUNK_BYTES:raise RequestError('网页麦克风录音块长度不正确')
            try:return self.reply(VOICE.ingest(self.rfile.read(length)))
            except ValueError as exc:raise RequestError(str(exc)) from exc
        if path=='/api/voice':
            body=self.body();action=body.get('action')
            if action=='start':
                try:return self.reply(VOICE.start(body.get('source','browser')))
                except ValueError as exc:raise RequestError(str(exc)) from exc
            if action=='stop':return self.reply(VOICE.stop())
            raise RequestError('语音监听操作无效')
        body=self.body()
        if path=='/api/connect':return self.reply(LINK.connect(body.get('mode','ble')))
        if path=='/api/disconnect':return self.reply(LINK.disconnect())
        if path in ('/api/play','/api/validate','/api/behavior'):
            program,duration,size=validate_program(body)
            if path=='/api/play':return self.reply(LINK.command('/api/play',program))
            if path=='/api/behavior':
                DATA.mkdir(exist_ok=True);target=DATA/(program['name']+'.json');tmp=target.with_suffix('.tmp')
                tmp.write_text(json.dumps(program,ensure_ascii=False,indent=2));tmp.replace(target)
            return self.reply(dict(program=program,duration=duration,bytes=size))
        if path=='/api/servo':
            pose=validate_angles(body.get('pose'));duration=number(body.get('duration',300),1,2147483647,'duration',True)
            return self.reply(LINK.command(path,dict(pose=[pose[k] for k in CHANNELS],duration=duration)))
        if path=='/api/face':
            catalog=resource_catalog()['expressions']
            ids={e['id'] for e in catalog if e.get('onDevice', True)}
            if body.get('expression') not in ids:
                raise RequestError('未知或未烧录到机身的动画 ID')
            payload={'expression':body['expression']}
            if 'loopCount' in body:
                try: payload['loopCount']=max(1,min(99,int(body['loopCount'])))
                except (TypeError,ValueError): raise RequestError('loopCount 必须为 1–99 的整数')
            return self.reply(LINK.command(path,payload))
        if path=='/api/output':
            if not isinstance(body.get('enabled'),bool):raise RequestError('enabled 必须为布尔值')
            return self.reply(LINK.command(path,body))
        if path in ('/api/stop','/api/home'):return self.reply(LINK.command(path,{}))
        raise RequestError('路径不存在',404)
    def safe(self,method):
        try:self.handle_request(method)
        except RequestError as exc:self.reply(dict(error=str(exc)),exc.status)
        except StoreError as exc:self.reply(dict(error=str(exc)),exc.status)
        except (OSError,ValueError) as exc:self.reply(dict(error=str(exc)),503)
        except Exception as exc:
            print('[http] unhandled', type(exc).__name__, exc)
            try:self.reply(dict(error=str(exc) or type(exc).__name__),500)
            except Exception:pass
    def do_GET(self):self.safe('GET')
    def do_POST(self):self.safe('POST')
    def log_message(self,fmt,*args):
        if args and args[0] in ('GET /api/status HTTP/1.1','GET /api/voice HTTP/1.1',
                                 'GET /api/compositions/run HTTP/1.1'):return
        print('[http] '+fmt%args)

if __name__=='__main__':
    port=int(setting('OTTO_PORT',8765))
    print(f'Otto Studio · BLE / Wi-Fi · http://127.0.0.1:{port}')
    ThreadingHTTPServer(('127.0.0.1',port),Handler).serve_forever()
