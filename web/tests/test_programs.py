import copy,io,json,sys,tempfile,unittest,wave
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import server

TEMPO_SUFFIXES=('p250','p500','p750','p1000')
TEMPO_BY_SUFFIX={'p250':('快',250),'p500':('中',500),'p750':('慢',750),'p1000':('原',1000)}
VARIANT_LABELS={'p250':('快速','快速补全'),'p500':('中速','中速补全'),'p750':('慢速','慢速补全'),'p1000':('原速','原速补全')}

class ProgramTests(unittest.TestCase):
    def setUp(self):
        self.catalog=json.loads((server.STATIC/'actions.json').read_text(encoding='utf-8'))
        # Custom choreography programs (e.g. grok long stomp) are not Otto tempo-library entries.
        self.custom=[a for a in self.catalog if a.get('source')!='OttoDIY/OttoDIYLib']
        self.legacy=[a for a in self.catalog if 'tempoPeriodMs' not in a and a.get('source')=='OttoDIY/OttoDIYLib']
        self.variants=[a for a in self.catalog if 'tempoPeriodMs' in a]
        self.by_id={a['id']:a for a in self.catalog}

    def test_every_upstream_action_validates(self):
        self.assertEqual(len(self.legacy),68)
        self.assertEqual(len(self.variants),68*4)
        self.assertEqual(len(self.catalog),68+68*4+len(self.custom))
        for a in self.catalog:
            with self.subTest(action=a['id']):
                value,duration,size=server.validate_program(a['program'])
                self.assertEqual(value,a['program']);self.assertGreater(duration,0);self.assertLessEqual(size,65536)

    def test_original_walk_parameters(self):
        s=next(a for a in self.legacy if a['id']=='walk')['program']['segments'][0]
        self.assertEqual(s,dict(type='oscillate',duration=1750,period=438,amplitude=[30,30,20,20],offset=[0,0,4,-4],phase=[0,0,90,90]))

    def test_walk_turn_slower_midpoint_tempo(self):
        by_id={a['id']:a for a in self.legacy}
        for aid in ['walk','walk_complete']:
            periods=[s['period'] for s in by_id[aid]['program']['segments'] if s.get('type')=='oscillate']
            self.assertEqual(periods,[438],aid)
        for aid in ['walk_reverse','walk_reverse_complete']:
            periods=[s['period'] for s in by_id[aid]['program']['segments'] if s.get('type')=='oscillate']
            self.assertEqual(periods,[750],aid)
        for aid in ['turn','turn_reverse','turn_complete','turn_reverse_complete']:
            periods=[s['period'] for s in by_id[aid]['program']['segments'] if s.get('type')=='oscillate']
            self.assertEqual(periods,[512],aid)
        ref=by_id['gesture_superhappy']
        self.assertEqual([s['period'] for s in ref['program']['segments'] if s.get('type')=='oscillate'],[250,250])

    def test_motion_speedup_keeps_original_backup(self):
        if not (server.ROOT/'library/_backups/motions-before-2x-20261010/actions.json').exists():
            self.skipTest('Historical pre-speedup catalog not included in public repository')
        backup=json.loads((server.ROOT/'library/_backups/motions-before-2x-20261010/actions.json').read_text())
        self.assertEqual(len(backup),len(self.legacy))
        reverse={'walk_reverse','walk_reverse_complete'}
        for before,after in zip(backup,self.legacy):
            with self.subTest(action=after['id']):
                self.assertEqual(before['id'],after['id'])
                self.assertEqual(len(before['program']['segments']),len(after['program']['segments']))
                for old,new in zip(before['program']['segments'],after['program']['segments']):
                    if after['id'] in reverse:
                        self.assertLessEqual(new['duration'],old['duration'])
                        if 'period' in old:self.assertLessEqual(new['period'],old['period'])
                    else:
                        self.assertLessEqual(new['duration'],max(1,round(old['duration']/2)))
                        if 'period' in old:self.assertLessEqual(new['period'],max(1,round(old['period']/2)))

    def test_motions_aligned_to_superhappy_tempo(self):
        walk_turn={'walk','walk_reverse','turn','turn_reverse','walk_complete','walk_reverse_complete','turn_complete','turn_reverse_complete'}
        ref=next(a for a in self.legacy if a['id']=='gesture_superhappy')
        ref_periods=[s['period'] for s in ref['program']['segments'] if s.get('type')=='oscillate']
        self.assertEqual(ref_periods,[250,250])
        happy=next(a for a in self.legacy if a['id']=='gesture_happy')
        happy_periods=[s['period'] for s in happy['program']['segments'] if s.get('type')=='oscillate']
        self.assertEqual(happy_periods,[250])
        oscillating=0
        non_oscillating=0
        markers_1ms=0
        for a in self.legacy:
            with self.subTest(action=a['id']):
                has_osc=False
                for s in a['program']['segments']:
                    if s.get('duration')==1 and s.get('type')=='output':
                        markers_1ms+=1
                        continue
                    if s.get('type')=='oscillate' and 'period' in s:
                        has_osc=True
                        if a['id'] in walk_turn:
                            if a['id'] in ('walk','walk_complete'):
                                expected=438
                            elif a['id'] in ('walk_reverse','walk_reverse_complete'):
                                expected=750
                            else:
                                expected=512
                            self.assertEqual(s['period'],expected,a['id'])
                        else:
                            self.assertLessEqual(s['period'],250)
                            self.assertEqual(s['period'],250,a['id'])
                    if s.get('type')=='move':
                        if a['id'] in ('walk_reverse','walk_reverse_complete'):
                            self.assertLessEqual(s['duration'],400,a['id'])
                        elif a['id'] in walk_turn:
                            self.assertLessEqual(s['duration'],250,a['id'])
                        else:
                            self.assertLessEqual(s['duration'],250,a['id'])
                if has_osc:oscillating+=1
                else:non_oscillating+=1
        self.assertEqual(oscillating+non_oscillating,68)
        self.assertEqual(oscillating,38)
        self.assertEqual(non_oscillating,30)
        self.assertEqual(markers_1ms,30)

    def test_tempo_variants_cover_all_motions(self):
        if not (server.ROOT/'library/_backups/motions-before-2x-20261010/actions.json').exists():
            self.skipTest('Historical pre-speedup catalog not included in public repository')
        backup=json.loads((server.ROOT/'library/_backups/motions-before-2x-20261010/actions.json').read_text())
        self.assertEqual(len(backup),68)
        defaults=[a for a in self.variants if a.get('isDefaultCatalog')]
        self.assertEqual(len(defaults),34)
        for item in defaults:
            self.assertTrue(item['isComplete'])
            self.assertEqual(item['variantLabel'],'中速补全')
            self.assertEqual(item['tempoPeriodMs'],500)
        for base in backup:
            is_complete='original_id' in base
            for suffix,(label,period) in TEMPO_BY_SUFFIX.items():
                aid=f"{base['id']}_{suffix}"
                with self.subTest(action=aid):
                    self.assertIn(aid,self.by_id)
                    item=self.by_id[aid]
                    self.assertEqual(item['tempo'],label)
                    self.assertEqual(item['tempoPeriodMs'],period)
                    self.assertEqual(item['baseId'],base['id'])
                    stem_plain,stem_complete=VARIANT_LABELS[suffix]
                    expect_variant=stem_complete if is_complete else stem_plain
                    self.assertEqual(item['variantLabel'],expect_variant)
                    self.assertEqual(item['isComplete'],is_complete)
                    self.assertTrue(item['label'].endswith('· '+expect_variant) or item['label'].endswith('·'+expect_variant) or (' · '+expect_variant) in item['label'])
                    self.assertEqual(item['program']['name'],aid)
                    periods=[s['period'] for s in item['program']['segments'] if s.get('type')=='oscillate' and 'period' in s]
                    for p in periods:
                        self.assertEqual(p,period,aid)
                    for s in item['program']['segments']:
                        if s.get('type')=='output' and s.get('duration')==1:
                            self.assertEqual(s['duration'],1)
                    if is_complete:
                        self.assertEqual(item.get('original_id'),f"{base['original_id']}_{suffix}")
                        self.assertIn(item['original_id'],self.by_id)
                        self.assertEqual(self.by_id[item['original_id']]['tempoPeriodMs'],period)
                    else:
                        self.assertNotIn('original_id',item)

    def test_tempo_variant_scaling_from_backup(self):
        if not (server.ROOT/'library/_backups/motions-before-2x-20261010/actions.json').exists():
            self.skipTest('Historical pre-speedup catalog not included in public repository')
        backup={a['id']:a for a in json.loads((server.ROOT/'library/_backups/motions-before-2x-20261010/actions.json').read_text())}
        # walk original period 1000 -> 慢 750 scales duration 4000->3000
        walk_slow=self.by_id['walk_p750']
        self.assertEqual(walk_slow['program']['segments'][0]['period'],750)
        self.assertEqual(walk_slow['program']['segments'][0]['duration'],3000)
        # reverse 慢 matches user-preferred 750
        rev=self.by_id['walk_reverse_p750']
        self.assertEqual(rev['program']['segments'][0]['period'],750)
        self.assertEqual(rev['label'],'行走（后退） · 慢速')
        # non-oscillating home uses 1000ms reference: 中 => ×0.5
        home_mid=self.by_id['home_p500']
        home_bak=backup['home']
        for old,new in zip(home_bak['program']['segments'],home_mid['program']['segments']):
            if old.get('type')=='output' and old.get('duration')==1:
                self.assertEqual(new['duration'],1)
            else:
                self.assertEqual(new['duration'],max(1,round(old['duration']*0.5)))
        # complete 快 links to base 快
        self.assertEqual(self.by_id['walk_complete_p250']['original_id'],'walk_p250')
        self.assertEqual(self.by_id['walk_complete_p250']['variantLabel'],'快速补全')
        self.assertIn('快速补全',self.by_id['walk_complete_p250']['label'])
        # 原速 from backup period 1000
        walk_orig=self.by_id['walk_p1000']
        self.assertEqual(walk_orig['tempoPeriodMs'],1000)
        self.assertEqual(walk_orig['program']['segments'][0]['period'],1000)
        self.assertEqual(walk_orig['program']['segments'][0]['duration'],4000)
        self.assertEqual(self.by_id['walk_complete_p1000']['variantLabel'],'原速补全')

    def test_reverse_uses_same_duration_and_period(self):
        by_id={a['id']:a for a in self.legacy}
        for name in ['turn','bend','shakeleg','moonwalker','crusaito','flapping']:
            a,b=[by_id[k]['program']['segments'] for k in [name,name+'_reverse']]
            self.assertEqual(sum(x['duration'] for x in a),sum(x['duration'] for x in b),name)
            self.assertEqual([x.get('period') for x in a],[x.get('period') for x in b],name)
        self.assertEqual(by_id['walk']['program']['segments'][0]['period'],438)
        self.assertEqual(by_id['walk_reverse']['program']['segments'][0]['period'],750)
        self.assertEqual(by_id['walk_reverse']['program']['segments'][0]['phase'],[0,0,-90,-90])
        self.assertNotEqual(by_id['shakeleg']['program'],by_id['shakeleg_reverse']['program'])

    def test_repeat_roundtrip_and_type(self):
        p=copy.deepcopy(self.by_id['walk']['program']);p['repeat']=True
        self.assertTrue(server.validate_program(p)[0]['repeat'])
        p['repeat']=False;self.assertFalse(server.validate_program(p)[0]['repeat'])
        for invalid in [1,'true',None]:
            p['repeat']=invalid
            with self.assertRaises(server.RequestError):server.validate_program(p)

    def test_completed_versions_close_pose(self):
        originals={a['id']:a for a in self.legacy if 'original_id' not in a}
        variants=[a for a in self.legacy if 'original_id' in a]
        self.assertEqual(len(originals),34);self.assertEqual(len(variants),34)
        for a in variants:
            self.assertIn(a['original_id'],originals)
            s=a['program']['segments']
            self.assertEqual(s[0]['pose'],[90,90,100,90]);self.assertEqual(s[-1]['pose'],s[0]['pose'])
            self.assertTrue(a['program']['reset_phase_on_repeat'])
            self.assertIn('[补全版]',a['label'])
        # tempo complete variants also close pose
        tempo_complete=[a for a in self.variants if 'original_id' in a]
        self.assertEqual(len(tempo_complete),34*4)
        for a in tempo_complete:
            s=a['program']['segments']
            self.assertEqual(s[0]['pose'],[90,90,100,90]);self.assertEqual(s[-1]['pose'],s[0]['pose'])
            self.assertTrue(a['program']['reset_phase_on_repeat'])
            self.assertTrue(a['isComplete'])
            self.assertTrue(a['variantLabel'].endswith('补全'))

    def test_removed_old_limits(self):
        p=dict(name='long_program',segments=[dict(type='move',duration=120000,pose=[0,180,30,150])]*100)
        _,duration,size=server.validate_program(p)
        self.assertGreater(duration,10000);self.assertGreater(size,512)

    def test_invalid_values(self):
        for bad in [True,float('nan'),float('inf'),-1,181,None]:
            with self.subTest(value=bad),self.assertRaises(server.RequestError):
                server.validate_angles(dict(ll=bad,rl=90,lf=90,rf=90))

    def test_oscillator_must_stay_in_physical_angle_domain(self):
        p=copy.deepcopy(self.by_id['walk']['program']);p['segments'][0]['amplitude']=[91,0,0,0]
        with self.assertRaises(server.RequestError):server.validate_program(p)

    def test_duration_uint32_overflow(self):
        with self.assertRaises(server.RequestError):server.validate_program(dict(name='overflow',segments=[dict(type='hold',duration=4294967295),dict(type='hold',duration=1)]))

    def test_protocol_capacity(self):
        with self.assertRaises(server.RequestError):server.validate_program(dict(name='oversize',segments=[dict(type='hold',duration=1)]*3000))

    def test_unknown_and_missing_fields(self):
        for segment in [dict(type='script',duration=1),dict(type='output',duration=1,enabled='yes'),dict(type='move',duration=1,pose=[90]*3),dict(type='hold',duration=.5)]:
            with self.subTest(segment=segment),self.assertRaises(server.RequestError):server.validate_program(dict(name='invalid',segments=[segment]))

    def test_screens_have_unique_ids_and_available_previews(self):
        expressions=server.resource_catalog()['expressions']
        self.assertEqual(len(expressions),len({e['id'] for e in expressions}))
        self.assertGreaterEqual(len(expressions),34)
        self.assertNotIn('happy_star',{e['id'] for e in expressions})
        for e in expressions:
            self.assertGreater(e['durationMs'],0)
            if e['preview']:
                self.assertTrue((server.STATIC/e['preview'].lstrip('/')).exists())
                if e.get('thumbnailVideo'):
                    self.assertTrue((server.STATIC/e['thumbnailVideo'].lstrip('/')).exists())
            else:self.assertTrue(e['durationEstimated'])

    def test_disconnected_status_does_not_reconnect(self):
        link=server.RobotLink()
        with patch.object(link,'request') as request:
            self.assertFalse(link.status()['connected']);request.assert_not_called()

    def test_commands_require_connection(self):
        with self.assertRaises(server.RequestError):server.RobotLink().command('/api/stop',{})

    def test_reject_wrong_device(self):
        link=server.RobotLink()
        with patch.object(link,'request',return_value={'device_id':'other'}),self.assertRaises(server.RequestError):link.connect('wifi')
        self.assertFalse(link.connected)

    def test_speaker_sends_pcm_only_to_verified_otto(self):
        with tempfile.TemporaryDirectory() as directory:
            file=Path(directory)/'sample.wav'
            with wave.open(str(file),'wb') as wav:
                wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(24000)
                wav.writeframes(b'\x01\x00\xfe\xff\x20\x4e\xe0\xb1')
            calls=[]
            def open_url(request,timeout):
                calls.append(request)
                if len(calls)==1:return io.BytesIO(b'{"device_id":"14:c1:9f:30:0e:70","audio_available":true}')
                return io.BytesIO(b'{"accepted":true}')
            with patch.object(server,'audio_file',return_value=file),patch.object(server.urllib.request,'urlopen',side_effect=open_url):
                self.assertTrue(server.RobotLink().play_audio(file.name)['accepted'])
            self.assertTrue(calls[1].full_url.endswith(':81/api/audio/pcm'))
            self.assertEqual(calls[1].data,b'\x02\x00\xfc\xff\xff\x7f\x00\x80')

if __name__=='__main__':unittest.main()
