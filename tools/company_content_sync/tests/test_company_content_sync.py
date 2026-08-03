from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import uuid
import unittest
from pathlib import Path
from unittest import mock


MODULE_PATH = Path(__file__).resolve().parents[1] / "company_content_sync.py"
SPEC = importlib.util.spec_from_file_location("company_content_sync", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
FORMAT_ADAPTER = sys.modules["locked_format_adapter"]


class CompanyContentSyncTests(unittest.TestCase):
    def setUp(self) -> None:
        self.test_temp_root = Path(__file__).resolve().parent / "tmp"
        self.test_temp_root.mkdir(exist_ok=True)
        self.package = self.test_temp_root / (
            "company-content-sync-" + uuid.uuid4().hex
        )
        self.package.mkdir()
        self.journal_patcher = mock.patch.object(
            MODULE, "JOURNAL_ROOT", self.package / ".journal"
        )
        self.journal_patcher.start()

    def tearDown(self) -> None:
        self.journal_patcher.stop()
        shutil.rmtree(self.package)

    def write_package(
        self,
        *,
        status: str = "ready",
        body: str = "# 测试标题\n\n## 第一节\n\n正文。",
        adapter: str = "appsso",
        delivery_mode: str = "manual_editor",
        layout_profile: str = "default",
    ) -> None:
        self.package.joinpath("draft.md").write_text(
            "\n".join(
                [
                    "---",
                    'title: "测试标题"',
                    "platform: wechat",
                    f"status: {status}",
                    "---",
                    "",
                    body,
                    "",
                ]
            ),
            encoding="utf-8",
        )
        self.package.joinpath("publish.yml").write_text(
            "\n".join(
                [
                    f'project_adapter: "{adapter}"',
                    f'delivery_mode: "{delivery_mode}"',
                    f'layout_profile: "{layout_profile}"',
                    "",
                ]
            ),
            encoding="utf-8",
        )

    def prepare_push(self) -> dict[str, object]:
        MODULE.build_report(str(self.package))
        with mock.patch.object(MODULE, "run_content_validator"):
            return MODULE.feishu_prepare_push_report(
                str(self.package), "a" * 64, "fldcnCompanyTest"
            )

    def begin_push(self, report: dict[str, object]) -> dict[str, object]:
        with (
            mock.patch.object(MODULE, "run_content_validator"),
            mock.patch.object(
                MODULE, "live_feishu_connector_available", return_value=True
            ),
        ):
            return MODULE.feishu_begin_push_report(
                str(self.package),
                str(report["operation_id"]),
                str(report["authorization_scope_sha256"]),
            )

    def load_intent(self, report: dict[str, object]) -> tuple[dict, Path]:
        intent_path = self.package / str(report["intent_path"])
        return json.loads(intent_path.read_text(encoding="utf-8")), intent_path

    def write_push_receipt(
        self,
        report: dict[str, object],
        *,
        outcome: str = "confirmed",
        write_performed: object = True,
        body: str | None = None,
    ) -> Path:
        intent, intent_path = self.load_intent(report)
        operation_dir = intent_path.parent
        payload_path = self.package / intent["content"]["payload_path"]
        readback_body = (
            payload_path.read_text(encoding="utf-8") if body is None else body
        )
        readback_body = MODULE.normalize_collaboration_text(readback_body)
        body_path = operation_dir / "readback.md"
        body_path.write_text(readback_body, encoding="utf-8")
        assets_path = self.package / intent["content"]["assets_path"]
        assets = json.loads(assets_path.read_text(encoding="utf-8"))
        receipt = {
            "schema_version": MODULE.SCHEMA_VERSION,
            "protocol": MODULE.FEISHU_PROTOCOL_VERSION,
            "provider": "feishu",
            "operation": "push_create",
            "operation_id": intent["operation_id"],
            "intent_sha256": str(report["intent_sha256"]),
            "idempotency_key": intent["idempotency_key"],
            "authorization_scope_sha256": str(report["authorization_scope_sha256"]),
            "outcome": outcome,
            "write_performed": write_performed,
            "completed_at": MODULE.load_sync_state(self.package)["dispatch"][
                "claimed_at"
            ],
        }
        if outcome == "confirmed":
            receipt.update(
                {
                    "mcp": {
                        "server_id": MODULE.FEISHU_MCP_SERVER_ID,
                        "write_tool": "create-doc",
                        "write_call_id": "write-call-1",
                        "write_result_is_error": False,
                        "write_response_sha256": "b" * 64,
                        "read_tool": "fetch-doc",
                        "read_call_id": "read-call-1",
                        "read_result_is_error": False,
                        "read_response_sha256": "c" * 64,
                    },
                    "access": {
                        "tenant_fingerprint": intent["target"]["tenant_fingerprint"],
                        "parent_fingerprint": intent["target"]["parent_fingerprint"],
                        "acl_verified": True,
                        "public_access": False,
                        "external_shared": False,
                    },
                    "observed": {
                        "document_id": "doccnCompanyTest",
                        "document_url": (
                            "https://company.feishu.cn/docx/doccnCompanyTest"
                        ),
                        "revision": "revision-1",
                        "title": intent["content"]["title"],
                        "body_path": body_path.relative_to(self.package).as_posix(),
                        "body_sha256": MODULE.sha256_bytes(
                            readback_body.encode("utf-8")
                        ),
                        "asset_mappings": [
                            {
                                "order": item["order"],
                                "source_sha256": item["sha256"],
                                "remote_token": f"remote-{item['order']}",
                                "resolved": True,
                            }
                            for item in assets
                        ],
                    },
                }
            )
        receipt_path = operation_dir / "receipt.json"
        receipt_path.write_text(
            json.dumps(receipt, ensure_ascii=False), encoding="utf-8"
        )
        return receipt_path

    def commit_push(self) -> dict[str, object]:
        report = self.prepare_push()
        self.begin_push(report)
        receipt_path = self.write_push_receipt(report)
        return MODULE.feishu_commit_push_report(str(self.package), str(receipt_path))

    def write_pull_receipt(
        self,
        report: dict[str, object],
        body: str,
        *,
        title: str = "测试标题",
    ) -> Path:
        intent, intent_path = self.load_intent(report)
        operation_dir = intent_path.parent
        normalized_body = MODULE.normalize_collaboration_text(body)
        body_path = operation_dir / "readback.md"
        body_path.write_text(normalized_body, encoding="utf-8")
        snapshot = MODULE.collaboration_snapshot(
            self.package,
            title,
            normalized_body,
            validate_markdown=not normalized_body.startswith("---\n"),
        )
        receipt = {
            "schema_version": MODULE.SCHEMA_VERSION,
            "protocol": MODULE.FEISHU_PROTOCOL_VERSION,
            "provider": "feishu",
            "operation": "pull_read",
            "operation_id": intent["operation_id"],
            "intent_sha256": str(report["intent_sha256"]),
            "idempotency_key": intent["idempotency_key"],
            "outcome": "confirmed",
            "write_performed": False,
            "completed_at": "2026-07-27T12:10:00+09:00",
            "mcp": {
                "server_id": MODULE.FEISHU_MCP_SERVER_ID,
                "read_tool": "fetch-doc",
                "read_call_id": "read-call-2",
                "read_result_is_error": False,
                "read_response_sha256": "d" * 64,
            },
            "access": {
                "tenant_fingerprint": intent["target"]["tenant_fingerprint"],
                "acl_verified": True,
                "public_access": False,
                "external_shared": False,
            },
            "observed": {
                "document_id": intent["target"]["document_id"],
                "revision": "revision-2",
                "title": title,
                "body_path": body_path.relative_to(self.package).as_posix(),
                "body_sha256": MODULE.sha256_bytes(normalized_body.encode("utf-8")),
                "asset_mappings": [
                    {
                        "order": item["order"],
                        "source_sha256": item["sha256"],
                        "remote_token": f"remote-{item['order']}",
                        "resolved": True,
                    }
                    for item in snapshot["assets"]
                ],
            },
        }
        receipt_path = operation_dir / "receipt.json"
        receipt_path.write_text(
            json.dumps(receipt, ensure_ascii=False), encoding="utf-8"
        )
        return receipt_path

    def test_doctor_verifies_locked_sources(self) -> None:
        report = MODULE.doctor_report()
        self.assertTrue(report["ok"], report["blockers"])
        self.assertIn("feishu_remote_mcp", report["connectors"])
        self.assertTrue(report["qualification"]["local_build_capable"])
        self.assertFalse(report["qualification"]["production_qualified"])
        self.assertFalse(report["qualification"]["evidence_receipt_verified"])
        self.assertIn(
            "qualification_receipt_path_missing",
            report["qualification"]["binding_issues"],
        )
        self.assertTrue(
            all(item["verified"] for item in report["format"]["verified_files"])
        )

    def test_feishu_connector_doctor_without_config(self) -> None:
        codex_home = self.package / "codex-home"
        codex_home.mkdir()
        codex_home.joinpath("config.toml").write_text(
            'model = "gpt-test"\n', encoding="utf-8"
        )
        with mock.patch.object(MODULE.os, "environ", {"CODEX_HOME": str(codex_home)}):
            report = MODULE.feishu_remote_mcp_report()

        self.assertEqual(
            {
                "config_present",
                "config_valid",
                "credential_env_present",
                "restart_required_or_unknown",
                "host_tools_attested",
                "trusted_executor_available",
                "safe_config_template",
            },
            set(report),
        )
        self.assertFalse(report["config_present"])
        self.assertFalse(report["config_valid"])
        self.assertFalse(report["credential_env_present"])
        self.assertFalse(report["restart_required_or_unknown"])
        self.assertFalse(report["host_tools_attested"])
        self.assertFalse(report["trusted_executor_available"])

    def test_feishu_connector_doctor_accepts_safe_config(self) -> None:
        codex_home = self.package / "codex-home"
        codex_home.mkdir()
        codex_home.joinpath("config.toml").write_text(
            MODULE.FEISHU_REMOTE_MCP_SAFE_CONFIG_TEMPLATE,
            encoding="utf-8",
        )
        secret_sentinel = "must-never-appear-in-report"
        environment = {
            "CODEX_HOME": str(codex_home),
            MODULE.FEISHU_REMOTE_MCP_CREDENTIAL_ENV: secret_sentinel,
        }
        with mock.patch.object(MODULE.os, "environ", environment):
            report = MODULE.feishu_remote_mcp_report()
            command_report = MODULE.connector_doctor_report()

        self.assertTrue(report["config_present"])
        self.assertTrue(report["config_valid"])
        self.assertTrue(report["credential_env_present"])
        self.assertTrue(report["restart_required_or_unknown"])
        self.assertFalse(report["host_tools_attested"])
        self.assertFalse(report["trusted_executor_available"])
        self.assertNotIn(secret_sentinel, json.dumps(command_report))
        self.assertEqual(
            "connector-doctor",
            MODULE.parser().parse_args(["connector-doctor", "--json"]).command,
        )

    def test_feishu_connector_requires_exact_host_tool_attestation(self) -> None:
        codex_home = self.package / "codex-home"
        codex_home.mkdir()
        codex_home.joinpath("config.toml").write_text(
            MODULE.FEISHU_REMOTE_MCP_SAFE_CONFIG_TEMPLATE,
            encoding="utf-8",
        )
        base_environment = {
            "CODEX_HOME": str(codex_home),
            MODULE.FEISHU_REMOTE_MCP_CREDENTIAL_ENV: "guarded-secret",
        }
        environment = {
            **base_environment,
            MODULE.FEISHU_REMOTE_MCP_HOST_ATTESTATION_ENV: "create-doc,fetch-doc",
        }
        with mock.patch.object(MODULE.os, "environ", environment):
            report = MODULE.feishu_remote_mcp_report()
            self.assertTrue(MODULE.live_feishu_connector_available())

        self.assertTrue(report["host_tools_attested"])
        self.assertTrue(report["trusted_executor_available"])
        self.assertFalse(report["restart_required_or_unknown"])

        wrong_environment = {
            **base_environment,
            MODULE.FEISHU_REMOTE_MCP_HOST_ATTESTATION_ENV: "fetch-doc,create-doc",
        }
        with mock.patch.object(MODULE.os, "environ", wrong_environment):
            wrong_report = MODULE.feishu_remote_mcp_report()
        self.assertFalse(wrong_report["host_tools_attested"])
        self.assertFalse(wrong_report["trusted_executor_available"])

    def test_feishu_connector_doctor_rejects_wrong_tools_or_header(self) -> None:
        codex_home = self.package / "codex-home"
        codex_home.mkdir()
        cases = {
            "wrong_local_allowlist": MODULE.FEISHU_REMOTE_MCP_SAFE_CONFIG_TEMPLATE.replace(
                'enabled_tools = ["create-doc", "fetch-doc"]',
                'enabled_tools = ["create-doc", "update-doc"]',
            ),
            "wrong_remote_header": MODULE.FEISHU_REMOTE_MCP_SAFE_CONFIG_TEMPLATE.replace(
                '"create-doc,fetch-doc"',
                '"create-doc,fetch-doc,update-doc"',
                1,
            ),
            "wrong_approval_mode": MODULE.FEISHU_REMOTE_MCP_SAFE_CONFIG_TEMPLATE.replace(
                'default_tools_approval_mode = "prompt"',
                'default_tools_approval_mode = "auto"',
            ),
            "extra_static_header": MODULE.FEISHU_REMOTE_MCP_SAFE_CONFIG_TEMPLATE.replace(
                'http_headers = { "X-Lark-MCP-Allowed-Tools" = "create-doc,fetch-doc" }',
                'http_headers = { "X-Lark-MCP-Allowed-Tools" = "create-doc,fetch-doc", "X-Debug" = "1" }',
            ),
            "extra_tat_mapping": MODULE.FEISHU_REMOTE_MCP_SAFE_CONFIG_TEMPLATE.replace(
                'env_http_headers = { "X-Lark-MCP-UAT" = "FEISHU_MCP_UAT" }',
                'env_http_headers = { "X-Lark-MCP-UAT" = "FEISHU_MCP_UAT", "X-Lark-MCP-TAT" = "FEISHU_MCP_TAT" }',
            ),
            "bearer_token": (
                MODULE.FEISHU_REMOTE_MCP_SAFE_CONFIG_TEMPLATE
                + 'bearer_token_env_var = "UNRELATED_TOKEN"\n'
            ),
        }
        for name, config in cases.items():
            with self.subTest(name=name):
                codex_home.joinpath("config.toml").write_text(config, encoding="utf-8")
                with mock.patch.object(
                    MODULE.os, "environ", {"CODEX_HOME": str(codex_home)}
                ):
                    report = MODULE.feishu_remote_mcp_report()
                self.assertTrue(report["config_present"])
                self.assertFalse(report["config_valid"])

    def test_feishu_connector_doctor_checks_only_credential_key_presence(
        self,
    ) -> None:
        codex_home = self.package / "codex-home"
        codex_home.mkdir()
        codex_home.joinpath("config.toml").write_text(
            MODULE.FEISHU_REMOTE_MCP_SAFE_CONFIG_TEMPLATE,
            encoding="utf-8",
        )

        class PresenceOnlyEnvironment(dict[str, str]):
            def __getitem__(self, key: str) -> str:
                if key == MODULE.FEISHU_REMOTE_MCP_CREDENTIAL_ENV:
                    raise AssertionError("credential value was read")
                return super().__getitem__(key)

            def get(self, key: str, default: str | None = None) -> str | None:
                if key == MODULE.FEISHU_REMOTE_MCP_CREDENTIAL_ENV:
                    raise AssertionError("credential value was read")
                return super().get(key, default)

        environment = PresenceOnlyEnvironment(
            {
                "CODEX_HOME": str(codex_home),
                MODULE.FEISHU_REMOTE_MCP_CREDENTIAL_ENV: "guarded-secret",
            }
        )
        with mock.patch.object(MODULE.os, "environ", environment):
            report = MODULE.feishu_remote_mcp_report()

        self.assertTrue(report["credential_env_present"])
        self.assertNotIn("guarded-secret", json.dumps(report))

    def test_format_contract_ignores_control_plane_identity(self) -> None:
        baseline = MODULE.doctor_report()

        with (
            mock.patch.object(MODULE, "__file__", str(self.package / "control.py")),
            mock.patch.object(MODULE, "TOOL_VERSION", "99.0-control-only"),
        ):
            changed = MODULE.doctor_report()

        self.assertEqual(
            baseline["format"]["adapter_sha256"],
            changed["format"]["adapter_sha256"],
        )
        self.assertEqual(
            baseline["format"]["format_contract_sha256"],
            changed["format"]["format_contract_sha256"],
        )

    def test_profile_roles_are_unique_and_required(self) -> None:
        baseline, _profile_sha256 = MODULE.load_profile()
        cases = (
            ("source_files", "role", "markdown_adapter", "missing"),
            ("source_files", "role", "renderer_bridge", "missing"),
            ("source_files", "role", "renderer_and_semantics", "missing"),
            ("brand_assets", "id", "appso_title", "missing"),
            ("source_files", "role", "markdown_adapter", "duplicate"),
            ("source_files", "role", "renderer_bridge", "duplicate"),
            ("source_files", "role", "renderer_and_semantics", "duplicate"),
            ("brand_assets", "id", "appso_title", "duplicate"),
        )
        for collection, key, identifier, mode in cases:
            with self.subTest(identifier=identifier, mode=mode):
                profile = json.loads(json.dumps(baseline))
                matches = [
                    item for item in profile[collection] if item.get(key) == identifier
                ]
                self.assertEqual(1, len(matches))
                if mode == "missing":
                    profile[collection] = [
                        item
                        for item in profile[collection]
                        if item.get(key) != identifier
                    ]
                else:
                    profile[collection].append(dict(matches[0]))
                profile_sha256 = MODULE.sha256_bytes(MODULE.canonical_json(profile))
                with mock.patch.object(
                    MODULE,
                    "load_profile",
                    return_value=(profile, profile_sha256),
                ):
                    report = MODULE.doctor_report()
                self.assertFalse(report["ok"])
                self.assertTrue(report["blockers"])

    def test_runtime_dependency_versions_are_exact(self) -> None:
        original_version = FORMAT_ADAPTER.importlib.metadata.version

        def changed_version(name: str) -> str:
            if name == "mdurl":
                return "9.9.9"
            return original_version(name)

        with mock.patch.object(
            FORMAT_ADAPTER.importlib.metadata,
            "version",
            side_effect=changed_version,
        ):
            report = MODULE.doctor_report()

        self.assertFalse(report["ok"])
        self.assertTrue(
            any("dependency version mismatch" in item for item in report["blockers"])
        )

    def test_qualification_only_change_preserves_format_contract_and_build(
        self,
    ) -> None:
        self.write_package()
        built = MODULE.build_report(str(self.package))
        profile, _profile_sha256 = MODULE.load_profile()
        baseline = MODULE.doctor_report()
        changed_profile = json.loads(json.dumps(profile))
        changed_profile["qualification"]["audit_note"] = "qualification-only change"
        changed_profile_sha256 = MODULE.sha256_bytes(
            MODULE.canonical_json(changed_profile)
        )

        with mock.patch.object(
            MODULE,
            "load_profile",
            return_value=(changed_profile, changed_profile_sha256),
        ):
            changed_doctor = MODULE.doctor_report()
            status = MODULE.status_report(str(self.package))

        self.assertNotEqual(
            built["profile_sha256"], changed_doctor["format"]["profile_sha256"]
        )
        self.assertEqual(
            baseline["format"]["format_contract_sha256"],
            changed_doctor["format"]["format_contract_sha256"],
        )
        self.assertFalse(status["build"]["stale"])

    def test_markdown_validation_does_not_read_or_embed_image_bytes(self) -> None:
        self.write_package(body="# 测试标题\n\n## 第一节\n\n![示例](image.png)")
        image_path = self.package / "image.png"
        image_path.write_bytes(b"\x89PNG\r\n\x1a\n")

        with mock.patch.object(
            Path, "read_bytes", side_effect=AssertionError("image bytes were read")
        ):
            blocks, image_bytes = MODULE.markdown_blocks(
                "# 测试标题\n\n## 第一节\n\n![示例](image.png)\n",
                self.package,
                "测试标题",
                embed_images=False,
            )

        self.assertEqual(image_path.stat().st_size, image_bytes)
        image_block = next(block for block in blocks if block["type"] == "image")
        self.assertNotIn("dataUri", image_block["image"])

    def test_locked_format_golden_fixture_is_deterministic(self) -> None:
        shutil.rmtree(self.package)
        self.package = self.test_temp_root / "company-content-sync-format-golden"
        if self.package.exists():
            shutil.rmtree(self.package)
        self.package.mkdir()
        body = "\n".join(
            [
                "# 测试标题",
                "",
                "## 第一节",
                "",
                "正文含 **粗体**、*斜体*、[链接](https://example.com) 和 `code`。  ",
                "下一行。",
                "",
                "> 这是引用。",
                "",
                "- 无序项目",
                "",
                "1. 有序项目",
                "",
                "```python",
                "print('hello')",
                "```",
                "",
                "---",
                "",
                "![单图](one.png)",
                "",
                "![画廊一](one.png)",
                "![画廊二](two.png)",
                "",
                "### 第二层标题",
                "",
                "结尾。",
            ]
        )
        self.write_package(body=body)
        tiny_png = bytes.fromhex(
            "89504e470d0a1a0a0000000d494844520000000100000001"
            "08060000001f15c4890000000d49444154789c636000000002"
            "0001e221bc330000000049454e44ae426082"
        )
        (self.package / "one.png").write_bytes(tiny_png)
        (self.package / "two.png").write_bytes(tiny_png)

        first = MODULE.build_report(str(self.package))
        second = MODULE.build_report(str(self.package))
        actual = {
            "payload_sha256": first["payload_sha256"],
            "fixture_sha256": first["fixture_sha256"],
            "html_sha256": first["html_sha256"],
            "sealed_build_sha256": first["sealed_build_sha256"],
            "block_count": first["block_count"],
            "image_count": first["image_count"],
            "gallery_count": first["gallery_count"],
            "warning_codes": first["warning_codes"],
        }
        expected = {
            "payload_sha256": "863bbf616ad8811a5390bae81881dd0fc95cc69ce402b1206a848ea2f466670d",
            "fixture_sha256": "cbfbbdef59be041f9b9c2d5bd56ab03d15a853918e0efaab95138a1d05fe434b",
            "html_sha256": "fc00fc187c2e0976ca1b95f448ac14ea774856245229eeb4587adb9072a9efe3",
            "sealed_build_sha256": "90b54d942cac912f8005b134839e339387701d8243c189636a2f9e03ccfdaf29",
            "block_count": 11,
            "image_count": 4,
            "gallery_count": 1,
            "warning_codes": [],
        }

        self.assertEqual(expected, actual)
        for field in (
            "payload_sha256",
            "fixture_sha256",
            "html_sha256",
            "sealed_build_sha256",
        ):
            self.assertEqual(first[field], second[field])

    def test_configure_company_route_is_safe_and_idempotent(self) -> None:
        self.write_package(adapter="other")
        with self.assertRaisesRegex(MODULE.WorkflowError, "conflicting"):
            MODULE.configure_company_report(str(self.package))
        self.assertIn(
            'project_adapter: "other"',
            (self.package / "publish.yml").read_text(encoding="utf-8"),
        )

        (self.package / "publish.yml").write_text(
            "existing_field: keep\n", encoding="utf-8"
        )
        first = MODULE.configure_company_report(str(self.package))
        second = MODULE.configure_company_report(str(self.package))
        publish_text = (self.package / "publish.yml").read_text(encoding="utf-8")

        self.assertTrue(first["changed"])
        self.assertFalse(second["changed"])
        self.assertIn("existing_field: keep", publish_text)
        self.assertIn('project_adapter: "appsso"', publish_text)
        self.assertIn('delivery_mode: "manual_editor"', publish_text)
        self.assertIn('layout_profile: "default"', publish_text)

    def test_partial_company_route_is_completed_without_overwriting_choices(
        self,
    ) -> None:
        self.write_package()
        publish_path = self.package / "publish.yml"
        publish_path.write_text('project_adapter: "appsso"\n', encoding="utf-8")

        status = MODULE.status_report(str(self.package))

        self.assertEqual("configure_company_route", status["next_action"]["id"])
        self.assertIn("company_route_incomplete", status["workflow_blockers"])
        configured = MODULE.configure_company_report(str(self.package))
        self.assertEqual(
            ["delivery_mode", "layout_profile"], configured["added_fields"]
        )

        publish_path.write_text(
            "\n".join(
                [
                    'project_adapter: "appsso"',
                    'delivery_mode: "sealed_draft"',
                    "",
                ]
            ),
            encoding="utf-8",
        )
        incomplete = MODULE.status_report(str(self.package))
        self.assertEqual("complete_company_route", incomplete["next_action"]["id"])
        with self.assertRaisesRegex(MODULE.WorkflowError, "conflicting"):
            MODULE.configure_company_report(str(self.package))

    def test_fake_qualification_strings_cannot_enable_production(self) -> None:
        profile, _profile_sha256 = MODULE.load_profile()
        baseline = MODULE.doctor_report()
        account_fingerprint = "a" * 64
        qualified_at = "2026-07-27T00:00:00+09:00"
        profile["qualification"] = {
            "local_fixture_qualified": True,
            "wechat_roundtrip_qualified": True,
            "production_qualified": True,
            "scope": {
                "profile_id": profile["profile_id"],
                "format_contract_sha256": baseline["format"]["format_contract_sha256"],
                "renderer_sha256": baseline["format"]["renderer_sha256"],
                "delivery_mode": "sealed_draft",
                "layout_profile": "appsso-article-v1",
                "wechat_account_fingerprint": account_fingerprint,
            },
            "evidence": {
                "record_id": "fake-record",
                "receipt_path": (self.package / "missing-qualification-receipt.json")
                .relative_to(MODULE.REPO_ROOT)
                .as_posix(),
                "receipt_sha256": "b" * 64,
                "qualified_at": qualified_at,
            },
        }
        profile_sha256 = MODULE.sha256_bytes(MODULE.canonical_json(profile))

        with mock.patch.object(
            MODULE,
            "load_profile",
            return_value=(profile, profile_sha256),
        ):
            report = MODULE.doctor_report()

        self.assertFalse(report["qualification"]["production_qualified"])
        self.assertIn(
            "qualification_receipt_unreadable",
            report["qualification"]["binding_issues"],
        )

    def test_verified_receipt_can_enable_exact_qualification(self) -> None:
        profile, _profile_sha256 = MODULE.load_profile()
        baseline = MODULE.doctor_report()
        account_fingerprint = "a" * 64
        qualified_at = "2026-07-27T00:00:00+09:00"
        scope = {
            "profile_id": profile["profile_id"],
            "format_contract_sha256": baseline["format"]["format_contract_sha256"],
            "renderer_sha256": baseline["format"]["renderer_sha256"],
            "delivery_mode": "sealed_draft",
            "layout_profile": "appsso-article-v1",
            "wechat_account_fingerprint": account_fingerprint,
        }
        receipt = {
            **scope,
            **{field: True for field in MODULE.QUALIFICATION_CONFIRMATIONS},
            "record_id": "verified-record",
            "qualified_at": qualified_at,
        }
        receipt_raw = MODULE.canonical_json(receipt)
        receipt_path = self.package / "qualification-receipt.json"
        receipt_path.write_bytes(receipt_raw)
        profile["qualification"] = {
            "local_fixture_qualified": True,
            "wechat_roundtrip_qualified": True,
            "production_qualified": True,
            "scope": scope,
            "evidence": {
                "record_id": "verified-record",
                "receipt_path": receipt_path.relative_to(MODULE.REPO_ROOT).as_posix(),
                "receipt_sha256": MODULE.sha256_bytes(receipt_raw),
                "qualified_at": qualified_at,
            },
        }
        profile_sha256 = MODULE.sha256_bytes(MODULE.canonical_json(profile))

        with mock.patch.object(
            MODULE,
            "load_profile",
            return_value=(profile, profile_sha256),
        ):
            report = MODULE.doctor_report()

        self.assertTrue(report["qualification"]["production_qualified"])
        self.assertTrue(report["qualification"]["evidence_receipt_verified"])
        self.assertEqual([], report["qualification"]["binding_issues"])

        receipt["save_confirmed"] = 1
        numeric_receipt_raw = MODULE.canonical_json(receipt)
        receipt_path.write_bytes(numeric_receipt_raw)
        profile["qualification"]["evidence"]["receipt_sha256"] = MODULE.sha256_bytes(
            numeric_receipt_raw
        )
        numeric_profile_sha256 = MODULE.sha256_bytes(MODULE.canonical_json(profile))
        with mock.patch.object(
            MODULE,
            "load_profile",
            return_value=(profile, numeric_profile_sha256),
        ):
            numeric_report = MODULE.doctor_report()

        self.assertFalse(numeric_report["qualification"]["production_qualified"])
        self.assertIn(
            "qualification_receipt_save_confirmed_mismatch",
            numeric_report["qualification"]["binding_issues"],
        )

    def test_ready_local_package_has_one_planned_feishu_action(self) -> None:
        self.write_package()
        report = MODULE.status_report(str(self.package))
        self.assertEqual("run_local_build", report["next_action"]["id"])
        self.assertTrue(report["next_action"]["implemented"])
        self.assertFalse(report["next_action"]["external_write"])
        self.assertFalse(report["next_action"]["authorization_required"])
        self.assertFalse(report["external_writes_performed"])

        MODULE.build_report(str(self.package))
        report = MODULE.status_report(str(self.package))
        self.assertEqual("prepare_feishu_create", report["next_action"]["id"])
        self.assertTrue(report["next_action"]["implemented"])
        self.assertFalse(report["next_action"]["external_write"])
        self.assertFalse(report["next_action"]["authorization_required"])
        self.assertEqual(
            ["tenant_fingerprint"],
            report["next_action"]["required_inputs"],
        )
        self.assertFalse(report["external_writes_performed"])

    def test_feishu_prepare_defaults_to_my_library_wiki_space(self) -> None:
        self.write_package()
        MODULE.build_report(str(self.package))
        with mock.patch.object(MODULE, "run_content_validator"):
            report = MODULE.feishu_prepare_push_report(
                str(self.package),
                "a" * 64,
            )

        intent, _intent_path = self.load_intent(report)
        self.assertEqual("my_library", intent["target"]["parent_id"])
        self.assertEqual("wiki_space", intent["target"]["parent_kind"])
        self.assertEqual(
            "wiki_space",
            intent["connector_contract"]["write_target_parameter"],
        )

    def write_locally_qualified_build(self, phase: str) -> None:
        self.write_sync_phase(phase)
        state_path = self.package / "dist" / "content-sync" / "state.json"
        state_path.with_name("build.json").write_text(
            json.dumps(
                {
                    "local_format_qualified": True,
                    "warning_codes": [],
                    "html_sha256": "a" * 64,
                }
            ),
            encoding="utf-8",
        )

    def status_with_valid_build(self) -> dict[str, object]:
        with mock.patch.object(
            MODULE,
            "build_integrity",
            return_value=([], "a" * 64),
        ):
            return MODULE.status_report(str(self.package))

    def test_local_only_valid_build_does_not_preempt_feishu_push(self) -> None:
        self.write_package()
        self.write_locally_qualified_build("local_only")
        report = self.status_with_valid_build()
        self.assertEqual("prepare_feishu_create", report["next_action"]["id"])
        self.assertNotIn("company_format_not_qualified", report["workflow_blockers"])
        self.assertTrue(report["workflow_ready"])

    def test_sealed_api_route_requires_company_format_qualification(self) -> None:
        self.write_package(
            delivery_mode="sealed_draft",
            layout_profile="appsso-article-v1",
        )
        self.write_locally_qualified_build("sealed")
        report = self.status_with_valid_build()
        self.assertEqual("qualify_company_format", report["next_action"]["id"])
        self.assertIn("company_format_not_qualified", report["workflow_blockers"])
        self.assertFalse(report["workflow_ready"])

    def test_manual_route_does_not_claim_company_qualification_blocker(self) -> None:
        self.write_package()
        self.write_locally_qualified_build("sealed")
        report = self.status_with_valid_build()
        self.assertEqual("select_api_delivery_route", report["next_action"]["id"])
        self.assertNotIn("company_format_not_qualified", report["workflow_blockers"])
        self.assertTrue(report["workflow_ready"])

    def test_conflict_is_the_only_next_action(self) -> None:
        self.write_package()
        state = self.package / "dist" / "content-sync" / "state.json"
        state.parent.mkdir(parents=True)
        state.write_text('{"phase":"conflict"}', encoding="utf-8")
        report = MODULE.status_report(str(self.package))
        self.assertEqual("resolve_sync_conflict", report["next_action"]["id"])
        self.assertFalse(report["next_action"]["external_write"])

    def test_status_is_read_only(self) -> None:
        self.write_package(status="draft")
        before = sorted(
            path.relative_to(self.package) for path in self.package.rglob("*")
        )
        report = MODULE.status_report(str(self.package))
        after = sorted(
            path.relative_to(self.package) for path in self.package.rglob("*")
        )
        self.assertEqual(before, after)
        self.assertEqual("$self-media-ops", report["next_action"]["handler"])
        self.assertTrue(report["next_action"]["implemented"])
        self.assertIn("lifecycle_not_ready", report["workflow_blockers"])
        self.assertTrue(report["operational_ok"])
        self.assertFalse(report["workflow_ready"])
        self.assertFalse(report["ok"])

    @unittest.skipUnless(shutil.which("node"), "Node.js is required")
    def test_build_uses_locked_renderer_and_writes_sealed_html(self) -> None:
        self.write_package(
            body=(
                "# 测试标题\n\n"
                "## 第一节\n\n"
                "正文有 **重点** 和 [链接](https://example.com)。\n\n"
                "> 一段引用。\n"
            )
        )
        report = MODULE.build_report(str(self.package))
        html_path = self.package / "dist" / "content-sync" / "article.html"
        receipt_path = self.package / "dist" / "content-sync" / "build.json"
        rendered = html_path.read_text(encoding="utf-8")
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))

        self.assertIn("font-size:22px", rendered)
        self.assertIn("font-size:15px", rendered)
        self.assertIn('data-ifanr-title-brand="appso"', rendered)
        self.assertTrue(report["local_format_qualified"])
        self.assertFalse(report["company_format_qualified"])
        self.assertEqual(report["sealed_build_sha256"], receipt["sealed_build_sha256"])

    def write_sync_phase(self, phase: str) -> None:
        state = MODULE.default_sync_state()
        state.update(
            {
                "phase": phase,
                "tenant_fingerprint": "a" * 64,
                "document_id": "doccnCompanyTest",
                "document_fingerprint": "e" * 64,
                "base_sha256": "b" * 64,
                "base_body_sha256": "c" * 64,
                "base_assets_sha256": "d" * 64,
                "remote_sha256": "b" * 64,
                "remote_revision": "revision-1",
                "last_synced_at": "2026-07-27T12:00:00+09:00",
            }
        )
        MODULE.write_sync_state(self.package, state)

    def test_prepare_push_is_local_idempotent_and_authorization_bound(self) -> None:
        self.write_package()
        draft_before = self.package.joinpath("draft.md").read_bytes()
        publish_before = self.package.joinpath("publish.yml").read_bytes()

        first = self.prepare_push()
        second = self.prepare_push()

        self.assertEqual(first["operation_id"], second["operation_id"])
        self.assertEqual(first["idempotency_key"], second["idempotency_key"])
        self.assertFalse(first["replayed"])
        self.assertTrue(second["replayed"])
        self.assertTrue(first["authorization_required_for_execution"])
        self.assertFalse(first["external_writes_performed"])
        self.assertEqual(draft_before, self.package.joinpath("draft.md").read_bytes())
        self.assertEqual(
            publish_before, self.package.joinpath("publish.yml").read_bytes()
        )
        state = MODULE.load_sync_state(self.package)
        self.assertEqual("push_prepared", state["phase"])
        status = MODULE.status_report(str(self.package))
        self.assertEqual(
            "integrate_trusted_feishu_executor", status["next_action"]["id"]
        )
        self.assertFalse(status["next_action"]["authorization_required"])
        self.assertTrue(status["capabilities"]["feishu_protocol"])
        self.assertFalse(status["capabilities"]["feishu_connector_connected"])
        claim_path = MODULE.dispatch_claim_file(
            self.package, str(first["operation_id"])
        )
        with self.assertRaisesRegex(MODULE.WorkflowError, "executor is unavailable"):
            MODULE.feishu_begin_push_report(
                str(self.package),
                str(first["operation_id"]),
                str(first["authorization_scope_sha256"]),
            )
        self.assertFalse(claim_path.exists())
        self.assertEqual("push_prepared", MODULE.load_sync_state(self.package)["phase"])
        with mock.patch.object(
            MODULE, "live_feishu_connector_available", return_value=True
        ):
            connected_status = MODULE.status_report(str(self.package))
        self.assertEqual("begin_feishu_create", connected_status["next_action"]["id"])
        self.assertTrue(connected_status["next_action"]["authorization_required"])

    def test_confirmed_push_requires_readback_and_receipt_replays(self) -> None:
        self.write_package()
        prepared = self.prepare_push()
        self.begin_push(prepared)
        receipt_path = self.write_push_receipt(prepared)

        committed = MODULE.feishu_commit_push_report(
            str(self.package), str(receipt_path)
        )
        replayed = MODULE.feishu_commit_push_report(
            str(self.package), str(receipt_path)
        )

        self.assertEqual("feishu_synced", committed["phase"])
        self.assertTrue(committed["remote_revision_present"])
        self.assertEqual(
            "https://company.feishu.cn/docx/doccnCompanyTest",
            committed["document_url"],
        )
        self.assertFalse(committed["external_writes_performed"])
        self.assertTrue(replayed["replayed"])
        self.assertEqual(committed["document_url"], replayed["document_url"])
        state = MODULE.load_sync_state(self.package)
        self.assertEqual(state["base_sha256"], state["remote_sha256"])
        self.assertNotIn("document_id", MODULE.status_report(str(self.package))["sync"])
        self.assertEqual(
            committed["document_url"],
            MODULE.status_report(str(self.package))["sync"]["document_url"],
        )

    def test_push_receipt_rejects_untrusted_document_url(self) -> None:
        self.write_package()
        prepared = self.prepare_push()
        self.begin_push(prepared)
        receipt_path = self.write_push_receipt(prepared)
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        receipt["observed"]["document_url"] = (
            "https://company.feishu.cn/docx/doccnCompanyTest?share=public"
        )
        receipt_path.write_text(
            json.dumps(receipt, ensure_ascii=False), encoding="utf-8"
        )

        with self.assertRaisesRegex(MODULE.WorkflowError, "document_url"):
            MODULE.feishu_commit_push_report(str(self.package), str(receipt_path))

        self.assertEqual(
            "result_unknown", MODULE.load_sync_state(self.package)["phase"]
        )

    def test_numeric_success_boolean_locks_result_unknown(self) -> None:
        self.write_package()
        prepared = self.prepare_push()
        self.begin_push(prepared)
        receipt_path = self.write_push_receipt(prepared, write_performed=1)

        with self.assertRaisesRegex(MODULE.WorkflowError, "write_performed true"):
            MODULE.feishu_commit_push_report(str(self.package), str(receipt_path))

        state = MODULE.load_sync_state(self.package)
        self.assertEqual("result_unknown", state["phase"])
        status = MODULE.status_report(str(self.package))
        self.assertEqual("reconcile_feishu_result", status["next_action"]["id"])
        self.assertIn("external_result_unknown", status["workflow_blockers"])
        self.assertNotIn("公众号后台", status["next_action"]["reason"])

    def test_explicit_unknown_receipt_never_retries_create(self) -> None:
        self.write_package()
        prepared = self.prepare_push()
        self.begin_push(prepared)
        receipt_path = self.write_push_receipt(
            prepared, outcome="result_unknown", write_performed=None
        )

        report = MODULE.feishu_commit_push_report(str(self.package), str(receipt_path))

        self.assertFalse(report["ok"])
        self.assertEqual("result_unknown", report["phase"])
        with mock.patch.object(MODULE, "run_content_validator"):
            with self.assertRaisesRegex(MODULE.WorkflowError, "unavailable"):
                MODULE.feishu_prepare_push_report(
                    str(self.package), "a" * 64, "fldcnCompanyTest"
                )

    def test_pull_remote_change_stages_without_touching_draft(self) -> None:
        self.write_package()
        self.commit_push()
        draft_before = self.package.joinpath("draft.md").read_bytes()
        _meta, body, _raw = MODULE.read_draft(self.package / "draft.md")
        prepared = MODULE.feishu_prepare_pull_report(str(self.package))
        receipt_path = self.write_pull_receipt(prepared, body + "\n团队修改。\n")

        report = MODULE.feishu_stage_pull_report(str(self.package), str(receipt_path))

        self.assertEqual("remote_dirty", report["phase"])
        self.assertEqual("remote_change_staged", report["outcome"])
        self.assertFalse(report["draft_modified"])
        self.assertEqual(draft_before, self.package.joinpath("draft.md").read_bytes())
        status = MODULE.status_report(str(self.package))
        self.assertEqual("accept_feishu_pull", status["next_action"]["id"])

    def test_accept_pull_reopens_editorial_and_copyedit_gates(self) -> None:
        self.write_package()
        self.commit_push()
        publish_before = self.package.joinpath("publish.yml").read_bytes()
        _meta, body, _raw = MODULE.read_draft(self.package / "draft.md")
        prepared = MODULE.feishu_prepare_pull_report(str(self.package))
        receipt_path = self.write_pull_receipt(prepared, body + "\n团队修改。\n")
        MODULE.feishu_stage_pull_report(str(self.package), str(receipt_path))

        report = MODULE.feishu_accept_pull_report(str(self.package))

        metadata, accepted_body, _accepted_raw = MODULE.read_draft(
            self.package / "draft.md"
        )
        self.assertEqual("pulled", report["phase"])
        self.assertEqual("editorial_review", metadata["status"])
        self.assertIs(metadata["fact_checked"], False)
        self.assertIs(metadata["copyedit_checked"], False)
        self.assertEqual("", metadata["copyedit_body_sha256"])
        self.assertIn("团队修改。", accepted_body)
        self.assertEqual(
            publish_before, self.package.joinpath("publish.yml").read_bytes()
        )
        status = MODULE.status_report(str(self.package))
        self.assertEqual("complete_editorial_gates", status["next_action"]["id"])

    def test_accept_pull_detects_local_change_after_staging(self) -> None:
        self.write_package()
        self.commit_push()
        _meta, body, _raw = MODULE.read_draft(self.package / "draft.md")
        prepared = MODULE.feishu_prepare_pull_report(str(self.package))
        receipt_path = self.write_pull_receipt(prepared, body + "\n团队修改。\n")
        MODULE.feishu_stage_pull_report(str(self.package), str(receipt_path))
        draft_path = self.package / "draft.md"
        local_text = draft_path.read_text(encoding="utf-8").replace(
            "正文。", "本地正文。"
        )
        draft_path.write_text(local_text, encoding="utf-8")

        with self.assertRaisesRegex(MODULE.WorkflowError, "changed after"):
            MODULE.feishu_accept_pull_report(str(self.package))

        self.assertIn("本地正文。", draft_path.read_text(encoding="utf-8"))
        self.assertNotIn("团队修改。", draft_path.read_text(encoding="utf-8"))
        self.assertEqual("conflict", MODULE.load_sync_state(self.package)["phase"])

    def test_pull_three_way_matrix_marks_local_only_change(self) -> None:
        self.write_package()
        self.commit_push()
        draft_path = self.package / "draft.md"
        _meta, base_body, _raw = MODULE.read_draft(draft_path)
        draft_path.write_text(
            draft_path.read_text(encoding="utf-8").replace("正文。", "仅本地修改。"),
            encoding="utf-8",
        )
        prepared = MODULE.feishu_prepare_pull_report(str(self.package))
        receipt_path = self.write_pull_receipt(prepared, base_body)

        report = MODULE.feishu_stage_pull_report(str(self.package), str(receipt_path))

        self.assertEqual("local_dirty", report["phase"])
        status = MODULE.status_report(str(self.package))
        self.assertEqual("safe_feishu_update_unavailable", status["next_action"]["id"])
        self.assertIn("safe_feishu_update_unavailable", status["workflow_blockers"])

    def test_remote_title_change_becomes_conflict(self) -> None:
        self.write_package()
        self.commit_push()
        prepared = MODULE.feishu_prepare_pull_report(str(self.package))
        receipt_path = self.write_pull_receipt(
            prepared, "## 第一节\n\n正文。\n", title="另一个标题"
        )

        report = MODULE.feishu_stage_pull_report(str(self.package), str(receipt_path))

        self.assertFalse(report["ok"])
        self.assertEqual("conflict", report["phase"])
        state = MODULE.load_sync_state(self.package)
        self.assertEqual("remote_title_changed", state["conflict"]["reason_code"])

    def test_readback_path_escape_locks_push_unknown(self) -> None:
        self.write_package()
        prepared = self.prepare_push()
        self.begin_push(prepared)
        receipt_path = self.write_push_receipt(prepared)
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        receipt["observed"]["body_path"] = "draft.md"
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")

        with self.assertRaisesRegex(MODULE.WorkflowError, "operation directory"):
            MODULE.feishu_commit_push_report(str(self.package), str(receipt_path))

        self.assertEqual(
            "result_unknown", MODULE.load_sync_state(self.package)["phase"]
        )

    def test_begin_is_one_time_and_journal_recovers_in_flight(self) -> None:
        self.write_package()
        prepared = self.prepare_push()

        begun = self.begin_push(prepared)

        self.assertEqual("push_in_flight", begun["phase"])
        self.assertTrue(begun["dispatch_claimed"])
        status = MODULE.status_report(str(self.package))
        self.assertEqual("reconcile_feishu_result", status["next_action"]["id"])
        self.assertIn("feishu_dispatch_in_flight", status["workflow_blockers"])
        with self.assertRaisesRegex(MODULE.WorkflowError, "already claimed"):
            self.begin_push(prepared)

        shutil.rmtree(self.package / "dist")
        recovered = MODULE.load_sync_state(self.package)
        self.assertEqual("push_in_flight", recovered["phase"])
        self.assertTrue(recovered.get("_recovered_from_journal"))
        self.assertEqual(
            "reconcile_feishu_result",
            MODULE.status_report(str(self.package))["next_action"]["id"],
        )

    def test_protocol_state_without_journal_fails_closed(self) -> None:
        self.write_package()
        prepared = self.prepare_push()
        journal_path = MODULE.journal_file(self.package)
        claim_path = MODULE.dispatch_claim_file(
            self.package, str(prepared["operation_id"])
        )
        journal_path.unlink()

        with self.assertRaisesRegex(MODULE.WorkflowError, "without its write-ahead"):
            MODULE.load_sync_state(self.package)
        with (
            mock.patch.object(MODULE, "run_content_validator"),
            mock.patch.object(
                MODULE, "live_feishu_connector_available", return_value=True
            ),
            self.assertRaisesRegex(MODULE.WorkflowError, "without its write-ahead"),
        ):
            MODULE.feishu_begin_push_report(
                str(self.package),
                str(prepared["operation_id"]),
                str(prepared["authorization_scope_sha256"]),
            )
        self.assertFalse(claim_path.exists())

    def test_synced_journal_survives_dist_deletion(self) -> None:
        self.write_package()
        prepared = self.prepare_push()
        prepared_state = dict(MODULE.load_sync_state(self.package))
        self.begin_push(prepared)
        in_flight_state = dict(MODULE.load_sync_state(self.package))
        receipt_path = self.write_push_receipt(prepared)
        committed = MODULE.feishu_commit_push_report(
            str(self.package), str(receipt_path)
        )
        synced_state = dict(MODULE.load_sync_state(self.package))

        self.assertEqual("feishu_synced", committed["phase"])
        self.assertLess(
            prepared_state["state_sequence"], in_flight_state["state_sequence"]
        )
        self.assertLess(
            in_flight_state["state_sequence"], synced_state["state_sequence"]
        )

        MODULE.atomic_write_json(
            self.package / MODULE.STATE_RELATIVE_PATH, in_flight_state
        )
        crash_recovered = MODULE.load_sync_state(self.package)
        self.assertEqual("feishu_synced", crash_recovered["phase"])
        self.assertTrue(crash_recovered.get("_recovered_from_journal"))

        shutil.rmtree(self.package / "dist")
        recovered = MODULE.load_sync_state(self.package)

        self.assertEqual("feishu_synced", recovered["phase"])
        self.assertTrue(recovered.get("_recovered_from_journal"))
        self.assertEqual("revision-1", recovered["remote_revision"])
        next_action = MODULE.status_report(str(self.package))["next_action"]
        self.assertEqual("wait_for_team_review", next_action["id"])
        self.assertIn("feishu-prepare-pull", next_action["command"])

    def test_push_receipt_contract_is_exact_and_fail_closed(self) -> None:
        def wrong_server(receipt: dict) -> None:
            receipt["mcp"]["server_id"] = "untrusted-mcp"

        def wrong_tool(receipt: dict) -> None:
            receipt["mcp"]["write_tool"] = "update-doc"

        def wrong_scope(receipt: dict) -> None:
            receipt["authorization_scope_sha256"] = "f" * 64

        def reused_call_id(receipt: dict) -> None:
            receipt["mcp"]["read_call_id"] = receipt["mcp"]["write_call_id"]

        def unknown_top_level(receipt: dict) -> None:
            receipt["raw_response"] = {"secret": "must-not-persist"}

        def unknown_mcp_field(receipt: dict) -> None:
            receipt["mcp"]["headers"] = {"authorization": "must-not-persist"}

        def predates_dispatch(receipt: dict) -> None:
            receipt["completed_at"] = "2000-01-01T00:00:00+00:00"

        for name, mutate in (
            ("server", wrong_server),
            ("tool", wrong_tool),
            ("scope", wrong_scope),
            ("call_id", reused_call_id),
            ("unknown_top", unknown_top_level),
            ("unknown_mcp", unknown_mcp_field),
            ("predates_dispatch", predates_dispatch),
        ):
            with self.subTest(name=name):
                if self.package.exists():
                    shutil.rmtree(self.package)
                self.package.mkdir()
                self.write_package()
                prepared = self.prepare_push()
                self.begin_push(prepared)
                receipt_path = self.write_push_receipt(prepared)
                receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
                mutate(receipt)
                receipt_path.write_text(
                    json.dumps(receipt, ensure_ascii=False), encoding="utf-8"
                )

                with self.assertRaises(MODULE.WorkflowError):
                    MODULE.feishu_commit_push_report(
                        str(self.package), str(receipt_path)
                    )

                self.assertEqual(
                    "result_unknown", MODULE.load_sync_state(self.package)["phase"]
                )
                self.assertEqual(
                    "reconcile_feishu_result",
                    MODULE.status_report(str(self.package))["next_action"]["id"],
                )

    def test_publish_change_invalidates_prepared_authorization(self) -> None:
        self.write_package()
        prepared = self.prepare_push()
        publish_path = self.package / "publish.yml"
        publish_path.write_text(
            publish_path.read_text(encoding="utf-8") + "note: changed\n",
            encoding="utf-8",
        )

        status = MODULE.status_report(str(self.package))
        self.assertEqual("inspect_stale_feishu_intent", status["next_action"]["id"])
        self.assertIn("pending_source_changed", status["workflow_blockers"])
        with self.assertRaisesRegex(MODULE.WorkflowError, "stale"):
            self.begin_push(prepared)

    def test_pull_prepare_report_exposes_local_payload_and_assets(self) -> None:
        self.write_package(body="# 测试标题\n\n## 第一节\n\n![示例](image.png)")
        (self.package / "image.png").write_bytes(b"\x89PNG\r\n\x1a\n")
        self.commit_push()

        report = MODULE.feishu_prepare_pull_report(str(self.package))
        intent, _intent_path = self.load_intent(report)

        self.assertEqual(
            intent["content"]["local_payload_sha256"], report["payload_sha256"]
        )
        self.assertEqual(1, intent["content"]["local_asset_count"])
        self.assertEqual(1, report["asset_count"])

    def test_tampered_push_artifacts_do_not_consume_dispatch_claim(self) -> None:
        def tamper_payload(intent: dict, intent_path: Path) -> None:
            payload_path = self.package / intent["content"]["payload_path"]
            payload_path.write_text("tampered\n", encoding="utf-8")

        def tamper_assets(intent: dict, intent_path: Path) -> None:
            assets_path = self.package / intent["content"]["assets_path"]
            assets_path.write_text('[{"bad": 1}]', encoding="utf-8")

        def remove_template(intent: dict, intent_path: Path) -> None:
            (self.package / intent["receipt_template_path"]).unlink()

        for name, tamper in (
            ("payload", tamper_payload),
            ("assets", tamper_assets),
            ("template", remove_template),
        ):
            with self.subTest(name=name):
                if self.package.exists():
                    shutil.rmtree(self.package)
                self.package.mkdir()
                self.write_package()
                prepared = self.prepare_push()
                intent, intent_path = self.load_intent(prepared)
                tamper(intent, intent_path)
                claim_path = MODULE.dispatch_claim_file(
                    self.package, str(prepared["operation_id"])
                )

                with self.assertRaises((OSError, MODULE.WorkflowError)):
                    self.begin_push(prepared)

                self.assertFalse(claim_path.exists())
                self.assertEqual(
                    "push_prepared", MODULE.load_sync_state(self.package)["phase"]
                )
                status = MODULE.status_report(str(self.package))
                self.assertEqual("recover_feishu_intent", status["next_action"]["id"])
                recovered = self.prepare_push()
                self.assertEqual(prepared["operation_id"], recovered["operation_id"])

    def test_claim_overlay_recovers_when_state_write_crashes(self) -> None:
        self.write_package()
        prepared = self.prepare_push()
        claim_path = MODULE.dispatch_claim_file(
            self.package, str(prepared["operation_id"])
        )

        with (
            mock.patch.object(MODULE, "run_content_validator"),
            mock.patch.object(
                MODULE, "live_feishu_connector_available", return_value=True
            ),
            mock.patch.object(
                MODULE,
                "write_sync_state",
                side_effect=MODULE.WorkflowError("simulated state write crash"),
            ),
        ):
            with self.assertRaisesRegex(MODULE.WorkflowError, "simulated"):
                MODULE.feishu_begin_push_report(
                    str(self.package),
                    str(prepared["operation_id"]),
                    str(prepared["authorization_scope_sha256"]),
                )

        self.assertTrue(claim_path.is_file())
        recovered = MODULE.load_sync_state(self.package)
        self.assertEqual("push_in_flight", recovered["phase"])
        self.assertTrue(recovered.get("_claim_recovered"))
        self.assertEqual(
            "reconcile_feishu_result",
            MODULE.status_report(str(self.package))["next_action"]["id"],
        )

    def test_journal_rejects_impossible_newer_dist_state(self) -> None:
        self.write_package()
        self.commit_push()
        trusted = MODULE.load_sync_state(self.package)
        forged = {
            key: value for key, value in trusted.items() if not key.startswith("_")
        }
        forged["state_sequence"] += 1
        forged["phase"] = "local_only"
        MODULE.atomic_write_json(self.package / MODULE.STATE_RELATIVE_PATH, forged)

        with self.assertRaisesRegex(MODULE.WorkflowError, "newer than"):
            MODULE.load_sync_state(self.package)

    def test_stale_state_writer_is_rejected(self) -> None:
        self.write_package()
        state = MODULE.default_sync_state()
        MODULE.write_sync_state(self.package, state)
        stale = dict(state)
        MODULE.write_sync_state(self.package, state)

        with self.assertRaisesRegex(MODULE.WorkflowError, "stale sync state"):
            MODULE.write_sync_state(self.package, stale)

    def test_pull_intent_recovery_and_connector_gate(self) -> None:
        self.write_package()
        self.commit_push()
        prepared = MODULE.feishu_prepare_pull_report(str(self.package))

        status = MODULE.status_report(str(self.package))
        self.assertEqual(
            "integrate_trusted_feishu_executor", status["next_action"]["id"]
        )
        self.assertIn(
            "feishu_trusted_executor_unavailable", status["workflow_blockers"]
        )

        intent, intent_path = self.load_intent(prepared)
        self.assertEqual("pull_read", intent["operation"])
        shutil.rmtree(intent_path.parent)
        missing_status = MODULE.status_report(str(self.package))
        self.assertEqual(
            "recover_feishu_pull_intent", missing_status["next_action"]["id"]
        )

        recovered = MODULE.feishu_prepare_pull_report(str(self.package))
        self.assertEqual(prepared["operation_id"], recovered["operation_id"])
        self.assertTrue((self.package / str(recovered["intent_path"])).is_file())

    def test_legacy_post_feishu_state_fails_closed(self) -> None:
        self.write_package()
        state_path = self.package / MODULE.STATE_RELATIVE_PATH
        state_path.parent.mkdir(parents=True)
        state_path.write_text('{"phase":"sealed"}', encoding="utf-8")

        with self.assertRaisesRegex(MODULE.WorkflowError, "legacy_untrusted"):
            MODULE.status_report(str(self.package))

    def test_strict_state_never_downgrades_malformed_phase(self) -> None:
        self.write_package()
        state_path = self.package / MODULE.STATE_RELATIVE_PATH
        state_path.parent.mkdir(parents=True)
        state_path.write_text(
            json.dumps(
                {
                    "schema_version": MODULE.SCHEMA_VERSION,
                    "protocol": MODULE.FEISHU_PROTOCOL_VERSION,
                    "provider": "feishu",
                    "phase": "surprise",
                }
            ),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(MODULE.WorkflowError, "unsupported"):
            MODULE.status_report(str(self.package))

    def test_unqualified_build_cannot_advance_to_wechat(self) -> None:
        self.write_package()
        MODULE.build_report(str(self.package))
        self.write_sync_phase("team_review_complete")
        receipt_path = self.package / "dist" / "content-sync" / "build.json"
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        receipt["local_format_qualified"] = False
        receipt["warning_codes"] = ["wechat-size-limit"]
        seal_fields = (
            "draft_sha256",
            "format_profile_sha256",
            "adapter_sha256",
            "bridge_sha256",
            "renderer_sha256",
            "format_contract_sha256",
            "style_version",
            "html_sha256",
            "title_image_sha256",
            "local_format_qualified",
            "warning_codes",
        )
        receipt["sealed_build_sha256"] = MODULE.sha256_bytes(
            MODULE.canonical_json({field: receipt[field] for field in seal_fields})
        )
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")

        report = MODULE.status_report(str(self.package))
        self.assertEqual("repair_local_build", report["next_action"]["id"])
        self.assertFalse(report["next_action"]["external_write"])

    def test_local_build_waits_for_account_profile_qualification(self) -> None:
        self.write_package(
            delivery_mode="sealed_draft",
            layout_profile="appsso-article-v1",
        )
        MODULE.build_report(str(self.package))
        self.write_sync_phase("sealed")

        report = MODULE.status_report(str(self.package))
        self.assertEqual("qualify_company_format", report["next_action"]["id"])
        self.assertTrue(report["next_action"]["external_write"])
        self.assertTrue(report["next_action"]["authorization_required"])
        self.assertFalse(report["qualification"]["company_format_qualified"])

    def test_manual_editor_never_routes_to_wechat_api(self) -> None:
        self.write_package()
        MODULE.build_report(str(self.package))
        self.write_sync_phase("sealed")

        report = MODULE.status_report(str(self.package))
        self.assertEqual("select_api_delivery_route", report["next_action"]["id"])
        self.assertNotEqual("wechat_create_draft", report["next_action"]["id"])
        self.assertEqual("$self-media-ops", report["next_action"]["handler"])
        self.assertFalse(report["next_action"]["external_write"])

    def test_route_rechecks_both_api_delivery_axes(self) -> None:
        build = {
            "local_format_qualified": True,
            "company_format_qualified": True,
            "required_delivery_mode": "sealed_draft",
            "required_layout_profile": "appsso-article-v1",
        }
        for delivery_mode, layout_profile in (
            ("manual_editor", "default"),
            ("sealed_draft", "default"),
        ):
            with self.subTest(
                delivery_mode=delivery_mode,
                layout_profile=layout_profile,
            ):
                action = MODULE.choose_next_action(
                    self.package,
                    "ready",
                    {
                        "project_adapter": "appsso",
                        "delivery_mode": delivery_mode,
                        "layout_profile": layout_profile,
                    },
                    {"phase": "sealed"},
                    build,
                    False,
                    True,
                )
                self.assertEqual("select_api_delivery_route", action["id"])

        blocked = MODULE.choose_next_action(
            self.package,
            "ready",
            {
                "project_adapter": "appsso",
                "delivery_mode": "sealed_draft",
                "layout_profile": "appsso-article-v1",
            },
            {"phase": "sealed"},
            build,
            False,
            True,
        )
        self.assertEqual("integrate_wechat_draft_adapter", blocked["id"])
        self.assertFalse(blocked["external_write"])

        allowed = MODULE.choose_next_action(
            self.package,
            "ready",
            {
                "project_adapter": "appsso",
                "delivery_mode": "sealed_draft",
                "layout_profile": "appsso-article-v1",
            },
            {"phase": "sealed"},
            build,
            False,
            True,
            wechat_draft_adapter_available=True,
        )
        self.assertEqual("wechat_create_draft", allowed["id"])
        self.assertTrue(allowed["authorization_required"])

    def test_oversize_html_is_not_hashed_by_status(self) -> None:
        self.write_package()
        MODULE.build_report(str(self.package))
        self.write_sync_phase("sealed")
        self.package / "dist" / "content-sync" / "article.html"

        with mock.patch.object(MODULE, "MAX_RENDERED_HTML_BYTES", 1):
            report = MODULE.status_report(str(self.package))

        self.assertIn("build_html_oversize", report["build"]["integrity_issues"])
        self.assertIsNone(report["build"]["actual_html_sha256"])
        self.assertEqual("run_local_build", report["next_action"]["id"])

    def test_stale_build_keeps_original_media_warning(self) -> None:
        self.write_package()
        MODULE.build_report(str(self.package))
        receipt_path = self.package / "dist" / "content-sync" / "build.json"
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        receipt["warning_codes"] = ["wechat-size-limit"]
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")

        report = MODULE.status_report(str(self.package))

        self.assertIn("wechat-size-limit", report["workflow_blockers"])
        self.assertIn("wechat-size-limit", report["blockers"])

    def test_tampered_html_routes_back_to_build(self) -> None:
        self.write_package()
        MODULE.build_report(str(self.package))
        self.write_sync_phase("sealed")
        html_path = self.package / "dist" / "content-sync" / "article.html"
        html_path.write_text(
            html_path.read_text(encoding="utf-8") + "<!-- tampered -->",
            encoding="utf-8",
        )

        report = MODULE.status_report(str(self.package))
        self.assertEqual("run_local_build", report["next_action"]["id"])
        self.assertIn("build_html_hash_mismatch", report["build"]["integrity_issues"])

    def test_raw_html_and_tables_fail_instead_of_drifting(self) -> None:
        cases = (
            "# 测试标题\n\n## 第一节\n\n<section>内部 HTML</section>",
            "# 测试标题\n\n## 第一节\n\n| A | B |\n|---|---|\n| 1 | 2 |",
        )
        for body in cases:
            with self.subTest(body=body):
                self.write_package(body=body)
                with self.assertRaisesRegex(
                    MODULE.WorkflowError, "unsupported Markdown"
                ):
                    MODULE.build_report(str(self.package))

    def test_heading_mapping_fails_instead_of_guessing(self) -> None:
        self.write_package(
            body="# 测试标题\n\n### 跳级标题\n\n正文。\n\n## 后出现的二级标题"
        )
        with self.assertRaisesRegex(MODULE.WorkflowError, "H3 requires an H2"):
            MODULE.build_report(str(self.package))


if __name__ == "__main__":
    unittest.main()
