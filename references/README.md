# references/ — 解读资料层溯源

> 解读层知识源：bazi / 紫微斗数两个经过时间验证的 skill 的参考资料**逐字节原样**拷入
> （2026-10-01），未裁剪未改写；七政解读册为本仓自建（七政无参照 skill）。
> 保持逐字节原样是为了将来上游更新时可整文件覆盖同步（cp + diff 即可审计）。
> 解读时先查对应文件，不靠模型记忆；排盘数字以 `scripts/` 引擎输出为准。

## 溯源表

| 文件 | 来源 | 说明 |
|------|------|------|
| `bazi/classical-texts.md` | bazi skill `references/classical-texts.md` | 九本典籍（穷通宝典/三命通会/滴天髓/渊海子平/千里命稿/协纪辨方书/子平真诠/神峰通考/果老星宗）核心论命规则摘要 |
| `bazi/wuxing-tables.md` | bazi skill `references/wuxing-tables.md` | 五行/天干地支/十神/藏干参考表（与八字引擎同口径） |
| `bazi/shichen-table.md` | bazi skill `references/shichen-table.md` | 时辰对照表、五鼠遁元日上起时 |
| `bazi/dayun-rules.md` | bazi skill `references/dayun-rules.md` | 大运顺逆排规则、起运年龄、流年分析规则 |
| `bazi/shensha-table.md` | bazi skill `references/shensha-table.md` | 神煞吉凶、查法与口诀（与八字引擎同口径） |
| `ziwei/classics.md` | ziwei-doushu skill `references/classics.md` | 《骨髓赋》《紫微斗数全书》《紫微斗数全集》条目原文（引用标注书名+章节） |
| `ziwei/patterns.md` | ziwei-doushu skill `references/patterns.md` | 41 格局全目录（含义/成立/加分/破格；由 ziwei vendor patterns.ts 自动提取） |
| `ziwei/sihua-tables.md` | ziwei-doushu skill `references/sihua-tables.md` | 十天干四化表 + 十四主星速查（与紫微引擎同口径） |
| `qizheng/reading.md` | **本仓自建** | 七政四余判读条目：十一曜五行、恩用难仇、度主、昼夜取重、安命法；每条带出处 |
| `domain-signals.md` | **本仓自建**（自 SKILL.md §13 迁入） | 四领域（感情/事业/财运/健康）× 三盘信号映射索引 |

## 引用密度约定（详见 SKILL.md 解读管线节）

- 轻引用管线（运势查询/推算/共鸣/知识）：每篇主判断挂 1-2 条最贴典籍依据
- 详批模式（fortune-full-reading）：每节全出处
