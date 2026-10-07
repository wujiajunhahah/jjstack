# AGENTS

给在这个仓库里工作的 agent 看的约定。

## 核心约定

- **`SKILL.md` 是生成物。** 改 `SKILL.tmpl` 或 `lib/preamble.md`，然后跑 `python3 scripts/gen-skills.py`。
- **改完必跑 `python3 scripts/validate.py`。** 11 项静态检查，免费、<2s。不全绿不算完成。
- **新增检查规则必须带对抗性测试**：证明它能抓到目标问题，不只是会说 PASS。
- **不要引入**：网络调用、后台进程、二进制、遥测。
- **不要提交个人数据**：手机号、邮箱、真实项目指标、App 链接。真实事实库走 `references/facts.md`（gitignored）。

## 体积上限（ratchet）

| 文件 | 上限 |
|---|---|
| `ETHOS.md` | 260 行 |
| `README.md` | 140 行 |
| `SKILL.md`（各技能） | 200 行 |
| `references/facts.md` | 200 行 |
| `references/conventions.md` | 160 行 |
| `references/anti-patterns.md` | 140 行 |
| `lib/preamble.md` | 80 行 |
| `SECURITY.md` | 140 行 |

超了就**拆分**，不要放宽阈值。

## 验证纪律

改任何东西时按这个顺序：

1. **先列已知失败**：哪些检查红了、日志、最小复现。
2. **先诊断再改**：区分"产品缺陷 / 检查器缺陷 / 环境问题"。保留原始失败证据，不要无证据地说"这是本来就有的问题"。
3. **用最小复现验证修复**：不要把阈值调低、跳过用例、或重新判定一个失败来制造通过。
4. **跑便宜的检查在前**：`validate.py` 全绿再谈别的。
5. **冻结代码后跑一次完整检查**，最后再报结果。

## 完成状态

用 `DONE` / `DONE_WITH_CONCERNS` / `BLOCKED` / `NEEDS_CONTEXT` 收尾，并附证据。

**已知未覆盖**：静态检查只能证明文件干净、结构自洽，不能证明技能给出的建议是否正确。行为层验证见 `docs/validation.md`。

## 口吻

按 `ETHOS.md` 的 Voice：直接、具体、builder-to-builder。不用"显著提升/赋能/打造闭环"，不用 em 破折号，结尾给下一步动作。
