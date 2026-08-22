#!/usr/bin/env python3
"""Verify that a fresh clone contains and can run the local workflow toolchain.

This verifier deliberately separates clone-local capabilities from credentials,
browser state, remote connectors, and user authorization.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import re
import shutil
import subprocess
import sys
import tokenize
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = Path(__file__).with_name("workflow-toolchain.json")
WINDOWS_ABSOLUTE_RE = re.compile(r"(?<![A-Za-z0-9_])[A-Za-z]:[\\/]")
UNIX_HOME_RE = re.compile(r"(?<![A-Za-z0-9_])/(?:Users|home)/[^\s'\"`]+")
PIN_RE = re.compile(
    r"^([A-Za-z0-9_.-]+)(?:\[[^\]]+\])?==([^\s;]+)(?:\s*;.*)?$"
)


def normalized_name(value: str) -> str:
    return re.sub(r"[-_.]+", "-", value).lower()


def posix_relative(path: Path, root: Path = REPO_ROOT) -> str:
    return path.relative_to(root).as_posix()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected a JSON object: {posix_relative(path)}")
    return value


def run_command(
    command: list[str], *, cwd: Path = REPO_ROOT, timeout: int = 120
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )


def version_tuple(value: str) -> tuple[int, int, int]:
    match = re.search(r"(\d+)\.(\d+)(?:\.(\d+))?", value)
    if not match:
        raise ValueError(f"cannot parse version: {value!r}")
    return tuple(int(part or 0) for part in match.groups())  # type: ignore[return-value]


def make_check(name: str, ok: bool, detail: str) -> dict[str, Any]:
    return {"name": name, "ok": ok, "detail": detail}


def parse_git_nul_paths(output: str) -> set[str]:
    return {item.replace("\\", "/") for item in output.split("\0") if item}


def parse_git_attr_nul(output: str) -> dict[str, dict[str, str]]:
    parts = [item for item in output.split("\0") if item]
    if len(parts) % 3:
        raise ValueError("unexpected git check-attr -z output")
    parsed: dict[str, dict[str, str]] = {}
    for index in range(0, len(parts), 3):
        path, attribute, value = parts[index : index + 3]
        parsed.setdefault(path.replace("\\", "/"), {})[attribute] = value
    return parsed


def parse_requirements(
    path: Path,
    *,
    packages: dict[str, tuple[str, str]] | None = None,
    visited: set[Path] | None = None,
) -> tuple[dict[str, tuple[str, str]], set[Path]]:
    """Resolve local -r includes and require every dependency to use an exact pin."""

    packages = packages if packages is not None else {}
    visited = visited if visited is not None else set()
    resolved = path.resolve()
    if resolved in visited:
        return packages, visited
    if not resolved.is_file():
        raise ValueError(f"requirements file is missing: {resolved}")
    visited.add(resolved)

    for line_number, raw_line in enumerate(
        resolved.read_text(encoding="utf-8-sig").splitlines(), start=1
    ):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if " #" in line:
            line = line.split(" #", 1)[0].rstrip()
        if line.startswith("-r ") or line.startswith("--requirement "):
            include = line.split(maxsplit=1)[1].strip().strip("'\"")
            parse_requirements(
                resolved.parent / include, packages=packages, visited=visited
            )
            continue
        match = PIN_RE.fullmatch(line)
        if not match:
            raise ValueError(
                f"unpinned or unsupported requirement at "
                f"{resolved}:{line_number}: {raw_line}"
            )
        display_name, version = match.groups()
        key = normalized_name(display_name)
        previous = packages.get(key)
        if previous and previous[0] != version:
            raise ValueError(
                f"conflicting pins for {display_name}: {previous[0]} vs {version}"
            )
        packages[key] = (version, display_name)
    return packages, visited


def check_python_runtime(manifest: dict[str, Any]) -> dict[str, Any]:
    minimum = str(manifest["python"]["minimum"])
    actual = ".".join(str(item) for item in sys.version_info[:3])
    ok = sys.version_info[:3] >= version_tuple(minimum)
    return make_check(
        "python.version", ok, f"actual={actual}; minimum={minimum}; tested={manifest['python']['tested']}"
    )


def check_requirements(manifest: dict[str, Any]) -> dict[str, Any]:
    try:
        requirements_path = REPO_ROOT / manifest["python"]["requirements_file"]
        actual, visited = parse_requirements(requirements_path)
        expected = {
            normalized_name(name): (str(version), name)
            for name, version in manifest["python"]["packages"].items()
        }
        actual_versions = {name: item[0] for name, item in actual.items()}
        expected_versions = {name: item[0] for name, item in expected.items()}
        expected_sources = {
            (REPO_ROOT / item).resolve()
            for item in manifest["python"]["requirement_sources"]
        }
        if actual_versions != expected_versions:
            return make_check(
                "source.requirements",
                False,
                f"manifest={expected_versions}; resolved={actual_versions}",
            )
        if visited != expected_sources:
            rendered_actual = sorted(posix_relative(item) for item in visited)
            rendered_expected = sorted(posix_relative(item) for item in expected_sources)
            return make_check(
                "source.requirements",
                False,
                f"include graph mismatch; expected={rendered_expected}; actual={rendered_actual}",
            )
        return make_check(
            "source.requirements",
            True,
            f"{len(actual_versions)} exact pins from {len(visited)} tracked manifests",
        )
    except Exception as exc:  # noqa: BLE001 - verifier must report all failures
        return make_check("source.requirements", False, str(exc))


def check_node_lock(manifest: dict[str, Any]) -> dict[str, Any]:
    try:
        package = read_json(REPO_ROOT / manifest["node"]["package_file"])
        lock = read_json(REPO_ROOT / manifest["node"]["lock_file"])
        expected_packages = {
            str(name): str(version)
            for name, version in manifest["node"]["packages"].items()
        }
        expected_overrides = {
            str(name): str(version)
            for name, version in manifest["node"]["overrides"].items()
        }
        package_dependencies = package.get("dependencies", {})
        package_overrides = package.get("overrides", {})
        lock_root = lock.get("packages", {}).get("", {})
        lock_dependencies = lock_root.get("dependencies", {})
        problems: list[str] = []
        if package_dependencies != expected_packages:
            problems.append(f"package.json dependencies={package_dependencies}")
        if package_overrides != expected_overrides:
            problems.append(f"package.json overrides={package_overrides}")
        if lock.get("lockfileVersion") != 3:
            problems.append(f"lockfileVersion={lock.get('lockfileVersion')}")
        if lock_dependencies != expected_packages:
            problems.append(f"lock root dependencies={lock_dependencies}")
        for name, version in expected_packages.items():
            locked = lock.get("packages", {}).get(f"node_modules/{name}", {}).get("version")
            if locked != version:
                problems.append(f"{name} locked={locked!r}; expected={version!r}")
        return make_check(
            "source.node_lock",
            not problems,
            "; ".join(problems) if problems else "package.json and lockfile pins agree",
        )
    except Exception as exc:  # noqa: BLE001
        return make_check("source.node_lock", False, str(exc))


def git_tracked_paths(paths: Iterable[str]) -> tuple[set[str], str | None]:
    path_list = list(paths)
    completed = run_command(
        [
            "git",
            "-c",
            "core.quotepath=false",
            "ls-files",
            "--cached",
            "-z",
            "--",
            *path_list,
        ]
    )
    if completed.returncode != 0:
        return set(), completed.stderr.strip() or "git ls-files failed"
    return parse_git_nul_paths(completed.stdout), None


def check_required_tracked(manifest: dict[str, Any]) -> dict[str, Any]:
    required_set = {
        str(item).replace("\\", "/") for item in manifest["required_tracked_paths"]
    }
    required_set.update(
        str(item).replace("\\", "/") for item in manifest["entrypoints"].values()
    )
    required_set.update(
        str(item).replace("\\", "/") for item in manifest["portable_docs"]
    )
    required_set.update(
        str(item).replace("\\", "/") for item in manifest["python"]["requirement_sources"]
    )
    required_set.update(
        {
            str(manifest["node"]["package_file"]).replace("\\", "/"),
            str(manifest["node"]["lock_file"]).replace("\\", "/"),
        }
    )
    required = sorted(required_set)
    missing_disk = [item for item in required if not (REPO_ROOT / item).is_file()]
    tracked, error = git_tracked_paths(required)
    missing_git = [item for item in required if item not in tracked]
    problems = []
    if error:
        problems.append(error)
    if missing_disk:
        problems.append(f"missing on disk={missing_disk}")
    if missing_git:
        problems.append(f"not tracked={missing_git}")
    return make_check(
        "source.tracked_contract",
        not problems,
        "; ".join(problems) if problems else f"{len(required)} required files are tracked",
    )


def check_line_endings(manifest: dict[str, Any]) -> dict[str, Any]:
    expected = {
        str(path).replace("\\", "/"): {
            str(name): str(value) for name, value in attributes.items()
        }
        for path, attributes in manifest["line_endings"].items()
    }
    attributes = sorted({name for item in expected.values() for name in item})
    completed = run_command(
        ["git", "check-attr", "-z", *attributes, "--", *expected]
    )
    if completed.returncode != 0:
        return make_check(
            "source.line_endings",
            False,
            completed.stderr.strip() or "git check-attr failed",
        )
    try:
        actual = parse_git_attr_nul(completed.stdout)
    except ValueError as exc:
        return make_check("source.line_endings", False, str(exc))
    problems = [
        f"{path}: expected={values}; actual={actual.get(path, {})}"
        for path, values in expected.items()
        if actual.get(path) != values
    ]
    return make_check(
        "source.line_endings",
        not problems,
        "; ".join(problems) if problems else f"{len(expected)} hash-bound files have deterministic checkout EOL",
    )


def selected_python_files(manifest: dict[str, Any]) -> list[Path]:
    completed = run_command(
        [
            "git",
            "-c",
            "core.quotepath=false",
            "ls-files",
            "--cached",
            "-z",
            "--",
            "*.py",
        ]
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "git ls-files failed")
    roots = tuple(
        str(item).strip("/").replace("\\", "/") + "/"
        for item in manifest["python_compile_roots"]
    )
    selected: list[Path] = []
    for item in completed.stdout.split("\0"):
        relative = item.replace("\\", "/")
        if relative and relative.startswith(roots):
            selected.append(REPO_ROOT / relative)
    return selected


def check_python_sources(manifest: dict[str, Any]) -> dict[str, Any]:
    failures: list[str] = []
    try:
        paths = selected_python_files(manifest)
        for path in paths:
            try:
                with tokenize.open(path) as handle:
                    source = handle.read()
                compile(source, str(path), "exec")
            except Exception as exc:  # noqa: BLE001
                failures.append(f"{posix_relative(path)}: {exc}")
        return make_check(
            "source.python_syntax",
            not failures,
            "; ".join(failures) if failures else f"compiled {len(paths)} tracked Python files in memory",
        )
    except Exception as exc:  # noqa: BLE001
        return make_check("source.python_syntax", False, str(exc))


def absolute_path_findings(root: Path, documents: Iterable[str]) -> list[str]:
    findings: list[str] = []
    for relative in documents:
        path = root / relative
        if not path.is_file():
            findings.append(f"{relative}: missing")
            continue
        for line_number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if WINDOWS_ABSOLUTE_RE.search(line) or UNIX_HOME_RE.search(line):
                findings.append(f"{relative}:{line_number}: {line.strip()[:180]}")
    return findings


def check_portable_docs(manifest: dict[str, Any]) -> dict[str, Any]:
    findings = absolute_path_findings(REPO_ROOT, manifest["portable_docs"])
    return make_check(
        "source.portable_docs",
        not findings,
        "; ".join(findings) if findings else f"scanned {len(manifest['portable_docs'])} operational documents",
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def tree_fingerprint(root: Path) -> tuple[list[Path], int, str]:
    files = sorted((path for path in root.rglob("*") if path.is_file()), key=lambda p: p.relative_to(root).as_posix())
    material = "".join(
        f"{path.relative_to(root).as_posix()}\t{sha256_file(path)}\n" for path in files
    ).encode("utf-8")
    return files, sum(path.stat().st_size for path in files), hashlib.sha256(material).hexdigest().upper()


def check_company_extension(manifest: dict[str, Any]) -> dict[str, Any]:
    config = manifest["company_extension"]
    root = REPO_ROOT / config["root"]
    problems: list[str] = []
    try:
        files, total_bytes, fingerprint = tree_fingerprint(root)
        manifest_sha = sha256_file(REPO_ROOT / config["manifest"])
        if len(files) != int(config["file_count"]):
            problems.append(f"files={len(files)}; expected={config['file_count']}")
        if total_bytes != int(config["total_bytes"]):
            problems.append(f"bytes={total_bytes}; expected={config['total_bytes']}")
        if fingerprint != str(config["tree_sha256"]).upper():
            problems.append(f"tree_sha256={fingerprint}; expected={config['tree_sha256']}")
        if manifest_sha != str(config["manifest_sha256"]).upper():
            problems.append(f"manifest_sha256={manifest_sha}; expected={config['manifest_sha256']}")

        repo_relative_files = {posix_relative(path) for path in files}
        tracked, error = git_tracked_paths([str(config["root"])])
        if error:
            problems.append(error)
        elif tracked != repo_relative_files:
            problems.append(
                f"tracked tree mismatch; missing={sorted(repo_relative_files - tracked)}; "
                f"extra={sorted(tracked - repo_relative_files)}"
            )
        return make_check(
            "source.company_extension",
            not problems,
            "; ".join(problems)
            if problems
            else f"{len(files)} files, {total_bytes} bytes, tree hash verified",
        )
    except Exception as exc:  # noqa: BLE001
        return make_check("source.company_extension", False, str(exc))


def check_installed_python_packages(manifest: dict[str, Any]) -> dict[str, Any]:
    problems: list[str] = []
    for name, expected in manifest["python"]["packages"].items():
        try:
            actual = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            problems.append(f"{name}=missing (expected {expected})")
            continue
        if actual != str(expected):
            problems.append(f"{name}={actual} (expected {expected})")
    return make_check(
        "runtime.python_packages",
        not problems,
        "; ".join(problems) if problems else f"{len(manifest['python']['packages'])} exact package pins installed",
    )


def check_node_runtime(manifest: dict[str, Any]) -> dict[str, Any]:
    node = shutil.which("node")
    npm = shutil.which("npm.cmd") or shutil.which("npm")
    if not node or not npm:
        return make_check(
            "runtime.node",
            False,
            f"node={node or 'missing'}; npm={npm or 'missing'}",
        )
    node_result = run_command([node, "--version"])
    npm_result = run_command([npm, "--version"])
    if node_result.returncode or npm_result.returncode:
        return make_check(
            "runtime.node",
            False,
            f"node stderr={node_result.stderr.strip()}; npm stderr={npm_result.stderr.strip()}",
        )
    node_version = node_result.stdout.strip()
    npm_version = npm_result.stdout.strip()
    minimum = str(manifest["node"]["minimum"])
    try:
        version_ok = version_tuple(node_version) >= version_tuple(minimum)
    except ValueError as exc:
        return make_check("runtime.node", False, str(exc))
    return make_check(
        "runtime.node",
        version_ok,
        f"node={node_version}; npm={npm_version}; minimum={minimum}; tested={manifest['node']['tested']}",
    )


def check_installed_node_packages(manifest: dict[str, Any]) -> dict[str, Any]:
    package_root = REPO_ROOT / manifest["node"]["package_root"]
    problems: list[str] = []
    for name, expected in manifest["node"]["packages"].items():
        package_file = package_root / "node_modules" / name / "package.json"
        if not package_file.is_file():
            problems.append(f"{name}=missing (run npm ci)")
            continue
        try:
            actual = read_json(package_file).get("version")
        except Exception as exc:  # noqa: BLE001
            problems.append(f"{name}: {exc}")
            continue
        if actual != str(expected):
            problems.append(f"{name}={actual!r} (expected {expected!r})")
    return make_check(
        "runtime.node_packages",
        not problems,
        "; ".join(problems) if problems else "locked Wenyan package installed",
    )


def check_javascript_syntax(manifest: dict[str, Any]) -> dict[str, Any]:
    node = shutil.which("node")
    if not node:
        return make_check("runtime.javascript_syntax", False, "node is missing")
    extension_root = REPO_ROOT / manifest["company_extension"]["root"]
    paths = sorted(extension_root.rglob("*.js"))
    paths.append(REPO_ROOT / "tools/company_content_sync/render_with_extension.js")
    failures: list[str] = []
    for path in paths:
        completed = run_command([node, "--check", str(path)])
        if completed.returncode != 0:
            failures.append(
                f"{posix_relative(path)}: {completed.stderr.strip() or completed.stdout.strip()}"
            )
    return make_check(
        "runtime.javascript_syntax",
        not failures,
        "; ".join(failures) if failures else f"node --check passed for {len(paths)} files",
    )


def json_probe(name: str, command: list[str]) -> dict[str, Any]:
    try:
        completed = run_command(command, timeout=180)
        if completed.returncode != 0:
            detail = completed.stderr.strip() or completed.stdout.strip()
            return make_check(name, False, detail[:500])
        report = json.loads(completed.stdout)
        ok = isinstance(report, dict) and report.get("ok") is True
        return make_check(name, ok, "reported ok=true" if ok else "JSON report did not contain ok=true")
    except Exception as exc:  # noqa: BLE001
        return make_check(name, False, str(exc))


def source_checks(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        check_python_runtime(manifest),
        check_requirements(manifest),
        check_node_lock(manifest),
        check_required_tracked(manifest),
        check_line_endings(manifest),
        check_python_sources(manifest),
        check_portable_docs(manifest),
        check_company_extension(manifest),
    ]


def runtime_checks(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    entrypoints = manifest["entrypoints"]
    return [
        check_installed_python_packages(manifest),
        check_node_runtime(manifest),
        check_installed_node_packages(manifest),
        check_javascript_syntax(manifest),
        json_probe(
            "runtime.wechat_capability",
            [sys.executable, str(REPO_ROOT / entrypoints["wechat"]), "capability", "--json"],
        ),
        json_probe(
            "runtime.company_doctor",
            [sys.executable, str(REPO_ROOT / entrypoints["company"]), "doctor", "--json"],
        ),
    ]


def build_report(manifest: dict[str, Any], *, source_only: bool) -> dict[str, Any]:
    checks = source_checks(manifest)
    if not source_only:
        checks.extend(runtime_checks(manifest))
    return {
        "schema_version": 1,
        "contract_id": manifest["contract_id"],
        "mode": "source-only" if source_only else "runtime",
        "ok": all(item["ok"] for item in checks),
        "checks": checks,
        "external_gates": manifest["external_gates"],
    }


def print_text_report(report: dict[str, Any]) -> None:
    for item in report["checks"]:
        label = "PASS" if item["ok"] else "FAIL"
        print(f"[{label}] {item['name']}: {item['detail']}")
    print("External gates (reported, never auto-installed or auto-authorized):")
    for gate in report["external_gates"]:
        print(f"  - {gate['id']}: {gate['required_for']}")
    if report["ok"]:
        if report["mode"] == "source-only":
            print("SOURCE CONTRACT READY")
        else:
            print("CLONE-LOCAL TOOLCHAIN READY")
    else:
        print("CLONE READINESS FAILED")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-only",
        action="store_true",
        help="Verify tracked files, pins, syntax, portability, and vendored assets without installed dependencies.",
    )
    parser.add_argument("--json", action="store_true", help="Emit a machine-readable report.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        manifest = read_json(MANIFEST_PATH)
        if manifest.get("schema_version") != 1:
            raise ValueError("unsupported workflow-toolchain schema_version")
        report = build_report(manifest, source_only=args.source_only)
    except Exception as exc:  # noqa: BLE001
        report = {
            "schema_version": 1,
            "contract_id": "CORE-PORTABILITY-001",
            "mode": "source-only" if args.source_only else "runtime",
            "ok": False,
            "checks": [make_check("manifest", False, str(exc))],
            "external_gates": [],
        }
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_text_report(report)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
