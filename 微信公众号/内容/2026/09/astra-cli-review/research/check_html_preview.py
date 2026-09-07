from pathlib import Path
import json
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[1]
dist = root/'dist'
url = (dist/'wechat-preview.html').as_uri()
results = []
with sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome',headless=True)
    page = browser.new_page(viewport={'width':1100,'height':950},device_scale_factor=1)
    page.route('http://**/*',lambda route:route.abort())
    page.route('https://**/*',lambda route:route.abort())
    page.goto(url,wait_until='load',timeout=60000)
    for width in [375,390]:
        page.locator(f'[data-width="{width}"]').click()
        page.wait_for_timeout(350)
        result = page.locator('#phone-preview').evaluate('''el => ({
            width: el.clientWidth, scrollWidth: el.scrollWidth,
            images: [...el.querySelectorAll('img')].map(i => ({alt:i.alt,loaded:i.complete&&i.naturalWidth>0,
                naturalWidth:i.naturalWidth,displayWidth:i.getBoundingClientRect().width,gif:i.src.startsWith('data:image/gif')})),
            editorCommentsVisible: el.innerText.includes('编辑待办') || el.innerText.includes('编辑状态')
        })''')
        result['requestedWidth'] = width
        assert result['scrollWidth'] <= result['width']+1, result
        assert all(i['loaded'] for i in result['images'])
        assert not result['editorCommentsVisible']
        results.append(result)
        page.locator('#phone-preview p').first.scroll_into_view_if_needed()
        page.screenshot(path=str(dist/f'preview-{width}-top.png'))
    image = page.locator('#phone-preview img').filter(has_not=page.locator('nonexistent'))
    gif = page.locator('#phone-preview img').nth(3)
    # Use the known Logo GIF alt instead of relying on display order.
    gif = page.locator('#phone-preview img[alt="Astra APPSO Logo 乐园的实际操作与掉落重生"]')
    gif.scroll_into_view_if_needed()
    a = gif.screenshot(path=str(dist/'preview-logo-gif-a.png'),animations='allow')
    page.wait_for_timeout(850)
    b = gif.screenshot(path=str(dist/'preview-logo-gif-b.png'),animations='allow')
    animation_changed = a != b
    page.locator('#phone-preview h2').last.scroll_into_view_if_needed()
    page.screenshot(path=str(dist/'preview-ending.png'))
    scroll=page.locator('.preview-vertical-scroll')
    assert scroll.count()==1, 'Expected the actual article long-image window'
    scroll.scroll_into_view_if_needed()
    before=scroll.screenshot(path=str(dist/'preview-scroll-top.png'))
    initial=scroll.evaluate('el=>({height:el.clientHeight,total:el.scrollHeight,top:el.scrollTop})')
    assert initial['total']>initial['height']+1, initial
    scroll.focus()
    page.keyboard.press('End')
    page.wait_for_timeout(400)
    final=scroll.evaluate('el=>({height:el.clientHeight,total:el.scrollHeight,top:el.scrollTop})')
    after=scroll.screenshot(path=str(dist/'preview-scroll-bottom.png'))
    assert final['top']>initial['top']+1 and before!=after, final
    scroll_check=dict(before=initial,after=final,keyboard_scroll_verified=True)
    assert page.locator('#phone-preview img[alt^="Astra 小妖快跑"]').count()==3
    assert page.locator('#phone-preview img[alt^="Fable 5.1 小妖快跑"]').count()==3
    page.locator('#phone-preview img[alt="Fable 5.1 小妖快跑的起点与场景细节"]').scroll_into_view_if_needed()
    page.screenshot(path=str(dist/'preview-fable-ghost-corrected.png'))
    for n,alt in enumerate(['APPSO 实测观察：Astra 与 Fable 5.1 的三道创作题',
                           'Greg Brockman 接受 TIME 的 AGI 专访', 'OpenAI 发布 Astra 的完整 X 原帖', 'Lydia Hallie 宣布再次重置 Claude Max 周额度的完整原帖',
                           'Paperweave 研究工作台的文献关系画布', 'Paperweave 将阅读问题和论文来源保存在研究笔记中'],1):
        info=page.locator(f'#phone-preview img[alt="{alt}"]')
        info.scroll_into_view_if_needed()
        info.screenshot(path=str(dist/f'preview-current-figure-{n}-mobile.png'))
    table=page.locator('#phone-preview table')
    assert table.count()==0
    benchmark=page.locator('#phone-preview img[alt="APPSO 跑分对照：OpenAI 发布页中的 Astra 与 Fable 5.1 六项成绩"]')
    assert benchmark.count()==1
    benchmark.scroll_into_view_if_needed()
    benchmark.screenshot(path=str(dist/'preview-benchmark-infographic-mobile.png'))
    browser.close()
record = dict(width_checks=results,logo_gif_screenshot_changed=animation_changed,scroll_check=scroll_check,external_requests='blocked during local check')
(dist/'preview-check.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'widths':[r['width'] for r in results],'images_loaded':len(results[0]['images']),
                  'gif_count':sum(i['gif'] for i in results[0]['images']),'logo_gif_changed':animation_changed},ensure_ascii=False))
