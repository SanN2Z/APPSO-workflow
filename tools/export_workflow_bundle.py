"""Export committed workflow sources; omit article bodies, credentials and runtimes."""
from __future__ import annotations

import argparse
from datetime import date
import hashlib
import json
from pathlib import Path
import re
import subprocess
import zipfile


ROOT = Path(__file__).resolve().parents[1]


def export_extension(bundle: Path, destination: Path, version: str) -> int:
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("invalid extension version")
    prefix = f"tools/company/ifanr-feishu-wechat-layout/v{version}/"
    # Do not git-archive HEAD:subtree: that loses root .gitattributes and can
    # change line endings. Extract already validated bytes from the root archive.
    with zipfile.ZipFile(bundle) as source:
        audit = json.loads(source.read(prefix + "local-validation.json"))
        files = {entry["file"]: source.read(prefix + "extension/" + entry["file"])
                 for entry in audit["files"]}
        for entry in audit["files"]:
            name = entry["file"]
            if Path(name).is_absolute() or ".." in Path(name).parts or "\\" in name:
                raise ValueError("unsafe extension member")
            if hashlib.sha256(files[name]).hexdigest().lower() != entry["sha256"].lower():
                raise ValueError(f"extension byte mismatch: {name}")
        if json.loads(files["manifest.json"])["version"] != version:
            raise ValueError("extension manifest version mismatch")
        with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as output:
            for name, content in files.items():
                output.writestr(name, content)
    return len(files)


def export_bundle(root: Path, output: Path, version: str = "1.10.3") -> dict:
    root = root.resolve()

    def git(*args):
        return subprocess.check_output(["git", "-C", str(root), *args])

    commit = git("rev-parse", "HEAD").decode().strip()
    tree_names = lambda tree: git("ls-tree", "--name-only", "-z", tree).decode("utf-8").rstrip("\0").split("\0")
    selected = [p for p in tree_names("HEAD") if p not in ["微信公众号", "X"]]
    for parent, excluded in [("微信公众号", {"内容", "选题"}), ("X", {"content", "内容"})]:
        selected += [parent + "/" + p for p in tree_names(f"HEAD:{parent}") if p and p not in excluded]
    output.mkdir(parents=True, exist_ok=True)
    bundle = output / f"workflow-{commit[:12]}.zip"
    git("archive", "--format=zip", f"--output={bundle}", commit, *selected)
    with zipfile.ZipFile(bundle) as z:
        names = set(z.namelist())
        toolchain = json.loads(z.read("tools/workflow-toolchain.json"))
        sources = json.loads(z.read("tools/workflow-source-assets.json"))["assets"]
        missing = set(toolchain["required_tracked_paths"]) - names
        if missing:
            raise ValueError(f"missing required paths: {sorted(missing)}")
        for asset in sources:
            if hashlib.sha256(z.read(asset["path"])).hexdigest().lower() != asset["sha256"].lower():
                raise ValueError(f"workflow input byte mismatch: {asset['path']}")
        for name in names:
            if name.startswith(("微信公众号/内容/", "微信公众号/选题/", "X/content/")) or Path(name).name == ".env" or "node_modules/" in name:
                raise ValueError("unexpected article, secret config or dependency directory")
        members = len([n for n in names if not n.endswith("/")])
    extension = output / f"wechat-extension-{version}-{commit[:12]}.zip"
    count = export_extension(bundle, extension, version)
    result = {
        "commit": commit, "workflow_file_count": members,
        "required_paths_verified": len(toolchain["required_tracked_paths"]),
        "source_hashes_verified": len(sources), "extension_file_hashes_verified": count,
        "artifacts": [{"name": p.name, "bytes": p.stat().st_size,
                       "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in [bundle, extension]],
        "scope": "Committed source backup; no Git history or runtime dependencies. Use private clone + bootstrap for a new installation. Real WeChat roundtrip remains pending.",
    }
    (output / f"receipt-{commit[:12]}.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "output" / f"workflow-pack-{date.today():%Y%m%d}")
    parser.add_argument("--extension-version", default="1.10.3")
    args = parser.parse_args()
    print(json.dumps(export_bundle(ROOT, args.output.resolve(), args.extension_version), ensure_ascii=False))


if __name__ == "__main__":
    main()
