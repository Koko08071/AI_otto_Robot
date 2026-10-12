import queue
import sys
import threading
import time
import types
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy
import opencc

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from voice_trigger import CHUNK_BYTES, WAKE_ALIASES, VoiceListener

class Runner:
    def __init__(self):self.runs=[]
    def status(self):return {'running':False}
    def start(self,identifier,source):self.runs.append((identifier,source))

class Link:
    connected=True
    mode='wifi'
    def __init__(self):self.faces=[];self.connected=True;self.mode='wifi'
    def connect(self,mode):self.connected=True;self.mode=mode;return {}
    def request(self,path,body=None):
        if path=='/api/status':return {'mic_available':True}
        self.faces.append(body['expression']);return {}

class VoiceTriggerTests(unittest.TestCase):
    def test_default_source_is_browser(self):
        listener=VoiceListener(Link(),Runner(),lambda:[],lambda *_:None)
        self.assertEqual(listener.status()['source'],'browser')

    def test_ingest_requires_browser_listening(self):
        listener=VoiceListener(Link(),Runner(),lambda:[{'id':'dance','name':'跳舞','trigger':'跳舞'}],lambda *_:None)
        with self.assertRaises(ValueError):
            listener.ingest(b'\x00'*CHUNK_BYTES)

    def test_ingest_accepts_pcm_while_browser_listening(self):
        listener=VoiceListener(Link(),Runner(),lambda:[{'id':'dance','name':'跳舞','trigger':'跳舞'}],lambda *_:None)
        with self.lock_free_start(listener):
            status=listener.ingest(b'\x20\x03'* (CHUNK_BYTES//2))
            self.assertTrue(status['listening'])
            self.assertEqual(listener.chunks.qsize(),1)

    def lock_free_start(self,listener):
        class Ctx:
            def __enter__(ctx):
                listener.state.update(listening=True,source='browser',phase='wake',error=None)
                listener.chunks=queue.Queue(maxsize=5)
                return listener
            def __exit__(ctx,*_):
                listener.stop()
        return Ctx()

    def test_wake_aliases_include_common_mishears(self):
        self.assertIn('小黄小黄',WAKE_ALIASES)
        self.assertIn('小巴',WAKE_ALIASES)
        self.assertIn('小黄黄',WAKE_ALIASES)

    def test_wake_word_required_before_command(self):
        for wake in ['小黄小黄','小黄','小巴小巴','小黄黄']:
            with self.subTest(wake=wake):
                words=queue.Queue()
                for phrase in ['跳舞',wake,'跳舞']:words.put(phrase)
                class Model:
                    def __init__(self,*args,**kwargs):pass
                    def transcribe(self,*args,**kwargs):return [types.SimpleNamespace(text=words.get_nowait())],None
                runner=Runner()
                link=Link()
                listener=VoiceListener(link,runner,lambda:[{'id':'dance','name':'跳舞','trigger':'跳舞'}],
                                       lambda text,items:items[0] if '跳舞' in text else None)
                with patch.dict(sys.modules,{'faster_whisper':types.SimpleNamespace(WhisperModel=Model)}):
                    listener.state['listening']=True
                    worker=threading.Thread(target=listener._listen,args=(listener.cancel,listener.chunks))
                    worker.start()
                    for count in range(1,4):
                        listener.chunks.put(b'\x20\x03'*32768)
                        end=time.monotonic()+3
                        while listener.status()['capturedChunks']<count and time.monotonic()<end:time.sleep(.01)
                        if count<3:self.assertEqual(runner.runs,[])
                    end=time.monotonic()+3
                    while not runner.runs and time.monotonic()<end:time.sleep(.01)
                    self.assertEqual(runner.runs,[('dance','voice')],listener.status())
                    self.assertEqual(listener.status()['triggerCount'],1)
                    self.assertEqual(link.faces,['question_05s'])
                    listener.stop()
                    worker.join(timeout=2)

if __name__=='__main__':unittest.main()
