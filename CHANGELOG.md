# Changelog

## [0.2.0] - 2026-09-28

### 新增

- **`DESIGN.md`** —— 可移植规格：机器可读 token（动效时长、介入阈值、排版约束）+ 立场与决定日志。复制进任何项目即可生效，不要求 skills 协议。
- **`references/refusal-list.md`** —— 八条"不做" + 例外 + 冲突优先级。
- **`references/cases.md`** —— 三个案例，展示规则如何改变决定。
- **`jj-embodied` 补具体阈值规则表** —— 干预强度、落点优先级、动效时长的可判定规则。
- 新增两项自检：**判据表三段完整性**（缺"为什么/边界"直接报错）、**DESIGN.md 规格完整性**。

### 变更

- 所有技能的判据表统一为三段：**判据 / 为什么 / 边界**。只有判据会退化成教条。
- README 重写：开头放一个 before/after 对话示例，而不是先讲概念。
- 泄露扫描放行「仓库自身 URL」这条必要元数据。

### 为什么不合并两个仓库

判断规则（拒绝清单、介入阈值、动效语义）**本来就属于**工作流的一部分——`jj-embodied` 讲"什么时候不该打断"，`jj-measure` 讲"怎么证明有用"，`jj-honesty` 讲"怎么说边界"。拆成两个仓库是人为的重复。

## [0.1.1] - 2026-09-28

## [0.1.1] - 2026-09-28

### 变更

- **移除 `jj-apply`** —— 求职材料属于个人事务，不属于工作方法套件。技能数 7 → 6（含路由器）。
- 路由表、安装器、卸载器、文档与示例同步更新。

## [0.1.0] - 2026-09-28

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)；版本号遵循 [SemVer](https://semver.org/lang/zh-CN/)。

## [0.1.0] - 2026-09-28

首个公开版本。

### 新增

- **七个技能**：`jjstack`（路由器）+ `jj-problem` / `jj-prototype` / `jj-measure` / `jj-honesty` / `jj-embodied` / `jj-apply`
- **ETHOS.md**：七条工作原则，每条带出处与反模式
- **共享 references**：事实库模板、技术惯例、反模式清单、learnings
- **模板生成**：`SKILL.tmpl` + `lib/preamble.md` → `SKILL.md`，消除文档漂移
- **静态验证**：`scripts/validate.py` 共 11 项检查，免费、<2s、不联网
- **安装器**：`setup`（支持 `--dry-run` / `--target` / `--force`）
- **卸载器**：`scripts/uninstall.sh`（白名单 + 二次校验 + 需确认）
- **显式状态初始化**：`scripts/init-state.sh`（启动块本身只读）
- **CI**：GitHub Actions 跑 freshness + validate
- **文档**：ARCHITECTURE / SECURITY / CONTRIBUTING / AGENTS / docs/ / examples/

### 设计决定

- **无网络、无遥测、无二进制** —— 判断质量不该靠上报使用量衡量
- **默认不自动触发** —— `allow_implicit_invocation: false`
- **启动块只读** —— 会改盘的启动块违反"破坏性操作先确认"
- **事实库不进版本库** —— 仓库给模板，真实数据留在本机

### 已知未覆盖

- 行为层验证（gstack 的 Tier 2 E2E / Tier 3 LLM 裁判）未建立
- 静态检查只能证明文件干净、结构自洽，不能证明建议质量
