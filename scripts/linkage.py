"""Joint-derived planar forward constructions. Units are supplied by the model."""
import math
import numpy as np

J=np.array([[0.,-1.],[1.,0.]])
def rotation(t):
    return np.array([[math.cos(t),-math.sin(t)],[math.sin(t),math.cos(t)]])

class GeometryError(ValueError):
    def __init__(self,code,message):
        self.code=code
        super().__init__(f'{code}: {message}')

def unit(v):
    v=np.asarray(v,dtype=float);n=np.linalg.norm(v)
    if not np.isfinite(n) or n<=1e-12:raise GeometryError('singular','zero or invalid direction')
    return v/n

def branch_value(branch):
    if branch not in (-1,1):raise GeometryError('branch_required','choose +1 or -1 from initial assembly')
    return branch

def circles(p,q,r,s,branch,tol=1e-10):
    b=branch_value(branch)
    if r<=0 or s<=0:raise GeometryError('invalid_model','radii must be positive')
    p=np.asarray(p,float);q=np.asarray(q,float);d=np.linalg.norm(q-p)
    if d<=tol:raise GeometryError('singular','coincident circle centers')
    if d>r+s+tol or d<abs(r-s)-tol:raise GeometryError('unreachable','circle pair does not intersect')
    u=(q-p)/d;a=(r*r-s*s+d*d)/(2*d);h2=r*r-a*a
    if h2<=tol*max(r,s,1):raise GeometryError('singular','tangent or near-tangent circles; branch continuation needs analysis')
    return p+a*u+b*math.sqrt(h2)*(J@u)

def circle_line(p,r,q,v,branch,tol=1e-10):
    b=branch_value(branch);v=unit(v);p=np.asarray(p,float);q=np.asarray(q,float)
    if r<=0:raise GeometryError('invalid_model','radius must be positive')
    foot=q+np.dot(p-q,v)*v;distance=np.linalg.norm(p-foot)
    if distance>r+tol:raise GeometryError('unreachable','circle does not intersect guide')
    h2=r*r-distance*distance
    if h2<=tol*max(r,1):raise GeometryError('singular','tangent or near-tangent circle/guide')
    return foot+b*math.sqrt(h2)*v

def frame(p,st):
    u=unit(p[st['known']]-p[st['origin']]);u0=unit(st.get('known_local',[1,0]))
    return np.column_stack((u,J@u))@np.column_stack((u0,J@u0)).T

def solve(model,degrees):
    p={k:np.asarray(v,float) for k,v in model['fixed'].items()}
    if any(v.shape!=(2,) or not np.all(np.isfinite(v)) for v in p.values()):
        raise GeometryError('invalid_model','fixed points must be finite 2-vectors')
    pending=list(model['plan'])
    while pending:
        progress=False
        for st in pending[:]:
            op=st['op'];out=st['out']
            if out in p:raise GeometryError('invalid_model',f'duplicate point {out}')
            deps={'rotate':['origin'],'circles':['p','q'],'rigid':['origin','known'],
                  'circle_line':['p'],'project':['p']} .get(op)
            if deps is None:raise GeometryError('unsupported',f'unknown primitive {op}')
            if any(st[k] not in p for k in deps):continue
            if op=='rotate':v=p[st['origin']]+rotation(math.radians(degrees*st.get('ratio',1)+st.get('phase_deg',0)))@np.asarray(st['local'])
            elif op=='circles':v=circles(p[st['p']],p[st['q']],st['r'],st['s'],st.get('branch'))
            elif op=='rigid':v=p[st['origin']]+frame(p,st)@np.asarray(st['target_local'])
            elif op=='circle_line':v=circle_line(p[st['p']],st['r'],st['q'],st['v'],st.get('branch'))
            else:
                q=np.asarray(st['q'],float);u=unit(st['v']);v=q+np.dot(p[st['p']]-q,u)*u
            if not np.all(np.isfinite(v)):raise GeometryError('invalid_model','nonfinite coordinate')
            p[out]=v;pending.remove(st);progress=True
        if not progress:raise GeometryError('unresolved_dependencies','missing inputs or a closed group outside supported constructions')
    return p

def guide_frame(g,p):
    # Fixed guide: origin/axis. Moving guide: origin_point/through_point.
    if 'origin_point' in g:return p[g['origin_point']],unit(p[g['through_point']]-p[g['origin_point']])
    return np.asarray(g['origin'],float),unit(g['axis'])

def check_pose(model,p):
    errors=[];margins=[]
    for a,b,length in model.get('lengths',[]):errors.append(abs(np.linalg.norm(p[a]-p[b])-length))
    for st in model['plan']:
        if st['op']=='circle_line':
            errors.append(abs(np.dot(p[st['out']]-st['q'],J@unit(st['v']))))
            errors.append(abs(np.linalg.norm(p[st['out']]-p[st['p']])-st['r']))
        elif st['op']=='circles':
            errors.extend([abs(np.linalg.norm(p[st['out']]-p[st[k]])-st[r]) for k,r in [('p','r'),('q','s')]])
        elif st['op']=='rigid':
            expected=p[st['origin']]+frame(p,st)@st['target_local'];errors.append(np.linalg.norm(expected-p[st['out']]))
    for g in model.get('guides',[]):
        origin,u=guide_frame(g,p);d=p[g['point']]-origin;t=float(d@u)
        errors.append(abs(d@(J@u)));half=g['sleeve_length']/2
        margin=min(t-half-g['lo'],g['hi']-t-half)
        gap=(g['hole_width']-g['rod_width'])/2
        if margin<0:raise GeometryError('disengaged',f"{g['point']} exceeds finite guide by {-margin:g}")
        if gap<=0:raise GeometryError('interference','sleeve hole must exceed rod width')
        margins.append((margin,gap))
    return float(max(errors,default=0)),margins

def verify(model,step=.1):
    if not 0<step<=360:raise ValueError('step must be in (0,360]')
    maximum=0.;axial=math.inf;gap=math.inf
    angles=np.linspace(0,360,math.ceil(360/step)+1)
    for deg in angles:
        try:
            p=solve(model,float(deg));e,m=check_pose(model,p)
        except GeometryError as exc:
            return {'passed':False,'angle_deg':float(deg),'code':exc.code,'detail':str(exc)}
        maximum=max(maximum,e)
        for a,b in m:axial=min(axial,a);gap=min(gap,b)
    a=solve(model,0);b=solve(model,360);closure=max(np.linalg.norm(a[k]-b[k]) for k in a)
    passed=maximum<1e-8 and closure<1e-8
    return {'passed':bool(passed),'code':'ok' if passed else 'constraint_error','sample_count':len(angles),
            'maximum_residual':maximum,'closure_error':float(closure),
            'minimum_sampled_axial_margin':None if math.isinf(axial) else axial,
            'minimum_side_clearance':None if math.isinf(gap) else gap,
            'continuous_reachability_proven':False,
            'scope':'sampled kinematics and declared guide engagement; derive continuous bounds separately'}
