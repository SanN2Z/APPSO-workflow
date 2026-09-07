// Offline regression. Uses Node built-ins and an installed Chrome; no account access.
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const vm = require('node:vm');
const {execFileSync} = require('node:child_process');
const {pathToFileURL} = require('node:url');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '..');
const version = process.argv[2] || '1.10.1';
if (!['1.10.1','1.10.2','1.10.3'].includes(version)) throw Error('Unknown candidate version');
const ext = path.join(root, 'v'+version, 'extension');
const output = path.join(root, 'tests', 'artifacts', version);
fs.mkdirSync(output, {recursive:true});
const chrome = [process.env.CHROME_PATH,
  path.join(process.env.LOCALAPPDATA || '', 'Google/Chrome/Application/chrome.exe'),
  path.join(process.env.PROGRAMFILES || '', 'Google/Chrome/Application/chrome.exe')
].find(p => p && fs.existsSync(p));
if (!chrome) throw Error('Chrome missing; set CHROME_PATH to the installed browser.');
const reader = fs.readFileSync(path.join(ext, 'feishu-page-reader.js'), 'utf8');
const original = fs.readFileSync(path.join(root, 'v1.10.0/extension/feishu-page-reader.js'), 'utf8');
const adapter = fs.readFileSync(path.join(ext, 'editor-adapter.js'), 'utf8');
const image = 'data:image/gif;base64,'+fs.readFileSync(path.join(ext, 'assets/appso-title.gif')).toString('base64');
const sample = {title:'独立段落编辑测试', titleImage:{dataUri:image,mime:'image/gif',brand:'appso'},
  blocks:[{type:'text',order:1,text:'正文左右各缩进 16 像素。'},
    {type:'heading1',order:2,text:'独立的小标题'},
    {type:'quote',order:3,text:'引用保留原有边线。'},
    {type:'bullet',order:4,text:'列表项目'},
    {type:'image',order:5,image:{dataUri:image,mime:'image/gif'}},
    {type:'image',order:6,image:{dataUri:image,mime:'image/gif'}}]};
const render = (source,input=sample) => {const ctx={Blob};vm.createContext(ctx);vm.runInContext(source,ctx);return ctx.IFANR_FEISHU_PAGE_READER.buildFixture(input);};
const before = render(original), after = render(reader);
if(before.galleryCount!==after.galleryCount || before.imageCount!==after.imageCount || before.summary!==after.summary) throw Error('Content regression');
// Private functions exposed only in this isolated test document.
const instrumented = adapter.replace('global.WechatEditorAdapter = {',
 'global.testStaging = {stageAnimatedImages, insertStagedImage, imageOrderConfirmed, restoreAnimatedHostingPlaceholder}; global.WechatEditorAdapter = {');
const edgeSample={...sample,blocks:[
 {type:'text',order:1,text:'正文示例'}, {type:'image',order:2,image:{dataUri:image,mime:'image/gif'}},
 {type:'text',order:3,text:'正文单图仍缩进'}, {type:'image',order:4,image:{dataUri:image,mime:'image/gif'}}]};
const manualEdges=render(reader,edgeSample).html;
const markedTail=render(reader,{...edgeSample,tailImageMode:'last-source-image'}).html;
const html = `<!doctype html><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="img-src data:"><title>头图与正文独立编辑验证</title>
<style>body{font:16px sans-serif;background:#f3f3f3;margin:24px}main{display:flex;gap:24px}.pane{width:390px;background:white;padding:12px}.editor{width:390px;min-height:400px}h2{font-size:20px}#report{white-space:pre-wrap}</style>
<h1>头图 0 缩进 · 正文 16 像素</h1><main><div class="pane"><h2>旧版：缩进在段落外层</h2><div id="before" class="editor">${before.html}</div></div>
<div class="pane"><h2>修正版：可单独编辑</h2><div id="after" class="editor" contenteditable="true">${after.html}</div></div></main><pre id="report">RUNNING</pre>
<script>${instrumented}</script><script>
const fixture=${JSON.stringify(after.html)};
const checks=[]; function check(ok,name){if(!ok)throw Error(name);checks.push(name);}
try {
 const editor=document.querySelector('#after');
 const title=editor.querySelector('[data-ifanr-title-image]');
 const body=editor.querySelector('[data-ifanr-block="paragraph"]');
 check(title.tagName==='P'&&body.tagName==='P','头图和正文是独立段落');
 check(getComputedStyle(title).marginLeft==='0px'&&getComputedStyle(body).marginLeft==='16px','初始 0 / 16 缩进');
 const origin=body.getBoundingClientRect().left;
 body.style.marginLeft=body.style.marginRight='0px';
 check(Math.abs(origin-body.getBoundingClientRect().left-16)<0.5,'修改正文段落为 0 能移除全部左右缩进');
 check(getComputedStyle(title).marginLeft==='0px','正文调整不影响头图');
 body.style.marginLeft=body.style.marginRight='16px';
 check(editor.querySelectorAll('[data-ifanr-block="gallery"]').length===1,'连续正文图片仍分组，头图不进图库');
 for(const manual of [false,true]) {
  editor.innerHTML=fixture;
  const staged=testStaging.stageAnimatedImages(fixture,manual?[{order:1,name:'test.gif'}]:[]);
  editor.innerHTML=staged.html;
  let target=editor.querySelector('[data-ifanr-title-image]');
  if(!manual) {
   const anchor=target.querySelector('[data-ifanr-gif-placeholder]');
   check(testStaging.restoreAnimatedHostingPlaceholder(editor,staged.animatedImages[0],anchor),'上传失败回到头图原段落');
  }
  check(!target.querySelector('section,figure,p'),'补图占位不增加嵌套块');
  check([...target.querySelectorAll('*')].every(n=>getComputedStyle(n).paddingLeft==='0px'&&getComputedStyle(n).marginLeft==='0px'),'补图标记无左右内边距');
  editor.focus();const range=document.createRange();range.selectNodeContents(target);
  const selection=getSelection();selection.removeAllRanges();selection.addRange(range);
  check(document.execCommand('insertHTML',false,'<img src="'+${JSON.stringify(image)}+'" style="display:block;width:100%;height:auto;">'),'模拟选中标记后粘贴图片');
  target=editor.querySelector('[data-ifanr-title-image]');
  check(target.querySelectorAll('img').length===1,'手动补图保留在独立头图段落');
  check(Math.abs(target.getBoundingClientRect().width-390)<0.5,'补图容器全宽');
  check(getComputedStyle(editor.querySelector('[data-ifanr-block="paragraph"]')).marginLeft==='16px','补图后正文仍缩进 16');
  editor.innerHTML=WechatEditorAdapter.sanitizeArticleHtml(editor.innerHTML);
  check(editor.querySelector('[data-ifanr-title-image]').tagName==='P','清理与重新解析后结构保留');
 }
 if (${JSON.stringify(version)}==='1.10.3') {
  editor.innerHTML=${JSON.stringify(manualEdges)};
  const originX=editor.getBoundingClientRect().left;
  const bodyImages=[...editor.querySelectorAll('p[data-ifanr-block="image"]')].filter(n=>!n.hasAttribute('data-ifanr-title-image'));
  check(bodyImages.length===2&&bodyImages.every(n=>Math.abs(n.getBoundingClientRect().left-originX-16)<0.5&&Math.abs(n.getBoundingClientRect().width-358)<0.5),'所有正文单图左右均为 16');
  check(!editor.querySelector('[data-ifanr-tail-image]'),'默认不把正文末图猜成尾图');
  const slot=editor.querySelector('[data-ifanr-tail-slot]');
  check(slot&&slot.tagName==='P'&&Math.abs(slot.getBoundingClientRect().width-390)<0.5,'手动尾图有通栏段落');
  slot.innerHTML='<img style="width:100%;height:20px" src="'+${JSON.stringify(image)}+'">';
  check(Math.abs(slot.querySelector('img').getBoundingClientRect().width-390)<0.5,'手动插入尾图保持通栏');
  editor.innerHTML=${JSON.stringify(markedTail)};
  const tail=editor.querySelector('[data-ifanr-tail-image]');
  check(tail&&Math.abs(tail.getBoundingClientRect().width-390)<0.5,'明确指定的原稿末图通栏');
  check(!tail.closest('[data-ifanr-block="gallery"]'),'尾图不混入正文图库');
  editor.innerHTML=fixture;
  const gallery=editor.querySelector('[data-ifanr-block="gallery"]');
  check(Math.abs(gallery.getBoundingClientRect().left-originX-16)<0.5&&Math.abs(gallery.getBoundingClientRect().width-358)<0.5,'图库视窗左右均为 16');
  const staged=testStaging.stageAnimatedImages(fixture);editor.innerHTML=staged.html;
  let pastedFile=null;
  const onPaste=e=>{pastedFile=e.clipboardData.files[0];e.preventDefault();document.execCommand('insertHTML',false,staged.animatedImages[0].html);};
  editor.addEventListener('paste',onPaste);
  const insertion=testStaging.insertStagedImage(editor,staged.animatedImages[0]);editor.removeEventListener('paste',onPaste);
  check(insertion.filePasteAccepted&&pastedFile?.type==='image/gif'&&pastedFile.size===${fs.readFileSync(path.join(ext,'assets/appso-title.gif')).length},'文件粘贴收到原始 GIF 字节，保留动画格式');
  check(editor.querySelectorAll('[data-ifanr-title-image] img').length===1,'文件事件接受后不再补发 HTML，避免重复头图');
  editor.innerHTML=staged.html;
  const fallback=testStaging.insertStagedImage(editor,staged.animatedImages[0]);
  check(fallback.filePasteAttempted&&!fallback.filePasteAccepted&&fallback.method==='selection-insert-html','文件事件未接受时有明确 HTML 回退诊断');
  editor.innerHTML='';
  for(let order=2;order<=23;order++) {
   const p=document.createElement('p');p.dataset.ifanrImageOrder=order;
   const hosted=document.createElement('img');hosted.src='https://mmbiz.qpic.cn/fictional-'+order;hosted.style='width:100px;height:30px';
   Object.defineProperties(hosted,{complete:{value:true},naturalWidth:{value:100}});
   const hidden=document.createElement('img');hidden.src='https://mp.weixin.qq.com/hidden';hidden.style='display:none';p.append(hosted,hidden);editor.append(p);
  }
  const inspection=WechatEditorAdapter.inspectImages(editor);
  check(inspection.imageCount===44&&inspection.hostedImageCount===22&&inspection.pendingEmbeddedImageCount===0,'复现日志：44 个节点只算 22 张可见托管图');
  check(!testStaging.imageOrderConfirmed(inspection,1),'缺失头图不能因正文图足够而通过');
  const foreign=document.createElement('img');foreign.src='https://example.com/foreign';foreign.style='width:100px;height:30px';foreign.dataset.ifanrImageOrder='1';Object.defineProperties(foreign,{complete:{value:true},naturalWidth:{value:100}});editor.append(foreign);
  check(!testStaging.imageOrderConfirmed(WechatEditorAdapter.inspectImages(editor),1),'第三方图片地址不冒充微信托管');
 }
 editor.innerHTML=fixture;
 document.querySelector('#report').textContent='PASS '+checks.length+' checks\\n'+checks.join('\\n');
 document.body.dataset.result='pass';
}catch(e){document.querySelector('#report').textContent='FAIL '+e.stack;document.body.dataset.result='fail';}
</script>`;
const page = path.join(output,'paragraph-editability.html');fs.writeFileSync(page,html);
const profile = fs.mkdtempSync(path.join(os.tmpdir(),'ifanr-layout-check-'));
try {
 const dom=execFileSync(chrome,['--headless','--disable-gpu','--no-first-run','--no-default-browser-check',
  '--user-data-dir='+profile,'--allow-file-access-from-files','--virtual-time-budget=2500','--dump-dom',pathToFileURL(page).href],
  {encoding:'utf8',maxBuffer:32*1024*1024,timeout:30000,stdio:['ignore','pipe','pipe']});
 const report=dom.match(/<pre id="report">([\s\S]*?)<\/pre>/)?.[1]||'No browser report';
 fs.writeFileSync(path.join(output,'result.txt'),report+'\n');
 console.log(report);
 if(!dom.includes('data-result="pass"')) process.exitCode=1;
 if(!process.exitCode) {
  const files=fs.readdirSync(ext,{recursive:true}).map(f=>String(f).replaceAll('\\','/')).filter(f=>fs.statSync(path.join(ext,f)).isFile()).sort();
  const hash=bytes=>crypto.createHash('sha256').update(bytes).digest('hex').toUpperCase();
  const fingerprints=files.map(file=>({file,sha256:hash(fs.readFileSync(path.join(ext,file))),bytes:fs.statSync(path.join(ext,file)).size}));
  const tree=fingerprints.map(f=>f.file+'\t'+f.sha256+'\n').join('');
  const manifest=JSON.parse(fs.readFileSync(path.join(ext,'manifest.json'),'utf8'));
  const previous=JSON.parse(fs.readFileSync(path.join(root,'v1.10.0/extension/manifest.json'),'utf8'));
  for(const key of ['permissions','host_permissions','content_scripts','background','web_accessible_resources']) {
   if(JSON.stringify(manifest[key])!==JSON.stringify(previous[key])) throw Error('Unexpected manifest permission/runtime change: '+key);
  }
  const changed=files.filter(f=>!fs.existsSync(path.join(root,'v1.10.0/extension',f)) || !fs.readFileSync(path.join(ext,f)).equals(fs.readFileSync(path.join(root,'v1.10.0/extension',f))));
  const expected = version==='1.10.1' ? ['editor-adapter.js','feishu-page-reader.js','manifest.json']
    : ['content-script.js','editor-adapter.js','feishu-content-script.js','feishu-page-reader.js','manifest.json','page-connection.js','popup.html','popup.js','service-worker.js'];
  if(JSON.stringify(changed)!==JSON.stringify(expected)) throw Error('Unexpected modified files: '+changed);
  const audit={version:manifest.version,status:'local_test_candidate',file_count:files.length,total_bytes:fingerprints.reduce((n,f)=>n+f.bytes,0),
   manifest_sha256:hash(fs.readFileSync(path.join(ext,'manifest.json'))),tree_sha256:hash(tree),files:fingerprints,
   modified_from_1_10_0:changed,permissions_and_network_scope_unchanged:true,
   regression_checks:Number(report.match(/^PASS (\d+)/)?.[1]||0),real_wechat_roundtrip:'pending',cold_clone:'not_run',
   credential_review:'Changes reviewed: packaged script loading and layout, no credentials or new network hosts; connection status contains error codes, no page text.'};
  fs.writeFileSync(path.join(root,'v'+version,'local-validation.json'),JSON.stringify(audit,null,2)+'\n');
 }
}finally {fs.rmSync(profile,{recursive:true,force:true});}
