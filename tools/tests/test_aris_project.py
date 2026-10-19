import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

import pytest

SPEC=importlib.util.spec_from_file_location('aris_project',Path(__file__).parents[1]/'aris_project.py')
ARIS=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ARIS)


def test_source_drift_is_reported_before_install(tmp_path,monkeypatch):
    source=tmp_path/'source.txt'
    source.write_text('fixed source',encoding='utf-8')
    lock={'files':{'source.txt':hashlib.sha256(source.read_bytes()).hexdigest()}}
    (tmp_path/'source-lock.json').write_text(json.dumps(lock),encoding='utf-8')
    monkeypatch.setattr(ARIS,'BUNDLE',tmp_path)
    assert ARIS.verify_sources()==[]
    source.write_text('changed source',encoding='utf-8')
    assert ARIS.verify_sources()==['source.txt']


def test_existing_user_skill_is_preserved(tmp_path):
    skill=tmp_path/'.agents/skills/aris-init'
    skill.mkdir(parents=True)
    own=skill/'SKILL.md'
    own.write_text('user owned',encoding='utf-8')
    with pytest.raises(RuntimeError,match='user-owned'):
        ARIS.link_initializer(tmp_path,'codex',False)
    assert own.read_text(encoding='utf-8')=='user owned'


def test_dry_run_does_not_change_ignore_or_create_links(tmp_path,monkeypatch):
    ignore=tmp_path/'.gitignore'
    ignore.write_text('existing\n',encoding='utf-8')
    monkeypatch.setattr(ARIS,'inventory',lambda platform:['research-lit'])
    ARIS.prepare_ignore(tmp_path,True)
    ARIS.link_initializer(tmp_path,'claude',True)
    assert ignore.read_text(encoding='utf-8')=='existing\n'
    assert not (tmp_path/'.claude').exists()


def test_generated_ignores_do_not_hide_daily_content_skills(tmp_path,monkeypatch):
    subprocess.run(['git','init','-q',str(tmp_path)],check=True)
    monkeypatch.setattr(ARIS,'inventory',lambda platform:['research-lit'])
    ARIS.prepare_ignore(tmp_path,False)
    new_skill=tmp_path/'.agents/skills/self-media-ops/extra.md'
    new_skill.parent.mkdir(parents=True)
    new_skill.touch()
    research=tmp_path/'.agents/skills/research-lit/SKILL.md'
    research.parent.mkdir(parents=True)
    research.touch()
    assert subprocess.run(['git','check-ignore',str(new_skill)],cwd=tmp_path,capture_output=True).returncode==1
    assert subprocess.run(['git','check-ignore',str(research)],cwd=tmp_path,capture_output=True).returncode==0


def test_project_environment_keeps_global_home_and_pins_sources(tmp_path):
    env=ARIS.environment(tmp_path)
    assert env['ARIS_PROJECT_LOCAL']=='1'
    assert Path(env['ARIS_REPO'])==ARIS.UPSTREAM
    assert Path(env['ARIS_USER_SKILLS'])==tmp_path/'.claude/skills'
