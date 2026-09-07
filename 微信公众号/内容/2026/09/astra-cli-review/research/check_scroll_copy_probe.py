"""Local rendering and clipboard serialization checks, not a WeChat backend test."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright

pkg=Path(__file__).resolve().parents[1]
results=[]
with sync_playwright() as p:
    browser=p.chromium.launch(channel='chrome',headless=True)
    page=browser.new_page(viewport={'width':800,'height':900})
    page.goto((pkg/'dist/scroll-copy-test.html').as_uri())
    image=page.locator('#component img')
    assert image.evaluate('i=>i.complete&&i.naturalWidth>0')
    for width in (375,390):
        page.locator('.preview').evaluate('(e,w)=>e.style.maxWidth=w+"px"',width)
        scroll=page.locator('#component > section > section')
        scroll.evaluate('e=>e.scrollTop=0')
        before=scroll.evaluate('e=>({height:e.clientHeight,total:e.scrollHeight})')
        assert before['height']==260 and before['total']-before['height']>100,before
        scroll.hover()
        page.mouse.wheel(0,520)
        page.wait_for_timeout(300)
        assert scroll.evaluate('e=>e.scrollTop')>100
        results.append({'width':width,**before,'wheel_scroll':True})
    # Exercise the real button handler with an in-memory ClipboardEvent.
    # This checks MIME data without replacing the user's OS clipboard.
    page.evaluate('''()=>{document.execCommand=(name)=>{
      const data=new DataTransfer();
      const event=new ClipboardEvent('copy',{clipboardData:data,cancelable:true});
      document.dispatchEvent(event);
      window.copied={html:data.getData('text/html'),text:data.getData('text/plain')};
      return event.defaultPrevented;
    };}''')
    page.locator('#copy-scroll').click()
    result=page.evaluate('''()=>{
      const d=new DOMParser().parseFromString(window.copied.html,'text/html');
      return {images:d.images.length,inline:[...d.images].every(i=>i.src.startsWith('data:image/')),
      sections:d.querySelectorAll('section').length,scripts:d.scripts.length,
      styles:[...d.querySelectorAll('section')].map(e=>e.getAttribute('style')),
      controls:d.querySelectorAll('button').length};
    }''')
    assert result['images']==1 and result['inline'] and result['sections']==3,result
    assert result['scripts']==result['controls']==0
    assert 'overflow-y:scroll' in result['styles'][1]
    assert '已复制完整组件' in page.locator('#status').inner_text()
    payload=page.evaluate('window.copied.html')
    receiver=browser.new_page(viewport={'width':390,'height':900})
    receiver.set_content('<main contenteditable="true" id="receiver"></main>')
    receiver.locator('#receiver').evaluate('(e,s)=>e.innerHTML=s',payload)
    receiver.locator('img').wait_for()
    receiver.wait_for_function('document.images[0].complete')
    loaded=receiver.locator('#receiver > section > section')
    assert loaded.evaluate('e=>e.scrollHeight>e.clientHeight+100')
    loaded.evaluate('e=>e.scrollTop=e.scrollHeight')
    assert loaded.evaluate('e=>e.scrollTop===e.scrollHeight-e.clientHeight')
    # A browser returning true without firing copy must not report success.
    page.evaluate('document.execCommand=()=>true')
    page.locator('#copy-scroll').click()
    assert '复制未成功' in page.locator('#status').inner_text()
    page.locator('#status').evaluate('e=>e.textContent=""')
    page.locator('#component > section > section').evaluate('e=>e.scrollTop=0')
    page.screenshot(path=str(pkg/'dist/scroll-copy-test-check.png'),full_page=True)
    browser.close()
report={'local_scroll':results,'clipboard_handler_simulated':result,'parsed_html_scroll':True,
        'copy_failure_not_reported_as_success':True,'os_clipboard_changed':False,
        'wechat_backend_roundtrip':'pending'}
(pkg/'research/scroll-copy-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
