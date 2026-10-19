"""aris_init.py — ARIS 科研项目一键建库（/aris-init、$aris-init）的确定性部分。

子命令：
  enable    [Claude] 在 .claude/settings.local.json 里启用已安装的 ARIS skill，并提高 skill 清单预算
  codex     [Codex]  用 ARIS 官方安装器把 Codex 镜像版 skill 装进项目的 .agents/skills/
  scaffold  写入 / 刷新项目说明（CLAUDE.md 或 AGENTS.md）的 ARIS 段，新建 RESEARCH_BRIEF.md，补 .gitignore
  wiki      用 ARIS 官方脚本初始化 research-wiki/
  workflow  只同步共享科研流程及客户端入口，不改 Pipeline Status 或安装 skill
  all       按 --platform 依次执行需要的步骤

--platform：claude（只用 Claude Code）| codex（只用 Codex）| both（两个都用：AGENTS.md 为唯一来源，CLAUDE.md 用 @AGENTS.md 引用）

全部幂等：重复运行只补缺和刷新，不覆盖用户已有内容。出错一律 [fail] 退出。
"""
import argparse
import datetime
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

HOME = Path.home()
USER_SKILLS = Path(os.environ.get('ARIS_USER_SKILLS') or HOME / '.claude' / 'skills')
ARIS_REPO = Path(os.environ.get('ARIS_REPO') or HOME / '.claude' / '_aris_upstream')
EXCLUDE_FILE = Path(os.environ.get('ARIS_EXCLUDE_FILE') or HOME / '.claude' / 'aris-exclude.txt')
TEMPLATES = Path(__file__).resolve().parent.parent / 'templates'

NEVER_ENABLE = {'meta-optimize', 'meta-apply'}  # 依赖 ARIS 使用日志 hook，不属于科研流程
BUDGET_FRACTION = 0.02                          # 1M 上下文 = 8 万字符，够放下全部 ARIS 描述
BEGIN, END = '<!-- ARIS-INIT:BEGIN -->', '<!-- ARIS-INIT:END -->'
WORKFLOW_BEGIN, WORKFLOW_END = '<!-- ARIS-WORKFLOW:BEGIN -->', '<!-- ARIS-WORKFLOW:END -->'
ENTRY_BEGIN, ENTRY_END = '<!-- ARIS-WORKFLOW-ENTRY:BEGIN -->', '<!-- ARIS-WORKFLOW-ENTRY:END -->'
GITIGNORE_BASE = ['.claude/settings.local.json', '.aris/traces/']
GITIGNORE_CODEX = ['.aris/tools']  # 指向 ARIS 仓库的 junction，不进版本库
BRIEF_PLACEHOLDER = '[2-3 段：当前方法存在什么问题/缺失？]'
STATUS_RE = re.compile(r'\n*## Pipeline Status\s*\n+```yaml\n.*?\n```[ \t]*\n?', re.S)


def fail(msg):
    raise SystemExit(f'[fail] {msg}')


def write_text(path, text, dry):
    if dry:
        print(f'  [dry-run] 将写入 {path}（{len(text)} 字符）')
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8', newline='\n')


def tpl(fname):
    p = TEMPLATES / fname
    if not p.is_file():
        fail(f'缺少模板 {p}')
    return p.read_text(encoding='utf-8')


def marked(text, fname):
    text = text.strip()
    if not (text.startswith(BEGIN) and text.endswith(END)):
        fail(f'{fname} 必须以 ARIS-INIT BEGIN/END 标记开头和结尾')
    return text


# ---------------------------------------------------------------- Claude：启用 skill
def claude_aris_skills(allow_uninstalled=False):
    """已安装（~/.claude/skills）且属于 ARIS 仓库的 skill。aris-exclude.txt 排除的本来就没装。"""
    up_dir = ARIS_REPO / 'skills'
    if not up_dir.is_dir():
        fail(f'找不到 ARIS 仓库的 skills 目录：{up_dir}（检查 ARIS_REPO 环境变量）')
    upstream = {p.name for p in up_dir.iterdir() if (p / 'SKILL.md').is_file()}
    installed = {p.name for p in USER_SKILLS.iterdir() if (p / 'SKILL.md').is_file()} if USER_SKILLS.is_dir() else set()
    selected = upstream - set(codex_excludes()) if allow_uninstalled else upstream & installed
    names = sorted(selected - NEVER_ENABLE)
    if not names:
        fail('~/.claude/skills 里没有任何 ARIS skill（先运行 sync_aris.sh 同步）')
    return names


def cmd_enable(project, dry):
    path = project / '.claude' / 'settings.local.json'
    data = {}
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
        except json.JSONDecodeError as e:
            fail(f'{path} 不是合法 JSON（第 {e.lineno} 行第 {e.colno} 列）；先修好再重跑，脚本不会覆盖它')
    overrides = data.setdefault('skillOverrides', {})
    names = claude_aris_skills(allow_uninstalled=dry)
    added = [n for n in names if n not in overrides]  # 项目里已有的设置（包括手动设的 off）保持不动
    for n in added:
        overrides[n] = 'on'
    frac = data.get('skillListingBudgetFraction')
    if not isinstance(frac, (int, float)) or frac < BUDGET_FRACTION:
        data['skillListingBudgetFraction'] = BUDGET_FRACTION
    write_text(path, json.dumps(data, indent=2, ensure_ascii=False) + '\n', dry)
    print(f'[ok] enable（Claude）：ARIS skill 共 {len(names)} 个，本次新启用 {len(added)} 个，'
          f'已有设置保留 {len(names) - len(added)} 个；清单预算 {data["skillListingBudgetFraction"]}')


# ---------------------------------------------------------------- Codex：官方安装器
def codex_excludes():
    """aris-exclude.txt ∪ NEVER_ENABLE，只保留 Codex 镜像里真实存在的名字（安装器遇到未知名字会直接报错）。"""
    mirror = ARIS_REPO / 'skills' / 'skills-codex'
    if not mirror.is_dir():
        fail(f'找不到 ARIS 的 Codex 镜像目录：{mirror}')
    names = {p.name for p in mirror.iterdir() if (p / 'SKILL.md').is_file()}
    wanted = set(NEVER_ENABLE)
    if EXCLUDE_FILE.is_file():
        for line in EXCLUDE_FILE.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if line and not line.startswith('#'):
                wanted.add(line)
    return sorted(wanted & names)


def ps_quote(s):
    return "'" + str(s).replace("'", "''") + "'"


def cmd_codex(project, dry):
    installer = ARIS_REPO / 'tools' / 'install_aris.ps1'
    if not installer.is_file():
        fail(f'找不到 ARIS 官方安装器 {installer}')
    call = ' '.join([
        '&', ps_quote(installer),
        '-ProjectPath', ps_quote(project), '-Platform', 'codex', '-ArisRepo', ps_quote(ARIS_REPO),
        '-All', '-Exclude', ps_quote(','.join(codex_excludes())), '-Quiet', '-NoDoc',
    ] + (['-DryRun'] if dry else []))
    script = '[Console]::OutputEncoding=[Text.Encoding]::UTF8; $ErrorActionPreference="Stop"; ' + call
    r = subprocess.run(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', script],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    out = (r.stdout or '') + (r.stderr or '')
    if r.returncode != 0:
        fail(f'ARIS 官方安装器失败（exit {r.returncode}）。如果这个项目已有别的方式装的 Codex 版 ARIS，'
             f'可以加 --skip-codex-install 跳过这一步。\n{out.strip()[-2000:]}')
    keep = [ln.strip() for ln in out.splitlines()
            if re.match(r'\s*(Selection:|CREATE:|ADOPT:|UPDATE_TARGET:|REUSE:|REMOVE:|CONFLICT:)', ln)]
    print(f'[ok] codex：ARIS 官方安装器{"预演" if dry else "完成"} — ' + ' | '.join(keep))


# ---------------------------------------------------------------- 项目说明文件
def render(name, direction, date):
    status = tpl('pipeline_status.md').replace('{{DATE}}', date).strip()
    head = (tpl('project_head.md')
            .replace('{{NAME}}', name)
            .replace('{{DIRECTION}}', direction or '（待补充，见 RESEARCH_BRIEF.md）')
            .replace('{{DATE}}', date)
            .replace('{{PIPELINE_STATUS}}', status))
    routing = marked(tpl('routing.md'), 'routing.md')
    return head, status, routing


def upsert_doc(path, head, status, routing, dry):
    """新建：head + routing。已存在：刷新标记段，或追加（缺 Pipeline Status 时一并补上）。"""
    if not path.exists():
        write_text(path, head.rstrip() + '\n\n' + routing + '\n', dry)
        print(f'[ok] {path.name}：新建')
        return
    text = path.read_text(encoding='utf-8')
    if BEGIN in text and END in text:
        pre, rest = text.split(BEGIN, 1)
        new, action = pre + routing + rest.split(END, 1)[1], '刷新 ARIS 段'
    else:
        extra = '' if '## Pipeline Status' in text else '\n\n' + status
        new = text.rstrip() + extra + '\n\n' + routing + '\n'
        action = '追加 ARIS 段' + ('和 Pipeline Status' if extra else '')
    if new == text:
        print(f'[ok] {path.name}：已是最新，无变化')
    else:
        write_text(path, new, dry)
        print(f'[ok] {path.name}：{action}（原有内容保留）')


def claude_md_for_both(project, name, dry):
    """both 模式：CLAUDE.md 只保留一行 @AGENTS.md 引用 + 说明段，状态和路由统一在 AGENTS.md。"""
    md = project / 'CLAUDE.md'
    note = marked(tpl('claude_both_note.md'), 'claude_both_note.md')
    if not md.exists():
        write_text(md, f'# Project: {name}\n\n@AGENTS.md\n\n{note}\n', dry)
        print('[ok] CLAUDE.md：新建（引用 AGENTS.md）')
        return
    text = md.read_text(encoding='utf-8')
    new = text
    if not re.search(r'(?m)^@AGENTS\.md\s*$', new):
        m = re.match(r'(# [^\n]*\n)', new)
        new = (m.group(1) + '\n@AGENTS.md\n' + new[m.end():]) if m else '@AGENTS.md\n\n' + new
    if BEGIN in new and END in new:
        pre, rest = new.split(BEGIN, 1)
        new = pre + note + rest.split(END, 1)[1]
    else:
        new = new.rstrip() + '\n\n' + note + '\n'
    if new == text:
        print('[ok] CLAUDE.md：已是最新，无变化')
    else:
        write_text(md, new, dry)
        print('[ok] CLAUDE.md：改为引用 AGENTS.md（原有内容保留）')


def refresh_managed(path, block, begin, end, dry):
    """Refresh only this initializer's block; retain all surrounding project text."""
    text = path.read_text(encoding='utf-8') if path.exists() else ''
    if (begin in text) != (end in text):
        fail(f'{path} 的 {begin} / {end} 标记不完整；原文未覆盖')
    if begin in text:
        pre, rest = text.split(begin, 1)
        new = pre + block.strip() + rest.split(end, 1)[1]
    else:
        new = (text.rstrip() + '\n\n' if text.strip() else '') + block.strip() + '\n'
    if new != text:
        write_text(path, new, dry)
        print(f'[ok] {path.name}：同步共享科研流程（原有内容保留）')
    else:
        print(f'[ok] {path.name}：共享科研流程已是最新')


def cmd_workflow(project, platform, dry):
    workflow = tpl('research_workflow.md').strip()
    if not (workflow.startswith(WORKFLOW_BEGIN) and workflow.endswith(WORKFLOW_END)):
        fail('research_workflow.md 缺少 ARIS-WORKFLOW 标记')
    refresh_managed(project / 'RESEARCH_WORKFLOW.md', workflow,
                    WORKFLOW_BEGIN, WORKFLOW_END, dry)
    if platform in ('codex', 'both'):
        entry = (ENTRY_BEGIN + '\n## Shared research workflow\n\n'
                 'Before research work, read [RESEARCH_WORKFLOW.md](RESEARCH_WORKFLOW.md). '
                 'It defines the user-adopted Fable/Astra/Gemini/Sol division of labor, '
                 'evidence checks and cross-client handoff. Preserve project-specific '
                 'scientific, coding, resource and state-ownership rules.\n' + ENTRY_END)
        refresh_managed(project / 'AGENTS.md', entry, ENTRY_BEGIN, ENTRY_END, dry)
    if platform in ('claude', 'both'):
        entry = ENTRY_BEGIN + '\nResearch tasks: read RESEARCH_WORKFLOW.md and the active research handoff. Daily writing follows AGENTS.md content routing.\n' + ENTRY_END
        refresh_managed(project / 'CLAUDE.md', entry, ENTRY_BEGIN, ENTRY_END, dry)


def cmd_scaffold(project, platform, name, direction, dry):
    date = datetime.date.today().isoformat()
    head, status, routing = render(name, direction, date)

    if platform == 'claude':
        upsert_doc(project / 'CLAUDE.md', head, status, routing, dry)
    else:
        agents = project / 'AGENTS.md'
        claude = project / 'CLAUDE.md'
        # both 模式下，如果 Pipeline Status 目前在 CLAUDE.md 里，把它搬到 AGENTS.md，保证只有一份
        moved = None
        if platform == 'both' and claude.exists():
            ctext = claude.read_text(encoding='utf-8')
            has_agents_status = agents.exists() and '## Pipeline Status' in agents.read_text(encoding='utf-8')
            m = STATUS_RE.search(ctext)
            if m and not has_agents_status:
                moved = m.group(0).strip()
                write_text(claude, ctext[:m.start()] + '\n\n' + ctext[m.end():].lstrip('\n'), dry)
                print('[ok] CLAUDE.md：Pipeline Status 已搬到 AGENTS.md')
        if moved:
            head = head.replace(status, moved)
            status = moved
        upsert_doc(agents, head, status, routing, dry)
        if platform == 'both':
            claude_md_for_both(project, name, dry)

    brief = project / 'RESEARCH_BRIEF.md'
    if brief.exists():
        print('[ok] RESEARCH_BRIEF.md：已存在，跳过')
    else:
        src = ARIS_REPO / 'templates' / 'RESEARCH_BRIEF_TEMPLATE_CN.md'
        if not src.is_file():
            fail(f'找不到 ARIS 模板 {src}')
        text = src.read_text(encoding='utf-8')
        if direction:
            if BRIEF_PLACEHOLDER not in text:
                fail('ARIS 简报模板格式变了（找不到「问题陈述」占位行），请手动填写方向')
            text = text.replace(BRIEF_PLACEHOLDER, f'研究方向：{direction}\n\n{BRIEF_PLACEHOLDER}', 1)
        write_text(brief, text, dry)
        print('[ok] RESEARCH_BRIEF.md：从 ARIS 中文模板新建')

    gi = project / '.gitignore'
    text = gi.read_text(encoding='utf-8') if gi.exists() else ''
    lines = GITIGNORE_BASE + (GITIGNORE_CODEX if platform != 'claude' else [])
    missing = [ln for ln in lines if ln not in text.splitlines()]
    if missing:
        if text and not text.endswith('\n'):
            text += '\n'
        text += ('\n' if text else '') + '# ARIS (aris-init)\n' + '\n'.join(missing) + '\n'
        write_text(gi, text, dry)
        print(f'[ok] .gitignore：补上 {", ".join(missing)}')
    else:
        print('[ok] .gitignore：无需改动')

    cmd_workflow(project, platform, dry)


# ---------------------------------------------------------------- research-wiki
def cmd_wiki(project, dry):
    wiki = project / 'research-wiki'
    if (wiki / 'index.md').exists():
        print('[ok] research-wiki：已存在，跳过')
        return
    helper = ARIS_REPO / 'tools' / 'research_wiki.py'
    if not helper.is_file():
        fail(f'找不到 ARIS wiki 脚本 {helper}')
    if dry:
        print(f'  [dry-run] 将运行：python {helper} init research-wiki/')
        return
    r = subprocess.run([sys.executable, str(helper), 'init', 'research-wiki/'], cwd=project,
                       capture_output=True, text=True, encoding='utf-8', errors='replace',
                       env={**os.environ, 'PYTHONUTF8': '1'})
    if r.returncode != 0:
        fail(f'research-wiki init 失败（exit {r.returncode}）\n{r.stdout}\n{r.stderr}')
    if not (wiki / 'index.md').exists():
        fail('research-wiki init 返回成功，但没有生成 research-wiki/index.md')
    print('[ok] research-wiki：已用 ARIS 官方脚本初始化')


def main():
    ap = argparse.ArgumentParser(description='ARIS 科研项目一键建库')
    ap.add_argument('command', choices=['enable', 'codex', 'scaffold', 'wiki', 'workflow', 'all'])
    ap.add_argument('--project', required=True, help='项目根目录')
    ap.add_argument('--platform', choices=['claude', 'codex', 'both'], default='claude')
    ap.add_argument('--name', default='', help='课题名，默认用目录名')
    ap.add_argument('--direction', default='', help='研究方向（一两句话）')
    ap.add_argument('--skip-codex-install', action='store_true', help='项目已有其他方式装的 Codex 版 ARIS 时使用')
    ap.add_argument('--dry-run', action='store_true', help='只打印将要做的改动')
    a = ap.parse_args()

    project = Path(a.project).resolve()
    if not project.is_dir():
        fail(f'项目目录不存在：{project}')
    claude_home = (HOME / '.claude').resolve()
    if project in (HOME.resolve(), Path(project.anchor)) or project == claude_home or claude_home in project.parents:
        fail(f'拒绝在 {project} 建库：请在具体的课题目录里运行')

    print(f'项目：{project} · 平台：{a.platform}' + ('（预演，不写任何文件）' if a.dry_run else ''))
    if a.platform == 'claude' and ((project / 'AGENTS.md').exists() or (project / '.agents' / 'skills').is_dir()):
        print('[hint] 项目里已有 Codex 配置（AGENTS.md / .agents/skills），两边都用的话请改用 --platform both')
    if a.platform == 'codex' and (project / 'CLAUDE.md').exists():
        print('[hint] 项目里已有 CLAUDE.md，两边都用的话请改用 --platform both')

    run = a.command
    uses_claude = a.platform in ('claude', 'both')
    uses_codex = a.platform in ('codex', 'both')
    if run in ('enable', 'all') and uses_claude:
        cmd_enable(project, a.dry_run)
    if run in ('scaffold', 'all'):
        cmd_scaffold(project, a.platform, a.name or project.name, a.direction.strip(), a.dry_run)
    if run in ('codex', 'all') and uses_codex:
        if a.skip_codex_install:
            print('[ok] codex：按要求跳过官方安装器')
        else:
            cmd_codex(project, a.dry_run)
    if run in ('wiki', 'all'):
        cmd_wiki(project, a.dry_run)
    if run == 'workflow':
        cmd_workflow(project, a.platform, a.dry_run)


if __name__ == '__main__':
    main()
