from pathlib import Path
import json,re,yaml
from PIL import Image
root=Path(__file__).resolve().parents[1]
draft=root/'draft.md'
old=draft.read_text(encoding='utf-8')
history=root/'research/history/2026-09-05-before-benchmark-ending.md'
if not history.exists():history.write_text(old,encoding='utf-8')
start=old.index('Cognition 已经把 Astra 接入 Devin。')
end=old.index('<!-- 编辑待办：',start)
replacement='''## 跑分里，两家的长处也不一样

回到跑分，OpenAI 发布页里的对比更具体。下面摘出六项，两边都用原表数字，均为越高越好。[OpenAI 官方数据](https://openai.com/index/gpt-6-astra/)

| 评测 | Astra | Fable 5.1 |
|---|---:|---:|
| 终端任务 · Terminal-Bench 4.0 | 57.9% | 55.8% |
| 软件工程 · DeepSWE v1.1 | 74.1% | 67.4% |
| 科研工作流 · Terminal-Bench Science 0.1 | 64.6% | 52.6% |
| 高难数学 · FrontierMath Tier 4（v2） | 97.6% | 87.8% |
| Humanity’s Last Exam（带工具） | 57.2% | 65.0% |
| AA 综合智能指数 v4.1.1 | 61.2 | 65.7 |

*截至 2026 年 9 月 5 日，摘录自 OpenAI 发布页。原页说明成绩取各推理强度下的最高值；研究环境与实际产品的工具、系统提示等可能不同。最后一行为指数分，不是百分比。*

这六项里，Astra 在终端、软件工程、科研工作流和高难数学上更高。Fable 5.1 则在带工具的 HLE 和 AA 综合智能指数上更高。

独立机构 Artificial Analysis 的原图也放在这里。上半张是综合智能指数，下半张是编程智能体指数。后者把模型放进实际编程工具里测：Astra 在 Codex 中得到约 67，Fable 5.1 在 Claude Code 中得到约 70。[Artificial Analysis 原文](https://artificialanalysis.ai/articles/benchmarking-gpt-6-astra)

![Artificial Analysis 发布的综合智能与编程智能体排名原图](assets/external/aa-astra-original-1.png)

*图源：Artificial Analysis，2026 年 9 月 3 日原图。综合指数为 v4.1.1，编程指数为 v1.4；图中分数取整，Fable 5.1 标有 max / with fallback。*

Cognition 的 FrontierCode 1.1 则把工程质量和代码能否合并纳入评分。在它的自有测试里，Astra 高于 Fable 5.1。[Cognition 测评](https://devin.ai/blog/gpt-6-astra)

我会把这几张成绩单分开看。具体工程题和综合知识题的排序不同，连编程评测也会受到运行工具的影响。这轮的游戏和网页，更多是在看成品是否合我的口味，以及操作能否跑通。

## 最高档，值不值得一直开

Artificial Analysis 还公布了同一套编程测试的费用。Astra 在 max 档位平均每个任务花费 4.72 美元；Fable 5.1 的 max（带回退）为 9.18 美元。后者分数更高，前者费用更低。[原始成本分析](https://artificialanalysis.ai/articles/benchmarking-gpt-6-astra)

![Artificial Analysis 编程智能体得分与单任务 API 成本原图](assets/external/aa-astra-original-3.png)

*图源：Artificial Analysis，2026 年 9 月 3 日。横轴为单任务 API 费用，纵轴为编程智能体指数；各点的模型、工具和推理档位见原图。*

更有意思的是 Astra 自己的档位差别。xhigh 的平均费用是 3.27 美元，max 是 4.72 美元，两者的指数都在 67 左右。这套测试里，多花的钱没有换来同样明显的分数提升。

这些是按 Token 计费的 API 测试费用，不能直接换算成 ChatGPT 或 Claude 订阅的额度。我们这轮也没有完整记录用量，所以不算谁更省订阅。

接下来再做活动页或小游戏，我会先用常规档位做初稿。遇到难修的问题，再提高推理强度。至于画面要不要重做，还是得自己点开玩一遍。

'''
draft.write_text(old[:start]+replacement+old[end:],encoding='utf-8')
receipt=json.loads((root/'research/benchmark-originals-receipt.json').read_text(encoding='utf-8'))
manifest=root/'asset-manifest.yml'
raw=manifest.read_text(encoding='utf-8')
known={a['file'] for a in yaml.safe_load(raw)['assets']}
for row in receipt:
    if row['file'] in known:continue
    with Image.open(root/row['file']) as im:im.verify()
    entry=dict(file=row['file'],used_in_draft=row['file'].endswith(('original-1.png','original-3.png')),
      visual_route='source_original',source_original_kind='official_original',original_pixels_preserved=True,
      source_type='official',source='Artificial Analysis 测评机构官网原图',source_url=row['source_url'],
      creator_or_rightsholder='Artificial Analysis',obtained_on='2026-09-05',modifications='CDN 原字节下载，无重绘、裁切或改字',
      rights_status='pending',allowed_platforms=[],attribution='图源：Artificial Analysis，2026 年 9 月 3 日',
      notes='原始文件 URL 和 SHA256 见 research/benchmark-originals-receipt.json；公开来源不等于已获转载许可。')
    raw+=''.join('  '+line+'\n' for line in yaml.safe_dump([entry],allow_unicode=True,sort_keys=False,width=100000).splitlines())
body=draft.read_text(encoding='utf-8')
def usage(match):
    block=match.group(0)
    file=re.search(r'file: (.+)',block).group(1).strip()
    return re.sub(r'used_in_draft: (true|false)','used_in_draft: '+str(f']({file})' in body).lower(),block)
manifest.write_text(re.sub(r'  - file:.*?(?=  - file:|\Z)',usage,raw,flags=re.S),encoding='utf-8')
print('Replaced benchmark section and ending; registered three original AA figures')
