from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
from pathlib import Path

import pytest


X_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = X_ROOT.parent
SCRIPTS = X_ROOT / "scripts"


@pytest.mark.parametrize(
    "script_name",
    [
        "check_x_env.py",
        "check_x_api_readonly.py",
        "check_x_visibility.py",
        "post_x.py",
        "publish_daily_queue.py",
        "trend_scan.py",
    ],
)
def test_every_x_entrypoint_exposes_help_without_credentials(script_name: str) -> None:
    completed = subprocess.run(
        [sys.executable, str(SCRIPTS / script_name), "--help"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=20,
    )
    assert completed.returncode == 0, completed.stderr or completed.stdout
    assert "usage:" in completed.stdout.lower()


def load_queue_module():
    sys.path.insert(0, str(SCRIPTS))
    try:
        spec = importlib.util.spec_from_file_location(
            "x_publish_daily_queue", SCRIPTS / "publish_daily_queue.py"
        )
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(str(SCRIPTS))


def test_queue_paths_are_x_project_relative_and_timezone_is_available() -> None:
    module = load_queue_module()
    date_value = module.today_jst()
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_value)
    assert module.queue_path_for(date_value).parent == X_ROOT / "content"
    assert module.log_path_for(date_value).parent == X_ROOT / "content"
