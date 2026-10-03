"""Forward inversion for centered/offset translating knife-edge disk cams.
Angles supplied to stroke are degrees in [0, 360]; offset is signed world x.
"""
import math
import numpy as np
from linkage import rotation, GeometryError

class Cam:
 def __init__(self, stroke, base_radius, offset=0., direction='clockwise'):
  self.stroke=stroke;self.r0=float(base_radius);self.e=float(offset)
  if not callable(stroke) or not all(math.isfinite(v) for v in [self.r0,self.e]) or self.r0<=abs(self.e):
   raise ValueError('callable stroke and finite base_radius > abs(offset) required')
  if direction not in ['clockwise','counterclockwise']:raise ValueError('invalid direction')
  self.direction=direction;self.sign=-1 if direction=='clockwise' else 1
  self.l0=math.sqrt((self.r0-self.e)*(self.r0+self.e))
 def pose(self,theta_deg):
  a=float(theta_deg)
  if not math.isfinite(a) or not 0<=a<=360:raise ValueError('theta_deg must be in [0,360]')
  s=float(self.stroke(a))
  if not math.isfinite(s) or s<0:raise GeometryError('invalid_stroke',f'finite nonnegative stroke required at {a} degrees')
  beta=-self.sign*math.radians(a);R=rotation(beta)
  tip=np.array([self.e,self.l0+s]);foot=R@np.array([self.e,0.]);axis=R@np.array([0.,1.])
  return {'theta_deg':a,'stroke':s,'beta':beta,'tip':tip,'profile':R@tip,'foot':foot,'axis':axis,'zero':foot+self.l0*axis}

def verify_cam(cam,step=.1,tolerance=1e-8):
 """Sample geometric constraints; endpoint checked without modulo wrapping."""
 if not math.isfinite(step) or not 0<step<=.1:raise ValueError('verification step must be in (0,.1]')
 if not math.isfinite(tolerance) or tolerance<=0:raise ValueError('positive finite tolerance required')
 first=cam.pose(0);end=cam.pose(360)
 closure=float(np.linalg.norm(first['profile']-end['profile']))
 if abs(first['stroke'])>tolerance or abs(end['stroke'])>tolerance:
  raise GeometryError('invalid_zero_stroke','stroke(0) and stroke(360) must be zero at the reference base-circle contact')
 if closure>tolerance:raise GeometryError('nonperiodic_cam','profile endpoints do not close')
 residual=0.;n=math.ceil(360/step)+1
 for a in np.linspace(0,360,n):
  p=cam.pose(a);restored=rotation(-p['beta'])@p['profile'];T=p['foot'];d=p['axis']
  residual=max(residual,float(np.linalg.norm(restored-p['tip'])),abs(float(T@d)),abs(float(np.linalg.norm(T))-abs(cam.e)),
               abs(float((p['profile']-T)@np.array([-d[1],d[0]]))),abs(float(np.linalg.norm(p['zero']))-cam.r0),
               abs(float((p['profile']-p['zero'])@d)-p['stroke']))
 if residual>tolerance:raise GeometryError('constraint_error','sampled cam constraints exceed tolerance')
 return {'passed':True,'samples':n,'step_deg':360/(n-1),'maximum_constraint_error':residual,'closure_error':closure,
         'continuous_proven':False,'scope':'sampled ideal prescribed knife-edge contact; no force closure, interference or manufacturability proof',
         'base_radius':cam.r0,'offset':cam.e,'direction':cam.direction}
