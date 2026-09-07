import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { startServer } from 'file:///D:/projects/AgentLab_Gpt/paperweave/server/index.js';
import { root } from 'file:///D:/projects/AgentLab_Gpt/paperweave/server/config.js';
import { seedDemo, freePort } from 'file:///D:/projects/AgentLab_Gpt/paperweave/test/fixtures.js';
import { chromium } from 'file:///D:/projects/AgentLab_Gpt/paperweave/node_modules/@playwright/test/index.mjs';

// Dedicated synthetic demo: never open the author's research database or CLI account.
const pkg=path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const out=path.join(pkg,'assets','user-results');
await fs.mkdir(out,{recursive:true});
const dir=await fs.mkdtemp(path.join(os.tmpdir(),'appso-paperweave-capture-'));
const app=await startServer({root,dataDir:dir,vault:path.join(dir,'vault'),terminalCwd:dir,agent:'shell',terminalShellArgs:['-NoLogo','-NoProfile'],terminalThemeFile:path.join(dir,'no-theme.json'),port:await freePort()});
const browser=await chromium.launch({headless:true,channel:'chrome'});
try {
  await seedDemo((n,a)=>app.store.call(n,a));
  const page=await browser.newPage({viewport:{width:1150,height:780},deviceScaleFactor:1.5});
  await page.goto(app.origin);
  await page.locator('.graph-node').first().waitFor();
  await page.getByRole('button',{name:'隐藏终端面板',exact:true}).click();
  await page.waitForTimeout(900);
  await page.screenshot({path:path.join(out,'paperweave-map.png')});
  const firstBox=await page.locator('.graph-node').nth(0).boundingBox();
  const secondBox=await page.locator('.graph-node').nth(1).boundingBox();
  const focus={x:Math.min(firstBox.x,secondBox.x)-15,y:Math.min(firstBox.y,secondBox.y)-15};
  focus.width=Math.max(firstBox.x+firstBox.width,secondBox.x+secondBox.width)-focus.x+15;
  focus.height=Math.max(firstBox.y+firstBox.height,secondBox.y+secondBox.height)-focus.y+15;
  await page.screenshot({path:path.join(out,'paperweave-map-focus.png'),clip:focus});
  const node=page.locator('.graph-node').first();
  const box=await node.boundingBox();
  await page.mouse.move(box.x+65,box.y+35);
  await page.mouse.down();
  await page.mouse.move(box.x+100,box.y+75,{steps:10});
  await page.mouse.up();
  await page.waitForTimeout(400);
  await page.screenshot({path:path.join(out,'paperweave-map-drag.png')});
  await page.getByRole('button',{name:'研究笔记',exact:true}).first().click();
  await page.waitForTimeout(500);
  await page.getByRole('button',{name:/为什么轻量模块能改变表征/}).first().click();
  await page.waitForTimeout(500);
  await page.screenshot({path:path.join(out,'paperweave-notes.png')});
  await page.screenshot({path:path.join(out,'paperweave-notes-focus.png'),clip:{x:260,y:255,width:685,height:440}});
  console.log(JSON.stringify({captured:['paperweave-map.png','paperweave-map-drag.png','paperweave-notes.png'],demo:'Existing seedDemo synthetic fixtures; no live research results or model run',viewport:'1150x780 @1.5'},null,2));
} finally { await browser.close(); await app.close(); }
