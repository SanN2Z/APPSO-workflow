from pathlib import Path
import hashlib
import json

p=Path(__file__).resolve().parents[1]
records={
    'sources.md': '\n\n## FB032｜学习、复杂任务与 Paperweave\n\n新增引语采用[印度科学理工学院的 Hassabis 对谈实录](https://eecs.iisc.ac.in/fireside-chat-sir-demis-hassabis-and-prof-govindan-rangarajan/)，活动为 2026-02-17，谈学习方法而非 Astra。用户项目用独立演示实例截图。事实边界见 [核对记录](research/paperweave-learning-evidence.md)。\n',
    'retrospective.md': '\n\n## FB032｜新增不易展示的进步与学习角度\n\n2026-09-05，用户要求补充复杂执行、科学推理难以展示的观察，联系学习、专业判断和有价值的工作，并加入其 Paperweave 项目。原候选引用人按作者要求撤下，改用 Hassabis 公开对谈。保留前文，新增两张明确标注演示数据的实际界面图；不写模型归属、生成轮次或科研发现。末尾接到读论文和小实验。来源与边界见 research/paperweave-learning-evidence.md；case_only，不新增 SOP。\n',
    'research/co-writing-log.md': '\n\n## FB032｜作者确定的新增论点\n\n合同：漂亮作品容易展示，长任务与科研推理的进步需要深入使用体会；用作者工作台连接学习与有用的工作。用户要求更换原引用人，采用 Hassabis 公开学习建议。两幅实际截图为演示数据，不视为 Astra 直接实测结果。跑分图与前文保留，末尾两段调整为继续学习、实验并呼应额度。\n',
    'research/visual-notes.md': '\n\n## FB032｜Paperweave 配图\n\n画布图接工作台介绍，展示文献关系；笔记图接核对原文，展示问题与出处。两图均为独立演示实例的实际截图，保留原始像素并标注演示内容。拖动后的同类图留作交互核对，不在正文重复放。\n',
}
for name,entry in records.items():
    target=p/name
    if '\n## FB032｜' not in target.read_text(encoding='utf-8'):
        with target.open('a',encoding='utf-8',newline='\n') as f:f.write(entry)
rows=[{'file':f.relative_to(p).as_posix(),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size} for f in (p/'assets/user-results').glob('paperweave-*.png')]
(p/'research/paperweave-capture-receipt.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Registered {len(rows)} captures and case records')
