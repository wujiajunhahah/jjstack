# 架构

## 一句话

**skill 是廉价的 Markdown；值钱的是"判断被固化成每次都会读到的判据"这件事。**

和 gstack 的差别：gstack 的硬工程在浏览器守护进程，jjstack 的硬工程在**生成 + 验证闭环**。

---

## 三层

```
┌──────────────────────────────────────────────────────┐
│ 技能层（Markdown，7 个 SKILL.md）                     │
│ · 路由器按意图分派                                    │
│ · 每个技能 = 一套判据 + 工作流 + 反模式 + 自检          │
└──────────────────────────────────────────────────────┘
                        +
┌──────────────────────────────────────────────────────┐
│ 判据层（ETHOS + references）                          │
│ · ETHOS.md 七条原则 → 注入每个技能的启动块             │
│ · references/ 事实库 / 技术惯例 / 反模式 / learnings    │
└──────────────────────────────────────────────────────┘
                        +
┌──────────────────────────────────────────────────────┐
│ 工程层（3 个本地脚本）                                 │
│ · gen-skills.py   模板 → SKILL.md（防漂移）            │
│ · validate.py     11 项静态验证（免费、不联网）          │
│ · init/uninstall  显式状态与干净卸载                    │
└──────────────────────────────────────────────────────┘
```

---

## 为什么要生成器

**问题**：`SKILL.md` 是人维护的，逻辑是人改的。改了流程忘了改文档，agent 拿到的就是过期判据——经典的文档漂移。

**做法**（对齐 gstack 的 `SKILL.md.tmpl` → `gen-skill-docs.ts`）：

```
SKILL.tmpl          （人写：frontmatter + 工作流 + 占位符 {{PREAMBLE}}）
      ↓
gen-skills.py       （把 lib/preamble.md 注入占位符）
      ↓
SKILL.md            （提交进仓库，带 GENERATED 标记）
```

`validate.py` 的 freshness 检查会重新渲染一遍并逐字节比对，任何直接手改都会被拦下。

---

## 启动块注入

每个技能的第一节都是同一段 `{{PREAMBLE}}`：

```bash
JJ="$HOME/.agents/skills/jjstack"
[ -d "$JJ" ] || { echo "jjstack: 未安装" >&2; exit 1; }
echo "SKILL_PROTO: 1"
echo "ETHOS: $JJ/ETHOS.md"
...
```

它做三件事：

1. **报状态** —— 安装是否完整、learnings 有几行、有哪些 references
2. **告诉 agent 按需读 references**（不是全读，省上下文）
3. **声明写操作边界** —— 只读启动，写状态必须显式运行 `init-state.sh`

**降级规则**：没看到 `SKILL_PROTO: 1` 就按安全默认走——不假设安装完整，告诉用户，继续干活，不因为技能环境问题阻断任务。

---

## 路由

`jjstack/SKILL.tmpl` 里是一张意图→技能的对照表。判断依据是**任务处在流程的哪一步**，不是关键词匹配：

- 还没有一句话问题陈述 → `jj-problem`
- 有问题陈述，要出能跑的东西 → `jj-prototype`
- 有东西了，要证明有没有用 → `jj-measure`
- 有结论了，要对外说 → `jj-honesty`

路由错了两处会被 `validate.py` 抓到：路由到不存在的技能、技能存在但没被路由。

---

## 状态与写盘

**默认只读。** 唯一会持续写入的文件是 `references/learnings.md`，而且只在你要求记录时追加。

为什么不让启动块自动创建：启动块每次调用都跑，一个会改盘的启动块违反"破坏性操作先确认"原则。所以初始化拆成显式的 `scripts/init-state.sh`。

---

## 仓库态 vs 安装态

生成器和验证器支持两种目录布局，自动探测：

| 布局 | 结构 | 用途 |
|---|---|---|
| **仓库态** | 仓库根 = 路由器技能，子技能是它的子目录 | 开发、发布 |
| **安装态** | `~/.agents/skills/jjstack` + 同级的 `jj-*` | 使用 |

探测逻辑：如果根目录下有 `jj-*` 子目录，就是仓库态；否则看父目录的兄弟目录。

---

## 为什么不做的事

| 没做 | 原因 |
|---|---|
| 网络请求 | 增加攻击面；这些流程不需要外部数据 |
| 遥测 | 判断质量不该靠上报使用量衡量 |
| 自动更新 | 自动改用户全局 skill 目录是危险默认 |
| 后台进程 | 没有需要长驻的东西 |
| 二进制 | 纯文本才能被审计；`validate.py` 就是审计工具 |

---

## 扩展点

加一个新技能：

1. 建 `jj-<name>/SKILL.tmpl`（frontmatter + `{{PREAMBLE}}` + 正文）
2. 建 `jj-<name>/agents/openai.yaml`
3. 在 `jjstack/SKILL.tmpl` 的路由表加一行
4. `python3 scripts/gen-skills.py && python3 scripts/validate.py`

`validate.py` 会检查：frontmatter 的 name 与目录一致、description 长度合理、路由双向一致、体积没超上限。
