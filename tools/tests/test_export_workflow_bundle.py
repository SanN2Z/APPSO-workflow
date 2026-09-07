import hashlib
import importlib.util
import json
from pathlib import Path
import zipfile

import pytest

spec = importlib.util.spec_from_file_location("workflow_export", Path(__file__).resolve().parents[1] / "export_workflow_bundle.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def fixture(path, *, corrupt=False):
    prefix = "tools/company/ifanr-feishu-wechat-layout/v1.10.3/"
    content = b"const example = 1;\r\n"
    files = {"manifest.json": b'{"version":"1.10.3"}\r\n', "script.js": content}
    audit = {"files": [{"file": name, "sha256": hashlib.sha256(data).hexdigest()} for name, data in files.items()]}
    with zipfile.ZipFile(path, "w") as z:
        z.writestr(prefix + "local-validation.json", json.dumps(audit))
        for name, data in files.items():
            z.writestr(prefix + "extension/" + name, data.replace(b"\r\n", b"\n") if corrupt else data)
    return files


def test_extension_zip_keeps_verified_crlf_bytes_and_root_manifest(tmp_path):
    bundle, output = tmp_path / "bundle.zip", tmp_path / "extension.zip"
    files = fixture(bundle)
    assert module.export_extension(bundle, output, "1.10.3") == 2
    with zipfile.ZipFile(output) as z:
        assert set(z.namelist()) == set(files)
        assert all(z.read(name) == data for name, data in files.items())


def test_extension_zip_rejects_changed_bytes_before_writing(tmp_path):
    bundle, output = tmp_path / "bundle.zip", tmp_path / "extension.zip"
    fixture(bundle, corrupt=True)
    with pytest.raises(ValueError, match="byte mismatch"):
        module.export_extension(bundle, output, "1.10.3")
    assert not output.exists()
