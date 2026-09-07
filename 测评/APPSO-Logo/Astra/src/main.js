import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { toCreasedNormals } from 'three/addons/utils/BufferGeometryUtils.js';
import './style.css';
import { letters, bridges, start, goal, checkpoints, route, RADIUS, TOP, Physics, surfaceAt, obstaclesAt } from './level.js';

const $=s=>document.querySelector(s);
const icons={
  sound:'<path d="M11 5 6 9H3v6h3l5 4z"/><path d="M15 8a6 6 0 0 1 0 8m3-11a10 10 0 0 1 0 14"/>',
  mute:'<path d="M11 5 6 9H3v6h3l5 4z"/><path d="m16 9 5 6m0-6-5 6"/>',
  pause:'<path d="M8 5v14M16 5v14"/>',
  play:'<path d="m8 5 11 7-11 7z"/>',
  restart:'<path d="M3 10a9 9 0 1 1 1 8M3 4v6h6"/>',
};
function icon(el,name){el.innerHTML=`<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">${icons[name]}</svg>`;}
icon($('#sound'),'sound');icon($('#pause'),'pause');icon($('#restart'),'restart');

const stage=$('#stage');
const scene=new THREE.Scene();
scene.background=null;
const camera=new THREE.OrthographicCamera(-12,12,6,-6,.1,100);
let renderer;
try {
  renderer=new THREE.WebGLRenderer({antialias:true,alpha:true,powerPreference:'high-performance'});
} catch(error) {
  $('#loading').textContent='无法启动 3D 画面，请开启浏览器硬件加速后刷新。';
  $('#start').disabled=true;
  throw error;
}
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.shadowMap.enabled=true;
renderer.shadowMap.type=THREE.PCFSoftShadowMap;
renderer.outputColorSpace=THREE.SRGBColorSpace;
renderer.toneMapping=THREE.NeutralToneMapping;
renderer.toneMappingExposure=1;
stage.appendChild(renderer.domElement);
renderer.domElement.setAttribute('aria-label','3D 游戏画面。WASD 或方向键移动，空格刹车。');
renderer.domElement.tabIndex=0;
const pmrem=new THREE.PMREMGenerator(renderer);
const room=new RoomEnvironment();
const environment=pmrem.fromScene(room,.04);
scene.environment=environment.texture;
scene.environmentIntensity=.35;
room.dispose();pmrem.dispose();
scene.add(new THREE.HemisphereLight(0xffffff,0xb1a797,.85));
const sun=new THREE.DirectionalLight(0xfff7ed,2.1);
sun.position.set(-5,14,6);sun.castShadow=true;
Object.assign(sun.shadow.camera,{left:-14,right:14,top:9,bottom:-9,near:1,far:35});
sun.shadow.mapSize.set(2048,2048);sun.shadow.normalBias=.035;sun.shadow.bias=-.00008;sun.shadow.radius=3;
scene.add(sun);
const fill=new THREE.DirectionalLight(0xe0ecff,.4);fill.position.set(8,5,-8);scene.add(fill);

const mat=(color,extra={})=>new THREE.MeshStandardMaterial({color,roughness:.4,metalness:.04,...extra});
const white=mat('#fffefa',{roughness:.27});
const side=mat('#deddd4',{roughness:.38});
const red=mat('#f72f2f',{roughness:.45});
const flatRed=new THREE.MeshBasicMaterial({color:'#f72f2f',toneMapped:false});
const flatWhite=new THREE.MeshBasicMaterial({color:'#ffffff',toneMapped:false});
const dark=mat('#343b37',{roughness:.3,metalness:.35});
const metal=mat('#d9ddd7',{roughness:.27,metalness:.8});
const railMat=mat('#f9ccc7',{transparent:true,opacity:.7,roughness:.2,metalness:.3});
const bridgeMat=mat('#f4d4cd',{transparent:true,opacity:.50,roughness:.17,metalness:.1,depthWrite:false});
const root=new THREE.Group();scene.add(root);
const letterGroup=new THREE.Group();root.add(letterGroup);
const details=new THREE.Group();root.add(details);
const extras=new THREE.Group();root.add(extras);
function mesh(geo,material,parent=details){const m=new THREE.Mesh(geo,material);m.castShadow=true;m.receiveShadow=true;parent.add(m);return m;}
function makeShape(outline,holes=[]){
  const shape=new THREE.Shape(outline.map(p=>new THREE.Vector2(p.x,-p.z)));
  for(const h of holes)shape.holes.push(new THREE.Path(h.map(p=>new THREE.Vector2(p.x,-p.z))));
  return shape;
}
function extrude(shape,depth,bevel=.03){
  const geo=new THREE.ExtrudeGeometry(shape,{depth,bevelEnabled:bevel>0,bevelThickness:bevel,bevelSize:bevel,bevelSegments:3,steps:1,curveSegments:24});
  geo.rotateX(-Math.PI/2);return toCreasedNormals(geo,Math.PI/3);
}
function roundedRect(w,h,r){
  const s=new THREE.Shape(),x=-w/2,y=-h/2;
  s.moveTo(x+r,y);s.lineTo(x+w-r,y);s.quadraticCurveTo(x+w,y,x+w,y+r);s.lineTo(x+w,y+h-r);s.quadraticCurveTo(x+w,y+h,x+w-r,y+h);
  s.lineTo(x+r,y+h);s.quadraticCurveTo(x,y+h,x,y+h-r);s.lineTo(x,y+r);s.quadraticCurveTo(x,y,x+r,y);return s;
}
const board=mesh(extrude(roundedRect(21.2,7.25,.32),.32,.055),red,root);board.position.y=-.38;
const boardEdge=mesh(extrude(roundedRect(21.19,7.24,.32),.09,.035),mat('#c52428'),root);boardEdge.position.y=-.42;
const floor=mesh(new THREE.PlaneGeometry(200,200),new THREE.ShadowMaterial({color:'#5a4a43',opacity:.16}),scene);floor.rotation.x=-Math.PI/2;floor.position.y=-.65;floor.castShadow=false;
for(const l of letters){
  const m=mesh(extrude(makeShape(l.outline,l.holes),TOP-.05,.035),[white,side],letterGroup);m.position.y=.015;
  m.userData.name=l.name;
  const contact=mesh(new THREE.ShapeGeometry(makeShape(l.outline,l.holes)),new THREE.MeshBasicMaterial({color:'#870a0f',transparent:true,opacity:.10,depthWrite:false}),extras);
  contact.rotation.x=-Math.PI/2;contact.position.set(.035,.004,.055);contact.castShadow=false;
}
const startPad=mesh(new THREE.CylinderGeometry(.68,.68,start.h,64),[side,white,side]);startPad.position.set(start.x,start.h/2,start.z);
const goalPad=mesh(new THREE.CylinderGeometry(.59,.59,goal.h,64),dark);goalPad.position.set(goal.x,goal.h/2,goal.z);

function cylinderBetween(a,b,r,material=metal,parent=details){
  const diff=new THREE.Vector3().subVectors(b,a);
  const m=mesh(new THREE.CylinderGeometry(r,r,diff.length(),8),material,parent);
  m.position.copy(a).add(b).multiplyScalar(.5);m.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),diff.normalize());return m;
}
for(const b of bridges){
  const dx=b.b.x-b.a.x,dz=b.b.z-b.a.z,length=Math.hypot(dx,dz),slope=b.h1-b.h0;
  const bridge=mesh(new THREE.BoxGeometry(b.width,.105,Math.hypot(length,slope)),bridgeMat);
  bridge.position.set((b.a.x+b.b.x)/2,(b.h0+b.h1)/2-.058,(b.a.z+b.b.z)/2);
  bridge.quaternion.setFromUnitVectors(new THREE.Vector3(0,0,1),new THREE.Vector3(dx,slope,dz).normalize());
  for(const sign of [-1,1]){
    const ox=-dz/length*b.width/2*sign,oz=dx/length*b.width/2*sign;
    cylinderBetween(new THREE.Vector3(b.a.x+ox,b.h0+.008,b.a.z+oz),new THREE.Vector3(b.b.x+ox,b.h1+.008,b.b.z+oz),.022,railMat);
  }
  for(const t of [.18,.82]){
    const h=b.h0+slope*t;
    const post=mesh(new THREE.CylinderGeometry(.035,.048,h-.07,10),metal);post.position.set(b.a.x+dx*t,h/2-.035,b.a.z+dz*t);
  }
}
// A gently lit dotted route makes the intended path readable without replacing the letter faces.
const dotGeo=new THREE.CircleGeometry(.025,12);
const dotMat=new THREE.MeshBasicMaterial({color:'#bb4140',transparent:true,opacity:.6,side:THREE.DoubleSide});
let routeDistance=0;
for(let i=1;i<route.length;i++){
  const a=route[i-1],b=route[i],len=Math.hypot(b.x-a.x,b.z-a.z);
  for(let d=.08;d<len;d+=.22){
    const t=d/len,x=a.x+(b.x-a.x)*t,z=a.z+(b.z-a.z)*t,h=surfaceAt(x,z).h;
    if(!Number.isFinite(h))continue;
    const dot=mesh(dotGeo,dotMat);dot.rotation.x=-Math.PI/2;dot.position.set(x,h+.012,z);dot.castShadow=false;
  }
  routeDistance+=len;
}
function ring(x,z,r,y,material=red,tube=.018){const m=mesh(new THREE.TorusGeometry(r,tube,8,64),material);m.rotation.x=-Math.PI/2;m.position.set(x,y,z);return m;}
ring(start.x,start.z,.49,start.h+.012,metal,.012);
const markers=checkpoints.map((p,i)=>{
  const group=new THREE.Group();details.add(group);
  const torus=mesh(new THREE.TorusGeometry(.29,.022,10,48),red,group);torus.rotation.x=-Math.PI/2;torus.position.set(p.x,TOP+.027,p.z);
  if(p.save){
    const base=mesh(new THREE.CylinderGeometry(.082,.082,.022,24),dark,group);base.position.set(p.x,TOP+.02,p.z);
    ring(p.x,p.z,.38,TOP+.008,new THREE.MeshBasicMaterial({color:'#b1b9ab'}),.008);
  }
  return {group,torus};
});
const goalRings=[.23,.42,.56].map((r,i)=>ring(goal.x,goal.z,r,goal.h+.018,mat('#fff7eb',{emissive:'#efc7a7',emissiveIntensity:.25}),.013));
const goalPin=mesh(new THREE.CylinderGeometry(.06,.06,.012,24),white);goalPin.position.set(goal.x,goal.h+.017,goal.z);

function label(text,x,z,width,color='#ffc0b8'){
  const canvas=document.createElement('canvas');canvas.width=1024;canvas.height=80;
  const ctx=canvas.getContext('2d');ctx.fillStyle=color;ctx.font='500 28px Arial';ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(text,512,40);
  const tex=new THREE.CanvasTexture(canvas);tex.colorSpace=THREE.SRGBColorSpace;
  const m=mesh(new THREE.PlaneGeometry(width,width*80/1024),new THREE.MeshBasicMaterial({map:tex,transparent:true,depthWrite:false}),extras);
  m.rotation.x=-Math.PI/2;m.position.set(x,.015,z);m.castShadow=false;
}
label('01 / START',-7.7,2.68,2.1);label('A P P S O   /   P L A Y   L A B',0,2.94,4);label('05 / HOME',6.6,2.68,2.1);
for(const x of [-10.02,10.02])for(const z of [-3.12,3.12]){
  const screw=mesh(new THREE.CylinderGeometry(.054,.054,.012,16),mat('#cc3333',{metalness:.65}),extras);screw.position.set(x,.005,z);
  const slit=mesh(new THREE.BoxGeometry(.052,.008,.012),mat('#912c2d'),extras);slit.position.set(x,.014,z);slit.rotation.y=.5;
}
const ball=mesh(new THREE.SphereGeometry(1,48,32),mat('#fffefa',{roughness:.18,metalness:.12}),root);
const seam=mesh(new THREE.TorusGeometry(.996,.013,8,64),mat('#d4d5cc',{roughness:.4}),ball);seam.rotation.y=.7;
// A soft contact ellipse anchors the small marble even in the wide camera.
const shadowCanvas=document.createElement('canvas');shadowCanvas.width=shadowCanvas.height=64;
const sc=shadowCanvas.getContext('2d'),grad=sc.createRadialGradient(32,32,1,32,32,32);
grad.addColorStop(0,'rgba(30,20,20,.32)');grad.addColorStop(1,'rgba(30,20,20,0)');sc.fillStyle=grad;sc.fillRect(0,0,64,64);
const ballShadow=mesh(new THREE.PlaneGeometry(.85,.85),new THREE.MeshBasicMaterial({map:new THREE.CanvasTexture(shadowCanvas),transparent:true,depthWrite:false}),root);ballShadow.rotation.x=-Math.PI/2;ballShadow.castShadow=false;
const obstacleMeshes=[];
for(const o of obstaclesAt(0)){
  let m;
  if(o.type==='bar'){
    m=new THREE.Group();details.add(m);
    const bar=mesh(new THREE.CapsuleGeometry(o.r,.52,6,12),red,m);bar.rotation.z=Math.PI/2;
    const bolt=mesh(new THREE.CylinderGeometry(.068,.068,.19,20),metal,m);bolt.position.y=-.01;
  }else{
    m=mesh(new THREE.CylinderGeometry(o.r,o.r+.025,.19,32),red);
    const cap=mesh(new THREE.CylinderGeometry(o.r*.5,o.r*.5,.012,24),white,m);cap.position.y=.10;
  }
  obstacleMeshes.push(m);
}
// Quiet mechanical trim around the P windows adds depth without changing the supplied silhouette.
for(const l of letters.filter(l=>l.name.startsWith('P'))){
  const hole=l.holes[0];
  const points=hole.map(p=>new THREE.Vector3(p.x,TOP-.16,p.z));points.push(points[0]);
  const line=new THREE.Line(new THREE.BufferGeometry().setFromPoints(points),new THREE.LineBasicMaterial({color:'#a1a49c',transparent:true,opacity:.6}));details.add(line);
}

let audioContext,muted=false,lastTone=0;
try{muted=localStorage.getItem('appso-muted')==='true';}catch{}
function unlockAudio(){if(!audioContext)audioContext=new(window.AudioContext||window.webkitAudioContext)();audioContext.resume().catch(()=>{});}
function tone(freq=440,duration=.1,volume=.035,type='sine',delay=0){
  if(muted||!audioContext||audioContext.state!=='running')return;
  const t=audioContext.currentTime+delay,osc=audioContext.createOscillator(),gain=audioContext.createGain();
  osc.type=type;osc.frequency.setValueAtTime(freq,t);osc.frequency.exponentialRampToValueAtTime(freq*.8,t+duration);
  gain.gain.setValueAtTime(0,t);gain.gain.linearRampToValueAtTime(volume,t+.008);gain.gain.exponentialRampToValueAtTime(.001,t+duration);
  osc.connect(gain);gain.connect(audioContext.destination);osc.start(t);osc.stop(t+duration+.01);
}
let toastTimeout;
function toast(text){$('#toast').textContent=text;$('#toast').classList.add('visible');clearTimeout(toastTimeout);toastTimeout=setTimeout(()=>$('#toast').classList.remove('visible'),2400);}
let mode='intro',introTime=0,paused=false,topView=false,winTime=0,landPulse=0,lastCollisionTime=-10;
let idleTime=0;
const physics=new Physics((event,payload)=>{
  if(event==='checkpoint'){
    tone(660,.15);tone(880,.2,.03,'sine',.12);
    toast(payload.save?'检查点已点亮 · 掉落后从这里继续':payload.index===1?'A 已通过 · 沿圆点进入第一个 P':'S 已通过 · 向 O 出发');
    updateProgress();
  }
  if(event==='fall'){tone(190,.28,.04,'triangle');toast('掉下去也没关系，马上回到检查点');landPulse=1;}
  if(event==='respawn'){tone(480,.12);updateProgress();}
  if(event==='collision'&&physics.time-lastCollisionTime>.16){tone(260,.06,.025,'triangle');lastCollisionTime=physics.time;landPulse=.45;}
  if(event==='land'){tone(150,.07,.028,'triangle');landPulse=.6;}
  if(event==='win')win();
});
const keys=new Set();
function updateSound(){icon($('#sound'),muted?'mute':'sound');$('#sound').setAttribute('aria-label',muted?'开启声音':'静音');$('#sound').title=muted?'开启声音 · M':'静音 · M';$('#sound').setAttribute('aria-pressed',String(muted));}
function toggleSound(){muted=!muted;try{localStorage.setItem('appso-muted',String(muted));}catch{}unlockAudio();updateSound();if(!muted)tone(600,.1);}
updateSound();
function startGame(){
  unlockAudio();
  introTime=5.5;mode='playing';paused=false;physics.reset();winTime=0;idleTime=0;
  document.body.classList.add('playing');document.body.classList.remove('won');
  $('#start').hidden=true;$('#progress').hidden=false;$('#win-card').hidden=true;$('#pause-overlay').hidden=true;
  $('#ball-label').style.opacity=0;$('#scene-label').textContent='PLAYGROUND / LIVE';
  icon($('#pause'),'pause');$('#pause').setAttribute('aria-label','暂停');
  keys.clear();updateProgress();tone(520,.15);renderer.domElement.focus({preventScroll:true});
}
function pauseGame(force){
  if(mode!=='playing')return;
  paused=force??!paused;keys.clear();$('#pause-overlay').hidden=!paused;
  icon($('#pause'),paused?'play':'pause');$('#pause').setAttribute('aria-label',paused?'继续':'暂停');
  if(paused)$('#resume').focus();else renderer.domElement.focus({preventScroll:true});
}
function updateProgress(){
  const titles=['A · 从小圆点出发','P · 绕过移动撞柱','P · 穿过旋转横杆','S · 慢一点，转个弯','O · 回到圆心'];
  const descriptions=['沿斜坡登上 A，跟着红色圆点向前。','白色字面是道路。空格刹车，让过小撞柱。','沿 P 绕过横杆，弧线尽头是第二个检查点。','顺着 S 绕到上方，透明桥连接最后的 O。','绕过 O，从左侧斜坡滚进圆心。'];
  $('#status-title').textContent=physics.won?'这座 Logo，已被你玩通。':titles[physics.stage];
  $('#status-detail').textContent=physics.won?'再看一眼，你刚刚滚过的整座乐园。':descriptions[physics.stage];
  document.querySelectorAll('[data-stage]').forEach(el=>{const i=Number(el.dataset.stage);el.classList.toggle('active',!physics.won&&i===physics.stage);el.classList.toggle('done',physics.won||i<physics.stage);});
  $('#falls').textContent=`${physics.falls} 次掉落`;
  markers.forEach((m,i)=>{m.torus.material=i<physics.stage?dark:red;});
}
const confetti=[];
function win(){
  mode='won';winTime=0;keys.clear();document.body.classList.remove('playing');document.body.classList.add('won');
  clearTimeout(toastTimeout);$('#toast').classList.remove('visible');
  $('#win-card').hidden=false;$('#win-stats').textContent=`用时 ${formatTime(physics.time)} · ${physics.falls} 次掉落 · 好奇心满分`;
  $('#scene-label').textContent='PLAYGROUND / COMPLETED';updateProgress();
  [523,659,784,1047].forEach((f,i)=>tone(f,.35,.035,'sine',i*.13));
  for(let i=0;i<100;i++){
    const m=mesh(new THREE.BoxGeometry(.07,.02,.14),i%3===0?red:i%3===1?white:metal,root);
    m.position.set(goal.x,1.1,goal.z);m.userData.v=new THREE.Vector3((Math.random()-.5)*5,3+Math.random()*4,(Math.random()-.5)*5);confetti.push(m);
  }
}
function restartGame(){for(const c of confetti){root.remove(c);c.geometry.dispose();}confetti.length=0;startGame();}
$('#start').addEventListener('click',startGame);$('#restart').addEventListener('click',restartGame);$('#again').addEventListener('click',restartGame);$('#pause-restart').addEventListener('click',restartGame);
$('#pause').addEventListener('click',()=>pauseGame());$('#resume').addEventListener('click',()=>pauseGame(false));$('#sound').addEventListener('click',toggleSound);
function toggleView(){topView=!topView;$('#view').textContent=topView?'↘ 回到立体':'↗ 俯视全景';}
$('#view').addEventListener('click',toggleView);
const controlCodes=['KeyW','KeyA','KeyS','KeyD','ArrowUp','ArrowDown','ArrowLeft','ArrowRight','Space'];
window.addEventListener('keydown',e=>{
  if(controlCodes.includes(e.code)&&mode==='playing'&&!paused){e.preventDefault();keys.add(e.code);}
  if(e.repeat)return;
  if(e.code==='Escape'||e.code==='KeyP')pauseGame();
  if(e.code==='KeyM')toggleSound();
  if(e.code==='KeyR')restartGame();
  if(e.code==='KeyV')toggleView();
  if(e.code==='Enter'&&mode==='intro')startGame();
});
window.addEventListener('keyup',e=>keys.delete(e.code));
window.addEventListener('blur',()=>{keys.clear();if(mode==='playing')pauseGame(true);});
document.addEventListener('visibilitychange',()=>{if(document.hidden&&mode==='playing')pauseGame(true);});
document.querySelectorAll('[data-key]').forEach(btn=>{
  btn.addEventListener('pointerdown',e=>{e.preventDefault();if(mode!=='playing'||paused)return;btn.setPointerCapture(e.pointerId);keys.add(btn.dataset.key);});
  for(const name of ['pointerup','pointercancel','lostpointercapture'])btn.addEventListener(name,()=>keys.delete(btn.dataset.key));
});
function getInput(){
  return {x:Number(keys.has('KeyD')||keys.has('ArrowRight'))-Number(keys.has('KeyA')||keys.has('ArrowLeft')),
    z:Number(keys.has('KeyS')||keys.has('ArrowDown'))-Number(keys.has('KeyW')||keys.has('ArrowUp')),brake:keys.has('Space')};
}
function formatTime(t){return `${String(Math.floor(t/60)).padStart(2,'0')}:${String(Math.floor(t%60)).padStart(2,'0')}`;}
const smooth=t=>{t=THREE.MathUtils.clamp(t,0,1);return t*t*(3-2*t);};
let cameraLift=0,cameraPan=0,cameraWidth=11.65,aspect=1;
function resize(){
  const rect=stage.getBoundingClientRect();aspect=rect.width/rect.height;renderer.setSize(rect.width,rect.height);
  camera.updateProjectionMatrix();
}
new ResizeObserver(resize).observe(stage);resize();
function updateCamera(dt){
  let lift=mode==='intro'?smooth((introTime-1.3)/3):1;
  if(topView)lift=0;
  cameraLift=THREE.MathUtils.damp(cameraLift,lift,3.5,dt);
  // Keep APPSO left-to-right on screen, so keyboard directions remain intuitive.
  const follow=aspect<1.6&&mode==='playing'&&!topView;
  const pan=follow?THREE.MathUtils.clamp(physics.ball.x,-5.8,5.8):0;
  cameraPan=THREE.MathUtils.damp(cameraPan,pan,3,dt);
  camera.position.set(cameraPan,22-cameraLift*6.5,.001+cameraLift*12.5);
  camera.lookAt(cameraPan,0,0);
  let halfW=Math.max(11.65,5.15*aspect);
  if(follow)halfW=4.9;
  if(mode==='won')halfW*=1+.055*smooth(winTime/2);
  cameraWidth=THREE.MathUtils.damp(cameraWidth,halfW,3,dt);halfW=cameraWidth;
  camera.left=-halfW;camera.right=halfW;camera.top=halfW/aspect;camera.bottom=-halfW/aspect;
  camera.updateProjectionMatrix();
}
let last=performance.now(),accumulator=0,frames=0,fpsStart=last,fps=0;
function frame(now){
  requestAnimationFrame(frame);
  const dt=Math.min((now-last)/1000,.05);last=now;
  frames++;if(now-fpsStart>1000){fps=Math.round(frames*1000/(now-fpsStart));frames=0;fpsStart=now;}
  if(!paused){
    if(mode==='intro')introTime+=dt;
    if(mode==='playing'){
      accumulator+=dt;
      while(accumulator>=1/120){physics.step(1/120,getInput());accumulator-=1/120;}
      idleTime+=dt;
    }else accumulator=0;
    if(mode==='won')winTime+=dt;
    landPulse=Math.max(0,landPulse-dt*3);
  }
  const rise=mode==='intro'?smooth((introTime-1.2)/2.5):1;
  board.material=rise<.03?flatRed:red;
  letterGroup.children.forEach(m=>{m.material=rise<.03?flatWhite:[white,side];});
  if(mode==='intro')ball.material=rise<.03?flatWhite:white;
  letterGroup.scale.y=Math.max(.003,rise);
  details.scale.y=Math.max(.003,rise);details.visible=rise>.12;
  extras.visible=rise>.02;
  if(mode==='intro'){
    const morph=smooth((introTime-2.3)/1.5),r=THREE.MathUtils.lerp(.68,RADIUS,morph);
    ball.position.set(start.x,THREE.MathUtils.lerp(.006,start.h+RADIUS,morph),start.z);
    ball.scale.set(r,THREE.MathUtils.lerp(.003,RADIUS,morph),r);seam.visible=morph>.8;
    $('#start span:first-child').textContent=introTime<4.5?'跳过开场，开始玩':'开始冒险';
    $('#ball-label').style.opacity=introTime>4.5?'1':'0';
  }else{
    const b=physics.ball;ball.position.set(b.x,b.y,b.z);
    if(mode==='won')ball.position.lerp(new THREE.Vector3(goal.x,goal.h+RADIUS,goal.z),smooth(winTime));
    const squash=landPulse*.17;ball.scale.set(RADIUS*(1+squash*.5),RADIUS*(1-squash),RADIUS*(1+squash*.5));
    if(!paused&&physics.respawnDelay<=0){
      const rotation=new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(b.vz,0,-b.vx).normalize(),Math.hypot(b.vx,b.vz)*dt/RADIUS);
      if(Math.hypot(b.vx,b.vz)>.001)ball.quaternion.premultiply(rotation);
    }
    ball.visible=physics.respawnDelay<=0||Math.floor(now/85)%2===0;
    seam.visible=true;
  }
  const sh=surfaceAt(ball.position.x,ball.position.z).h;
  ballShadow.position.set(ball.position.x,Math.max(.02,Number.isFinite(sh)?sh+.012:.02),ball.position.z);
  ballShadow.visible=rise>.5;ballShadow.material.opacity=Math.max(.15,1-(ball.position.y-(Number.isFinite(sh)?sh:0))*.4);
  const obs=obstaclesAt(mode==='intro'?0:physics.time);
  obstacleMeshes.forEach((m,i)=>{m.position.set(obs[i].x,TOP+.11,obs[i].z);if(obs[i].type==='bar')m.rotation.y=-physics.time*.95;});
  markers.forEach((m,i)=>{if(i===physics.stage&&mode==='playing')m.torus.scale.setScalar(1+Math.sin(physics.time*3)*.045);else m.torus.scale.setScalar(1);});
  if(!paused)for(const c of confetti){
    c.userData.v.y-=4*dt;c.position.addScaledVector(c.userData.v,dt);c.rotation.x+=dt*2;c.rotation.z+=dt*3;
    if(c.position.y<.04){c.position.y=.04;c.userData.v.set(0,0,0);}
  }
  updateCamera(dt);
  $('#timer').textContent=formatTime(physics.time);
  const projected=new THREE.Vector3(start.x,start.h+RADIUS+.25,start.z).project(camera),rect=stage.getBoundingClientRect(),appRect=$('#app').getBoundingClientRect();
  $('#ball-label').style.left=`${rect.left-appRect.left+(projected.x+1)*rect.width/2-55}px`;
  $('#ball-label').style.top=`${rect.top-appRect.top+(1-projected.y)*rect.height/2-62}px`;
  renderer.render(scene,camera);
}
$('#loading').hidden=true;
requestAnimationFrame(frame);
// Read-only diagnostics are available to local tests. Mutation hooks exist only with ?test=1.
window.__APPSO__={snapshot:()=>({mode,paused,muted,topView,fps,stage:physics.stage,falls:physics.falls,time:physics.time,won:physics.won,collisions:physics.collisions,landings:physics.landings,saved:{...physics.saved},ball:{...physics.ball},introTime,letterRise:letterGroup.scale.y,renderer:renderer.info.render}),route,checkpoints};
if(new URLSearchParams(location.search).has('test'))Object.assign(window.__APPSO__,{
  setBall:state=>Object.assign(physics.ball,state),
  simulate:(steps,input)=>{for(let i=0;i<steps;i++)physics.step(1/120,input);},
  surfaceAt,
});
