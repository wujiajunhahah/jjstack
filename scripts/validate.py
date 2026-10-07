#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""jjstack Tier 1 静态验证（免费、<2s，不联网、不写盘）。

对齐 gstack 的做法：**先跑便宜的必过检查，再谈别的。** 这里全是确定性检查，
没有一次 LLM 调用。

用法：
  python3 scripts/validate.py            # 全部检查
  python3 scripts/validate.py --quiet     # 只输出失败
退出码：0 = 全过；1 = 有失败项。
"""
import argparse
import glob
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _layout():
    inside = sorted(d for d in os.listdir(ROOT)
                    if d.startswith('jj-') and os.path.isdir(os.path.join(ROOT, d)))
    if inside:
        return ROOT, [ROOT] + [os.path.join(ROOT, d) for d in inside]
    parent = os.path.dirname(ROOT)
    sibs = sorted(d for d in os.listdir(parent)
                  if d.startswith('jj-') and os.path.isdir(os.path.join(parent, d)))
    return parent, [os.path.join(parent, d) for d in sibs] + [ROOT]


SKILLS_DIR, SKILL_DIRS = _layout()


def skill_path(name):
    """返回技能目录的绝对路径（两种布局都支持）。"""
    for base in (ROOT, SKILLS_DIR):
        p = os.path.join(base, name)
        if os.path.isdir(p):
            return p
    return None


def skill_md_files():
    return [os.path.join(d, 'SKILL.md') for d in SKILL_DIRS
            if os.path.exists(os.path.join(d, 'SKILL.md'))]

# 体积上限（ratchet）：防止文件无界膨胀。超了就拆分，不是放宽阈值。
SIZE_CAPS = {
    'ETHOS.md': 260,
    'README.md': 140,
    'SKILL.md': 200,
    'references/facts.md': 200,
    'references/conventions.md': 160,
    'references/anti-patterns.md': 140,
    'lib/preamble.md': 80,
    'SECURITY.md': 140,
}

# 凭据特征（命中即失败）
SECRET_PATTERNS = [
    (r'sk-[A-Za-z0-9]{16,}', 'API key (sk-…)'),
    (r'ghp_[A-Za-z0-9]{20,}', 'GitHub token'),
    (r'AKIA[0-9A-Z]{16}', 'AWS access key'),
    (r'-----BEGIN [A-Z ]*PRIVATE KEY-----', '私钥'),
    (r'(?i)\b(api[_-]?key|secret|password|passwd|token)\s*[:=]\s*["\']?[A-Za-z0-9/_+-]{12,}', '硬编码凭据'),
    (r'(?i)bearer\s+[A-Za-z0-9._-]{20,}', 'Bearer token'),
]

# 隐私特征（命中即失败，除非在 ALLOW 列表里）
PII_PATTERNS = [
    (r'(?<!\d)1[3-9]\d{9}(?!\d)', '中国大陆手机号'),
    (r'(?<!\d)\d{17}[\dXx](?!\d)', '身份证号'),
    (r'[A-Za-z0-9._%+-]+@(?!example\.com)[A-Za-z0-9.-]+\.[A-Za-z]{2,}', '邮箱地址'),
]

# 允许出现的公开联系方式（本人自己的公开站点，属于有意保留）
PII_ALLOW = [
    # 允许出现的公开联系方式（本仓库默认不含任何个人联系方式）
    r'example\.com',
]

# 技能内容里不允许出现的命令（启动块必须只读；不得联网）
FORBIDDEN_CMD_PATTERNS = [
    (r'\bcurl\b|\bwget\b|\bnc\b|\bssh\b', '网络/外连命令'),
    (r'\brm\s+-rf\b|\bmkfs\b|\bdd\s+if=', '破坏性命令'),
    (r'\bsudo\b', '提权命令'),
]

# 只读启动块里允许的写操作：无。写状态必须走 scripts/init-state.sh（显式）
WRITE_CMD_PATTERNS = [
    (r'\bmkdir\b', 'mkdir'),
    (r'>\s*"?\$?\w*\.(md|json|txt|jsonl)', '重定向写文件'),
    (r'\btee\b', 'tee'),
]


LOCAL_TERMS_FILE = os.path.join(SKILLS_DIR, '.leak-terms.local')


def local_terms():
    """本地身份词表（不进版本库）。发布前跑一次即可挡住"开盒"。"""
    if not os.path.exists(LOCAL_TERMS_FILE):
        return []
    return [l.strip() for l in open(LOCAL_TERMS_FILE, encoding='utf-8').read().split('\n')
            if l.strip() and not l.strip().startswith('#')]


def files_under(path):
    out = []
    for base, _dirs, names in os.walk(path):
        for n in names:
            if n.endswith(('.md', '.tmpl', '.py', '.sh', '.yaml', '.yml')):
                out.append(os.path.join(base, n))
    return sorted(out)


def rel(p):
    return os.path.relpath(p, SKILLS_DIR)


def check(name, fn, quiet):
    try:
        problems = fn()
    except Exception as e:                                   # 检查器自身出错也要暴露
        problems = [f'检查器异常: {type(e).__name__}: {e}']
    ok = not problems
    if not ok or not quiet:
        print(f'[{"PASS" if ok else "FAIL"}] {name}')
    for p in problems:
        print(f'    - {p}')
    return ok


# ------------------------------------------------------------------ 检查项

def c_frontmatter():
    out = []
    for f in sorted(skill_md_files()):
        d = os.path.basename(os.path.dirname(f))
        t = open(f, encoding='utf-8').read()
        m = re.match(r'^---\n(.*?)\n---\n', t, re.S)
        if not m:
            out.append(f'{rel(f)}: 缺 frontmatter'); continue
        fm = m.group(1)
        mm = re.search(r'^name:\s*(\S+)\s*$', fm, re.M)
        if not mm:
            out.append(f'{rel(f)}: 缺 name')
        else:
            skill_name = mm.group(1)
            if not re.match(r'^(jjstack|jj-[a-z]+)$', skill_name):
                out.append(f'{rel(f)}: name={skill_name} 不是合法技能名（应为 jjstack 或 jj-<小写>）')
            elif d in ('jjstack',) or d.startswith('jj-'):
                # 目录名本身是技能名时才要求严格一致
                if skill_name != d:
                    out.append(f'{rel(f)}: name={skill_name} 与目录名 {d} 不一致')
            # 目录名不是技能名（例：github 下载解压成 jjstack-main/ 或 jjstack-0.1.0/）→ 跳过一致性检查
        dm = re.search(r'^description:\s*(.+)$', fm, re.M)
        if not dm:
            out.append(f'{rel(f)}: 缺 description')
        else:
            n = len(dm.group(1).strip())
            if n < 20:
                out.append(f'{rel(f)}: description 太短({n})，无法据以路由')
            if n > 400:
                out.append(f'{rel(f)}: description 过长({n})')
    return out


def c_freshness():
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'gen-skills.py'), '--check'],
                       capture_output=True, text=True)
    if r.returncode == 0:
        return []
    return [ln.strip() for ln in (r.stdout + r.stderr).splitlines() if ln.strip()]


def c_secrets():
    out = []
    for f in files_under(SKILLS_DIR):
        t = open(f, encoding='utf-8', errors='ignore').read()
        for pat, label in SECRET_PATTERNS:
            for m in re.finditer(pat, t):
                out.append(f'{rel(f)}: 命中{label} → {m.group(0)[:24]}…')
    return out


def c_pii():
    out = []
    for f in files_under(SKILLS_DIR):
        t = open(f, encoding='utf-8', errors='ignore').read()
        for pat, label in PII_PATTERNS:
            for m in re.finditer(pat, t):
                hit = m.group(0)
                if any(re.search(a, hit) for a in PII_ALLOW):
                    continue
                out.append(f'{rel(f)}: 命中{label} → {hit[:32]}')
    return out


def c_forbidden_cmds():
    out = []
    targets = [os.path.join(d, 'SKILL.md') for d in SKILL_DIRS] + \
              [os.path.join(ROOT, 'lib', 'preamble.md'), os.path.join(ROOT, 'ETHOS.md')]
    for f in targets:
        if not os.path.exists(f):
            continue
        t = open(f, encoding='utf-8').read()
        for pat, label in FORBIDDEN_CMD_PATTERNS:
            if re.search(pat, t):
                out.append(f'{rel(f)}: 含{label}（技能不得联网/提权/破坏）')
    return out


def c_preamble_readonly():
    out = []
    p = os.path.join(ROOT, 'lib', 'preamble.md')
    if not os.path.exists(p):
        return ['lib/preamble.md 缺失']
    t = open(p, encoding='utf-8').read()
    # 只允许出现在说明文字里的禁令，不允许真实写操作
    for pat, label in WRITE_CMD_PATTERNS:
        for m in re.finditer(pat, t):
            line = t[:m.start()].count('\n') + 1
            ctx = t.splitlines()[line - 1].strip()
            if ctx.startswith(('#', '**', '*', '>')) or '不允许' in ctx or '不得' in ctx:
                continue
            out.append(f'lib/preamble.md:{line}: 启动块含写操作 {label} → 应为只读')
    return out


def c_routes():
    out = []
    router = os.path.join(ROOT, 'SKILL.md')
    t = open(router, encoding='utf-8').read()
    routed = set(re.findall(r'`(jj-[a-z]+)`', t))
    for name in sorted(routed):
        if not skill_path(name):
            out.append(f'路由到不存在的技能: {name}')
    # 反向：存在但没被路由
    for d in sorted(os.listdir(SKILLS_DIR)):
        if d.startswith('jj-') and d not in routed:
            out.append(f'技能 {d} 存在但未出现在路由表中')
    return out


def c_refs():
    out = []
    for f in sorted(skill_md_files()) + [os.path.join(ROOT, 'SKILL.md'),
                                              os.path.join(ROOT, 'ETHOS.md')]:
        t = open(f, encoding='utf-8').read()
        for ref in set(re.findall(r'references/([a-z-]+\.md)', t)):
            if os.path.exists(os.path.join(ROOT, 'references', ref)):
                continue
            # facts.md / learnings.md 走 .gitignore，仓库里只有模板；
            # 模板存在即视为有效引用
            if ref in ('facts.md', 'learnings.md') and os.path.exists(
                    os.path.join(ROOT, 'references', ref.replace('.md', '.example.md'))):
                continue
            out.append(f'{rel(f)} 引用了不存在的 references/{ref}')
    return out


def c_size_ratchet():
    out = []
    for relp, cap in SIZE_CAPS.items():
        f = os.path.join(ROOT, relp)
        if not os.path.exists(f):
            # facts.md 走 .gitignore，仓库里只有模板；回退到 example 检查体积
            if relp == 'references/facts.md':
                ex = os.path.join(ROOT, 'references', 'facts.example.md')
                if os.path.exists(ex):
                    f = ex
                else:
                    out.append('references/facts.md 与其模板都不存在')
                    continue
            else:
                out.append(f'{relp} 缺失')
                continue
        n = sum(1 for _ in open(f, encoding='utf-8'))
        if n > cap:
            out.append(f'{relp}: {n} 行 > 上限 {cap}（拆分，不要放宽阈值）')
    return out


def c_leak_terms():
    """身份词扫描：只在本地词表存在时生效。"""
    terms = local_terms()
    if not terms:
        print('    （提示）未找到 .leak-terms.local —— 建议写入自己的姓名/项目名/域名后再跑，该文件不进仓库。')
        return []
    out = []
    for f in files_under(SKILLS_DIR):
        if os.path.basename(f) == '.leak-terms.local':
            continue
        t = open(f, encoding='utf-8', errors='ignore').read()
        for term in terms:
            if term in t:
                out.append(f'{rel(f)}: 命中本地词表「{term}」（身份信息不该出现在可发布内容里）')
    return out


def c_security_doc():
    out = []
    f = os.path.join(ROOT, 'SECURITY.md')
    if not os.path.exists(f):
        return ['SECURITY.md 缺失']
    t = open(f, encoding='utf-8').read()
    required = {
        '本地': r'本地|local',
        '不联网': r'不联网|无网络|no network|offline',
        '无遥测': r'遥测|telemetry',
        '显式调用': r'显式调用|implicit',
        '卸载': r'卸载|uninstall',
        '读取范围': r'读取|读取范围|read',
    }
    for label, pat in required.items():
        if not re.search(pat, t, re.I):
            out.append(f'SECURITY.md 未声明「{label}」')
    return out



def c_shell_syntax():
    """bash -n 语法检查 + 禁止 $VAR 紧跟非 ASCII（set -u 下会误判变量名）。"""
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, 'scripts', '*.sh'))):
        r = subprocess.run(['bash', '-n', f], capture_output=True, text=True)
        if r.returncode != 0:
            out.append(f'{rel(f)}: bash -n 语法错误 → {r.stderr.strip()[:120]}')
        t = open(f, encoding='utf-8').read()
        for i, line in enumerate(t.splitlines(), 1):
            if line.strip().startswith('#'):
                continue
            for m in re.finditer(r'\$[A-Za-z_][A-Za-z0-9_]*[^\x00-\x7F]', line):
                out.append(f'{rel(f)}:{i}: `{m.group(0)}` 变量名被中文粘连 → 改用 ${{VAR}}')
    return out

CHECKS = [
    ('frontmatter 合法且 name 与目录一致', c_frontmatter),
    ('SKILL.md 与模板一致（无漂移）', c_freshness),
    ('凭据扫描', c_secrets),
    ('隐私扫描（手机号/身份证/邮箱）', c_pii),
    ('内容不含联网/提权/破坏性命令', c_forbidden_cmds),
    ('启动块只读（无隐式写盘）', c_preamble_readonly),
    ('路由表与实际技能双向一致', c_routes),
    ('references 引用有效', c_refs),
    ('体积 ratchet', c_size_ratchet),
    ('SECURITY.md 声明齐全', c_security_doc),
    ('本地身份词扫描', c_leak_terms),
    ('shell 脚本语法与变量引用', c_shell_syntax),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--quiet', action='store_true')
    a = ap.parse_args()
    print(f'jjstack Tier 1 静态验证 · {SKILLS_DIR}\n')
    results = [check(n, f, a.quiet) for n, f in CHECKS]
    passed, total = sum(results), len(results)
    print(f'\n{passed}/{total} 通过')
    if passed < total:
        print('STATUS: BLOCKED — 先修上面的失败项，再谈别的')
        return 1
    print('STATUS: DONE — Tier 1 全过（免费层，未做行为验证）')
    return 0


if __name__ == '__main__':
    sys.exit(main())
