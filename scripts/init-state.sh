#!/usr/bin/env bash
# 显式初始化 jjstack 本地状态（learnings）。
# 启动块本身不写盘；需要状态时由你显式运行本脚本。
set -euo pipefail

JJ="${HOME}/.agents/skills/jjstack"
[ -d "$JJ" ] || { echo "jjstack 未安装：缺 ${JJ}" >&2; exit 1; }

REF="${JJ}/references"
mkdir -p "$REF"

LEARN="${REF}/learnings.md"
if [ -f "$LEARN" ]; then
  echo "已存在，未改动：${LEARN}（$(wc -l < "${LEARN}" | tr -d ' ') 行）"
else
  cat > "$LEARN" <<'EOF'
# jjstack learnings

格式：`YYYY-MM-DD | <技能> | <一句话洞察> | 来源: observed`

EOF
  echo "已创建：${LEARN}"
fi
