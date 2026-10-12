import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import composer_store as store


class ComposerStoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        for attr, path in [('LIBRARY', root), ('COMPOSITIONS', root/'compositions'),
                           ('AUDIO', root/'audio'), ('BEHAVIORS', root/'behaviors')]:
            patcher = patch.object(store, attr, path)
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_create_rename_reopen_and_revision_conflict(self):
        clip = dict(id='c1', resourceId='walk_complete', startMs=500, durationMs=4900,
                    muted=False, resourceSnapshot={'label': '行走 [补全版]', 'program': {'segments': []}})
        draft = dict(name='第一版', tracks=[dict(id='motion', kind='motion', muted=False, clips=[clip])])
        first = store.save_composition(draft)
        self.assertEqual((first['revision'], first['clipCount'], first['durationMs']), (1, 1, 5400))
        self.assertEqual(store.list_compositions()[0]['name'], '第一版')
        self.assertEqual(store.get_composition(first['id'])['tracks'][0]['clips'][0]['resourceSnapshot'], clip['resourceSnapshot'])

        first['name'] = '重命名后'
        first['tracks'][0]['clips'][0]['muted'] = True
        first['tracks'][0]['muted'] = True
        second = store.save_composition(first)
        self.assertEqual(second['revision'], 2)
        self.assertEqual(store.get_composition(first['id'])['name'], '重命名后')
        self.assertTrue(store.get_composition(first['id'])['tracks'][0]['clips'][0]['muted'])
        with self.assertRaises(store.StoreError) as conflict:
            store.save_composition(first)
        self.assertEqual(conflict.exception.status, 409)

    def test_dynamic_catalog_override(self):
        root = Path(self.tmp.name)
        actions = root/'actions.json'
        expressions = root/'expressions.json'
        actions.write_text(json.dumps([{'id': 'new_action', 'label': '新动作',
                                        'program': {'segments': [{'type': 'hold', 'duration': 800}]}}]))
        expressions.write_text(json.dumps([{'id': 'new_face', 'label': '新表情', 'durationMs': 800}]))
        with patch.dict('os.environ', {'OTTO_ACTION_CATALOG': str(actions),
                                       'OTTO_EXPRESSION_CATALOG': str(expressions)}):
            catalog = store.resource_catalog()
        self.assertEqual([a['id'] for a in catalog['actions']], ['new_action'])
        self.assertEqual([e['id'] for e in catalog['expressions']], ['new_face'])

    def test_voice_trigger_matches_each_phrase_and_rejects_duplicate(self):
        draft=dict(name='跳舞',trigger='奥托跳舞，开始跳舞',tracks=[dict(id='motion',kind='motion',muted=False,clips=[])])
        saved=store.save_composition(draft)
        self.assertEqual(store.match_voice_trigger('奧托，跳舞！',store.list_compositions())['id'],saved['id'])
        self.assertEqual(store.match_voice_trigger('请开始跳舞',store.list_compositions())['id'],saved['id'])
        self.assertIsNone(store.match_voice_trigger('今天天气很好',store.list_compositions()))
        with self.assertRaises(store.StoreError):
            store.save_composition(dict(draft,name='重复',trigger='先拍手，开始跳舞'))
        with self.assertRaises(store.StoreError):
            store.save_composition(dict(draft,name='自身重复',trigger='奥托跳舞，奥托跳舞'))

    def test_music_track_delete_composition_and_reject_overlap(self):
        clip=lambda cid,start:dict(id=cid,resourceId='song',startMs=start,durationMs=1000,
                                   muted=False,resourceSnapshot={'url':'/api/audio/song.wav'})
        draft=dict(name='音乐测试',tracks=[dict(id='music',kind='music',muted=False,
                                               clips=[clip('first',0),clip('second',1000)])])
        saved=store.save_composition(draft)
        self.assertEqual(saved['durationMs'],2000)
        draft['tracks'][0]['clips'][1]['startMs']=999
        with self.assertRaisesRegex(store.StoreError,'不能重叠'):
            store.save_composition(draft)
        self.assertTrue(store.delete_composition(saved['id'])['deleted'])
        self.assertEqual(store.list_compositions(),[])

    def test_mp4_upload_converts_to_wav_and_delete_preserves_saved_file(self):
        source=Path(self.tmp.name)/'test.mp4'
        subprocess.run([store.ffmpeg(),'-v','error','-f','lavfi','-i','sine=frequency=440:duration=1',
                        '-c:a','aac','-y',str(source)],check=True)
        data=source.read_bytes()
        item=store.save_audio(io.BytesIO(data),len(data),'test.mp4','video/mp4')
        self.assertEqual(item['mime'],'audio/wav')
        self.assertAlmostEqual(item['durationMs'],1000,delta=30)
        file=store.audio_file(item['url'].rsplit('/',1)[1])
        self.assertEqual(file.read_bytes()[:4],b'RIFF')
        renamed=store.update_audio(item['id'],'提示音')
        self.assertEqual((renamed['label'],renamed['revision']),('提示音',2))
        self.assertEqual(store.resource_catalog()['audio'][0]['label'],'提示音')
        store.delete_audio(item['id'])
        self.assertEqual(store.resource_catalog()['audio'],[])
        self.assertTrue(file.is_file())

    def test_tts_generates_playable_wav(self):
        item=store.synthesize_audio('你好，奥托机器人。','问候')
        self.assertEqual(item['origin'],'tts')
        self.assertEqual(item['text'],'你好，奥托机器人。')
        self.assertGreater(item['durationMs'],300)
        self.assertEqual(store.audio_file(item['url'].rsplit('/',1)[1]).read_bytes()[:4],b'RIFF')


    def test_expression_loop_count_extends_and_validates(self):
        exprs = store.resource_catalog()["expressions"]
        sample = next(e for e in exprs if e.get("hasLoopRange"))
        intro, loop, outro = sample["introMs"], sample["loopMs"], sample["outroMs"]
        snap = {
            "label": sample["label"], "revision": 1, "kind": "expression",
            "durationMs": intro + loop * 2 + outro, "preview": sample.get("preview"),
            "introMs": intro, "loopMs": loop, "outroMs": outro, "loopCount": 2,
        }
        item = store.save_composition({
            "name": "循环表情测试",
            "trigger": "循环表情测试词",
            "tracks": [
                {"id": "motion", "kind": "motion", "muted": False, "clips": []},
                {"id": "expression", "kind": "expression", "muted": False, "clips": [
                    {"id": "c1", "resourceId": sample["id"], "startMs": 0,
                     "durationMs": intro + loop * 2 + outro, "muted": False,
                     "loopCount": 2, "resourceSnapshot": snap},
                ]},
                {"id": "audio", "kind": "audio", "muted": False, "clips": []},
                {"id": "music", "kind": "music", "muted": True, "clips": []},
            ],
        })
        clip = item["tracks"][1]["clips"][0]
        self.assertEqual(clip["loopCount"], 2)
        self.assertEqual(clip["durationMs"], intro + loop * 2 + outro)
        with self.assertRaises(store.StoreError):
            store.save_composition({
                "name": "坏循环", "trigger": "坏循环词",
                "tracks": [
                    {"id": "motion", "kind": "motion", "muted": False, "clips": [
                        {"id": "m1", "resourceId": "home", "startMs": 0, "durationMs": 100, "muted": False,
                         "loopCount": 2, "resourceSnapshot": {"label": "x", "kind": "motion", "durationMs": 100}},
                    ]},
                    {"id": "expression", "kind": "expression", "muted": False, "clips": []},
                    {"id": "audio", "kind": "audio", "muted": False, "clips": []},
                    {"id": "music", "kind": "music", "muted": True, "clips": []},
                ],
            })


if __name__ == '__main__':
    unittest.main()
