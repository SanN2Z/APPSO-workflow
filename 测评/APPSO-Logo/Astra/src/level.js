import contours from './logo-contours.json';

export const RADIUS = 0.185;
export const TOP = 0.86;
export const world = ([x, y]) => ({ x: (x - 989) / 100, z: (y - 317) / 100 });
export const letters = contours.shapes.filter(s => s.name !== 'dot').map(s => ({ ...s,
  outline: s.outline.map(world), holes: s.holes.map(h => h.map(world)),
}));
export const start = { ...world([219, 444]), h: 0.40 };
export const goal = { ...world([1649, 317]), h: 0.30 };
export const bridges = [
  { a: world([219, 444]), b: world([286, 321]), width: .67, h0: .40, h1: TOP, name: 'A ramp' },
  { a: world([449, 452]), b: world([594, 452]), width: .66, h0: TOP, h1: TOP, name: 'A to P' },
  { a: world([731, 369]), b: world([910, 369]), width: .66, h0: TOP, h1: TOP, name: 'P to P' },
  { a: world([1040, 379]), b: world([1230, 455]), width: .68, h0: TOP, h1: TOP, name: 'P to S' },
  { a: world([1352, 187]), b: world([1575, 187]), width: .67, h0: TOP, h1: TOP, name: 'S to O' },
  { a: world([1552, 317]), b: goal, width: .65, h0: TOP, h1: .30, name: 'Home ramp' },
];
export const checkpoints = [
  { ...world([450, 450]), label: 'A · 热身斜坡', save: false },
  { ...world([731, 369]), label: 'P · 弧线巡游', save: true },
  { ...world([1040, 371]), label: 'P · 旋转节拍', save: true },
  { ...world([1352, 187]), label: 'S · 蛇形弯道', save: false },
];
export const routePixels = [
  [219,444],[264,362],[315,271],[327,245],[367,321],[409,400],[449,452],
  [520,452],[593,452],[593,367],[593,281],[593,186],[665,181],[722,192],
  [759,226],[757,274],[752,326],[731,369],[815,369],[910,369],[910,276],
  [910,186],[985,181],[1006,163],[1045,163],[1080,228],[1093,274],[1077,326],[1040,371],
  [1120,412],[1230,455],[1293,470],[1348,461],[1384,429],[1382,386],[1348,350],
  [1280,318],[1225,289],[1212,247],[1225,199],[1265,167],[1310,162],[1352,187],
  [1438,187],[1530,187],[1590,185],[1649,181],[1715,201],[1763,251],[1780,317],
  [1758,386],[1706,437],[1649,460],[1580,439],[1530,387],[1516,317],[1575,317],[1649,317],
];
export const route = routePixels.map(world);

export function pointInPolygon(x, z, poly) {
  let inside = false;
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
    const a = poly[i], b = poly[j];
    if (((a.z > z) !== (b.z > z)) && x < (b.x - a.x) * (z - a.z) / (b.z - a.z) + a.x) inside = !inside;
  }
  return inside;
}
export function segmentPoint(x, z, a, b) {
  const dx = b.x-a.x, dz = b.z-a.z;
  const t = Math.max(0,Math.min(1,((x-a.x)*dx+(z-a.z)*dz)/(dx*dx+dz*dz)));
  return { x:a.x+dx*t, z:a.z+dz*t, t };
}
export function surfaceAt(x, z) {
  let h = -Infinity;
  let slopeX = 0, slopeZ = 0;
  for (const l of letters) {
    if (pointInPolygon(x,z,l.outline) && !l.holes.some(p=>pointInPolygon(x,z,p))) { h = TOP; break; }
  }
  if (Math.hypot(x-start.x,z-start.z)<.68) h=Math.max(h,start.h);
  if (Math.hypot(x-goal.x,z-goal.z)<.58) h=Math.max(h,goal.h);
  for (const b of bridges) {
    const p=segmentPoint(x,z,b.a,b.b);
    if (Math.hypot(x-p.x,z-p.z)<=b.width/2) {
      const height=b.h0+(b.h1-b.h0)*p.t;
      if (height>h) {
        h=height;
        const d2=(b.b.x-b.a.x)**2+(b.b.z-b.a.z)**2;
        slopeX=(b.h1-b.h0)*(b.b.x-b.a.x)/d2;
        slopeZ=(b.h1-b.h0)*(b.b.z-b.a.z)/d2;
      }
    }
  }
  return {h,slopeX,slopeZ};
}

// World-space obstacles, used by both drawing and fixed-step collision response.
export function obstaclesAt(time) {
  const p1=world([801,274]), p2=world([1032,200]), s=world([1405,409]);
  const angle=time*.95;
  return [
    {type:'circle',x:p1.x+Math.sin(time*1.4)*.08,z:p1.z,r:.16,id:'bumper'},
    {type:'bar',x:p2.x,z:p2.z,ax:p2.x-Math.cos(angle)*.26,az:p2.z-Math.sin(angle)*.26,
      bx:p2.x+Math.cos(angle)*.26,bz:p2.z+Math.sin(angle)*.26,r:.065,id:'sweeper'},
    {type:'circle',x:s.x+.14,z:s.z,r:.12,id:'S bumper'},
  ];
}

export class Physics {
  constructor(onEvent=()=>{}) { this.onEvent=onEvent; this.reset(); }
  reset() {
    this.time=0;this.falls=0;this.stage=0;this.saved={...start};this.won=false;this.respawnDelay=0;this.collisions=0;this.landings=0;
    this.spawn();
  }
  spawn() { this.ball={x:this.saved.x,z:this.saved.z,y:this.saved.h+RADIUS+.012,vx:0,vz:0,vy:0,grounded:true}; }
  step(dt,input={x:0,z:0,brake:false}) {
    if(this.won)return;
    this.time+=dt;
    if(this.respawnDelay>0) {
      this.respawnDelay-=dt;
      if(this.respawnDelay<=0){this.spawn();this.onEvent('respawn');}
      return;
    }
    const b=this.ball;
    const prevH=b.y-RADIUS;
    const surface=surfaceAt(b.x,b.z);
    const grounded=b.grounded;
    const accel=grounded?5.1:1.5;
    let ix=input.x||0, iz=input.z||0;
    const m=Math.hypot(ix,iz);if(m>1){ix/=m;iz/=m;}
    b.vx+=ix*accel*dt;b.vz+=iz*accel*dt;
    if(grounded&&Number.isFinite(surface.h)) {b.vx-=surface.slopeX*3.2*dt;b.vz-=surface.slopeZ*3.2*dt;}
    const drag=grounded?(input.brake?10:1.65):.18;
    b.vx*=Math.exp(-drag*dt);b.vz*=Math.exp(-drag*dt);
    const speed=Math.hypot(b.vx,b.vz), max=input.brake?1.05:2.55;
    if(speed>max){b.vx*=max/speed;b.vz*=max/speed;}
    b.x+=b.vx*dt;b.z+=b.vz*dt;
    b.vy-=12*dt;b.y+=b.vy*dt;
    const under=surfaceAt(b.x,b.z);
    if(Number.isFinite(under.h)&&prevH>=under.h-.055&&b.y-RADIUS<=under.h+.02&&b.vy<=0) {
      if(!grounded&&b.vy<-.65){this.landings++;this.onEvent('land',Math.abs(b.vy));}
      b.y=under.h+RADIUS;b.vy=0;b.grounded=true;
    } else b.grounded=false;
    // Collision with solid elevated letter sides when the ball is below the top.
    if(Number.isFinite(under.h)&&b.y+RADIUS>0&&b.y-RADIUS<under.h-.09&&prevH<under.h-.055) {
      b.x-=b.vx*dt*1.4;b.z-=b.vz*dt*1.4;b.vx*=-.35;b.vz*=-.35;
    }
    if(b.y>TOP-.1&&b.y<TOP+.7) for(const o of obstaclesAt(this.time)) {
      let p=o;
      if(o.type==='bar')p=segmentPoint(b.x,b.z,{x:o.ax,z:o.az},{x:o.bx,z:o.bz});
      let dx=b.x-p.x,dz=b.z-p.z,d=Math.hypot(dx,dz),limit=RADIUS+o.r;
      if(d<limit) {
        if(d<.0001){dx=1;dz=0;d=1;}
        const nx=dx/d,nz=dz/d;
        b.x=p.x+nx*(limit+.003);b.z=p.z+nz*(limit+.003);
        const vn=b.vx*nx+b.vz*nz;
        if(vn<0){b.vx-=1.6*vn*nx;b.vz-=1.6*vn*nz;}
        b.vx+=nx*.18;b.vz+=nz*.18;
        this.collisions++;this.onEvent('collision');
      }
    }
    if(b.y-RADIUS<.025) {
      b.y=RADIUS+.025;b.vy=Math.abs(b.vy)*.18;
      this.falls++;this.respawnDelay=.85;this.onEvent('fall');
      return;
    }
    const cp=checkpoints[this.stage];
    if(cp&&b.grounded&&Math.hypot(b.x-cp.x,b.z-cp.z)<.46) {
      if(cp.save)this.saved={x:cp.x,z:cp.z,h:TOP};
      this.stage++;this.onEvent('checkpoint',{...cp,index:this.stage});
    }
    if(this.stage===4&&b.grounded&&Math.hypot(b.x-goal.x,b.z-goal.z)<.19&&b.y<.56){this.won=true;b.vx=0;b.vz=0;b.vy=0;this.onEvent('win');}
  }
}
