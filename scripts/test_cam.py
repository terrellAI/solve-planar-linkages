import math, unittest
import numpy as np
from cam import Cam, verify_cam
from linkage import GeometryError

def stroke(a):
 if a<180:return 15*(1-math.cos(math.pi*a/180))
 if a<210:return 30.
 if a<300:return 15*(1+math.cos(math.pi*(a-210)/90))
 return 0.

class CamTests(unittest.TestCase):
 def test_hand_positions_and_direction(self):
  np.testing.assert_allclose(Cam(lambda a:0,40,-10).pose(90)['profile'],[-math.sqrt(1500),-10],atol=1e-12)
  np.testing.assert_allclose(Cam(lambda a:0,40,10,'counterclockwise').pose(90)['profile'],[math.sqrt(1500),-10],atol=1e-12)
 def test_centered_and_offset_both_directions(self):
  for e in [0,-10,10]:
   for direction in ['clockwise','counterclockwise']:
    cam=Cam(stroke,40,e,direction);report=verify_cam(cam)
    self.assertTrue(report['passed']);self.assertEqual(report['samples'],3601)
    for a in [0,45,180,240,300,360]:
     p=cam.pose(a);self.assertAlmostEqual(p['tip'][0],e)
     self.assertAlmostEqual(np.linalg.norm(p['profile']),math.hypot(e,math.sqrt(1600-e*e)+stroke(a)))
 def test_zero_stroke_base_circle(self):
  for e in [0,-10,10]:
   cam=Cam(lambda a:0,40,e)
   for a in range(361):self.assertAlmostEqual(np.linalg.norm(cam.pose(a)['profile']),40)
 def test_invalid_input_and_endpoint(self):
  for args in [(stroke,10,10),(stroke,-40,0),(stroke,40,float('nan')),(stroke,40,0,'bad')]:
   with self.assertRaises(ValueError):Cam(*args)
  for fn in [lambda a:float('nan'),lambda a:-1,lambda a:a/360,lambda a:1]:
   with self.assertRaises(GeometryError):verify_cam(Cam(fn,40))
  with self.assertRaises(ValueError):Cam(stroke,40).pose(361)
  with self.assertRaises(ValueError):verify_cam(Cam(stroke,40),step=0)
 def test_nonperiodic_endpoint_not_wrapped(self):
  from run_cam import render_cam
  import tempfile
  with tempfile.TemporaryDirectory() as folder:
   with self.assertRaises(GeometryError):render_cam(Cam(lambda a:a/360,40),folder)
 def test_sampled_discontinuity_is_not_continuous_proof(self):
  cam=Cam(lambda a:10 if 100<a<200 else 0,40)
  self.assertFalse(verify_cam(cam)['continuous_proven'])
 def test_interpolated_stroke(self):
  angles=np.linspace(0,360,721);values=[stroke(a) for a in angles]
  cam=Cam(lambda a:float(np.interp(a,angles,values)),40,-10)
  self.assertTrue(verify_cam(cam)['passed'])

if __name__=='__main__':unittest.main()
