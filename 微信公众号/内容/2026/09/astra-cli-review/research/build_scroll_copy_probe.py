"""Build a local copy/paste diagnostic; this is not a release-cleared handoff."""
from pathlib import Path
import hashlib
import html
import importlib.util
import json
import re
import secrets
import sys

pkg = Path(__file__).resolve().parents[1]
repo = next(p for p in pkg.parents if (p / 'tools/workflow.ps1').is_file())
module_path = repo / '微信公众号/tools/wechat_publish.py'
spec = importlib.util.spec_from_file_location('scroll_probe_adapter', module_path)
adapter = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = adapter
spec.loader.exec_module(adapter)
draft = (pkg / 'draft.md').read_text(encoding='utf-8')
matches = re.findall(r'!\[(上下滑动：[^\]]+)\]\(([^)]+)\)', draft)
assert len(matches) == 1, 'Expected one explicit long-image marker in this case'
alt, source = matches[0]
source = adapter.canonical_package_relative_path(source, 'scroll probe', require_assets=True)
manifest = adapter.load_yaml(pkg / 'asset-manifest.yml')
assert any(a.get('file') == source for a in manifest['assets']), 'Image must be registered'
# Block flow avoids flex image shrinking. All styles and image bytes travel in HTML.
# This is a compatibility candidate, not a claim about WeChat's paste sanitizer.
fragment = adapter.vertical_scroll_fragment([source], height_px=260)
graph = adapter.prepare_inline_image_graph(fragment, pkg)
component = graph.rendered_fragment
out = pkg / 'dist'
out.mkdir(exist_ok=True)
nonce = secrets.token_urlsafe(18)
document = '''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src data:; style-src 'unsafe-inline'; script-src 'nonce-@NONCE@'; connect-src 'none'; object-src 'none'; base-uri 'none'">
<title>月屿长图 · 公众号试粘</title>
<style>body{margin:0;background:#f3f3f1;color:#222;font-family:Arial,'Microsoft YaHei',sans-serif;line-height:1.7}main{max-width:650px;padding:24px;margin:auto}h1{font-size:24px}button{border:0;border-radius:7px;background:#ff292d;color:white;padding:13px 22px;font-size:16px;cursor:pointer}.preview{max-width:390px;margin:24px auto;background:#fff;padding:16px}.note{font-size:13px;color:#666}#status{min-height:28px}</style></head>
<body><main><h1>月屿长图 · 公众号试粘</h1>
<p>点击按钮，将完整滑动框直接粘贴到公众号编辑器。不要只选图片复制，也不要经过飞书中转。</p>
<button id="copy-scroll">复制滑动框</button><p id="status" role="status"></p>
<div class="preview" id="component">@COMPONENT@</div>
<p class="note">本页是兼容性测试版。粘贴后保存草稿，在手机预览里试滑；本地能滑不能代替这一步。若图片正常但不能滑，需要检查公众号是否移除了滚动样式。</p>
</main><script nonce="@NONCE@">(function(){
const button=document.getElementById('copy-scroll'), component=document.getElementById('component'), status=document.getElementById('status');
button.addEventListener('click',()=>{
  let wrote=false;
  const copy=event=>{
    if(!event.clipboardData)return;
    event.clipboardData.setData('text/html',component.innerHTML);
    event.clipboardData.setData('text/plain','月屿完整网页（上下滑动）');
    event.preventDefault();wrote=true;
  };
  document.addEventListener('copy',copy);
  let result=false;
  try{result=document.execCommand('copy');}catch(error){}finally{document.removeEventListener('copy',copy);}
  status.textContent=result&&wrote?'已复制完整组件。请直接粘贴到公众号，再检查手机预览。':'复制未成功，请允许浏览器复制后重试。';
});
})();</script></body></html>'''.replace('@NONCE@', nonce).replace('@COMPONENT@', component)
(out / 'scroll-copy-test.html').write_text(document, encoding='utf-8')
(out / 'scroll-component-candidate.html').write_text(component, encoding='utf-8')
receipt = {
    'kind':'case_compatibility_probe_not_release_handoff',
    'source':source,
    'source_sha256':adapter.file_sha256(pkg / source),
    'component_sha256':hashlib.sha256(component.encode()).hexdigest(),
    'copy_bytes':len(component.encode()),
    'viewport_height_px':260,
    'previous_180px_version_user_feedback':'Copy/paste works; viewport too short',
    'wechat_backend_roundtrip':'pending',
    'draft_state_unchanged':True,
    'external_actions':'none',
}
(pkg / 'research/scroll-copy-probe.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt,ensure_ascii=False))
