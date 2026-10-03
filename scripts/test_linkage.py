import copy,json,unittest
from pathlib import Path
import numpy as np
from linkage import solve,verify,rotation,circles,circle_line,GeometryError
ROOT=Path(__file__).resolve().parents[1]

class Validation(unittest.TestCase):
 def test_examples(self):
  for file in (ROOT/'references/examples').glob('*.json'):
   with self.subTest(file=file.name):
    result=verify(json.loads(file.read_text()));self.assertTrue(result['passed'],result)
 def test_rotation_translation_and_shuffled_plan(self):
  q=rotation(.73);t=np.array([51.,-29.])
  for file in (ROOT/'references/examples').glob('*.json'):
   original=json.loads(file.read_text());m=copy.deepcopy(original)
   m['fixed']={k:(q@np.array(v)+t).tolist() for k,v in m['fixed'].items()}
   for s in m['plan']:
    if s['op']=='rotate':s['local']=(q@s['local']).tolist()
    if s['op'] in ['circle_line','project']:s['q']=(q@s['q']+t).tolist();s['v']=(q@s['v']).tolist()
   for g in m.get('guides',[]):
    if 'origin_point' not in g:g['origin']=(q@g['origin']+t).tolist();g['axis']=(q@g['axis']).tolist()
   m['plan'].reverse()
   for angle in [0,53,127,263,360]:
    a=solve(original,angle);b=solve(m,angle)
    for k in a:np.testing.assert_allclose(b[k],q@a[k]+t,atol=1e-10)
   self.assertTrue(verify(m,2)['passed'])
 def test_reflection(self):
  q=np.diag([1.,-1.]);m=json.loads((ROOT/'references/examples/case_6216.json').read_text());n=copy.deepcopy(m)
  n['fixed']={k:(q@v).tolist() for k,v in n['fixed'].items()}
  for s in n['plan']:
   if s['op']=='rotate':s['local']=(q@s['local']).tolist();s['ratio']=-1
   elif s['op']=='circles':s['branch']*=-1
   elif s['op']=='rigid':s['known_local']=(q@s['known_local']).tolist();s['target_local']=(q@s['target_local']).tolist()
  for angle in [0,51,199]:
   a=solve(m,angle);b=solve(n,angle)
   for k in a:np.testing.assert_allclose(b[k],q@a[k],atol=1e-10)
 def test_independent_hand_cases(self):
  np.testing.assert_allclose(circles([0,0],[6,0],5,5,1),[3,4])
  np.testing.assert_allclose(circle_line([2,3],5,[0,0],[7,0],1),[6,0])
 def test_failures(self):
  for fn,code in [(lambda:circles([0,0],[20,0],2,3,1),'unreachable'),(lambda:circles([0,0],[10,0],5,5,1),'singular'),(lambda:circle_line([0,9],2,[0,0],[1,0],1),'unreachable'),(lambda:circles([0,0],[6,0],5,5,None),'branch_required')]:
   with self.assertRaises(GeometryError) as e:fn()
   self.assertEqual(e.exception.code,code)
  m=json.loads((ROOT/'references/examples/slider_0.json').read_text());m['guides'][0]['hi']=100
  self.assertEqual(verify(m)['code'],'disengaged')
  self.assertEqual(verify({'fixed':{},'plan':[{'op':'rotate','out':'B','origin':'A','local':[2,0]}]})['code'],'unresolved_dependencies')
if __name__=='__main__':unittest.main()
