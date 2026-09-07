"""Collect public post metadata and unmodified media; no authentication."""
import concurrent.futures, hashlib, json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
IDS = {
    'astra-full-reset': '2096035437299237298',
    'astra-plus-business-live': '2096002992046796932',
    'berman-early-access': '2095595892464333065',
    'claude-reset': '2094856679250919746',
    'codex-reset': '2095651088502591861',
    'astra-allocation': '2095597659545591917',
    'astra-launch': '2095595741528125780',
    'skirano-3d': '2095595932335170031',
    'berman-simcity': '2095595893991129444',
}

def get(url):
    return urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=30).read()

def collect(item):
    label, tid = item
    data = json.loads(get(f'https://cdn.syndication.twimg.com/tweet-result?id={tid}&lang=en&token=1'))
    result = {k: data.get(k) for k in ['text', 'created_at', 'favorite_count', 'conversation_count', 'mediaDetails']}
    result.update(label=label, id=tid, author=data.get('user', {}).get('screen_name'), accessed_at=datetime.now(timezone.utc).isoformat())
    print(json.dumps({k:v for k,v in result.items() if k!='mediaDetails'}, ensure_ascii=False))
    for media in (data.get('mediaDetails') or []):
        url = media.get('media_url_https')
        if url and label in ['skirano-3d', 'berman-simcity']:
            raw = get(url)
            name = f'assets/{label}-video-preview.jpg'
            (ROOT/name).write_bytes(raw)
            result['download'] = dict(file=name, url=url, sha256=hashlib.sha256(raw).hexdigest())
            break
    return result

if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(collect, IDS.items()))
    (ROOT/'research/source-assets/goldweek-post-receipts.json').write_text(json.dumps(results, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
