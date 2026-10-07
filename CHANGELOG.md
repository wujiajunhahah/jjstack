# Changelog

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
