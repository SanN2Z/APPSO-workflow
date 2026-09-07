from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import pytest


def test_approved_workflow_sources_do_not_bypass_hash_or_secret_checks(tmp_path):
    powershell = shutil.which("powershell")
    git = shutil.which("git")
    if not powershell or not git:
        pytest.skip("Windows PowerShell and Git are required")
    script = Path(__file__).resolve().parents[1] / "repository_preflight.ps1"
    (tmp_path / "tools").mkdir()
    shutil.copyfile(script, tmp_path / "tools/repository_preflight.ps1")
    subprocess.run([git, "init", "-q", str(tmp_path)], check=True, capture_output=True)
    relative = "APPSO-数字资产/01-栏目与品牌/品牌视觉/生图-Prompt/test.md"
    source = tmp_path / relative
    source.parent.mkdir(parents=True)
    source.write_text("original prompt", encoding="utf-8")
    config = tmp_path / "tools/workflow-source-assets.json"

    def allow_current_bytes():
        config.write_text(json.dumps({"assets": [{"path": relative,
            "sha256": hashlib.sha256(source.read_bytes()).hexdigest()}]}, ensure_ascii=False), encoding="utf-8")

    def run():
        return subprocess.run([powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                               str(tmp_path / "tools/repository_preflight.ps1")],
                              cwd=tmp_path, capture_output=True, timeout=30)

    allow_current_bytes()
    assert run().returncode == 0
    source.write_text("changed prompt", encoding="utf-8")
    assert run().returncode != 0
    allow_current_bytes()
    other = source.with_name("not-approved.md")
    other.write_text("not an approved input", encoding="utf-8")
    assert run().returncode != 0
    other.unlink()
    source.write_text("sk-" + "a" * 32, encoding="utf-8")
    allow_current_bytes()
    result = run()
    assert result.returncode != 0
    assert source.read_bytes() not in result.stdout + result.stderr
