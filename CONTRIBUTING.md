# 贡献指南

## 最快路径

```bash
git clone <repo> && cd jjstack
./setup --dry-run          # 先看会做什么
./setup                    # 链接到 ~/.agents/skills
python3 scripts/validate.py # 11 项静态检查
```

改完东西之后：

```bash
python3 scripts/gen-skills.py   # 如果改了 .tmpl 或 lib/preamble.md
python3 scripts/validate.py     # 必须全绿
```

---

## 改哪一层

| 想改什么 | 改哪里 | 改完要做什么 |
|---|---|---|
| 原则、判据 | `ETHOS.md` | 同步 `SKILL.tmpl` 里的精简版 |
| 启动块行为 | `lib/preamble.md` | `gen-skills.py` |
| 路由规则 | `SKILL.tmpl` | `gen-skills.py` |
| 某技能的工作流 | `<skill>/SKILL.tmpl` | `gen-skills.py` |
| 技术惯例 | `references/conventions.md` | 无需重新生成 |
| 反模式清单 | `references/anti-patterns.md` | 无需重新生成 |
| 验证规则 | `scripts/validate.py` | 用对抗性测试证明新规则有效 |

---

## 两条硬规则

### 1. 不要直接改 `SKILL.md`

它是生成物。`validate.py` 的 freshness 检查会重新渲染并逐字节比对，手改必然失败。

改 `SKILL.tmpl`（或 `lib/preamble.md`），然后跑 `gen-skills.py`。

### 2. 新增验证规则必须带对抗性测试

一个只会说 PASS 的验证器没有价值。加检查项时，用最小复现证明它能**抓到**目标问题：

```bash
# 例：验证「凭据扫描」真的会失败
printf '\nAPI_KEY = "sk-'"$(printf 'a%.0s' {1..24})'"\n' >> jj-apply/SKILL.md
python3 scripts/validate.py --quiet ; echo "退出码=$? (期望 1)"
git checkout jj-apply/SKILL.md   # 恢复
```

不加对抗性测试的检查规则不会被合并。

---

## 提交前自检

- [ ] `python3 scripts/gen-skills.py --check` 无漂移
- [ ] `python3 scripts/validate.py` 全绿
- [ ] 新规则有对抗性测试
- [ ] 没有引入个人数据（手机号 / 邮箱 / 真实项目指标 / App 链接）
- [ ] 没有引入网络调用、后台进程、二进制
- [ ] 体积没超上限（超了就拆分，不要放宽阈值）
- [ ] 口吻符合 `ETHOS.md` 的 Voice 一节：直接、具体、不用空泛词、不用 em 破折号

---

## 加一个新技能

```bash
mkdir jj-<name>/agents
cat > jj-<name>/SKILL.tmpl <<'EOF'
---
name: jj-<name>
description: <一句话，写明触发条件；20–400 字>
---

{{PREAMBLE}}

# <技能名>

## 何时用
## 工作流
## 反模式
## 自检
EOF
printf 'policy:\n  allow_implicit_invocation: false\n' > jj-<name>/agents/openai.yaml
# 在 SKILL.tmpl 的路由表加一行
python3 scripts/gen-skills.py && python3 scripts/validate.py
```

验证器会检查：name 与目录名一致、description 长度、路由双向一致、体积上限。

---

## 隐私

**不要往仓库里提交个人数据。** 真实事实库放 `references/facts.md`（已 gitignore）。示例数据用 `facts.example.md` 里的占位符。

PR 会被检查：手机号、邮箱、身份证号、真实项目指标、App Store 链接。

---

## 报告问题

用 issue 模板。安全/隐私问题不要附带真实凭据，用最小复现。
