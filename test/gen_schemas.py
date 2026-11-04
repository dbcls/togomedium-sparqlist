"""
Generate test/schemas/*.json from the current API responses, and report
discrepancies against the published OpenAPI spec.

The actual JSON is treated as the source of truth: types are inferred from
the response to the default parameters (same request as test_schemas.py),
and keys present in every sampled object become `required`.

Usage:
    BASE_URL=https://togomedium.org python3 test/gen_schemas.py [--no-write]

Outputs:
    test/schemas/{endpoint}.json   (overwritten unless --no-write)
    test/spec_diff.md              discrepancies vs SPEC_URL
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.request

from test_schemas import (
    BASE_URL,
    CASES,
    SCHEMA_DIR,
    _build_url,
    _fetch_json,
    _parse_md_file,
)

SPEC_URL = "https://togomedium-api.yohak-lab.com/"
REPORT_PATH = os.path.join(os.path.dirname(__file__), "spec_diff.md")
TYPE_ORDER = ["null", "boolean", "integer", "number", "string", "array", "object"]


# ---------------------------------------------------------------------------
# Schema inference
# ---------------------------------------------------------------------------

def _json_type(value) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    return "object"


def infer(samples: list) -> dict:
    """Infer a JSON Schema that accepts every value in `samples`."""
    types = {_json_type(v) for v in samples}
    if {"integer", "number"} <= types:
        types.discard("integer")
    schema: dict = {}
    if types:
        ordered = [t for t in TYPE_ORDER if t in types]
        schema["type"] = ordered[0] if len(ordered) == 1 else ordered

    objects = [v for v in samples if isinstance(v, dict)]
    if objects:
        keys: list[str] = []
        for o in objects:
            keys += [k for k in o if k not in keys]
        schema["required"] = [k for k in keys if all(k in o for o in objects)]
        schema["properties"] = {
            k: infer([o[k] for o in objects if k in o]) for k in keys
        }

    elements = [e for v in samples if isinstance(v, list) for e in v]
    if elements:
        schema["items"] = infer(elements)
    return schema


# ---------------------------------------------------------------------------
# Spec comparison
# ---------------------------------------------------------------------------

def load_spec(url: str) -> dict:
    """Extract the OpenAPI document embedded in a ReDoc static page."""
    with urllib.request.urlopen(url, timeout=60) as response:
        html = response.read().decode("utf-8")
    m = re.search(r"const __redoc_state = (\{.*?\});\s*\n", html, re.DOTALL)
    if not m:
        raise RuntimeError(f"no __redoc_state found in {url}")
    return json.loads(m.group(1))["spec"]["data"]


def spec_response_schema(spec: dict, endpoint: str) -> dict | None:
    op = spec["paths"].get(f"/{endpoint}", {}).get("get", {})
    content = op.get("responses", {}).get("200", {}).get("content", {})
    for media in content.values():
        if "schema" in media:
            return media["schema"]
    return None


def _resolve(spec: dict, schema: dict) -> dict:
    while "$ref" in schema:
        node = spec
        for part in schema["$ref"].lstrip("#/").split("/"):
            node = node[part]
        schema = node
    return schema


def _types(schema: dict) -> set[str]:
    t = schema.get("type")
    return set(t) if isinstance(t, list) else ({t} if t else set())


def compare(spec: dict, expected: dict, actual: dict, path: str, out: list):
    """Append (path, spec, actual) tuples describing mismatches."""
    expected = _resolve(spec, expected)
    exp_t, act_t = _types(expected), _types(actual)
    # integer is a subset of number in JSON Schema
    if "number" in exp_t and "integer" in act_t:
        act_t = (act_t - {"integer"}) | {"number"}
    if exp_t and act_t and not act_t <= exp_t:
        out.append((path, " / ".join(sorted(exp_t)), " / ".join(sorted(act_t))))

    exp_props = expected.get("properties", {})
    act_props = actual.get("properties", {})
    if exp_props or act_props:
        for k in exp_props:
            if k not in act_props:
                out.append((f"{path}.{k}", "あり", "キーなし"))
        for k in act_props:
            if k not in exp_props:
                out.append((f"{path}.{k}", "未定義", " / ".join(sorted(_types(act_props[k]))) or "-"))
        for k in exp_props.keys() & act_props.keys():
            compare(spec, exp_props[k], act_props[k], f"{path}.{k}", out)

    if "items" in expected and "items" in actual:
        compare(spec, expected["items"], actual["items"], f"{path}[]", out)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    write = "--no-write" not in sys.argv[1:]
    spec = load_spec(SPEC_URL)
    spec_paths = {p.strip("/") for p in spec["paths"]}

    diffs: dict[str, list] = {}
    missing_in_spec, no_schema_in_spec, failed = [], [], []

    for endpoint, md_path, _ in CASES:
        url = _build_url(endpoint, _parse_md_file(md_path)["parameters"])
        try:
            body = _fetch_json(url)
        except Exception as e:  # noqa: BLE001 - report and continue
            print(f"✗ {endpoint}: {e}")
            failed.append((endpoint, str(e)))
            continue

        schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": endpoint,
            **infer([body]),
        }
        if write:
            with open(os.path.join(SCHEMA_DIR, f"{endpoint}.json"), "w", encoding="utf-8") as f:
                json.dump(schema, f, indent=2, ensure_ascii=False)
                f.write("\n")
        print(f"✓ {endpoint}")

        if endpoint not in spec_paths:
            missing_in_spec.append(endpoint)
            continue
        expected = spec_response_schema(spec, endpoint)
        if expected is None:
            no_schema_in_spec.append(endpoint)
            continue
        out: list = []
        compare(spec, expected, schema, "$", out)
        if out:
            diffs[endpoint] = out

    repo = {c[0] for c in CASES}
    spec_only = sorted(spec_paths - repo - {"gms_by_kegg_tids_3", "gms_kegg_code_tid"})

    lines = [
        "# API 仕様書と現状実装の差分",
        "",
        f"- 仕様書: {SPEC_URL} (OpenAPI {spec.get('openapi')}, {spec['info'].get('title')} {spec['info'].get('version')})",
        f"- 実装: {BASE_URL} の default パラメータでのレスポンス",
        "- `test/gen_schemas.py` で自動生成。「仕様」「実装」列は型、またはキーの有無。",
        "",
        "## 型・キーの食い違い",
        "",
    ]
    if diffs:
        lines += ["| endpoint | path | 仕様 | 実装 |", "|---|---|---|---|"]
        for endpoint in sorted(diffs):
            for path, exp, act in diffs[endpoint]:
                lines.append(f"| `{endpoint}` | `{path}` | {exp} | {act} |")
    else:
        lines.append("なし")
    lines += ["", "## 仕様書に載っていない endpoint", ""]
    lines += [f"- `{e}`" for e in sorted(missing_in_spec)] or ["なし"]
    lines += ["", "## 仕様書にレスポンススキーマがない endpoint", ""]
    lines += [f"- `{e}`" for e in sorted(no_schema_in_spec)] or ["なし"]
    lines += ["", "## 仕様書にだけある endpoint（repository に MD なし）", ""]
    lines += [f"- `{e}`" for e in spec_only] or ["なし"]
    if failed:
        lines += ["", "## 取得に失敗した endpoint（スキーマ未生成）", ""]
        lines += [f"- `{e}`: {err}" for e, err in failed]

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\nreport: {REPORT_PATH}")


if __name__ == "__main__":
    main()
