import { test, expect } from '@playwright/test';
import fs from 'node:fs';

const state=page=>page.evaluate(()=>window.__APPSO__.snapshot());
async function load(page){
  await page.goto('/?test=1');
  await page.waitForFunction(()=>window.__APPSO__);
}
async function start(page){await load(page);await page.locator('#start').click();}
async function drive(page,endIndex=100){
  return page.evaluate(endIndex=>{
    const api=window.__APPSO__;
    for(let i=1;i<Math.min(endIndex,api.route.length);i++){
      const target=api.route[i];let reached=false;
      for(let t=0;t<2400;t++){
        const s=api.snapshot(),b=s.ball;
        if(s.falls)return {ok:false,reason:'fall',i,state:s};
        if(s.won)return {ok:true,state:s};
        const dx=target.x-b.x,dz=target.z-b.z;
        if(Math.hypot(dx,dz)<.095){reached=true;break;}
        let x=dx*5.5-b.vx*3,z=dz*5.5-b.vz*3,l=Math.hypot(x,z);
        if(l>1){x/=l;z/=l;}
        api.simulate(1,{x,z,brake:false});
      }
      if(!reached)return {ok:false,reason:'stuck',i,state:api.snapshot()};
    }
    return {ok:true,state:api.snapshot()};
  },endIndex);
}

test('same-scene logo opening, skip, keyboard inertia, braking, pause and reset',async({page})=>{
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await load(page);
  expect((await state(page)).letterRise).toBeLessThan(.1);
  await page.screenshot({path:'artifacts/01-flat-logo.png'});
  await page.waitForFunction(()=>window.__APPSO__.snapshot().introTime>5);
  await page.screenshot({path:'artifacts/02-opening.png'});
  expect((await state(page)).letterRise).toBe(1);
  await page.locator('#start').click();
  const before=await state(page);
  await page.keyboard.down('ArrowRight');await page.waitForTimeout(230);await page.keyboard.up('ArrowRight');
  const moving=await state(page);expect(moving.ball.x).toBeGreaterThan(before.ball.x+.06);expect(moving.ball.vx).toBeGreaterThan(.5);
  await page.waitForTimeout(90);expect((await state(page)).ball.x).toBeGreaterThan(moving.ball.x);
  await page.keyboard.down('Space');await page.waitForTimeout(190);await page.keyboard.up('Space');
  expect(Math.abs((await state(page)).ball.vx)).toBeLessThan(.3);
  await page.keyboard.press('Escape');const paused=await state(page);await page.waitForTimeout(230);
  expect((await state(page)).time).toBe(paused.time);await expect(page.locator('#pause-overlay')).toBeVisible();
  await page.locator('#resume').click();expect((await state(page)).paused).toBe(false);
  await page.keyboard.press('m');expect((await state(page)).muted).toBe(true);
  await page.keyboard.press('m');expect((await state(page)).muted).toBe(false);
  await page.locator('#sound').click();await page.keyboard.down('w');await page.waitForTimeout(130);await page.keyboard.up('w');
  expect((await state(page)).ball.vz).toBeLessThan(0);await page.locator('#sound').click();
  await page.keyboard.press('v');expect((await state(page)).topView).toBe(true);
  await page.keyboard.press('v');
  await page.keyboard.press('r');const reset=await state(page);expect(reset.stage).toBe(0);expect(reset.falls).toBe(0);expect(reset.ball.x).toBeCloseTo(-7.7);
  // Every directional key enters the real keyboard handler.
  for(const key of ['w','s','a','d','ArrowUp','ArrowDown','ArrowLeft','ArrowRight']){
    await page.keyboard.press('r');const a=(await state(page)).ball;
    await page.keyboard.down(key);await page.waitForTimeout(130);await page.keyboard.up(key);const b=(await state(page)).ball;
    const axis=['a','d','ArrowLeft','ArrowRight'].includes(key)?'x':'z';
    expect(Math.abs(b[axis]-a[axis])).toBeGreaterThan(.012);
  }
  expect(errors).toEqual([]);
});

test('rolling off a real edge falls and respawns; high drop lands on a letter',async({page})=>{
  await start(page);
  await page.keyboard.down('ArrowLeft');
  await page.waitForFunction(()=>window.__APPSO__.snapshot().falls===1);
  await page.keyboard.up('ArrowLeft');
  await page.waitForTimeout(1100);
  const respawn=await state(page);expect(respawn.ball.x).toBeCloseTo(-7.7,1);expect(respawn.ball.grounded).toBe(true);
  await page.evaluate(()=>{window.__APPSO__.setBall({x:-3.96,z:-1.3,y:2.4,vx:0,vz:0,vy:0,grounded:false});window.__APPSO__.simulate(100,{x:0,z:0});});
  const land=await state(page);expect(land.landings).toBeGreaterThan(0);expect(land.ball.y).toBeCloseTo(1.045,2);expect(land.ball.grounded).toBe(true);
});

test('moving obstacle collision changes velocity, and goal cannot be won out of order',async({page})=>{
  await start(page);
  await page.evaluate(()=>{window.__APPSO__.setBall({x:-2.30,z:-.43,y:1.045,vx:2,vz:0,vy:0,grounded:true});window.__APPSO__.simulate(35,{x:0,z:0});});
  const s=await state(page);expect(s.collisions).toBeGreaterThan(0);expect(s.ball.vx).toBeLessThan(0);
  await page.evaluate(()=>{window.__APPSO__.setBall({x:6.6,z:0,y:.485,vx:0,vz:0,vy:0,grounded:true});window.__APPSO__.simulate(120,{x:0,z:0});});
  expect((await state(page)).won).toBe(false);
});

test('checkpoint survives an actual fall and preserves progress',async({page})=>{
  await start(page);
  const driven=await drive(page,18);expect(driven.ok,JSON.stringify(driven)).toBe(true);expect(driven.state.stage).toBe(2);
  await page.keyboard.down('Space');await page.waitForTimeout(1500);await page.keyboard.up('Space');
  await page.screenshot({path:'artifacts/03-gameplay.png'});
  await page.keyboard.down('ArrowDown');await page.waitForFunction(()=>window.__APPSO__.snapshot().falls>0);await page.keyboard.up('ArrowDown');
  await page.waitForTimeout(1100);
  const restored=await state(page);expect(restored.stage).toBe(2);expect(restored.ball.x).toBeCloseTo(restored.saved.x,1);expect(restored.ball.z).toBeCloseTo(restored.saved.z,1);
  await page.locator('#restart').click();expect((await state(page)).stage).toBe(0);expect((await state(page)).saved.x).toBe(-7.7);
});

test('complete connected course using physical acceleration, celebration and replay',async({page})=>{
  await start(page);const result=await drive(page);expect(result.ok,JSON.stringify(result)).toBe(true);expect(result.state.won).toBe(true);
  await expect(page.locator('#win-card')).toBeVisible();await page.waitForTimeout(2400);
  await page.screenshot({path:'artifacts/04-completion.png'});
  fs.writeFileSync('artifacts/course-result.json',JSON.stringify(result,null,2));
  await page.locator('#again').click();const s=await state(page);expect(s.mode).toBe('playing');expect(s.falls).toBe(0);expect(s.time).toBeLessThan(1);
});

test('mobile layout and touch control',async({page})=>{
  await page.setViewportSize({width:390,height:844});await start(page);
  const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);expect(overflow).toBe(false);
  const b=await state(page),button=page.locator('[data-key="ArrowRight"]');
  await button.dispatchEvent('pointerdown',{pointerId:1,pointerType:'touch'});await page.waitForTimeout(180);await button.dispatchEvent('pointerup',{pointerId:1,pointerType:'touch'});
  expect((await state(page)).ball.x).toBeGreaterThan(b.ball.x);
  await page.waitForTimeout(1600);
  await page.screenshot({path:'artifacts/05-mobile.png'});
});
