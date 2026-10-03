"""Reproduce this confirmed example; run from any working directory.
Dependencies: repository requirements.txt including mpmath.
"""
from pathlib import Path
import sys,json,math,copy,subprocess
import numpy as np
from mpmath import iv
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'scripts'))
from linkage import solve,check_pose,rotation
m=json.loads((OUT/'model.json').read_text())

def interval_proof(n=3600):
    iv.dps=30
    lower=lambda x:float(x.a)-1e-9
    upper=lambda x:float(x.b)+1e-9
    bounds={k:[math.inf,-math.inf] for k in ['D_x','D_y','E_y']}
    h2min=math.inf;z2min=math.inf
    for i in range(n):
        t=iv.mpf([i,i+1])*2*iv.pi/n
        ax=40*iv.cos(t);ay=40*iv.sin(t)
        vx=-ax;vy=100-ay
        dist=iv.sqrt(vx**2+vy**2)
        u=vx/dist;v=vy/dist
        a=(110**2-95**2+dist**2)/(2*dist)
        h2=110**2-a**2
        assert lower(h2)>0
        h=iv.sqrt(h2)
        bx=ax+a*u+h*v;by=ay+a*v-h*u
        dx=ax+iv.mpf(210)/110*(bx-ax)
        dy=ay+iv.mpf(210)/110*(by-ay)
        z2=90**2-(210-dx)**2
        assert lower(z2)>0
        ey=dy+iv.sqrt(z2)
        for k,val in [('D_x',dx),('D_y',dy),('E_y',ey)]:
            bounds[k][0]=min(bounds[k][0],lower(val));bounds[k][1]=max(bounds[k][1],upper(val))
        h2min=min(h2min,lower(h2));z2min=min(z2min,lower(z2))
    axial=min(bounds['E_y'][0]-12-85,320-bounds['E_y'][1]-12)
    assert axial>0
    return {'passed':True,'method':'mpmath interval arithmetic, 30 decimal digits; 3600 closed intervals covering [0,2*pi]; exported float bounds widened by 1e-9','interval_count':n,'fourbar_center_distance_range_mm':[60,140],'fourbar_strict_conditions':['abs(110-95)=15 < 60','140 < 110+95=205'],'bounds_mm':bounds,'minimum_two_circle_h_squared_mm2':h2min,'minimum_circle_line_radicand_mm2':z2min,'minimum_proven_guide_axial_margin_mm':axial,'side_clearance_mm':1,'scope':'Continuous geometric reachability on the fixed branches and finite slider engagement for this exact example model. Not a collision, strength or manufacturing proof.'}

proof=interval_proof()
(OUT/'continuous-proof.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2))
# Independent distance, collinearity, signed branch, rigid orientation and frame invariance checks.
maximum_distance=0.;maximum_collinear=0.;min_branch=math.inf;max_transform=0.;min_det=math.inf
R=rotation(.63);shift=np.array([73.,-29.]);t=copy.deepcopy(m)
for k,v in t['fixed'].items():t['fixed'][k]=(R@np.array(v)+shift).tolist()
for st in t['plan']:
    if st['op']=='rotate':st['local']=(R@np.array(st['local'])).tolist()
    if st['op']=='circle_line':
        st['q']=(R@np.array(st['q'])+shift).tolist();st['v']=(R@np.array(st['v'])).tolist()
for g in t['guides']:
    g['origin']=(R@np.array(g['origin'])+shift).tolist();g['axis']=(R@np.array(g['axis'])).tolist()
for deg in np.linspace(0,360,3601):
    p=solve(m,float(deg));q=solve(t,float(deg));check_pose(t,q)
    for a,b,l in m['lengths']:maximum_distance=max(maximum_distance,abs(np.linalg.norm(p[a]-p[b])-l))
    ab=p['B']-p['A'];ad=p['D']-p['A']
    maximum_collinear=max(maximum_collinear,abs(ab[0]*ad[1]-ab[1]*ad[0]))
    v=p['C']-p['A'];w=p['B']-p['A'];min_branch=min(min_branch,-(v[0]*w[1]-v[1]*w[0]))
    for k in p:max_transform=max(max_transform,float(np.linalg.norm(q[k]-(R@p[k]+shift))))
assert maximum_distance<1e-8 and maximum_collinear<1e-8 and min_branch>0 and max_transform<1e-8
poses=[solve(m,float(d)) for d in np.linspace(0,360,3601)]
ey=np.array([p['E'][1] for p in poses]);indices=[int(ey.argmin()),int(ey.argmax())]
audit={'passed':True,'sample_count':3601,'maximum_independent_length_error_mm':maximum_distance,'maximum_AB_AD_cross_product_mm2':maximum_collinear,'minimum_signed_branch_area_mm2':min_branch,'maximum_rigid_frame_transform_error_mm':max_transform,'sampled_output_range_mm':[float(ey.min()),float(ey.max())],'sampled_stroke_mm':float(np.ptp(ey)),'sampled_extremum_angles_deg':[i/10 for i in indices],'input_direction':'counterclockwise, explicitly selected example convention; user did not separately specify clockwise/counterclockwise','branches':{'B':-1,'E':1}}
(OUT/'additional-verification.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2))
subprocess.run([sys.executable,str(ROOT/'scripts/run_model.py'),str(OUT/'model.json'),'--out',str(OUT),'--gif'],check=True)
print(json.dumps({'continuous_proof':proof,'additional_checks':audit},ensure_ascii=False,indent=2))
