"""Run: python run_model.py model.json --out OUTPUT [--gif]."""
import argparse,csv,json,io
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from linkage import solve,verify,guide_frame,J,unit,check_pose,GeometryError

def animation_poses(model,frames=300):
    """One nonduplicated input revolution; validate directed crank steps and seam."""
    if not isinstance(frames,int) or frames<3:raise ValueError('frames must be an integer >= 3')
    poses=[solve(model,i*360/frames) for i in range(frames)]
    for p in poses:
        error,_=check_pose(model,p)
        if error>1e-8:raise GeometryError('constraint_error','animation pose violates constraints')
    end=solve(model,360)
    closure=max(np.linalg.norm(end[k]-poses[0][k]) for k in end)
    if closure>1e-8:raise GeometryError('nonperiodic_animation','360-degree input is not a full mechanism period')
    drives=[]
    for st in model['plan']:
        if st['op']!='rotate':continue
        expected=360*st.get('ratio',1)/frames
        if abs(expected)>=180:raise GeometryError('animation_aliasing','increase frames to resolve input direction')
        vectors=[unit(p[st['out']]-p[st['origin']]) for p in poses]
        steps=[]
        for i,a in enumerate(vectors):
            b=vectors[(i+1)%frames]
            steps.append(float(np.degrees(np.arctan2(a[0]*b[1]-a[1]*b[0],a@b))))
        error=max(abs(v-expected) for v in steps)
        if error>1e-8:raise GeometryError('discontinuous_animation','input angular increment changes at a frame or loop seam')
        drives.append({'point':st['out'],'expected_step_deg':expected,
                       'maximum_step_error_deg':error,'loop_seam_step_deg':steps[-1]})
    return poses,{'passed':True,'frames':frames,'closure_error':float(closure),'drives':drives}

def save_gif_under_limit(pictures,target,max_bytes=5_000_000):
    """Preserve every pose and its timing; compress palette/size instead of dropping frames."""
    if not pictures or max_bytes<=0:raise ValueError('pictures and positive max_bytes required')
    attempts=[]
    for factor,colors in [(1.,128),(1.,64),(.875,64),(.75,48)]:
        size=tuple(max(1,round(v*factor)) for v in pictures[0].size)
        palette=pictures[0].convert('RGB').resize(size,Image.Resampling.LANCZOS).quantize(colors=colors)
        encoded=[p.convert('RGB').resize(size,Image.Resampling.LANCZOS).quantize(palette=palette,dither=Image.Dither.NONE) for p in pictures]
        stream=io.BytesIO()
        encoded[0].save(stream,format='GIF',save_all=True,append_images=encoded[1:],duration=20,loop=0,optimize=True,disposal=1)
        data=stream.getvalue();attempts.append({'size':list(size),'colors':colors,'bytes':len(data)})
        if len(data)>=max_bytes:continue
        with Image.open(io.BytesIO(data)) as gif:
            if gif.n_frames!=len(pictures) or gif.info.get('loop')!=0:continue
            timings=[]
            for i in range(gif.n_frames):gif.seek(i);timings.append(gif.info.get('duration',0))
            if set(timings)!={20}:continue
        Path(target).write_bytes(data)
        return {'frames':len(pictures),'fps':50,'frame_duration_ms':20,'file_size_bytes':len(data),'file_size_limit_bytes':max_bytes,'under_size_limit':True,'loop':0,'export_size_px':list(size),'palette_colors':colors,'frame_dropping':False,'compression_attempts':attempts}
    raise GeometryError('animation_export_limit','cannot meet GIF size/frame/timing limits; simplify rendering without dropping poses')

def render(model,out,frames=300):
    poses,animation_report=animation_poses(model,frames)
    cloud=[]
    for p in poses:
        cloud.extend(p.values())
        for g in model.get('guides',[]):
            q,u=guide_frame(g,p);cloud.extend([q+g['lo']*u,q+g['hi']*u])
    cloud=np.array(cloud);lo=cloud.min(0);hi=cloud.max(0);center=(lo+hi)/2
    width=float(model.get('rod_width',8));scale=min(600/(hi[0]-lo[0]+60),360/(hi[1]-lo[1]+60))
    try:font=ImageFont.truetype('DejaVuSans.ttf',28)
    except OSError:font=ImageFont.load_default()
    pictures=[]
    for i,p in enumerate(poses):
        im=Image.new('RGB',(1440,960),'#101b2e');d=ImageDraw.Draw(im)
        def xy(v):return tuple((np.array([360,260])+np.array([1,-1])*(v-center)*scale)*2)
        def rect(q,u,a,b,c,e,color):
            d.polygon([xy(q+x*u+y*(J@u)) for x,y in [(a,c),(b,c),(b,e),(a,e)]],fill=color)
        def rod(a,b,color):
            delta=b-a;length=np.linalg.norm(delta)
            if length>1e-10:rect(a,delta/length,0,length,-width/2,width/2,color)
        # Fixed guide is an abstract axis with a short ground mark; no support frame.
        for g in model.get('guides',[]):
            q,u=guide_frame(g,p)
            if 'origin_point' not in g:
                d.line([xy(q+g['lo']*u),xy(q+g['hi']*u)],fill='#627d98',width=3)
                t=g['lo']+.12*(g['hi']-g['lo'])
                for offset in [-6,0,6]:
                    c=q+(t+offset)*u+8*(J@u)
                    d.line([xy(c),xy(c-4*u+4*(J@u))],fill='#627d98',width=2)
        rigid=set(model.get('rigid_points',[]))
        for a,b in model.get('rods',[]):rod(p[a],p[b],'#20c997' if a in rigid and b in rigid else '#ffb32c')
        for g in model.get('guides',[]):
            q,u=guide_frame(g,p);c=p[g['point']];h=g['hole_width']/2;wall=4;half=g['sleeve_length']/2
            for a,b in [(-h-wall,-h),(h,h+wall)]:rect(c,u,-half,half,a,b,'#c5d4e4')
        for key,v in p.items():
            x,y=xy(v)
            if key in model['fixed']:
                d.polygon([(x,y+5),(x-12,y+20),(x+12,y+20)],outline='#dce6ef')
                d.line((x-16,y+23,x+16,y+23),fill='#dce6ef',width=2)
                for h in [-12,-4,4,12]:d.line((x+h,y+23,x+h-5,y+29),fill='#627d98',width=2)
            d.ellipse((x-5,y-5,x+5,y+5),fill='#101b2e',outline='white',width=2)
            d.text((x+8,y-24),key,font=font,fill='white')
        d.text((25,15),model.get('name','Linkage'),font=font,fill='white')
        d.text((25,52),f'{i*360/frames:06.1f} deg | forward geometry | {model.get("units","units")}',font=font,fill='#83b9f1')
        d.text((25,905),'Abstract ground symbols | continuous input | functional joints',font=font,fill='white')
        pictures.append(im.resize((720,480),Image.Resampling.LANCZOS))
    export_report=save_gif_under_limit(pictures,out/'animation.gif')
    pictures[frames//3].save(out/'preview.png')
    with Image.open(out/'animation.gif') as exported:
        durations=[]
        for i in range(exported.n_frames):exported.seek(i);durations.append(exported.info.get('duration',0))
        if exported.n_frames!=frames or any(t!=20 for t in durations):
            raise GeometryError('animation_export','exported frame count or timing differs from requested animation')
    animation_report.update(export_report)
    animation_report.update({'frame_duration_ms':20,'fps':50,'period_seconds':sum(durations)/1000})
    return animation_report

def main():
    parser=argparse.ArgumentParser();parser.add_argument('model');parser.add_argument('--out',required=True);parser.add_argument('--gif',action='store_true');args=parser.parse_args()
    model=json.loads(Path(args.model).read_text());out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    report=verify(model);(out/'verification.json').write_text(json.dumps(report,indent=2))
    if not report['passed']:
        print(json.dumps(report,indent=2));raise SystemExit(2)
    with (out/'coordinates_10deg.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['theta_deg','point','x','y'])
        for deg in range(0,361,10):
            for key,value in solve(model,deg).items():w.writerow([deg,key,*value])
    if args.gif:
        try:report['animation']=render(model,out)
        except GeometryError as exc:
            report.update({'passed':False,'code':exc.code,'detail':str(exc)})
            (out/'verification.json').write_text(json.dumps(report,indent=2))
            print(json.dumps(report,indent=2));raise SystemExit(2)
        (out/'verification.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
