"""Regression checks for continuous cyclic input animation."""
import copy,json,unittest
from pathlib import Path
import numpy as np
from run_model import animation_poses
from linkage import GeometryError
ROOT=Path(__file__).resolve().parents[1]

class Animation(unittest.TestCase):
 def model(self):
  return json.loads((ROOT/'references/examples/slider_0.json').read_text())
 def test_gif_export_keeps_timing_and_size_limit(self):
  import tempfile
  from PIL import Image,ImageDraw
  from run_model import save_gif_under_limit
  pictures=[]
  for i in range(12):
   im=Image.new('RGB',(80,60),'#101b2e');ImageDraw.Draw(im).rectangle((i*4,20,i*4+10,30),fill='white');pictures.append(im)
  with tempfile.TemporaryDirectory() as folder:
   target=Path(folder)/'animation.gif';report=save_gif_under_limit(pictures,target)
   self.assertLess(target.stat().st_size,5_000_000)
   self.assertEqual(report['frames'],12)
   with Image.open(target) as gif:
    self.assertEqual(gif.n_frames,12)
    for i in range(12):gif.seek(i);self.assertEqual(gif.info['duration'],20)
   target.unlink()
   with self.assertRaises(GeometryError):save_gif_under_limit(pictures,target,max_bytes=100)
   self.assertFalse(target.exists())
 def test_full_cycle_and_seam(self):
  poses,report=animation_poses(self.model(),300)
  self.assertEqual(len(poses),300)
  self.assertTrue(report['passed'])
  self.assertAlmostEqual(report['drives'][0]['expected_step_deg'],1.2)
  self.assertAlmostEqual(report['drives'][0]['loop_seam_step_deg'],1.2)
  self.assertLess(report['drives'][0]['maximum_step_error_deg'],1e-10)
  self.assertFalse(np.allclose(poses[-1]['B'],poses[0]['B']))
 def test_negative_and_double_rotation(self):
  for ratio in [-1,2]:
   m=self.model();m['plan'][0]['ratio']=ratio
   poses,report=animation_poses(m,60)
   self.assertTrue(report['passed'])
   self.assertAlmostEqual(report['drives'][0]['loop_seam_step_deg'],ratio*6)
 def test_nonperiodic_input_rejected(self):
  m=self.model();m['plan'][0]['ratio']=.5
  with self.assertRaises(GeometryError):animation_poses(m,60)
 def test_invalid_frame_count_rejected(self):
  with self.assertRaises(ValueError):animation_poses(self.model(),1)

if __name__=='__main__':unittest.main()
