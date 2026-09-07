from pathlib import Path
import hashlib
import json
from PIL import Image

root = Path(__file__).resolve().parents[1]
path = root / 'assets/figma-make-kits.png'
with Image.open(path) as im:
    im.verify()
with Image.open(path) as im:
    size = im.size
receipt = dict(file='assets/figma-make-kits.png', width=size[0], height=size[1],
               bytes=path.stat().st_size, sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
               source_url='https://www.figma.com/blog/introducing-make-kits-and-make-attachments/',
               original_url='https://cdn.sanity.io/images/599r6htc/regionalized/c1de4013e89579987c5244b9b8f4946090ab5c41-1608x1206.png',
               accessed_on='2026-09-05', modified=False, rights_status='pending')
(root/'research/trend-image-receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps(receipt, ensure_ascii=False))

import yaml
import re
repo = root.parents[4]
manifest = root/'asset-manifest.yml'
manifest_text = manifest.read_text(encoding='utf-8')
manifest_text = re.sub(r'(\n    notes: [^\n]*)\n      (research/feishu-gif-receipt\.json。)', r'\1 \2', manifest_text)
manifest.write_text(manifest_text, encoding='utf-8')
for file in [repo/'共享/运营/复盘/SOP 变更台账.yml', root/'asset-manifest.yml']:
    yaml.safe_load(file.read_text(encoding='utf-8'))
log_bytes = (root/'research/final-validation.log').read_bytes()
log = log_bytes.decode('utf-16' if log_bytes.startswith((b'\xff\xfe', b'\xfe\xff')) else 'utf-8-sig')
print(json.dumps(dict(yaml_valid=True, warnings=log.count('[warn]'),
                     errors=[line for line in log.splitlines() if '[error]' in line.lower() or '[fail]' in line.lower()])))
