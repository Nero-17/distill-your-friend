"""Structural fixtures only: no conversation, training corpus or evaluation dataset."""
import importlib.util,json,tempfile,unittest
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
def module(name):
    spec=importlib.util.spec_from_file_location(name,BASE/'scripts'/(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

class Tools(unittest.TestCase):
    def test_split_and_training_memory(self):
        p=module('prepare')
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);source=root/'input.json'
            rows=[dict(id=str(i),speaker='actor',timestamp=1700000000+i*86400,text='fixture') for i in range(20)]
            source.write_text(json.dumps({'messages':rows}),encoding='utf-8')
            p.prepare(source,root/'out')
            sets=[{x['id'] for x in json.loads((root/'out'/(n+'.json')).read_text())['messages']} for n in ['train','dev','test']]
            self.assertFalse(sets[0]&sets[1] or sets[0]&sets[2] or sets[1]&sets[2])
            bank=json.loads((root/'out/memory/episodes.json').read_text())
            self.assertEqual({x['id'] for e in bank for x in e['messages']},sets[0])
            with self.assertRaises(ValueError):p.prepare(source,root/'out')
        with self.assertRaises(ValueError):p.external(BASE/'private')

    def test_memory_temporal_correction_and_source(self):
        m=module('memory')
        with tempfile.TemporaryDirectory() as td:
            m.ROOT=Path(td)
            def entry(ident,t,source='real_training',**extra):return dict(id=ident,date='2000-01-01',end_time=t,source=source,messages=[dict(speaker='actor',text='alpha beta',timestamp=t)],**extra)
            (m.ROOT/'episodes.json').write_text(json.dumps([entry('a',10),entry('future',100)]))
            self.assertEqual([x['id'] for x in m.retrieve('alpha beta',20)],['a'])
            m.remember(entry('b',30,'user_correction',supersedes='a'))
            self.assertEqual([x['id'] for x in m.retrieve('alpha beta',20)],['a'])
            self.assertEqual([x['id'] for x in m.retrieve('alpha beta',40)],['b'])
            with self.assertRaises(ValueError):m.remember(entry('fake',40,'synthetic_session'))
            with self.assertRaises(ValueError):m.remember(entry('b',40,'user_message'))

    def test_score_and_control_exclusion(self):
        m=module('score')
        keys=[dict(id='a',label='real'),dict(id='b',label='synthetic'),dict(id='c',label='synthetic',control=True)]
        preds=[dict(id='a',label='synthetic',p_synthetic=.8),dict(id='b',label='synthetic',p_synthetic=.7),dict(id='c',label='synthetic',p_synthetic=.9)]
        result=m.score(keys,preds)
        self.assertEqual(result['accuracy'],.5);self.assertEqual(result['n'],2);self.assertEqual(result['controls_correct'],1)
        with self.assertRaises(ValueError):m.score(keys,preds[:-1])

if __name__=='__main__':unittest.main()
