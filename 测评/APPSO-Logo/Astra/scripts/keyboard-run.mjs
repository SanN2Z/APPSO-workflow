import { chromium } from '@playwright/test';
import fs from 'node:fs';
const browser=await chromium.launch({channel:'msedge',headless:true});
const page=await browser.newPage({viewport:{width:1440,height:1000}});
await page.goto('http://127.0.0.1:5174/');
await page.waitForFunction(()=>window.__APPSO__);
await page.locator('#start').click();
const result=await page.evaluate(()=>new Promise(resolve=>{
  const api=window.__APPSO__,held=new Set(),began=performance.now();let index=1;
  const emit=(code,down)=>window.dispatchEvent(new KeyboardEvent(down?'keydown':'keyup',{code,key:code.replace('Key','').toLowerCase(),bubbles:true,cancelable:true}));
  const release=()=>{for(const code of held)emit(code,false);held.clear();};
  const finish=result=>{clearInterval(timer);release();resolve(result);};
  const timer=setInterval(()=>{
    const s=api.snapshot(),b=s.ball;
    if(s.won)return finish({success:true,kind:'real-time keyboard events; no physics mutation hooks',state:s,wallSeconds:(performance.now()-began)/1000});
    if(s.falls||performance.now()-began>180000)return finish({success:false,index,state:s});
    const target=api.route[index],dx=target.x-b.x,dz=target.z-b.z,dist=Math.hypot(dx,dz);
    if(dist<.11&&index<api.route.length-1){index++;return;}
    const speed=Math.min(1.05,dist*3.2),vx=dx/Math.max(dist,.001)*speed,vz=dz/Math.max(dist,.001)*speed;
    const ex=vx-b.vx,ez=vz-b.vz;
    const next=new Set();
    if(ex>.11)next.add('KeyD');if(ex<-.11)next.add('KeyA');
    if(ez>.11)next.add('KeyS');if(ez<-.11)next.add('KeyW');
    for(const code of held)if(!next.has(code))emit(code,false);
    for(const code of next)if(!held.has(code))emit(code,true);
    held.clear();for(const code of next)held.add(code);
  },16);
}));
console.log(JSON.stringify(result,null,2));
fs.writeFileSync('artifacts/keyboard-result.json',JSON.stringify(result,null,2));
await page.waitForTimeout(2200);
await page.screenshot({path:result.success?'artifacts/06-keyboard-completion.png':'artifacts/keyboard-failure.png'});
await browser.close();
if(!result.success)process.exitCode=1;
