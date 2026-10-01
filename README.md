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
| "你本月运势不错" | 解读以典籍考证为准（穷通宝典/紫微全书/果老星宗查表），每条论断挂出处；置信度只标在盘与盘的关联上 |
| 吉凶好坏标签 | 斯多葛收束：断语不说吉凶（典籍引文保持原貌），每条判断附「你可以把握的是」 |
| 每次都像第一次见你 | 历史事件校准 + 收束自校准：根据你的反馈持续修正解释器，越用越准 |
| 硬凑共鸣 | 共鸣溯源有硬性门槛：全部命题不命中就直说"不匹配" |

核心机制：

- **三套确定性排盘引擎**：八字（Meeus 定气定朔，纯标准库）/ 紫微（iztro 2.6.1）/ 七政四余（自研恒星制，口径全标注）——干支、安星、躔度一律脚本输出，**不靠大模型口算**
- **典籍考证式解读**：references 资料层（bazi/紫微两套经过时间验证的 skill 资料 + 自建七政册）查表解读，论断挂典籍出处；新增「详批」模式完整复刻传统长文批盘
- **五模式自动路由**：运势查询 / 推算推演 / 共鸣溯源 / 通用知识 / 详批解读，开口即识别
- **五层权重**：命格 40% + 大运 20% + 时代运 15% + 流年 15% + 流月 7% + 流日 3%
- **四层准确性防线**：数据（引擎优先，口算仅作离线降级并强制标注）/ 解读（references 查表 + 出处标注 + 置信度联系）/ 回归 / 活校准（历史事件校准 + 收束校准）
- **缺盘降级**：引擎不可用时自动降级，同步封顶置信度

## 安装 · Install

把本仓库克隆到 Claude Code 的 skills 目录：

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

**启用紫微引擎（一次性）**：

```bash
cd ~/.claude/skills/fortune-telling/scripts/pai_pan_ziwei && npm install
```

八字与七政引擎是纯 Python 标准库实现，有 `python3` 即可，无需安装任何包。紫微引擎不装也能用——自动降级为缺紫微盘模式（或按旧流程从排盘 App 导入）。

> **引擎与你的数据是分离的**：`git pull` 只更新引擎，你的命盘和记忆存在 `~/.claude/fortune-telling/`，不受升级影响，也不会被误提交。

> **不止 Claude Code**：本 skill 是纯 Markdown 指令 + 本地文件，任何支持 SKILL.md 的 agent CLI（Codex、Kimi Code 等）都可使用——克隆到对应 CLI 的 skills 目录（如 `~/.codex/skills/fortune-telling`）即可，数据目录路径不变。

## 使用 · Usage

在 agent CLI 中说 `/fortune-telling`，或直接开口（触发词自动命中）：

```
今日运势 / 本月感情运 / 今年事业运
我和这个岗位合不合 / 该不该换城市 / 什么时候是窗口期
刷到一个说"偏印人容易过度内化"的帖子，我是不是这样？
什么是伤官配印？/ 子午冲是什么意思？
帮我详批 / 批一命 / 完整解读我的盘
```

**首次运行自动进入建档**：引擎检测到你还没有命盘数据，会引导你完成（约 5 分钟）：

1. 出生信息（公历日期 / 时间 / 地点 / 性别）
2. 一键跑三套确定性引擎排盘（`scripts/build_chart.py`）：四柱大运 / 十二宫四化 / 十一曜躔度命度立命宫——**不需要去文墨天机、测测等 App 抄盘**
3. 历史事件校准：用 3-5 个你已发生的事件验证解读模型（可跳过，跳过则置信度封顶）
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
├── SKILL.md                  # 引擎主文件：路由/解读管线/置信度联系/语气/权重/降级推算规则
├── scripts/                  # 三套确定性排盘引擎（v4）
│   ├── pai_pan_bazi.py       # 八字：四柱/大运/神煞（Meeus 定气，纯标准库）
│   ├── pai_pan_qizheng.py    # 七政：躔度/命度/立命宫/恩用难仇（自研恒星制，口径声明在文件头）
│   ├── pai_pan_ziwei/        # 紫微：十二宫/四化/大限/格局（iztro 2.6.1，需 npm install）
│   ├── build_chart.py        # 建档总控：出生信息 → 三引擎 → chart.md
│   └── test_*.py             # 各引擎回归测试（对拍黄金值 + 古典规则例）
├── references/               # 解读资料层（v5）：典籍查表解读、论断挂出处
│   ├── bazi/                 # 九典籍摘要/十神藏干/神煞/大运规则（源自 bazi skill，逐字节原样）
│   ├── ziwei/                # 骨髓赋全书条目/41格局/四化速查（源自 ziwei skill，逐字节原样）
│   ├── qizheng/reading.md    # 七政判读条目（自建，每条带出处）
│   └── README.md             # 溯源表
├── workflows/                # 六个执行流程（路由命中后读取执行）
│   ├── fortune-full-reading.md           # 详批解读（v5 新增，长文批盘+历史校准）
│   ├── fortune-daily-weekly-monthly.md   # 运势查询
│   ├── fortune-specific.md               # 推算推演
│   ├── fortune-resonance.md              # 共鸣溯源
│   ├── fortune-knowledge.md              # 通用知识
│   └── fortune-close.md                  # 收束校准
├── templates/                # chart.md / memory.md 模板
├── docs/onboarding.md        # 首次建档流程（含历史事件校准步）
└── LICENSE                   # MIT
```

## 限制 · Limitations

1. 七政四余月限/小限需限度推算，当前不包含
2. 七政盘制为**恒星制**（角宿一=0°），与回归制排盘软件相差约 24°，属学派差异——口径与出处见 `scripts/pai_pan_qizheng.py` 文件头
3. 紫微引擎需要 node（`npm install` 一次）；无 node 时该盘自动降级，其余两盘不受影响
4. 三元九运交接点存在学派争议（本引擎统一用 2004/2024）
5. 运势是概率框架，不是预言

## English Overview

**High-Confidence Mingli Skill** is a Claude Code skill that turns your agent into a Chinese metaphysics reading companion. Instead of single-system fortune-telling, it cross-translates three chart systems — BaZi (Four Pillars), Ziwei Doushu (Purple Star Astrology), and Qizheng Siyu (Seven Governors & Four Remainders) — treating them as three languages describing the same underlying energy, never stacking them.

Key mechanics:

- **Deterministic engines for all three charts**: BaZi (Meeus solar-term math, pure stdlib Python), Ziwei Doushu (iztro 2.6.1), and Qizheng Siyu (self-built sidereal engine with fully documented school conventions) — no LLM mental arithmetic for chart data
- **Classical-text-grounded interpretation**: a `references/` knowledge layer (curated from two time-tested skill collections plus a self-built Qizheng reading manual) — every claim cites its classical source (穷通宝典, 紫微全书, 果老星宗…); a new "full reading" (详批) mode reproduces the traditional long-form chart-reading experience
- **Confidence as cross-chart linkage only**: the three-check star system (same domain → same direction → same source, with a same-name trap detector) applies exclusively to cross-chart correlations; single-chart claims are grounded by their citations instead
- **Five auto-routed modes**: time-based fortune queries, specific-question divination, resonance tracing, general knowledge Q&A, and full-chart reading
- **Stoic closing voice**: the agent's own verdicts avoid auspicious/inauspicious labels (classical quotations stay verbatim); each reading ends with one concrete practice suggestion
- **Self-calibrating memory**: historical-event calibration at onboarding (3-5 past events verify the reading model) plus per-session closing calibration, stored locally
- **Graceful degradation**: missing engines/charts cap the confidence ceiling accordingly
- **Privacy by design**: engine and user data are fully separated — your chart lives outside the skill directory and is never uploaded

**Install**: clone this repo into `~/.claude/skills/fortune-telling`, then say `/fortune-telling` in Claude Code. First run walks you through onboarding (birth data → all three charts computed by the built-in engines → historical-event calibration; no app copy-pasting needed). All data stays local under `~/.claude/fortune-telling/`.

*Note: interpretation content is primarily in Chinese, as the source metaphysics tradition is Chinese.*

## License

MIT — see [LICENSE](LICENSE).
