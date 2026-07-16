# Fortune-Close — 收束 Workflow

> 由 SKILL.md 在收束条件触发时执行。处理校准信号提取、跨模式关联、memory 更新。
> 输入: 当前会话内容回顾, query_types
> 数据文件: `~/.claude/fortune-telling/memory.md`（本 workflow 产出补丁，由主 agent 直接写入）

## 收束触发条件

- 用户说「结束 / 不问了 / 就到这」等明确收尾语
- 用户切换话题超过 5 轮且未回任何命理话题
- 用户说「谢谢 / 辛苦了」且之后 2 轮内未发起新查询

## Phase 1: 校准信号提取

从本次会话的用户反馈中提取:

| 信号类型 | 来源 | 处理 |
|----------|------|------|
| 追问信号 | 用户自发追问某判断方向 | → 写入"运行时画像"当前关注 |
| 确认信号 | 用户说「准」「对」「是这样的」 | → 对应条目验证次数+1 |
| 修正信号 | 用户说「不是X，是Y」 | → 立即修正对应条目 |
| 模糊否定 | 用户说「不准」但未具体说明 | → 该方向下次置信度降一级 |

⚠️ 用户沉默不反馈 → 不做推断，跳过校准。

**累积规则**:
- 同类校准 1-2 次 → 记录，标注「待二次验证」
- 同类校准 ≥ 5 次 → 合并为一条汇总记录
- 单次修正信号 → 立即修正，不等累积

输出: { calibration_signals: [{ type: string, target: string, action: string, content: string }] }

## Phase 2: 跨模式关联检查

检查两种跨模式关联:

1. **共鸣↔推算**: 共鸣模式中高共鸣概念 + 推算模式中相关领域 → 写入跨模式关联
2. **运势↔推算**: 运势预报某领域 + 后续问该领域推算 → 标记一致性

输出: { cross_mode_links: [{ concept: string, source_mode: string, target_mode: string, note: string }] }

## Phase 3: Memory 更新

生成结构化补丁，由主 agent 直接编辑 `~/.claude/fortune-telling/memory.md`:

```json
{
  "updates": [
    {
      "section": "运行时画像.当前关注|已验证解释偏移",
      "action": "append|update-row",
      "content": "更新内容"
    },
    {
      "section": "校准记录",
      "action": "update-row",
      "key": "条目标识",
      "fields": { "验证次数": "N", "置信度": "high|medium|low" }
    },
    {
      "section": "共鸣档案",
      "action": "append",
      "content": "| 日期 | 概念 | 共鸣等级 | 核心命题 | 备注 |"
    },
    {
      "section": "跨模式关联",
      "action": "append",
      "content": "| 关联 | 来源 | 目标 | 备注 |"
    },
    {
      "section": "对话日志",
      "action": "append",
      "content": "| 日期 | 查询类型 | 简要内容 | 收束状态 |"
    }
  ]
}
```

action 类型: `append`(追加) | `update-row`(更新已有行) | `merge`(合并多条为汇总) | `archive`(归档旧数据)

## Phase 4: 增长控制

| 数据区 | 控制策略 |
|--------|---------|
| 对话日志 | 保留最近 30 天，超期归档到 `~/.claude/fortune-telling/memory-archive/YYYY-MM/` |
| 校准记录 | 同类校准 ≥ 5 次时合并为一条汇总记录 |
| 共鸣档案 | 保留最近 20 条，超过后最旧的归档至 memory-archive/ |

输出: { archive_needed: boolean, archive_targets: string[] }

## 四模式收束差异

| 模式 | 收束提取重点 | 写入 memory.md 目标 |
|------|-------------|-------------------|
| 运势查询 | 追问点、确认信号、修正信号 | 运行时画像.当前关注 / 校准记录 |
| 推算查询 | 判断是否被用户反馈验证 | 运行时画像.已验证解释偏移 / 校准记录 |
| 共鸣溯源 | 共鸣结果归类（实质共鸣 vs 伪共鸣） | 共鸣档案 |
| 通用知识 | 仅记录用户关注的概念方向（不校准） | 运行时画像.当前关注 |
