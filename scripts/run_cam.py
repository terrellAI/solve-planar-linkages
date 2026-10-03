"""Trusted Python stroke module -> cam geometry, tables and synchronized GIF.
python run_cam.py stroke.py --radius 40 --offset -10 --out result --gif
"""
import argparse,csv,importlib.util,json,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from cam import Cam,verify_cam
from linkage import rotation,GeometryError
from run_model import save_gif_under_limit

def render_cam(cam,out,frames=300):
 if not isinstance(frames,int) or frames<3:raise ValueError('frames >= 3 required')
 report=verify_cam(cam)
 angles=np.linspace(0,360,3601)
 samples=[cam.pose(a) for a in angles];profile=np.array([p['profile'] for p in samples])
 maximum=max(p['stroke'] for p in samples);length=max(cam.r0,cam.l0+maximum,abs(cam.e),1.)
 scale=155/(length*1.6);extension=max(length*.7,2*maximum)
 centers=[np.array([240.,300.]),np.array([720.,300.])]
 try:font=ImageFont.truetype('DejaVuSans.ttf',16);title=ImageFont.truetype('DejaVuSans.ttf',22)
 except OSError:font=title=ImageFont.load_default()
 poses=[cam.pose(360*i/frames) for i in range(frames)];pictures=[]
 def xy(v,k):return tuple(centers[k]+scale*np.array([v[0],-v[1]]))
 for i,p in enumerate(poses):
  a=p['theta_deg'];im=Image.new('RGB',(960,720),'#f6f8fc');d=ImageDraw.Draw(im)
  def text(at,s,color='#26364a',f=font):d.text(at,s,font=f,fill=color)
  def line(points,k,color,width=2):d.line([xy(v,k) for v in points],fill=color,width=width)
  def dot(v,k,color,r=4):
   x,y=xy(v,k);d.ellipse((x-r,y-r,x+r,y+r),fill=color)
  def circle(radius,k,color,dashed=False):
   for start in (range(0,360,12) if dashed else [0]):
    stop=start+7 if dashed else 360
    points=[radius*np.array([math.cos(t),math.sin(t)]) for t in np.radians(np.linspace(start,stop,8 if dashed else 361))]
    line(points,k,color,1)
  def follower(tip,axis,k):
   normal=np.array([-axis[1],axis[0]])
   line([tip+extension*.12*axis,tip+extension*axis],k,'#da7131',5)
   d.polygon([xy(tip,k),xy(tip+extension*.12*axis+.025*length*normal,k),xy(tip+extension*.12*axis-.025*length*normal,k)],fill='#da7131')
   dot(tip,k,'#b85022',3)
  text((22,16),'Knife-edge disk cam | forward inversion',f=title)
  text((22,54),f'{cam.direction} | theta={a:06.1f} deg | s={p["stroke"]:.3f} | r0={cam.r0:g} | e={cam.e:g}')
  text((95,108),'Actual cam and fixed guide');text((548,108),'Fixed cam and inverse rotating guide')
  rotated=profile@rotation(-p['beta']).T
  d.polygon([xy(v,0) for v in rotated],fill='#d7e6f1',outline='#2a6993')
  circle(cam.r0,0,'#859aaf',True)
  tip=p['tip'];axis=np.array([0.,1.]);normal=np.array([1.,0.])
  for side in [-1,1]:
   v=np.array([cam.e,cam.l0+maximum])+extension*.15*axis+side*.045*length*normal
   line([v,v+extension*.2*axis],0,'#647588',3)
  follower(tip,axis,0);dot(rotation(-p['beta'])@profile[1500],0,'#287ba3')
  line(profile,1,'#bbc8d6',2)
  trace=profile[:int(a*10)+1]
  if len(trace)>1:line(np.vstack([trace,p['profile']]),1,'#c45b27',3)
  circle(cam.r0,1,'#859aaf',True)
  if cam.e:circle(abs(cam.e),1,'#47a395')
  T=p['foot'];axis=p['axis'];normal=np.array([-axis[1],axis[0]])
  line([T-length*.5*axis,T+(cam.l0+maximum+extension)*axis],1,'#7eae9e',1)
  line([np.zeros(2),T],1,'#47a395',2);dot(T,1,'#47a395',3)
  for side in [-1,1]:
   v=T+(cam.l0+maximum+extension*.15)*axis+side*.045*length*normal
   line([v,v+extension*.2*axis],1,'#647588',3)
  follower(p['profile'],axis,1)
  for k in [0,1]:
   x,y=centers[k];dot(np.zeros(2),k,'#273444',4)
   d.line([(x,y+6),(x-10,y+20),(x+10,y+20),(x,y+6)],fill='#596779',width=2)
  text((60,478),'Dashed: base circle | blue dot: cam material point')
  text((540,478),'Green: tangent guide | orange: tip trace')
  x0,y0,W,H=70,560,820,90;chartmax=maximum if maximum>0 else cam.r0
  def graph(angle,s):return (x0+W*angle/360,y0+H-H*s/chartmax)
  d.line([(x0,y0),(x0,y0+H),(x0+W,y0+H)],fill='#788798',width=1)
  d.line([graph(s['theta_deg'],s['stroke']) for s in samples],fill='#5169aa',width=2)
  x,y=graph(a,p['stroke']);d.line([(x,y),(x,y0+H)],fill='#d8652b',width=1)
  d.line([(x0,y),(x,y)],fill='#c9a387',width=1)
  d.ellipse((x-5,y-5,x+5,y+5),fill='#d8652b')
  text((70,525),'stroke(theta_deg), theta in [0,360]');text((670,525),f's={p["stroke"]:.3f}')
  for v in [0,90,180,270,360]:text((x0+W*v/360-12,y0+H+5),str(v))
  text((22,690),'Illustrative geometry | 50 fps | inverse drawing trace resets each cycle')
  pictures.append(im)
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 result=save_gif_under_limit(pictures,out/'animation.gif')
 pictures[frames//3].save(out/'preview.png')
 # Independent signed angular steps, including the cyclic seam, for a rigid cam marker.
 vectors=[rotation(-p['beta'])@np.array([1.,0.]) for p in poses]
 steps=[math.degrees(math.atan2(v[0]*w[1]-v[1]*w[0],v@w)) for v,w in zip(vectors,vectors[1:]+vectors[:1])]
 expected=cam.sign*360/frames
 error=max(abs(s-expected) for s in steps)
 if error>1e-8:raise GeometryError('animation_seam','cam input direction or seam incorrect')
 result.update({'expected_step_deg':expected,'maximum_step_error_deg':error,'loop_seam_step_deg':steps[-1],
                'closure_error':report['closure_error'],'period_seconds':frames*.02})
 return result

def export_cam(cam,out,gif=False):
 out=Path(out);out.mkdir(parents=True,exist_ok=True);report=verify_cam(cam)
 def table(filename,angles):
  with (out/filename).open('w',newline='') as f:
   w=csv.writer(f);w.writerow(['theta_deg','stroke','cam_x','cam_y','tip_x','tip_y'])
   for a in angles:
    p=cam.pose(a);w.writerow([a,p['stroke'],*p['profile'],*p['tip']])
 table('coordinates_10deg.csv',range(0,361,10));table('profile_0.1deg.csv',np.linspace(0,360,3601))
 if gif:report['animation']=render_cam(cam,out)
 (out/'verification.json').write_text(json.dumps(report,indent=2))
 return report

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('stroke_file',help='trusted Python file defining stroke(theta_deg)')
 parser.add_argument('--radius',type=float,required=True);parser.add_argument('--offset',type=float,default=0)
 parser.add_argument('--direction',choices=['clockwise','counterclockwise'],default='clockwise')
 parser.add_argument('--out',required=True);parser.add_argument('--gif',action='store_true');args=parser.parse_args()
 spec=importlib.util.spec_from_file_location('user_stroke',args.stroke_file);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 print(json.dumps(export_cam(Cam(module.stroke,args.radius,args.offset,args.direction),args.out,args.gif),indent=2))
if __name__=='__main__':main()
