# 来源

证据截止：2026-07-20。

| 来源 | URL/路径 | 类型 | 访问日期 | 支持表述 | 备注 |
|---|---|---|---|---|---|
| Stats Perform：*Stats Perform FAQs – Opta Brand, Data & Products* | <https://www.statsperform.com/faqs/stats-perform-faqs-opta-brand-data-products/> | 公司官方资料 | 2026-07-20 | Opta 是 Stats Perform 旗下体育数据品牌；其数据服务于媒体、球队和转播机构等。 | 公司自述，仅用于身份介绍。 |
| Opta Analyst：*Who Will Win the 2026 FIFA World Cup? The Opta Supercomputer Predictions* | <https://theanalyst.com/articles/who-will-win-2026-fifa-world-cup-predictions-opta-supercomputer> | Opta 官方赛前预测 | 2026-07-20 | 2026-06-01 赛前模拟 25,000 次；西班牙、法国、英格兰、阿根廷夺冠率依次为 16.1%、13.0%、11.2%、10.4%；西班牙进八强 52.1%、进四强 39.0%、进决赛 25.6%。 | 属模型方自报；未公开足以独立复算的完整世界杯模型与长期校准记录。 |
| FIFA：*England's semi-final history* | <https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/articles/england-semi-final-history> | FIFA 官方赛事资料 | 2026-07-20 | 半决赛两组对阵为英格兰对阿根廷、法国对西班牙，即四队均进入实际四强。 | 只支持实际四强名单，不证明 Opta 模型质量。 |
| Opta Analyst：*Spain 1-0 Argentina Stats (aet)* | <https://theanalyst.com/articles/spain-vs-argentina-stats-2026-world-cup-final> | Opta 官方赛后数据 | 2026-07-20 | 西班牙加时 1 比 0 战胜阿根廷，赢得 2026 世界杯。 | 本稿只使用最终冠军事实，不展开比赛过程。 |
| Brier, 1950：*Verification of Forecasts Expressed in Terms of Probability* | <https://journals.ametsoc.org/doi/10.1175/1520-0493%281950%29078%3C0001%3AVOFEIT%3E2.0.CO%3B2> | 原始论文 | 2026-07-20 | 概率预测评分与 Brier score 的基础定义。 | 不同后续资料存在二元 `[0,1]` 与原始多分类 `[0,2]` 口径，跨来源不能直接混比。 |
| Gneiting & Raftery, 2007：*Strictly Proper Scoring Rules, Prediction, and Estimation* | <https://sites.stat.washington.edu/people/raftery/Research/PDF/Gneiting2007jasa.pdf> | 学术论文 | 2026-07-20 | 适当评分规则用于评价完整概率预测；Brier 与 log score 均属常见方法。 | 不把 Brier 写成唯一标准。 |
| scikit-learn：*Probability calibration* | <https://scikit-learn.org/stable/modules/calibration.html> | 官方技术文档 | 2026-07-20 | 校准的通俗定义：被赋予约 0.8 概率的一组样本中，约 80% 应实际发生。 | 文档讨论分类器，不是对 Opta 的实证评测；只用于解释校准概念。 |
