# jjstack

[![CI](https://github.com/wujiajunhahah/jjstack/actions/workflows/ci.yml/badge.svg)](https://github.com/wujiajunhahah/jjstack/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.0-green.svg)](CHANGELOG.md)
[![No network](https://img.shields.io/badge/network-none-lightgrey.svg)](SECURITY.md)

把一个 builder 的工作方式编码成可复用的 agent skill 套件。

结构参考 [gstack](https://github.com/garrytan/gstack)（Garry Tan 的 Claude Code 套件）：路由器 + 子技能 + ETHOS 注入 + 共享 references + 模板生成 + 静态验证。

**七条原则，六个技能，纯 Markdown + 三个本地脚本。不联网、无遥测、默认不自动触发。**

---

## 它解决什么问题

面对空白 prompt，AI agent 会即兴发挥：你说"帮我写代码"它就闷头写，你说"看看这个方案"它按自己的理解来。流程不可复现，每次都不一样。

jjstack 把一个人的判断固化成 slash 命令式的工作流。不是"提示词合集"，是**把判断标准写成每次都会读到的判据**。

---

## 七条原则

| # | 原则 | 一句话 |
|---|---|---|
| 1 | 问题不对，后面全错 | 用「不是 A，而是 B」写清重构，写不出来就是没想清楚 |
| 2 | 做到能上手为止 | 交付物要能被别人打开/安装/上手 |
| 3 | 用测量代替猜测 | 说结论前先能回答：怎么测、样本多少、对照组是什么 |
| 4 | 先记录，再打断 | 默认安静做完；有证据且不打断会造成损失时才打断 |
| 5 | 把边界写进文档 | 每条对外陈述配一句"它能证明到哪一步" |
| 6 | 屏幕之外 | 反馈先想放进环境，再想能不能少一次 |
| 7 | 解耦状态与执行 | 先写状态帧协议，再写消费端 |

完整版与出处见 [`ETHOS.md`](ETHOS.md)。

---

## 六个技能

| 技能 | 干什么 | 什么时候用 |
|---|---|---|
| `jjstack` | 路由器 | 不确定走哪条流程 |
| `jj-problem` | 问题重构 | 想法没写成一句话问题陈述、范围太大、几个方向选一个 |
| `jj-prototype` | 原型到实机 | 问题清楚了，要出能上手的东西 |
| `jj-measure` | 测量与评测 | 定门槛、做评测、判断改动有没有用 |
| `jj-honesty` | 口径审查 | 某个数字或说法能不能写进简历/README/答辩 |
| `jj-embodied` | 具身与冷静交互 | 设计可穿戴/硬件/Agent 的反馈方式 |
| `jj-apply` | 个人材料 | 简历、投递材料、求职文案 |

常见串法：

```
从零做新东西   jj-problem → jj-prototype → jj-measure → jj-honesty
投递/上线前    jj-honesty（先查说法）→ jj-measure（补测量）
设计感知系统   jj-problem → jj-embodied → jj-prototype → jj-measure
```

---

## 安装

```bash
git clone https://github.com/<you>/jjstack.git
cd jjstack
./setup
```

`setup` 会把 6 个技能链接到 `~/.agents/skills/`（可用 `--target` 改），并初始化本地状态。

卸载：
```bash
bash scripts/uninstall.sh
```

---

## 快速验证

```bash
python3 scripts/validate.py     # 11 项静态检查，免费、<2s、不联网
```

---

## 目录结构

```
jjstack/                      # 仓库根 = 路由器技能
├── SKILL.tmpl  → SKILL.md    # 改 .tmpl，不要改 .md
├── ETHOS.md                  # 七条原则（完整版）
├── SECURITY.md               # 安全与隐私声明
├── CONTRIBUTING.md
├── ARCHITECTURE.md
├── CHANGELOG.md
├── VERSION
├── setup                     # 安装器
├── lib/preamble.md           # 共享启动块（只读，注入到每个技能）
├── references/               # 判断标准
│   ├── facts.example.md      # 事实库模板 —— 复制成 facts.md 填自己的
│   ├── conventions.md        # 技术惯例
│   ├── anti-patterns.md      # 反模式清单
│   └── learnings.md          # 会话级自我改进
├── scripts/                  # 生成器 + 验证器 + 初始化 + 卸载
├── docs/                     # 验证体系、如何写新技能
├── examples/                 # 一个走通的例子
├── jj-problem/               # 六个子技能（各自的 SKILL.tmpl + agents/openai.yaml）
├── jj-prototype/
├── jj-measure/
├── jj-honesty/
├── jj-embodied/
└── jj-apply/
```

---

## 两条纪律

1. **`references/facts.md` 是唯一事实来源。** 技能里涉及"我做过什么"的内容只能引用它；文件里没有的不写。这样套件不会替你说没做过的话。仓库里给的是 `facts.example.md` 模板，你自己的那份不进版本库。
2. **改 SKILL.md 的方式是改模板。** `SKILL.md` 由 `SKILL.tmpl` + `lib/preamble.md` 生成，`validate.py` 的 freshness 检查会拦下直接手改。

---

## 安全

- 无网络、无遥测、无二进制；默认**不自动触发**（`agents/openai.yaml` 里 `allow_implicit_invocation: false`）
- 启动块**只读**，不创建文件、不写盘；写操作只有两种：追加一行 learning，或写你指定的交付物

详见 [`SECURITY.md`](SECURITY.md)。

---

## 已知未覆盖

静态检查只能证明**文件干净、结构自洽**，不能证明**技能给出的建议是对的**。gstack 有 Tier 2（真实会话跑每个 skill）和 Tier 3（LLM 当裁判）；**本套件没有这两层**，所以状态是 `DONE_WITH_CONCERNS`。要补的话见 [`docs/validation.md`](docs/validation.md)。

---

## License

MIT
