import { chromium } from '@playwright/test';
const browser=await chromium.launch({channel:'msedge',headless:true});
const page=await browser.newPage({viewport:{width:1440,height:1000}});
await page.goto('http://127.0.0.1:5174/?test=1');
await page.waitForFunction(()=>window.__APPSO__);
await page.locator('#start').click();
const result=await page.evaluate(()=>{
  const api=window.__APPSO__, log=[];
  let total=0;
  for(let index=1;index<api.route.length;index++){
    const target=api.route[index];
    let reached=false;
    for(let t=0;t<2400;t++){
      const state=api.snapshot(), b=state.ball;
      if(state.falls>0)return {failed:'fall',index,target,state,log};
      if(state.won)return {success:true,state,log};
      const dx=target.x-b.x,dz=target.z-b.z;
      if(Math.hypot(dx,dz)<.095){reached=true;log.push({index,time:state.time,stage:state.stage});break;}
      // Feedback controller sends acceleration into the same fixed-step physics used by WASD.
      let x=dx*5.5-b.vx*3.0,z=dz*5.5-b.vz*3.0;
      const l=Math.hypot(x,z);if(l>1){x/=l;z/=l;}
      api.simulate(1,{x,z,brake:false});total++;
    }
    if(!reached)return {failed:'stuck',index,state:api.snapshot(),log};
  }
  api.simulate(180,{x:0,z:0,brake:true});
  return {success:api.snapshot().won,state:api.snapshot(),log,total};
});
console.log(JSON.stringify(result,null,2));
await page.waitForTimeout(2500);
await page.screenshot({path:result.success?'artifacts/04-completion.png':'artifacts/drive-failure.png'});
await browser.close();
