'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const version=process.argv[2] || '1.10.2';
if (!['1.10.2','1.10.3'].includes(version)) throw Error('Unknown candidate version');
const ext=path.resolve(__dirname,'../v'+version+'/extension');
const source=file=>fs.readFileSync(path.join(ext,file),'utf8');
const WECHAT='https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit&action=edit';
const FEISHU='https://test.feishu.cn/wiki/fictional';
let checks=0;
async function test(name,fn){await fn();checks++;console.log('PASS '+name);}
function environment(kind='wechat',options={}) {
 const listeners=[],injections=[],sends=[];
 const url=options.url || (kind==='wechat'?WECHAT:FEISHU);
 const page={location:{href:url},URL,Blob,console,chrome:{runtime:{getManifest:()=>({version}),onMessage:{addListener:fn=>listeners.push(fn)}}}};
 vm.createContext(page);
 function run(file) {let code=source(file);if(file==='content-script.js')code=code.replace('startWechatPageMonitor();','/* monitor omitted only in offline unit test */');vm.runInContext(code,page,{filename:file});}
 const chrome={runtime:{getManifest:()=>({version})},tabs:{get:async()=>({id:7,url}),sendMessage:async(id,message,target)=>{
  sends.push({id,message,target});if(options.sendFail)throw Error('port closed');return options.emptyResponse?undefined:{ok:true};}},scripting:{executeScript:async opts=>{
  if(options.denied)throw Error('Cannot access contents of url');
  if(opts.files){injections.push(opts.files);assert.equal(opts.target.documentIds[0],'doc-1');if(options.injectFail)throw Error('blocked');for(const file of opts.files)run(file);return [{documentId:'doc-1'}];}
  if(options.nav && injections.length)page.location.href=WECHAT+'&appmsgid=changed';
  const result=vm.runInContext('('+opts.func.toString()+')('+JSON.stringify(opts.args[0])+')',page);
  return [{documentId:options.noDocument?undefined:'doc-1',result}];
 }}};
 const caller={chrome,URL};vm.createContext(caller);vm.runInContext(source('source-link.js'),caller);vm.runInContext(source('page-connection.js'),caller);
 return {api:caller.IFANR_PAGE_CONNECTION,page,listeners,injections,sends,run,url};
}
(async()=>{
 for(const kind of ['wechat','feishu']) {
  await test(kind+' missing receiver loads packaged scripts then sends once',async()=>{
   const e=environment(kind);await e.api.send(7,kind,{type:'test'},e.url);assert.equal(e.injections.length,1);assert.equal(e.listeners.length,1);assert.equal(e.sends.length,1);assert.equal(e.sends[0].target.documentId,'doc-1');
   await e.api.send(7,kind,{type:'test'},e.url);assert.equal(e.injections.length,1);assert.equal(e.sends.length,2);
  });
  await test(kind+' repeated script injection cannot duplicate listeners',async()=>{
   const e=environment(kind);await e.api.ensure(7,kind,e.url);const file=kind==='wechat'?'content-script.js':'feishu-content-script.js';e.run(file);e.run(file);assert.equal(e.listeners.length,1);
  });
 }
 for(const [name,opts,code] of [
  ['wrong page',{url:'https://example.com'},'PAGE_TARGET_INVALID'],
  ['permission denied',{denied:true},'PAGE_SCRIPT_ACCESS_DENIED'],
  ['injection denied',{injectFail:true},'PAGE_SCRIPT_LOAD_FAILED'],
  ['page navigated',{nav:true},'PAGE_RECEIVER_NOT_READY'],
  ['missing document identity',{noDocument:true},'PAGE_TARGET_CHANGED']]) {
  await test(name+' blocks action before dispatch',async()=>{
   const e=environment('wechat',opts);await assert.rejects(e.api.send(7,'wechat',{type:'test'}),err=>err.code===code&&err.beforeDispatch===true);assert.equal(e.sends.length,0);
  });
 }
 await test('expected URL mismatch cannot write a different draft',async()=>{
  const e=environment();await assert.rejects(e.api.send(7,'wechat',{},WECHAT+'&appmsgid=other'),err=>err.code==='PAGE_TARGET_CHANGED');assert.equal(e.injections.length,0);assert.equal(e.sends.length,0);
 });
 for(const opts of [{sendFail:true},{emptyResponse:true}]) await test('lost/empty action response never retries',async()=>{
  const e=environment('wechat',opts);await assert.rejects(e.api.send(7,'wechat',{}),err=>err.code==='PAGE_ACTION_CONNECTION_LOST'&&err.beforeDispatch===false);assert.equal(e.sends.length,1);assert.equal(e.injections.length,1);
 });
 // Exercise the actual popup action with only UI/browser boundaries stubbed.
 const popup=source('popup.js');const start=popup.indexOf('async function syncStoredPackageToWechat()');const end=popup.indexOf('\nfunction renderFeishuPage(',start);const fn=popup.slice(start,end);
 for(const beforeDispatch of [true,false]) await test('popup connection failure clears processing status: '+beforeDispatch,async()=>{
  const writes={},statuses=[];const ctx={console,Date,crypto:{randomUUID:()=> 'test-request'},
   activeTab:{id:7,url:WECHAT},storedPackage:{html:'<p>fictional</p>',imageCount:0,blockCount:1},WRITE_STATUS_KEY:'write',LAST_RESULT_KEY:'last',
   chrome:{tabs:{query:async()=>[{id:7,url:WECHAT}]},storage:{local:{set:async data=>Object.assign(writes,data),remove:async()=>{}}}},
   IFANR_PAGE_CONNECTION:{send:async()=>{throw Object.assign(Error('test connection failure'),{code:'TEST',beforeDispatch});}},
   queryWechatEditorTabs:async()=>[{id:7}],manualImageReplacementsForPackage:()=>[],packageOptions:()=>({}),
   setStatus:status=>statuses.push(status),setPrimary:()=>{},showCompileProgress:()=>{},hideCompileProgress:()=>{},showResult:()=>{},renderLastResult:()=>{}
  };vm.createContext(ctx);vm.runInContext(fn,ctx);await ctx.syncStoredPackageToWechat();
  assert.equal(ctx.actionRunning,false);assert.equal(writes.write.state,'failed');assert.equal(writes.last.beforeDispatch,beforeDispatch);assert.equal(statuses.at(-1).copy,'test connection failure');
 });
 console.log('PASS '+checks+' connection checks');
})().catch(error=>{console.error(error);process.exitCode=1;});
