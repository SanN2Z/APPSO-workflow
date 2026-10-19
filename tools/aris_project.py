"""Install and check the pinned, project-local ARIS research workflow."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "tools/aris"
UPSTREAM = BUNDLE / "upstream"
INITIALIZER = BUNDLE / "initializer"


def profile() -> dict:
    return json.loads((BUNDLE / "project-profile.json").read_text(encoding="utf-8"))


def excluded() -> set[str]:
    return {line.strip() for line in (BUNDLE / "skills-excluded.txt").read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")}


def inventory(platform: str) -> list[str]:
    source = UPSTREAM / "skills"
    if platform == "codex":
        source /= "skills-codex"
    return sorted(p.name for p in source.iterdir() if (p / "SKILL.md").is_file() and p.name not in excluded())


def environment(project: Path) -> dict[str, str]:
    return {**os.environ, "ARIS_REPO": str(UPSTREAM), "ARIS_USER_SKILLS": str(project / ".claude/skills"),
            "ARIS_EXCLUDE_FILE": str(BUNDLE / "skills-excluded.txt"),
            "ARIS_PROJECT_LOCAL": "1", "PYTHONUTF8": "1"}


def run(command: list[str], project: Path) -> None:
    completed = subprocess.run(command, cwd=project, env=environment(project), check=False)
    if completed.returncode:
        raise RuntimeError(f"ARIS command failed (exit {completed.returncode}); stopped without fallback.")


def ps_literal(value: Path | str) -> str:
    return "'" + str(value).replace("'", "''") + "'"


def link_initializer(project: Path, platform: str, dry: bool) -> None:
    destination = project / (".claude/skills" if platform == "claude" else ".agents/skills") / "aris-init"
    if destination.exists():
        if destination.resolve() != INITIALIZER.resolve():
            raise RuntimeError(f"Existing user-owned aris-init is preserved: {destination}")
        return
    if dry:
        print(f"[dry-run] initializer link: {destination}")
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    script = ("$ErrorActionPreference='Stop'; New-Item -ItemType Junction -Path "
              + ps_literal(destination) + " -Target " + ps_literal(INITIALIZER) + " | Out-Null")
    run(["powershell", "-NoProfile", "-Command", script], project)


def prepare_ignore(project: Path, dry: bool) -> None:
    path = project / ".gitignore"
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    patterns = ["/.aris/tools", "/.aris/installed-skills*.txt*", "/.aris/skills-declined*.txt",
                "/.aris/runtime.local.json", "/.aris/.install*", "/.aris/traces/",
                "/.claude/settings.local.json"]
    for platform in ("claude", "codex"):
        directory = ".claude/skills" if platform == "claude" else ".agents/skills"
        patterns.extend(f"/{directory}/{name}" for name in [*inventory(platform), "shared-references", "aris-init"])
    additions = [p for p in dict.fromkeys(patterns) if p not in current.splitlines()]
    if additions and not dry:
        path.write_text(current.rstrip() + "\n\n# ARIS generated local links and runtime inputs\n"
                        + "\n".join(additions) + "\n", encoding="utf-8", newline="\n")


def verify_sources() -> list[str]:
    manifest = json.loads((BUNDLE / "source-lock.json").read_text(encoding="utf-8"))
    failures = []
    for relative, expected in manifest["files"].items():
        path = BUNDLE / relative
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            failures.append(relative)
    return failures


def setup(project: Path, dry: bool) -> None:
    failures = verify_sources()
    if failures:
        raise RuntimeError("Pinned ARIS source drift: " + ", ".join(failures[:8]))
    prepare_ignore(project, dry)
    for platform in ("claude", "codex"):
        source = UPSTREAM / "skills" / "skills-codex" if platform == "codex" else UPSTREAM / "skills"
        known = {p.name for p in source.iterdir() if (p / "SKILL.md").is_file()}
        args = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                str(UPSTREAM / "tools/install_aris.ps1"), "-ProjectPath", str(project),
                "-Platform", platform, "-ArisRepo", str(UPSTREAM), "-All", "-Exclude",
                ",".join(sorted(excluded() & known)), "-NoDoc", "-Quiet"]
        if dry:
            args.append("-DryRun")
        run(args, project)
        link_initializer(project, platform, dry)
    config = profile()
    command = [sys.executable, str(INITIALIZER / "scripts/aris_init.py"), "all", "--project", str(project),
               "--platform", "both", "--name", config["name"], "--direction", config["direction"]]
    if dry:
        command.append("--dry-run")
    run(command, project)
    print("[ok] ARIS dry-run complete; no project files written." if dry
          else "[ok] ARIS project setup complete. Existing writing and research state retained.")


def doctor(project: Path) -> dict:
    failures = verify_sources()
    links = {}
    for platform in ("claude", "codex"):
        directory = project / (".claude/skills" if platform == "claude" else ".agents/skills")
        source = UPSTREAM / "skills" / "skills-codex" if platform == "codex" else UPSTREAM / "skills"
        missing = [name for name in inventory(platform) if not (directory / name).is_dir()
                   or (directory / name).resolve() != (source / name).resolve()]
        if missing:
            failures.append(f"{platform}: missing/stale links: {','.join(missing)}")
        links[platform] = {"skills": len(inventory(platform)), "missing": missing}
    for name in ["AGENTS.md", "CLAUDE.md", "RESEARCH_WORKFLOW.md", "RESEARCH_BRIEF.md", "research-wiki/index.md"]:
        if not (project / name).is_file():
            failures.append(name)
    return {"ok": not failures, "source_commit": profile()["source_commit"],
            "source_workflow_date": profile()["source_workflow_date"], "skill_links": links,
            "failures": failures, "runtime_file_present": (project / ".aris/runtime.local.json").is_file(),
            "external_model_connectivity": "not probed by setup/doctor", "global_configuration_written": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("setup", "doctor", "wiki"):
        p = sub.add_parser(name)
        p.add_argument("--project", type=Path, default=ROOT)
        if name == "setup":
            p.add_argument("--dry-run", action="store_true")
        if name == "wiki":
            p.add_argument("args", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    project = args.project.resolve()
    try:
        if os.name != "nt":
            raise RuntimeError("This adapter supports Windows PowerShell; source skills remain portable.")
        if not project.is_dir() or project == Path(project.anchor) or project == Path.home().resolve():
            raise RuntimeError("Use an existing project directory, never a drive root or home directory.")
        if args.command == "setup":
            setup(project, args.dry_run)
        elif args.command == "doctor":
            result = doctor(project)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if result["ok"] else 1
        else:
            run([sys.executable, str(UPSTREAM / "tools/research_wiki.py"), *args.args], project)
        return 0
    except (RuntimeError, OSError, ValueError) as exc:
        print(f"[fail] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
