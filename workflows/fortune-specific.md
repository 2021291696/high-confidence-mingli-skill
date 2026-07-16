# Fortune-Specific — 推算查询 Workflow

> 由 SKILL.md §0 路由触发。处理具体问题的深度推演。
> 输入: question
> 数据: `~/.claude/fortune-telling/chart.md` + `~/.claude/fortune-telling/memory.md`

## Phase 1: 问题解构

1. **拆解子问题**: 将用户问题拆为可量化子问题
   - "姻缘怎么样" → ①盘面姻缘结构(SKILL.md §13 感情信号) ②大运推动(chart.md 大运表) ③流年引动(§6+§7) ④时间窗口
   - "该不该去X城市" → ①迁移宫+八字驿马信号 ②原局是否适合变动 ③当前时段变动能量 ④变动对核心矛盾的增强/削弱
   - "适合创业还是打工" → ①官禄宫结构 ②财帛宫模式 ③食伤配印程度 ④当前大运推力方向

2. **判断问题类型**: 确定权重配比
   - 结构性(命格50%/大运25%/流年15%/流月10%): 姻缘结构/事业方向/天赋
   - 时机性(命格20%/大运35%/流年30%/流月15%): 什么时候/该不该现在
   - 关系性(命格35%/大运20%/流年25%/流月20%): 和某人合不合/冲突判断
   - 方向选择型: 并入结构性，输出时展开方向对比表

输出: { sub_questions: [{ topic: string, aspects: string[] }], question_type: "结构性"|"时机性"|"关系性", weights: { mingGe: number, daYun: number, liuNian: number, liuYue: number } }

## Phase 2: 并行信号提取

有子 agent 工具时 parallel（无则顺序内联执行，schema 不变）。缺盘时跳过对应盘并按降级规则处理:

- **八字**: 针对每个子问题提取八字信号
  - 输入: 原局八字(chart.md) + 问题子项 + 相关干支
  - 任务: 从十神/干支/冲合角度分析每个子问题
  - schema: `{ sub_question: string, signals: [{ element: string, direction: string, strength: string, domain: string }] }`

- **紫微**（有数据时）: 针对每个子问题提取紫微信号
  - 输入: 原局紫微(chart.md) + 相关宫位 + 四化
  - 任务: 从宫位/星曜/四化角度分析每个子问题
  - schema: 同上

- **七政**（有数据时）: 针对每个子问题提取七政信号
  - 输入: 原局七政(chart.md) + 躔度/相位
  - 任务: 从命度/躔/难仇恩用角度分析每个子问题
  - schema: 同上

## Phase 3: 综合分析

1. **逐子问题验证**: 每个子问题走 SKILL.md §10 置信度三道题 (Q1同领域/Q2同方向/Q3同源)
2. **权重合成**: 按问题类型权重(Phase 1 确定)合成
3. **方向对比**: 方向选择型问题 → 生成对比表
4. **时间窗口**: 时机性问题 → 判断最佳窗口 + 置信度

输出: { analysis: [{ sub_question: string, synthesis: string, confidence: string }], direction_comparison: optional, time_window: optional, core_tension: string, practice_advice: string }

## Phase 4: 输出格式化

按 SKILL.md §14 模板 + §9 斯多葛语气:

```
### [问题]的能量格局
[多盘信号合述，标注多盘同指置信度]

### 关键张力
[核心矛盾如何作用在这个问题上——原局结构性张力从什么角度影响这个具体问题]

### 方向对比（仅方向选择型展开）
| 方向A | 盘面支撑 | 盘面阻力 | 当前时段推力 |
|-------|---------|---------|------------|
| ... | ... | ... | ... |

### 时间窗口（仅时机性）
[窗口判断 + 置信度]

> 🏛 盘面告诉你的是能量分布。你的选择是：在[方向A]和[方向B]之间，[时段]是更顺风的窗口。
```

## 约束

- 命格权重不参与截断重分配——它决定叙事框架，始终以背景形式出现
- 禁止替用户做决定——提供框架和工具，不替选择
