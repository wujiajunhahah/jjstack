#!/usr/bin/env bash
# 卸载 jjstack：只删本套件的 7 个目录，不碰任何其他路径。
# 需要显式确认。
set -euo pipefail

SKILLS="${HOME}/.agents/skills"
TARGETS=("jjstack" "jj-problem" "jj-prototype" "jj-measure" "jj-honesty" "jj-embodied")

echo "将删除以下目录："
FOUND=0
for t in "${TARGETS[@]}"; do
  p="${SKILLS}/${t}"
  if [ -d "$p" ]; then
    echo "  ${p}  ($(find "${p}" -type f | wc -l | tr -d ' ') 个文件)"
    FOUND=$((FOUND + 1))
  else
    echo "  ${p}  （不存在，跳过）"
  fi
done

if [ "$FOUND" -eq 0 ]; then
  echo "没有可删除的目录。"
  exit 0
fi

echo
echo "注意：references/learnings.md 里累积的记录会一并删除。"
printf '输入 yes 确认删除：'
read -r ans
if [ "$ans" != "yes" ]; then
  echo "已取消，未做任何改动。"
  exit 0
fi

for t in "${TARGETS[@]}"; do
  p="${SKILLS}/${t}"
  # 二次校验：必须是 $SKILLS 的直接子目录，防止变量意外为空时误删
  case "$p" in
    "$SKILLS"/jjstack|"$SKILLS"/jj-problem|"$SKILLS"/jj-prototype|"$SKILLS"/jj-measure|"$SKILLS"/jj-honesty|"$SKILLS"/jj-embodied)
      [ -d "$p" ] && rm -rf "$p" && echo "已删除 ${p}"
      ;;
    *)
      echo "跳过异常路径（未匹配白名单）：${p}" >&2
      ;;
  esac
done

echo "卸载完成。"
