#!/usr/bin/env python3
"""Deterministic lifecycle CLI for the insight-to-asset workspace."""

from __future__ import annotations

import argparse
import copy
import os
import re
import sys
import tempfile
import time
import unicodedata
from collections import Counter
from contextlib import contextmanager
from datetime import date, timedelta
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover - exercised only without dependencies
    raise SystemExit(
        "缺少依赖 PyYAML。请运行：python -m pip install -r "
        ".agents/skills/insight-to-asset/requirements.txt"
    ) from exc


DEFAULT_ROOT = Path("共享/研究/洞察实验室")
REGISTRY_NAME = "洞察台账.yml"
SCHEMA_VERSION = 1
DEFAULT_TIMEZONE = "Asia/Tokyo"
DEFAULT_WIP_LIMIT = 1

INSIGHT_STATUSES = (
    "captured",
    "framed",
    "test_ready",
    "running",
    "evaluated",
    "supported_scoped",
    "refined",
    "rejected",
    "assetized",
    "monitoring",
    "stable",
    "reopened",
    "retired",
    "archived",
)
EXPERIMENT_STATUSES = ("planned", "running", "evaluated", "cancelled")
EVIDENCE_LEVELS = ("E0", "E1", "E2", "E3")
CLASSIFICATIONS = ("public", "public-derived", "internal", "restricted-index")

INSIGHT_ID_RE = re.compile(r"^INSIGHT-(?P<number>\d{3,})$")
EXPERIMENT_ID_RE = re.compile(r"^EXP-[A-Z0-9][A-Z0-9-]{1,63}$")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
RECORD_PATH_RE = re.compile(
    r"^insights/(?P<id>INSIGHT-\d{3,})-(?P<slug>[a-z0-9]+(?:-[a-z0-9]+)*)/insight\.yml$"
)

REGISTRY_REQUIRED = (
    "schema_version",
    "updated_on",
    "timezone",
    "wip_limit",
    "insights",
)
REGISTRY_ENTRY_REQUIRED = (
    "id",
    "title",
    "record",
    "status",
    "evidence_level",
    "classification",
    "owner",
    "updated_on",
    "next_review_on",
)
RECORD_REQUIRED = (
    "schema_version",
    "id",
    "title",
    "classification",
    "status",
    "evidence_level",
    "owner",
    "created_on",
    "updated_on",
    "next_review_on",
    "claim",
    "falsifiability",
    "evidence",
    "experiments",
    "assetization",
    "next_action",
    "decision_log",
)
CLAIM_REQUIRED = ("statement", "scope", "mechanism", "exclusions")
FALSIFIABILITY_REQUIRED = (
    "prediction",
    "failure_condition",
    "alternative_explanations",
)
EXPERIMENT_REQUIRED = (
    "id",
    "title",
    "status",
    "question",
    "baseline",
    "intervention",
    "controls",
    "metrics",
    "evidence_refs",
    "decision",
    "end_condition",
)
METRICS_REQUIRED = ("primary", "secondary", "guardrails")
BASELINE_REQUIRED = ("description", "frozen_ref", "missing_data_rule")
INTERVENTION_REQUIRED = ("description", "artifact_ref", "version_ref")
METRIC_DEFINITION_REQUIRED = (
    "id",
    "definition",
    "direction",
    "success_threshold",
    "baseline",
    "result",
)
GUARDRAIL_REQUIRED = ("id", "condition")
ASSETIZATION_REQUIRED = (
    "status",
    "type",
    "target",
    "authoritative_refs",
    "regression_check",
    "transfer_test",
    "retirement_condition",
    "portable_core",
    "adapter_boundary",
)
EVIDENCE_ITEM_REQUIRED = ("relation", "ref", "note")
EVIDENCE_ITEM_ALLOWED = EVIDENCE_ITEM_REQUIRED + (
    "case_id",
    "prospective",
    "counterexample",
    "transfer_test",
)

DEFAULT_MECHANISM = (
    "反馈被转化为触发条件、动作、通过标准和回归检查后，可能降低同类问题复发。"
)
DEFAULT_PREDICTION = "在限定范围内，应用该洞察后，预先冻结的主指标应达到改善阈值。"
DEFAULT_FAILURE_CONDITION = (
    "若主指标未达到预设阈值，或任一质量护栏恶化，则拒绝或收窄该洞察。"
)
DEFAULT_SUCCESS_THRESHOLD = "实验启动前冻结可测阈值。"
DEFAULT_END_CONDITION = "达到预设样本数或触发质量护栏后结束。"
DEFAULT_NEXT_ACTION = "冻结首轮实验的主指标、阈值、对照和停止条件。"
GENERIC_STATEMENT_RE = re.compile(
    r"^(?:这是一条|这是|该|一个)?(?:待验证的?)?(?:洞察|判断|命题|假设)[。.!！]?$"
)

PLACEHOLDER_RE = re.compile(
    r"^(?:todo|tbd|n/?a|none|null|unknown|待补(?:充)?|待定|暂无|无|不适用)[。.!！]?$",
    re.IGNORECASE,
)
NON_FALSIFIABLE_RE = re.compile(
    r"(?:不可证伪|无法证伪|永远(?:正确|成立)|不会失败|"
    r"没有什么(?:结果)?(?:会)?(?:推翻|反驳|否定)|无论.+都(?:成立|正确)|"
    r"nothing\s+(?:can|could)\s+(?:falsify|disprove)|can(?:not|'t)\s+fail)",
    re.IGNORECASE,
)


def configure_utf8_stdio() -> None:
    """Keep Chinese diagnostics stable under Windows legacy code pages."""
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name)
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="strict")


class StrictLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate and merge keys."""

    yaml_implicit_resolvers = copy.deepcopy(yaml.SafeLoader.yaml_implicit_resolvers)

    def compose_node(self, parent: Any, index: Any) -> yaml.nodes.Node:
        if self.check_event(yaml.events.AliasEvent):
            event = self.peek_event()
            raise yaml.composer.ComposerError(
                "while composing a node",
                event.start_mark,
                "不允许 YAML alias；请展开为独立值",
                event.start_mark,
            )
        return super().compose_node(parent, index)


# Keep ISO dates as strings. This makes type checks and registry comparisons stable.
for _resolver_key, _resolvers in list(StrictLoader.yaml_implicit_resolvers.items()):
    StrictLoader.yaml_implicit_resolvers[_resolver_key] = [
        resolver
        for resolver in _resolvers
        if resolver[0] != "tag:yaml.org,2002:timestamp"
    ]


def _construct_unique_mapping(
    loader: StrictLoader, node: yaml.nodes.MappingNode, deep: bool = False
) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        if key_node.tag == "tag:yaml.org,2002:merge":
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                "不允许 YAML 合并键（<<）",
                key_node.start_mark,
            )
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in mapping
        except TypeError as exc:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                "YAML 映射键必须可哈希",
                key_node.start_mark,
            ) from exc
        if duplicate:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"重复 YAML 键：{key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


StrictLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_unique_mapping
)


class WorkspaceError(Exception):
    """Expected user-facing workspace or validation failure."""


def load_yaml(path: Path) -> Any:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise WorkspaceError(f"无法读取 {path}：{exc}") from exc
    try:
        return yaml.load(text, Loader=StrictLoader)
    except yaml.YAMLError as exc:
        raise WorkspaceError(f"YAML 解析失败 {path}：{exc}") from exc


def dump_yaml(value: Any) -> str:
    return yaml.safe_dump(
        value,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
        width=1000,
    )


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temp_path = Path(handle.name)
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
        temp_path = None
    except OSError as exc:
        raise WorkspaceError(f"无法原子写入 {path}：{exc}") from exc
    finally:
        if temp_path is not None:
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass


def parse_iso_date(value: Any, label: str, errors: list[str]) -> date | None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label} 必须是 YYYY-MM-DD 字符串")
        return None
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        errors.append(f"{label} 不是有效日期：{value!r}")
        return None
    if parsed.isoformat() != value:
        errors.append(f"{label} 必须使用规范 YYYY-MM-DD：{value!r}")
        return None
    return parsed


def require_mapping(value: Any, label: str, errors: list[str]) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        errors.append(f"{label} 必须是 mapping")
        return None
    if any(not isinstance(key, str) for key in value):
        errors.append(f"{label} 的键必须都是字符串")
        return None
    return value


def require_list(value: Any, label: str, errors: list[str]) -> list[Any] | None:
    if not isinstance(value, list):
        errors.append(f"{label} 必须是 list")
        return None
    return value


def require_nonempty_string(value: Any, label: str, errors: list[str]) -> str | None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label} 必须是非空字符串")
        return None
    if value != value.strip():
        errors.append(f"{label} 首尾不能包含空白")
        return None
    return value


def require_fields(
    mapping: dict[str, Any], fields: tuple[str, ...], label: str, errors: list[str]
) -> None:
    for field in fields:
        if field not in mapping:
            errors.append(f"{label} 缺少必填字段 {field}")


def reject_unknown_fields(
    mapping: dict[str, Any], allowed: tuple[str, ...], label: str, errors: list[str]
) -> None:
    for field in sorted(set(mapping) - set(allowed)):
        errors.append(f"{label} 包含未知字段 {field}")


def validate_string_list(
    value: Any,
    label: str,
    errors: list[str],
    *,
    allow_empty: bool = True,
) -> list[str] | None:
    items = require_list(value, label, errors)
    if items is None:
        return None
    if not allow_empty and not items:
        errors.append(f"{label} 不能为空")
    result: list[str] = []
    for index, item in enumerate(items):
        text = require_nonempty_string(item, f"{label}[{index}]", errors)
        if text is not None:
            result.append(text)
    return result


def validate_no_blank_strings(value: Any, label: str, errors: list[str]) -> None:
    if isinstance(value, str):
        if not value.strip():
            errors.append(f"{label} 不能包含空字符串")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            validate_no_blank_strings(item, f"{label}[{index}]", errors)
    elif isinstance(value, dict):
        for key, item in value.items():
            validate_no_blank_strings(item, f"{label}.{key}", errors)


def validate_enum(
    value: Any, allowed: tuple[str, ...], label: str, errors: list[str]
) -> str | None:
    text = require_nonempty_string(value, label, errors)
    if text is not None and text not in allowed:
        errors.append(f"{label} 未知值 {text!r}；允许：{', '.join(allowed)}")
        return None
    return text


def validate_id(value: Any, label: str, errors: list[str]) -> str | None:
    text = require_nonempty_string(value, label, errors)
    if text is not None and not INSIGHT_ID_RE.fullmatch(text):
        errors.append(f"{label} 必须匹配 INSIGHT-NNN：{text!r}")
        return None
    return text


def validate_falsifiable_text(value: Any, label: str, errors: list[str]) -> None:
    candidates: list[str] = []
    if isinstance(value, str):
        candidates = [value]
    elif isinstance(value, list):
        for index, item in enumerate(value):
            if not isinstance(item, str) or not item.strip():
                errors.append(f"{label}[{index}] 必须是非空字符串")
            else:
                candidates.append(item)
    else:
        errors.append(f"{label} 必须是非空字符串或非空字符串列表")
        return
    if not candidates:
        errors.append(f"{label} 至少需要一项")
        return
    usable = []
    for candidate in candidates:
        stripped = candidate.strip()
        if PLACEHOLDER_RE.fullmatch(stripped) or NON_FALSIFIABLE_RE.search(stripped):
            continue
        usable.append(stripped)
    if not usable:
        errors.append(f"{label} 没有可检验内容，不能使用占位语或不可证伪表述")


def validate_nullable_value(value: Any, label: str, errors: list[str]) -> None:
    if value is None:
        return
    if isinstance(value, (str, list, dict, int, float)) and not isinstance(value, bool):
        validate_no_blank_strings(value, label, errors)
        return
    errors.append(f"{label} 必须是 null、文本、数字、list 或 mapping")


def validate_nullable_string(value: Any, label: str, errors: list[str]) -> None:
    if value is None:
        return
    require_nonempty_string(value, label, errors)


def validate_baseline(value: Any, label: str, errors: list[str]) -> None:
    baseline = require_mapping(value, label, errors)
    if baseline is None:
        return
    require_fields(baseline, BASELINE_REQUIRED, label, errors)
    reject_unknown_fields(baseline, BASELINE_REQUIRED, label, errors)
    for field in ("description", "missing_data_rule"):
        if field in baseline:
            require_nonempty_string(baseline[field], f"{label}.{field}", errors)
    if "frozen_ref" in baseline:
        validate_nullable_string(baseline["frozen_ref"], f"{label}.frozen_ref", errors)


def validate_intervention(value: Any, label: str, errors: list[str]) -> None:
    intervention = require_mapping(value, label, errors)
    if intervention is None:
        return
    require_fields(intervention, INTERVENTION_REQUIRED, label, errors)
    reject_unknown_fields(intervention, INTERVENTION_REQUIRED, label, errors)
    if "description" in intervention:
        require_nonempty_string(intervention["description"], f"{label}.description", errors)
    for field in ("artifact_ref", "version_ref"):
        if field in intervention:
            validate_nullable_string(intervention[field], f"{label}.{field}", errors)


def validate_metric_definition(value: Any, label: str, errors: list[str]) -> None:
    metric = require_mapping(value, label, errors)
    if metric is None:
        return
    require_fields(metric, METRIC_DEFINITION_REQUIRED, label, errors)
    reject_unknown_fields(metric, METRIC_DEFINITION_REQUIRED, label, errors)
    for field in ("id", "definition", "direction", "success_threshold"):
        if field in metric:
            require_nonempty_string(metric[field], f"{label}.{field}", errors)
    for field in ("baseline", "result"):
        if field in metric:
            validate_nullable_value(metric[field], f"{label}.{field}", errors)


def validate_metric_definitions(value: Any, label: str, errors: list[str]) -> None:
    metrics = require_list(value, label, errors)
    if metrics is None:
        return
    for index, metric in enumerate(metrics):
        validate_metric_definition(metric, f"{label}[{index}]", errors)


def validate_guardrails(value: Any, label: str, errors: list[str]) -> None:
    guardrails = require_list(value, label, errors)
    if guardrails is None:
        return
    if not guardrails:
        errors.append(f"{label} 至少需要一个质量护栏")
    for index, raw_guardrail in enumerate(guardrails):
        guardrail_label = f"{label}[{index}]"
        guardrail = require_mapping(raw_guardrail, guardrail_label, errors)
        if guardrail is None:
            continue
        require_fields(guardrail, GUARDRAIL_REQUIRED, guardrail_label, errors)
        reject_unknown_fields(guardrail, GUARDRAIL_REQUIRED, guardrail_label, errors)
        for field in GUARDRAIL_REQUIRED:
            if field in guardrail:
                require_nonempty_string(
                    guardrail[field], f"{guardrail_label}.{field}", errors
                )


def validate_experiment(
    experiment: Any,
    label: str,
    errors: list[str],
) -> tuple[str | None, str | None]:
    item = require_mapping(experiment, label, errors)
    if item is None:
        return None, None
    require_fields(item, EXPERIMENT_REQUIRED, label, errors)
    reject_unknown_fields(item, EXPERIMENT_REQUIRED, label, errors)

    experiment_id = None
    if "id" in item:
        experiment_id = require_nonempty_string(item["id"], f"{label}.id", errors)
        if experiment_id is not None and not EXPERIMENT_ID_RE.fullmatch(experiment_id):
            errors.append(f"{label}.id 必须匹配 EXP-...：{experiment_id!r}")
            experiment_id = None
    for field in ("title", "question", "end_condition"):
        if field in item:
            require_nonempty_string(item[field], f"{label}.{field}", errors)
    if "baseline" in item:
        validate_baseline(item["baseline"], f"{label}.baseline", errors)
    if "intervention" in item:
        validate_intervention(item["intervention"], f"{label}.intervention", errors)

    experiment_status = None
    if "status" in item:
        experiment_status = validate_enum(
            item["status"], EXPERIMENT_STATUSES, f"{label}.status", errors
        )

    if "controls" in item:
        validate_string_list(item["controls"], f"{label}.controls", errors, allow_empty=False)
    if "evidence_refs" in item:
        validate_string_list(item["evidence_refs"], f"{label}.evidence_refs", errors)

    if "metrics" in item:
        metrics = require_mapping(item["metrics"], f"{label}.metrics", errors)
        if metrics is not None:
            require_fields(metrics, METRICS_REQUIRED, f"{label}.metrics", errors)
            reject_unknown_fields(metrics, METRICS_REQUIRED, f"{label}.metrics", errors)
            if "primary" in metrics:
                validate_metric_definition(
                    metrics["primary"], f"{label}.metrics.primary", errors
                )
            if "secondary" in metrics:
                validate_metric_definitions(
                    metrics["secondary"], f"{label}.metrics.secondary", errors
                )
            if "guardrails" in metrics:
                validate_guardrails(
                    metrics["guardrails"], f"{label}.metrics.guardrails", errors
                )

    if "decision" in item:
        decision = require_nonempty_string(item["decision"], f"{label}.decision", errors)
        if experiment_status == "evaluated" and decision == "pending":
            errors.append(f"{label}.decision 在 evaluated 状态下不能是 pending")
    return experiment_id, experiment_status


def validate_evidence(value: Any, label: str, errors: list[str]) -> list[dict[str, Any]]:
    evidence = require_mapping(value, label, errors)
    if evidence is None:
        return []
    required = ("supporting", "contradicting", "neutral", "unknowns")
    require_fields(evidence, required, label, errors)
    reject_unknown_fields(evidence, required, label, errors)
    valid_decisive_items: list[dict[str, Any]] = []
    expected_relations = {
        "supporting": "supports",
        "contradicting": "contradicts",
        "neutral": "neutral",
    }
    for relation in ("supporting", "contradicting", "neutral"):
        if relation not in evidence:
            continue
        items = require_list(evidence[relation], f"{label}.{relation}", errors)
        if items is None:
            continue
        for index, item in enumerate(items):
            item_label = f"{label}.{relation}[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{item_label} 必须是 mapping")
                continue
            before_count = len(errors)
            if not item:
                errors.append(f"{item_label} 不能为空")
            if any(not isinstance(key, str) or not key.strip() for key in item):
                errors.append(f"{item_label} 的键必须是非空字符串")
            require_fields(item, EVIDENCE_ITEM_REQUIRED, item_label, errors)
            reject_unknown_fields(item, EVIDENCE_ITEM_ALLOWED, item_label, errors)
            for field in ("ref", "note"):
                if field in item:
                    require_nonempty_string(item[field], f"{item_label}.{field}", errors)
            validate_no_blank_strings(item, item_label, errors)
            if "relation" in item:
                relation_value = validate_enum(
                    item["relation"],
                    ("supports", "contradicts", "neutral"),
                    f"{item_label}.relation",
                    errors,
                )
                if relation_value is not None and relation_value != expected_relations[relation]:
                    errors.append(
                        f"{item_label}.relation 应为 {expected_relations[relation]!r}，"
                        f"不能是 {relation_value!r}"
                    )
            if "case_id" in item:
                require_nonempty_string(item["case_id"], f"{item_label}.case_id", errors)
            for flag in ("prospective", "counterexample", "transfer_test"):
                if flag in item and type(item[flag]) is not bool:
                    errors.append(f"{item_label}.{flag} 必须是 boolean")
            if relation != "neutral" and len(errors) == before_count:
                valid_decisive_items.append(item)
    if "unknowns" in evidence:
        validate_string_list(evidence["unknowns"], f"{label}.unknowns", errors)
    return valid_decisive_items


def is_placeholder_or_default(value: Any, default: str) -> bool:
    return (
        not isinstance(value, str)
        or not value.strip()
        or value.strip() == default
        or bool(PLACEHOLDER_RE.fullmatch(value.strip()))
    )


def experiment_has_frozen_contract(experiment: Any) -> bool:
    if not isinstance(experiment, dict):
        return False
    baseline = experiment.get("baseline")
    intervention = experiment.get("intervention")
    metrics = experiment.get("metrics")
    primary = metrics.get("primary") if isinstance(metrics, dict) else None
    if not all(
        isinstance(value, dict)
        for value in (baseline, intervention, metrics, primary)
    ):
        return False
    required_refs = (
        baseline.get("frozen_ref"),
        intervention.get("artifact_ref"),
        intervention.get("version_ref"),
    )
    if any(not isinstance(value, str) or not value.strip() for value in required_refs):
        return False
    if is_placeholder_or_default(primary.get("success_threshold"), DEFAULT_SUCCESS_THRESHOLD):
        return False
    if is_placeholder_or_default(experiment.get("end_condition"), DEFAULT_END_CONDITION):
        return False
    return True


def validate_record(record: Any, label: str, errors: list[str]) -> dict[str, Any] | None:
    item = require_mapping(record, label, errors)
    if item is None:
        return None
    require_fields(item, RECORD_REQUIRED, label, errors)
    reject_unknown_fields(item, RECORD_REQUIRED, label, errors)
    if type(item.get("schema_version")) is not int or item.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"{label}.schema_version 必须是整数 {SCHEMA_VERSION}")

    if "id" in item:
        validate_id(item["id"], f"{label}.id", errors)
    for field in ("title", "owner", "next_action"):
        if field in item:
            require_nonempty_string(item[field], f"{label}.{field}", errors)
    if "classification" in item:
        validate_enum(item["classification"], CLASSIFICATIONS, f"{label}.classification", errors)
    insight_status = None
    if "status" in item:
        insight_status = validate_enum(
            item["status"], INSIGHT_STATUSES, f"{label}.status", errors
        )
    if "evidence_level" in item:
        validate_enum(item["evidence_level"], EVIDENCE_LEVELS, f"{label}.evidence_level", errors)

    created = parse_iso_date(item.get("created_on"), f"{label}.created_on", errors)
    updated = parse_iso_date(item.get("updated_on"), f"{label}.updated_on", errors)
    parse_iso_date(item.get("next_review_on"), f"{label}.next_review_on", errors)
    if created is not None and updated is not None and updated < created:
        errors.append(f"{label}.updated_on 不能早于 created_on")

    claim = None
    if "claim" in item:
        claim = require_mapping(item["claim"], f"{label}.claim", errors)
        if claim is not None:
            require_fields(claim, CLAIM_REQUIRED, f"{label}.claim", errors)
            reject_unknown_fields(claim, CLAIM_REQUIRED, f"{label}.claim", errors)
            for field in ("statement", "scope", "mechanism"):
                if field in claim:
                    require_nonempty_string(claim[field], f"{label}.claim.{field}", errors)
            if "exclusions" in claim:
                validate_string_list(claim["exclusions"], f"{label}.claim.exclusions", errors)

    falsifiability = None
    if "falsifiability" in item:
        falsifiability = require_mapping(
            item["falsifiability"], f"{label}.falsifiability", errors
        )
        if falsifiability is not None:
            require_fields(
                falsifiability,
                FALSIFIABILITY_REQUIRED,
                f"{label}.falsifiability",
                errors,
            )
            reject_unknown_fields(
                falsifiability,
                FALSIFIABILITY_REQUIRED,
                f"{label}.falsifiability",
                errors,
            )
            for field in ("prediction", "failure_condition"):
                if field in falsifiability:
                    validate_falsifiable_text(
                        falsifiability[field], f"{label}.falsifiability.{field}", errors
                    )
            if "alternative_explanations" in falsifiability:
                validate_string_list(
                    falsifiability["alternative_explanations"],
                    f"{label}.falsifiability.alternative_explanations",
                    errors,
                )

    if insight_status not in (None, "captured", "archived", "retired"):
        if isinstance(claim, dict):
            statement = claim.get("statement")
            if (
                not isinstance(statement, str)
                or PLACEHOLDER_RE.fullmatch(statement.strip())
                or GENERIC_STATEMENT_RE.fullmatch(statement.strip())
            ):
                errors.append(
                    f"{label}.claim.statement 在 {insight_status} 状态下不能是通用占位判断"
                )
            if is_placeholder_or_default(claim.get("mechanism"), DEFAULT_MECHANISM):
                errors.append(
                    f"{label}.claim.mechanism 在 {insight_status} 状态下不能保留 new 默认模板"
                )
        if isinstance(falsifiability, dict):
            if falsifiability.get("prediction") == DEFAULT_PREDICTION:
                errors.append(
                    f"{label}.falsifiability.prediction 在 {insight_status} 状态下不能保留 new 默认模板"
                )
            if falsifiability.get("failure_condition") == DEFAULT_FAILURE_CONDITION:
                errors.append(
                    f"{label}.falsifiability.failure_condition 在 {insight_status} 状态下不能保留 new 默认模板"
                )
            alternatives = falsifiability.get("alternative_explanations")
            if not isinstance(alternatives, list) or not alternatives:
                errors.append(
                    f"{label}.falsifiability.alternative_explanations 在 {insight_status} 状态下不能为空"
                )
        if is_placeholder_or_default(item.get("next_action"), DEFAULT_NEXT_ACTION):
            errors.append(
                f"{label}.next_action 在 {insight_status} 状态下不能保留 new 默认模板"
            )

    valid_decisive_evidence: list[dict[str, Any]] = []
    if "evidence" in item:
        valid_decisive_evidence = validate_evidence(
            item["evidence"], f"{label}.evidence", errors
        )
    evidence_level = item.get("evidence_level")
    if evidence_level in ("E1", "E2", "E3") and not valid_decisive_evidence:
        errors.append(
            f"{label}.evidence_level 为 {evidence_level} 时，"
            "supporting 或 contradicting evidence 不能为空"
        )
    if evidence_level in ("E2", "E3"):
        independent_cases = {
            evidence_item.get("case_id")
            for evidence_item in valid_decisive_evidence
            if isinstance(evidence_item.get("case_id"), str)
            and evidence_item["case_id"].strip()
        }
        if len(independent_cases) < 2:
            errors.append(
                f"{label}.evidence_level 为 {evidence_level} 时至少需要 2 个不同 case_id 的决定性证据"
            )
    if evidence_level == "E3" and valid_decisive_evidence:
        if not any(item.get("prospective") is True for item in valid_decisive_evidence):
            errors.append(f"{label}.evidence_level E3 至少需要一条 prospective 决定性证据")
        if not any(
            item.get("counterexample") is True or item.get("transfer_test") is True
            for item in valid_decisive_evidence
        ):
            errors.append(
                f"{label}.evidence_level E3 至少需要一条 counterexample 或 transfer_test 证据"
            )
    if insight_status == "supported_scoped" and not any(
        evidence_item.get("relation") == "supports"
        for evidence_item in valid_decisive_evidence
    ):
        errors.append(f"{label}.supported_scoped 状态至少需要一条 supports 证据")
    if insight_status == "rejected" and not any(
        evidence_item.get("relation") == "contradicts"
        for evidence_item in valid_decisive_evidence
    ):
        errors.append(f"{label}.rejected 状态至少需要一条 contradicts 证据")

    experiment_statuses: list[str] = []
    experiment_ids: list[str] = []
    if "experiments" in item:
        experiments = require_list(item["experiments"], f"{label}.experiments", errors)
        if experiments is not None:
            if not experiments:
                errors.append(f"{label}.experiments 至少需要一个实验")
            for index, experiment in enumerate(experiments):
                experiment_id, status = validate_experiment(
                    experiment, f"{label}.experiments[{index}]", errors
                )
                if experiment_id is not None:
                    experiment_ids.append(experiment_id)
                if status is not None:
                    experiment_statuses.append(status)
    duplicate_experiment_ids = sorted(
        experiment_id for experiment_id, count in Counter(experiment_ids).items() if count > 1
    )
    for experiment_id in duplicate_experiment_ids:
        errors.append(f"{label}.experiments 存在重复实验 ID：{experiment_id}")
    if insight_status == "running" and "running" not in experiment_statuses:
        errors.append(f"{label}.status 为 running 时至少需要一个 running 实验")
    if "running" in experiment_statuses and insight_status != "running":
        errors.append(f"{label} 含 running 实验时记录 status 必须是 running")
    frozen_contract_statuses = set(INSIGHT_STATUSES) - {
        "captured",
        "framed",
        "archived",
        "retired",
    }
    if insight_status in frozen_contract_statuses:
        candidate_experiments = item.get("experiments", [])
        if insight_status == "running":
            candidate_experiments = [
                experiment
                for experiment in candidate_experiments
                if isinstance(experiment, dict) and experiment.get("status") == "running"
            ]
        if not any(
            experiment_has_frozen_contract(experiment)
            for experiment in candidate_experiments
        ):
            errors.append(
                f"{label}.experiments 在 {insight_status} 状态下至少需要一个已冻结实验："
                "baseline.frozen_ref、intervention.artifact_ref/version_ref、"
                "非默认主指标阈值和非默认 end_condition 都必须就绪"
            )

    evidence_rank = {level: index for index, level in enumerate(EVIDENCE_LEVELS)}
    if insight_status in ("supported_scoped", "assetized", "monitoring"):
        if evidence_level not in evidence_rank or evidence_rank[evidence_level] < 1:
            errors.append(f"{label}.{insight_status} 状态至少需要 evidence_level E1")
    if insight_status == "stable" and evidence_level != "E3":
        errors.append(f"{label}.stable 状态必须使用 evidence_level E3")

    if "assetization" in item:
        assetization = require_mapping(item["assetization"], f"{label}.assetization", errors)
        if assetization is not None:
            asset_label = f"{label}.assetization"
            require_fields(assetization, ASSETIZATION_REQUIRED, asset_label, errors)
            reject_unknown_fields(assetization, ASSETIZATION_REQUIRED, asset_label, errors)
            if "status" in assetization:
                require_nonempty_string(assetization["status"], f"{asset_label}.status", errors)
            for field in (
                "type",
                "target",
                "regression_check",
                "transfer_test",
                "retirement_condition",
                "portable_core",
                "adapter_boundary",
            ):
                if field in assetization:
                    validate_nullable_string(assetization[field], f"{asset_label}.{field}", errors)
            if "authoritative_refs" in assetization:
                validate_string_list(
                    assetization["authoritative_refs"],
                    f"{asset_label}.authoritative_refs",
                    errors,
                )
            if insight_status in ("assetized", "monitoring", "stable"):
                for field in (
                    "type",
                    "regression_check",
                    "transfer_test",
                    "retirement_condition",
                ):
                    if not isinstance(assetization.get(field), str) or not assetization[field].strip():
                        errors.append(
                            f"{asset_label}.{field} 在 {insight_status} 状态下必须是非空字符串"
                        )
                refs = assetization.get("authoritative_refs")
                if not isinstance(refs, list) or not refs:
                    errors.append(
                        f"{asset_label}.authoritative_refs 在 {insight_status} 状态下不能为空"
                    )
    if "decision_log" in item:
        decision_log = require_list(item["decision_log"], f"{label}.decision_log", errors)
        if decision_log is not None:
            for index, decision in enumerate(decision_log):
                decision_label = f"{label}.decision_log[{index}]"
                if not isinstance(decision, dict) or not decision:
                    errors.append(f"{decision_label} 必须是非空 mapping")
                else:
                    validate_no_blank_strings(decision, decision_label, errors)
    return item


def validate_registry(registry: Any, label: str, errors: list[str]) -> dict[str, Any] | None:
    item = require_mapping(registry, label, errors)
    if item is None:
        return None
    require_fields(item, REGISTRY_REQUIRED, label, errors)
    reject_unknown_fields(item, REGISTRY_REQUIRED, label, errors)
    if type(item.get("schema_version")) is not int or item.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"{label}.schema_version 必须是整数 {SCHEMA_VERSION}")
    parse_iso_date(item.get("updated_on"), f"{label}.updated_on", errors)
    if "timezone" in item:
        require_nonempty_string(item["timezone"], f"{label}.timezone", errors)
    wip_limit = item.get("wip_limit")
    if isinstance(wip_limit, bool) or not isinstance(wip_limit, int) or wip_limit < 1:
        errors.append(f"{label}.wip_limit 必须是大于等于 1 的整数")
    if "insights" in item:
        require_list(item["insights"], f"{label}.insights", errors)
    return item


def validate_registry_entry(
    entry: Any, label: str, errors: list[str]
) -> dict[str, Any] | None:
    item = require_mapping(entry, label, errors)
    if item is None:
        return None
    require_fields(item, REGISTRY_ENTRY_REQUIRED, label, errors)
    reject_unknown_fields(item, REGISTRY_ENTRY_REQUIRED, label, errors)
    if "id" in item:
        validate_id(item["id"], f"{label}.id", errors)
    for field in ("title", "owner"):
        if field in item:
            require_nonempty_string(item[field], f"{label}.{field}", errors)
    if "status" in item:
        validate_enum(item["status"], INSIGHT_STATUSES, f"{label}.status", errors)
    if "evidence_level" in item:
        validate_enum(item["evidence_level"], EVIDENCE_LEVELS, f"{label}.evidence_level", errors)
    if "classification" in item:
        validate_enum(item["classification"], CLASSIFICATIONS, f"{label}.classification", errors)
    parse_iso_date(item.get("updated_on"), f"{label}.updated_on", errors)
    parse_iso_date(item.get("next_review_on"), f"{label}.next_review_on", errors)
    if "record" in item:
        record = require_nonempty_string(item["record"], f"{label}.record", errors)
        if record is not None:
            match = RECORD_PATH_RE.fullmatch(record)
            if match is None:
                errors.append(
                    f"{label}.record 必须匹配 insights/INSIGHT-NNN-<slug>/insight.yml：{record!r}"
                )
            elif isinstance(item.get("id"), str) and match.group("id") != item["id"]:
                errors.append(f"{label}.record 中的 ID 与 {label}.id 不一致")
    return item


def path_is_unsafe(relative_text: str) -> bool:
    if "\\" in relative_text:
        return True
    posix = PurePosixPath(relative_text)
    windows = PureWindowsPath(relative_text)
    if posix.is_absolute() or windows.is_absolute() or windows.drive:
        return True
    return any(part in ("", ".", "..") for part in posix.parts)


def ensure_safe_record_path(root: Path, relative_text: str, label: str) -> Path:
    if path_is_unsafe(relative_text):
        raise WorkspaceError(f"{label} 是不安全路径：{relative_text!r}")
    if root.is_symlink():
        raise WorkspaceError(f"工作区根目录不能是符号链接：{root}")

    candidate = root.joinpath(*PurePosixPath(relative_text).parts)
    current = root
    for part in PurePosixPath(relative_text).parts:
        current = current / part
        if current.is_symlink():
            raise WorkspaceError(f"{label} 不能经过符号链接：{current}")

    try:
        candidate.resolve(strict=False).relative_to(root.resolve(strict=False))
    except ValueError as exc:
        raise WorkspaceError(f"{label} 越出工作区：{relative_text!r}") from exc
    return candidate


def compare_registry_record(
    entry: dict[str, Any], record: dict[str, Any], label: str, errors: list[str]
) -> None:
    mirror_fields = (
        "id",
        "title",
        "status",
        "evidence_level",
        "classification",
        "owner",
        "updated_on",
        "next_review_on",
    )
    for field in mirror_fields:
        if entry.get(field) != record.get(field):
            errors.append(
                f"{label}.{field} 与记录不一致：台账={entry.get(field)!r}，记录={record.get(field)!r}"
            )


def validate_workspace(root: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    root = root.expanduser()
    if not root.exists():
        raise WorkspaceError(f"洞察工作区不存在：{root}")
    if not root.is_dir():
        raise WorkspaceError(f"洞察工作区不是目录：{root}")
    if root.is_symlink():
        raise WorkspaceError(f"洞察工作区不能是符号链接：{root}")

    registry_path = root / REGISTRY_NAME
    if registry_path.is_symlink():
        raise WorkspaceError(f"洞察台账不能是符号链接：{registry_path}")
    if not registry_path.is_file():
        raise WorkspaceError(f"缺少洞察台账：{registry_path}")

    registry = load_yaml(registry_path)
    errors: list[str] = []
    registry_mapping = validate_registry(registry, REGISTRY_NAME, errors)
    entries: list[Any] = []
    if registry_mapping is not None and isinstance(registry_mapping.get("insights"), list):
        entries = registry_mapping["insights"]

    records: list[dict[str, Any]] = []
    ids: list[str] = []
    paths: list[str] = []
    for index, raw_entry in enumerate(entries):
        label = f"{REGISTRY_NAME}.insights[{index}]"
        entry = validate_registry_entry(raw_entry, label, errors)
        if entry is None:
            continue
        insight_id = entry.get("id")
        record_text = entry.get("record")
        if isinstance(insight_id, str):
            ids.append(insight_id)
        if not isinstance(record_text, str) or not record_text.strip():
            continue
        paths.append(record_text)
        try:
            record_path = ensure_safe_record_path(root, record_text, f"{label}.record")
        except WorkspaceError as exc:
            errors.append(str(exc))
            continue
        if not record_path.is_file():
            errors.append(f"{label}.record 不存在或不是普通文件：{record_text}")
            continue
        try:
            raw_record = load_yaml(record_path)
        except WorkspaceError as exc:
            errors.append(str(exc))
            continue
        record = validate_record(raw_record, record_text, errors)
        if record is not None:
            compare_registry_record(entry, record, label, errors)
            records.append(record)

    for insight_id, count in sorted(Counter(ids).items()):
        if count > 1:
            errors.append(f"洞察台账存在重复 ID：{insight_id}")
    for record_path, count in sorted(Counter(paths).items()):
        if count > 1:
            errors.append(f"洞察台账存在重复记录路径：{record_path}")

    insights_dir = root / "insights"
    if insights_dir.is_symlink():
        errors.append(f"洞察记录目录不能是符号链接：{insights_dir}")
    elif insights_dir.exists():
        if not insights_dir.is_dir():
            errors.append(f"洞察记录路径必须是目录：{insights_dir}")
        else:
            registered_paths = set(paths)
            try:
                insight_children = sorted(insights_dir.iterdir(), key=lambda child: child.name)
            except OSError as exc:
                errors.append(f"无法扫描洞察记录目录 {insights_dir}：{exc}")
                insight_children = []
            for child in insight_children:
                if child.is_symlink():
                    errors.append(f"洞察记录目录不能是符号链接：{child}")
                    continue
                if not child.is_dir():
                    continue
                candidate = child / "insight.yml"
                relative_candidate = f"insights/{child.name}/insight.yml"
                if candidate.is_symlink():
                    errors.append(f"洞察记录不能是符号链接：{candidate}")
                elif not candidate.is_file():
                    errors.append(f"洞察记录目录缺少 insight.yml：{child}")
                elif relative_candidate not in registered_paths:
                    errors.append(f"发现未登记的孤立洞察记录：{relative_candidate}")

    running_experiments = sum(
        1
        for record in records
        for experiment in record.get("experiments", [])
        if isinstance(experiment, dict) and experiment.get("status") == "running"
    )
    wip_limit = registry_mapping.get("wip_limit") if registry_mapping else None
    if isinstance(wip_limit, int) and not isinstance(wip_limit, bool):
        if running_experiments > wip_limit:
            errors.append(
                f"全局 running 实验数 {running_experiments} 超过 wip_limit {wip_limit}"
            )

    if errors:
        joined = "\n".join(f"- {error}" for error in errors)
        raise WorkspaceError(f"洞察工作区校验失败（{len(errors)} 项）：\n{joined}")
    assert registry_mapping is not None
    return registry_mapping, records


def parse_cli_date(value: str, option_name: str) -> date:
    errors: list[str] = []
    parsed = parse_iso_date(value, option_name, errors)
    if errors or parsed is None:
        raise WorkspaceError(errors[0])
    return parsed


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii").lower()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_value).strip("-")
    return slug[:64].rstrip("-") or "insight"


def validate_slug(value: str) -> str:
    if len(value) > 64 or not SLUG_RE.fullmatch(value):
        raise WorkspaceError("--slug 必须是 1–64 位小写字母、数字和单连字符组合")
    return value


def next_insight_id(registry: dict[str, Any]) -> str:
    numbers = []
    for entry in registry.get("insights", []):
        if not isinstance(entry, dict):
            continue
        match = INSIGHT_ID_RE.fullmatch(str(entry.get("id", "")))
        if match:
            numbers.append(int(match.group("number")))
    return f"INSIGHT-{max(numbers, default=0) + 1:03d}"


def empty_registry(today_text: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "updated_on": today_text,
        "timezone": DEFAULT_TIMEZONE,
        "wip_limit": DEFAULT_WIP_LIMIT,
        "insights": [],
    }


def build_record(
    *,
    insight_id: str,
    title: str,
    statement: str,
    scope: str,
    owner: str,
    today_text: str,
    next_review_text: str,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "id": insight_id,
        "title": title,
        "classification": "internal",
        "status": "captured",
        "evidence_level": "E0",
        "owner": owner,
        "created_on": today_text,
        "updated_on": today_text,
        "next_review_on": next_review_text,
        "claim": {
            "statement": statement,
            "scope": scope,
            "mechanism": DEFAULT_MECHANISM,
            "exclusions": [],
        },
        "falsifiability": {
            "prediction": DEFAULT_PREDICTION,
            "failure_condition": DEFAULT_FAILURE_CONDITION,
            "alternative_explanations": [],
        },
        "evidence": {
            "supporting": [],
            "contradicting": [],
            "neutral": [],
            "unknowns": [],
        },
        "experiments": [
            {
                "id": "EXP-001",
                "title": "首轮验证",
                "status": "planned",
                "question": "该洞察在限定范围内是否产生可测变化？",
                "baseline": {
                    "description": "冻结当前流程作为基线。",
                    "frozen_ref": None,
                    "missing_data_rule": "没有实测数据时保留 null，不从记忆或代理指标推算。",
                },
                "intervention": {
                    "description": "应用由该洞察导出的最小工作流改动。",
                    "artifact_ref": None,
                    "version_ref": None,
                },
                "controls": ["保持输入、工具、操作者和质量门一致。"],
                "metrics": {
                    "primary": {
                        "id": "target-defect-recurrence-rate",
                        "definition": "同机制目标缺陷数除以预先声明的触发机会数。",
                        "direction": "lower",
                        "success_threshold": DEFAULT_SUCCESS_THRESHOLD,
                        "baseline": None,
                        "result": None,
                    },
                    "secondary": [
                        {
                            "id": "total-human-minutes",
                            "definition": "规划、实验、审校、返工和资产维护的实测人工分钟数。",
                            "direction": "lower",
                            "success_threshold": "实验启动前冻结可测阈值。",
                            "baseline": None,
                            "result": None,
                        },
                        {
                            "id": "revision-rounds",
                            "definition": "从首稿到同一审校状态的实质修改轮次。",
                            "direction": "lower",
                            "success_threshold": "实验分支不得高于对照分支。",
                            "baseline": None,
                            "result": None,
                        },
                    ],
                    "guardrails": [
                        {
                            "id": "release-blockers",
                            "condition": "事实、引语、版权、隐私、发布和语法阻断项不得增加。",
                        },
                        {
                            "id": "blind-read-quality",
                            "condition": "盲审清晰度与可信度不得恶化。",
                        },
                    ],
                },
                "evidence_refs": [],
                "decision": "pending",
                "end_condition": DEFAULT_END_CONDITION,
            }
        ],
        "assetization": {
            "status": "none",
            "type": None,
            "target": None,
            "authoritative_refs": [],
            "regression_check": None,
            "transfer_test": None,
            "retirement_condition": None,
            "portable_core": None,
            "adapter_boundary": None,
        },
        "next_action": DEFAULT_NEXT_ACTION,
        "decision_log": [
            {
                "date": today_text,
                "decision": "captured",
                "rationale": "已将原始洞察登记为待验证假设。",
            }
        ],
    }


def registry_entry(record: dict[str, Any], relative_path: str) -> dict[str, Any]:
    return {
        "id": record["id"],
        "title": record["title"],
        "record": relative_path,
        "status": record["status"],
        "evidence_level": record["evidence_level"],
        "classification": record["classification"],
        "owner": record["owner"],
        "updated_on": record["updated_on"],
        "next_review_on": record["next_review_on"],
    }


def load_registry_for_new(root: Path, today_text: str) -> dict[str, Any]:
    registry_path = root / REGISTRY_NAME
    if not registry_path.exists():
        if registry_path.is_symlink():
            raise WorkspaceError(f"洞察台账不能是符号链接：{registry_path}")
        return empty_registry(today_text)
    registry, _ = validate_workspace(root)
    return copy.deepcopy(registry)


@contextmanager
def registry_write_lock(root: Path, timeout_seconds: float = 10.0) -> Any:
    lock_path = root / ".洞察台账.lock"
    deadline = time.monotonic() + timeout_seconds
    descriptor: int | None = None
    while descriptor is None:
        try:
            descriptor = os.open(
                lock_path,
                os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                0o600,
            )
        except FileExistsError as exc:
            if time.monotonic() >= deadline:
                raise WorkspaceError(
                    f"等待洞察台账写锁超时；若确认没有其他 new 进程，请检查陈旧锁：{lock_path}"
                ) from exc
            time.sleep(0.05)
        except OSError as exc:
            raise WorkspaceError(f"无法创建洞察台账写锁 {lock_path}：{exc}") from exc
    try:
        os.write(descriptor, f"pid={os.getpid()}\n".encode("utf-8"))
        os.fsync(descriptor)
        yield
    finally:
        if descriptor is not None:
            os.close(descriptor)
        try:
            lock_path.unlink()
        except OSError as exc:
            raise WorkspaceError(
                f"无法清理洞察台账写锁，工作区状态不确定：{lock_path}：{exc}"
            ) from exc


def prepare_new_plan(
    *,
    root: Path,
    args: argparse.Namespace,
    today: date,
    next_review: date,
    title: str,
    statement: str,
    scope: str,
    owner: str,
) -> tuple[str, str, Path, dict[str, Any], dict[str, Any]]:
    registry = load_registry_for_new(root, today.isoformat())
    insight_id = args.id or next_insight_id(registry)
    id_errors: list[str] = []
    validate_id(insight_id, "--id", id_errors)
    if id_errors:
        raise WorkspaceError(id_errors[0])
    slug = validate_slug(args.slug) if args.slug else slugify(title)

    existing_ids = {
        entry.get("id") for entry in registry.get("insights", []) if isinstance(entry, dict)
    }
    if insight_id in existing_ids:
        raise WorkspaceError(f"洞察 ID 已存在，禁止覆盖：{insight_id}")
    relative_path = f"insights/{insight_id}-{slug}/insight.yml"
    target = ensure_safe_record_path(root, relative_path, "新记录路径")
    if target.exists() or target.parent.exists():
        raise WorkspaceError(f"目标记录目录已存在，禁止覆盖：{target.parent}")

    record = build_record(
        insight_id=insight_id,
        title=title,
        statement=statement,
        scope=scope,
        owner=owner,
        today_text=today.isoformat(),
        next_review_text=next_review.isoformat(),
    )
    record_errors: list[str] = []
    validate_record(record, relative_path, record_errors)
    if record_errors:
        raise WorkspaceError("内部生成记录未通过校验：\n" + "\n".join(record_errors))

    updated_registry = copy.deepcopy(registry)
    updated_registry["updated_on"] = today.isoformat()
    updated_registry.setdefault("insights", []).append(registry_entry(record, relative_path))
    updated_registry["insights"] = sorted(
        updated_registry["insights"], key=lambda item: item["id"]
    )
    return insight_id, relative_path, target, record, updated_registry


def command_new(args: argparse.Namespace) -> int:
    root = Path(args.root).expanduser()
    today = parse_cli_date(args.today or date.today().isoformat(), "--today")
    next_review = parse_cli_date(
        args.next_review_on or (today + timedelta(days=7)).isoformat(), "--next-review-on"
    )
    if next_review < today:
        raise WorkspaceError("--next-review-on 不能早于 --today")
    title = require_cli_text(args.title, "--title")
    statement = require_cli_text(args.statement, "--statement")
    scope = require_cli_text(args.scope, "--scope")
    owner = require_cli_text(args.owner, "--owner")

    if root.exists() and (not root.is_dir() or root.is_symlink()):
        raise WorkspaceError(f"--root 必须是非符号链接目录：{root}")

    if args.dry_run:
        insight_id, _, target, record, _ = prepare_new_plan(
            root=root,
            args=args,
            today=today,
            next_review=next_review,
            title=title,
            statement=statement,
            scope=scope,
            owner=owner,
        )
        print(f"DRY-RUN：将创建 {target}")
        print(dump_yaml(record), end="")
        return 0

    root_created = not root.exists()
    root.mkdir(parents=True, exist_ok=True)
    transaction_committed = False
    try:
        with registry_write_lock(root):
            insight_id, _, target, record, updated_registry = prepare_new_plan(
                root=root,
                args=args,
                today=today,
                next_review=next_review,
                title=title,
                statement=statement,
                scope=scope,
                owner=owner,
            )
            record_dir_created = False
            record_written = False
            registry_path = root / REGISTRY_NAME
            registry_existed = registry_path.exists()
            registry_original = registry_path.read_bytes() if registry_existed else None
            try:
                target.parent.mkdir(parents=True, exist_ok=False)
                record_dir_created = True
                atomic_write_text(target, dump_yaml(record))
                record_written = True
                atomic_write_text(registry_path, dump_yaml(updated_registry))
                # Read back inside the transaction so any failure restores both files.
                validate_workspace(root)
                transaction_committed = True
            except BaseException as original_error:
                rollback_errors: list[str] = []
                if record_written or target.exists() or target.is_symlink():
                    try:
                        target.unlink(missing_ok=True)
                    except OSError as exc:
                        rollback_errors.append(f"无法删除新记录 {target}：{exc}")
                if registry_existed and registry_original is not None:
                    try:
                        atomic_write_text(registry_path, registry_original.decode("utf-8"))
                    except (WorkspaceError, UnicodeError) as exc:
                        rollback_errors.append(f"无法恢复原台账 {registry_path}：{exc}")
                elif not registry_existed:
                    try:
                        registry_path.unlink(missing_ok=True)
                    except OSError as exc:
                        rollback_errors.append(f"无法删除新台账 {registry_path}：{exc}")
                if record_dir_created:
                    cleanup_empty_parents(target.parent, stop=root)
                if rollback_errors:
                    detail = "；".join(rollback_errors)
                    raise WorkspaceError(
                        "创建失败且回滚不完整，工作区状态不确定，请人工检查："
                        f"{detail}"
                    ) from original_error
                raise
    except BaseException:
        if root_created:
            try:
                root.rmdir()
            except OSError:
                pass
        raise
    if not transaction_committed:  # Defensive: every non-error path must read back.
        raise WorkspaceError("创建事务未完成")
    print(f"已创建洞察 {insight_id}")
    print(f"记录：{target}")
    print(f"台账：{registry_path}")
    return 0


def cleanup_empty_parents(start: Path, stop: Path) -> None:
    current = start
    while current != stop and current != current.parent:
        try:
            current.rmdir()
        except OSError:
            break
        current = current.parent


def require_cli_text(value: str, option_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise WorkspaceError(f"{option_name} 必须是非空字符串")
    if value != value.strip():
        raise WorkspaceError(f"{option_name} 首尾不能包含空白")
    return value


def command_validate(args: argparse.Namespace) -> int:
    root = Path(args.root).expanduser()
    registry, records = validate_workspace(root)
    running = sum(
        1
        for record in records
        for experiment in record["experiments"]
        if experiment["status"] == "running"
    )
    print(
        f"校验通过：{len(registry['insights'])} 条洞察，"
        f"{running}/{registry['wip_limit']} 个 running 实验"
    )
    return 0


def command_status(args: argparse.Namespace) -> int:
    root = Path(args.root).expanduser()
    as_of = parse_cli_date(args.as_of or date.today().isoformat(), "--as-of")
    registry, records = validate_workspace(root)
    entries = registry["insights"]
    records_by_id = {record["id"]: record for record in records}
    counts = Counter(entry["status"] for entry in entries)
    print(f"洞察状态（截至 {as_of.isoformat()}）")
    for status in INSIGHT_STATUSES:
        print(f"- {status}: {counts.get(status, 0)}")

    active_entries = [
        entry for entry in entries if entry["status"] not in ("archived", "retired")
    ]
    print("当前项：")
    if not active_entries:
        print("- 无")
    for entry in sorted(active_entries, key=lambda current: current["id"]):
        record = records_by_id[entry["id"]]
        active_experiment_ids = [
            experiment["id"]
            for experiment in record["experiments"]
            if experiment["status"] in ("planned", "running", "evaluated")
        ]
        experiments_text = ", ".join(active_experiment_ids) or "无活动实验"
        print(
            f"- {entry['id']} | {entry['status']} | {entry['evidence_level']} | "
            f"复查 {entry['next_review_on']} | {entry['title']}"
        )
        print(f"  实验：{experiments_text}")
        print(f"  下一步：{record['next_action']}")

    due: list[tuple[date, dict[str, Any]]] = []
    for entry in entries:
        review_date = date.fromisoformat(entry["next_review_on"])
        if review_date <= as_of:
            due.append((review_date, entry))
    due.sort(key=lambda pair: (pair[0], pair[1]["id"]))
    print("到期项：")
    if not due:
        print("- 无")
    for review_date, entry in due:
        print(
            f"- {entry['id']} | {entry['status']} | {review_date.isoformat()} | "
            f"{entry['title']}"
        )
    actionable_due = [
        entry for _, entry in due if entry["status"] not in ("archived", "retired")
    ]
    if args.fail_on_due and actionable_due:
        print(
            f"到期门禁失败：{len(actionable_due)} 条未归档／未退役洞察需要复查",
            file=sys.stderr,
        )
        return 2
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="把核心洞察登记为可证伪实验，并维护可迁移资产的确定性台账。"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    new_parser = subparsers.add_parser("new", help="创建洞察记录并原子更新台账")
    new_parser.add_argument("--root", default=str(DEFAULT_ROOT), help="洞察实验室根目录")
    new_parser.add_argument("--id", help="洞察 ID；默认按现有编号自动递增")
    new_parser.add_argument("--slug", help="记录目录短名；默认从标题生成")
    new_parser.add_argument("--title", required=True, help="洞察标题")
    new_parser.add_argument("--statement", required=True, help="待验证的核心判断")
    new_parser.add_argument("--scope", required=True, help="判断适用范围")
    new_parser.add_argument("--owner", default="unassigned", help="负责人")
    new_parser.add_argument("--today", help="固定创建日期 YYYY-MM-DD")
    new_parser.add_argument("--next-review-on", help="下次复查日期 YYYY-MM-DD")
    new_parser.add_argument("--dry-run", action="store_true", help="只输出计划，零写入")
    new_parser.set_defaults(handler=command_new)

    validate_parser = subparsers.add_parser("validate", help="严格校验台账和全部记录")
    validate_parser.add_argument("--root", default=str(DEFAULT_ROOT), help="洞察实验室根目录")
    validate_parser.set_defaults(handler=command_validate)

    status_parser = subparsers.add_parser("status", help="列出状态分布和到期项")
    status_parser.add_argument("--root", default=str(DEFAULT_ROOT), help="洞察实验室根目录")
    status_parser.add_argument("--as-of", help="状态截止日期 YYYY-MM-DD")
    status_parser.add_argument(
        "--fail-on-due",
        action="store_true",
        help="存在未归档／未退役到期项时返回 2，供定期审计使用",
    )
    status_parser.set_defaults(handler=command_status)
    return parser


def main(argv: list[str] | None = None) -> int:
    configure_utf8_stdio()
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.handler(args))
    except WorkspaceError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("错误：操作被中断", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
