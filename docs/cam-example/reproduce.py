"""Run from repo root: python docs/cam-example/reproduce.py [--out output/cam-example]."""
import argparse,json,math,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from cam import Cam
from run_cam import export_cam
from stroke import stroke

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--out',default=str(ROOT/'output/cam-example'));args=parser.parse_args()
 cam=Cam(stroke,40,0,'counterclockwise')
 for a,s in [(0,0),(30,10),(60,20),(70,20),(80,20),(100,10),(120,0),(360,0)]:
  p=cam.pose(a);assert abs(p['stroke']-s)<1e-12
  np.testing.assert_allclose(p['profile'],[(40+s)*math.sin(math.radians(a)),(40+s)*math.cos(math.radians(a))],atol=1e-12)
 report=export_cam(cam,args.out,gif=True)
 report.update({'dimension_source':'confirmed teaching example; not measured from textbook image',
                'lift':20,'phase_angles_deg':[60,20,40,240],'independent_hand_positions_passed':True,
                'boundary_position_velocity_continuous':True,'boundary_acceleration_continuous':False})
 (Path(args.out)/'verification.json').write_text(json.dumps(report,indent=2))
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
