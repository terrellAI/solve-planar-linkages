"""Independent functional checks for the added reference mechanisms."""
import json,unittest
from pathlib import Path
import numpy as np
from linkage import solve,verify
from run_model import animation_poses
ROOT=Path(__file__).resolve().parents[1]
NAMES=['hoeken','scott_russell_driven','klann']
class Expanded(unittest.TestCase):
 def load(self,name):return json.loads((ROOT/'references/examples'/f'{name}.json').read_text())
 def test_full_cycle(self):
  for name in NAMES:
   with self.subTest(name=name):
    m=self.load(name);r=verify(m,.1);self.assertTrue(r['passed'],r)
    _,a=animation_poses(m,300);self.assertTrue(a['passed'])
 def test_scott_russell_exact_line(self):
  m=self.load('scott_russell_driven')
  for deg in np.arange(0,360,.5):
   p=solve(m,float(deg));self.assertLess(abs(p['T'][0]),1e-9)
   np.testing.assert_allclose(p['S']+p['T'],2*p['M'],atol=1e-9)
 def test_klann_reference_pose(self):
  p=solve(self.load('klann'),0)
  for key,v in {'C':[74.1,75],'K':[23.2,86.6],'H':[86.6,150],'E':[0,0]}.items():
   np.testing.assert_allclose(p[key],v,atol=1e-8)
 def test_hoeken_is_approximate_not_exact(self):
  m=self.load('hoeken');pts=np.array([solve(m,float(d))['E'] for d in range(360)])
  self.assertGreater(np.linalg.svd(pts-pts.mean(0))[1][1],1.)
  segment=pts[90:271];self.assertLess(np.max(np.abs(segment[:,1]-segment[:,1].mean())),.25)
  self.assertAlmostEqual(np.ptp(segment[:,0]),160.,places=8)
if __name__=='__main__':unittest.main()
