# AGENTS.md — high-confidence-mingli-skill

## 项目一句话

高置信度命理 skill：八字/紫微/七政三盘由确定性引擎排盘（大模型只解读不计算），解读查典籍资料层并挂出处，置信度只标跨盘关联，斯多葛收束。

## 怎么跑起来

- 八字/七政引擎：`python3 scripts/pai_pan_bazi.py --solar YYYY-MM-DD --sex 男`、`python3 scripts/pai_pan_qizheng.py --solar ... --hour HH:MM --lat --lon`（纯标准库，无 pip 依赖）
- 紫微引擎：`cd scripts/pai_pan_ziwei && npm install && npx tsx pai_pan.ts --solar ... --hour ... --sex ...`
- 一键建档：`python3 scripts/build_chart.py --solar ... --hour ... --sex ... --lat ... --lon ...`
- 测试：`python3 scripts/test_pai_pan_bazi.py`、`python3 scripts/test_pai_pan_qizheng.py`（共 25 项，改引擎必跑）

## 技术栈

Python 3.8+（标准库）· Node.js 18+（仅紫微引擎）· 主体是 Markdown 指令（SKILL.md + workflows + references）

## 目录与约定

- `SKILL.md` 引擎主文件；`workflows/` 六个模式流程；`references/` 典籍资料层（bazi/ziwei 8 份**逐字节原样**移植，溯源表见 references/README.md——同步上游用整文件覆盖，不要就地改写）
- **排盘数字以 `scripts/` 引擎输出为准，禁止口算覆盖**；解读论断必须挂典籍出处；置信度 ⭐ 只标跨盘关联
- 引擎文件头的「口径声明」是学派定版（恒星制/安命法/四余锚点），改动等于换学派，需重跑对拍
- `chart.md`/`memory.md` 用户数据永不入库（已 gitignore）；改 README 记得中英两份同步

## 当前状态与下一步

- v4 三引擎（058ca66）+ v5 典籍解读层（7b20b8f）+ v6 新 README（cdf355f）均已推送 GitHub main
- 挂账：七政引擎与真实排盘 App 的对拍样本（≥3 张）；七政庙旺分度表未考证（引擎与解读册均不判庙旺）
- 注意：本仓在维护者的工作区大仓内是子目录，GitHub 独立仓为独立历史——推送走维护者的克隆同步流程，不要把工作区整仓当远端
