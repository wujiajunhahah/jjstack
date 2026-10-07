## 启动块（只读，不写盘）

```bash
JJ="$HOME/.agents/skills/jjstack"
[ -d "$JJ" ] || { echo "jjstack: 未安装（缺 $JJ）" >&2; exit 1; }
echo "SKILL_PROTO: 1"
echo "ETHOS: $JJ/ETHOS.md"
if [ -f "$JJ/references/learnings.md" ]; then
  echo "LEARNINGS: $(wc -l < "$JJ/references/learnings.md" | tr -d ' ') 行"
else
  echo "LEARNINGS: 未初始化（运行 scripts/init-state.sh 创建）"
fi
ls -1 "$JJ/references/"*.md 2>/dev/null | sed 's|.*/|REF: |'
[ -n "$(git rev-parse --show-toplevel 2>/dev/null)" ] && echo "REPO: $(git rev-parse --show-toplevel)"
```

**这个块只读**：不创建目录、不写文件、不联网、不读工作目录以外的内容。

**降级规则**：如果没看到 `SKILL_PROTO: 1`，按安全默认处理——不假设安装完整，明确告诉用户 jjstack 状态异常，然后继续完成用户的任务。不要因为技能环境问题阻断用户。

**按需读 references**（不要全读，每个都读会浪费上下文）：

| 任务涉及 | 读哪个 |
|---|---|
| "我做过什么"、项目数字、App 数据 | `references/facts.md` |
| 措辞、对外陈述、禁用词 | `references/anti-patterns.md` |
| 技术选型、目录、命名、交付形态 | `references/conventions.md` |
| 避免重踩以前的坑 | `references/learnings.md`（只读尾部 20 行） |

**写操作边界**：技能本身不写任何文件。只有两种情况例外，且都必须显式说明正在写什么：
1. 用户要求记录 learning → 追加一行到 `references/learnings.md`
2. 用户要求产出交付物（简历、文档、代码）→ 写到他指定的位置

除此之外，一律只读。
