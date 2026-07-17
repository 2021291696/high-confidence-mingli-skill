# 高置信度命理 Skill · High-Confidence Mingli Skill

> 八字 / 紫微斗数 / 七政四余 **三盘互译**的命理对话伴侣。
> 不是"AI 算命"——是一套带置信度体系、可自我校准的解读引擎。
>
> A Chinese metaphysics companion for agent CLIs (Claude Code / Codex / Kimi Code — any CLI that reads SKILL.md), built on **three-chart cross-translation** (BaZi / Ziwei Doushu / Qizheng Siyu). Not fortune-cookie generation — an interpretation engine with a confidence system and a self-calibration loop.

---

## 为什么不一样 · Why It's Different

| 普通 AI 算命 | 本 Skill |
|--------------|----------|
| 单盘断语，张口就来 | 三盘互译：同一能量在八字/紫微/七政中互相验证，**不叠加能量** |
| "你本月运势不错" | 置信度三道题（同领域→同方向→同名检测），⭐/⭐⭐/⭐⭐⭐ 分级标注 |
| 吉凶好坏标签 | 斯多葛语气：不说吉凶，说张力、火候、练习；每条判断附「你可以把握的是」 |
| 每次都像第一次见你 | 收束自校准：根据你的反馈持续修正解释器，越用越准 |
| 硬凑共鸣 | 共鸣溯源有硬性门槛：全部命题不命中就直说"不匹配" |

核心机制：

- **四模式自动路由**：运势查询 / 推算推演 / 共鸣溯源 / 通用知识，开口即识别
- **五层权重**：命格 40% + 大运 20% + 时代运 15% + 流年 15% + 流月 7% + 流日 3%
- **四层准确性防线**：数据（硬编码推算规则+历法交叉验证）/ 解读（置信度三道题）/ 回归 / 活校准
- **缺盘降级**：只有八字也能跑，自动降级为单盘/两盘模式并同步封顶置信度

## 安装 · Install

把本仓库克隆到 agent CLI 的 skills 目录：

```bash
# macOS / Linux
git clone https://github.com/2021291696/high-confidence-mingli-skill.git ~/.claude/skills/fortune-telling

# Windows (PowerShell)
git clone https://github.com/2021291696/high-confidence-mingli-skill.git "$USERPROFILE\.claude\skills\fortune-telling"
```

升级：

```bash
cd ~/.claude/skills/fortune-telling && git pull
```

> **引擎与你的数据是分离的**：`git pull` 只更新引擎，你的命盘和记忆存在 `~/.claude/fortune-telling/`，不受升级影响，也不会被误提交。

> **不止 Claude Code**：本 skill 是纯 Markdown 指令 + 本地文件，任何支持 SKILL.md 的 agent CLI（Codex、Kimi Code 等）都可使用——克隆到对应 CLI 的 skills 目录（如 `~/.codex/skills/fortune-telling`）即可，数据目录路径不变。

## 使用 · Usage

在 agent CLI 中说 `/fortune-telling`，或直接开口（触发词自动命中）：

```
今日运势 / 本月感情运 / 今年事业运
我和这个岗位合不合 / 该不该换城市 / 什么时候是窗口期
刷到一个说"偏印人容易过度内化"的帖子，我是不是这样？
什么是伤官配印？/ 子午冲是什么意思？
```

**首次运行自动进入建档**：引擎检测到你还没有命盘数据，会引导你完成（约 5 分钟）：

1. 出生信息（公历日期 / 时间 / 地点 / 性别）→ 自动真太阳时校正
2. 按硬编码规则排八字四柱，并做历法交叉验证
3. 紫微 / 七政数据可选——从文墨天机、测测等 App 粘贴即可；不提供则自动降级运行
4. 生成 `chart.md`（命盘）+ `memory.md`（记忆种子），**只存在你本地**

详细流程见 [docs/onboarding.md](docs/onboarding.md)。

## 数据与隐私 · Data & Privacy

| 内容 | 位置 |
|------|------|
| 引擎（可 `git pull` 升级） | `~/.claude/skills/fortune-telling/` |
| 你的命盘 `chart.md` | `~/.claude/fortune-telling/` |
| 你的记忆 `memory.md` + 归档 | `~/.claude/fortune-telling/` |

所有个人数据只存在本地，引擎本身不联网、不上传、不绑定任何账户。

## 目录结构 · Structure

```
├── SKILL.md                  # 引擎主文件：路由/置信度/语气/权重/推算规则
├── workflows/                # 五个执行流程（路由命中后读取执行）
│   ├── fortune-daily-weekly-monthly.md   # 运势查询
│   ├── fortune-specific.md               # 推算推演
│   ├── fortune-resonance.md              # 共鸣溯源
│   ├── fortune-knowledge.md              # 通用知识
│   └── fortune-close.md                  # 收束校准
├── templates/                # chart.md / memory.md 模板
├── docs/onboarding.md        # 首次建档流程
└── LICENSE                   # MIT
```

## 限制 · Limitations

1. 预计算表覆盖 2024-2035，超范围年份现场推算且置信度降级
2. 紫微/七政原局数据需从排盘工具导入，引擎不做安星与星历计算
3. 三元九运交接点存在学派争议（本引擎统一用 2004/2024）
4. 节气日期为近似值，边界日建议历法库交叉验证
5. 运势是概率框架，不是预言

## English Overview

**High-Confidence Mingli Skill** is a Claude Code skill that turns your agent into a Chinese metaphysics reading companion. Instead of single-system fortune-telling, it cross-translates three chart systems — BaZi (Four Pillars), Ziwei Doushu (Purple Star Astrology), and Qizheng Siyu (Seven Governors & Four Remainders) — treating them as three languages describing the same underlying energy, never stacking them.

Key mechanics:

- **Confidence-gated interpretation**: every cross-chart correlation must pass three checks (same domain → same direction → same source, with a same-name trap detector) before it earns ⭐/⭐⭐/⭐⭐⭐ confidence markers
- **Four auto-routed modes**: time-based fortune queries, specific-question divination, resonance tracing ("I saw a post that says..."), and general knowledge Q&A
- **Stoic voice**: no "auspicious/inauspicious" labels — tensions, timing, and one concrete practice suggestion per reading
- **Self-calibrating memory**: each session closes by comparing its judgments against your feedback and refining the interpreter profile stored locally
- **Graceful degradation**: works with BaZi alone; missing charts cap the confidence ceiling accordingly
- **Privacy by design**: engine and user data are fully separated — your chart lives outside the skill directory and is never uploaded

**Install**: clone this repo into `~/.claude/skills/fortune-telling`, then say `/fortune-telling` in your agent CLI. First run walks you through a ~5-minute chart onboarding (birth data → computed Four Pillars with calendar cross-validation; Ziwei/Qizheng optionally imported from apps like 文墨天机). All data stays local under `~/.claude/fortune-telling/`.

*Note: interpretation content is primarily in Chinese, as the source metaphysics tradition is Chinese.*

## License

MIT — see [LICENSE](LICENSE).
