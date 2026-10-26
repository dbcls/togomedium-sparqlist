"""
L1: JSON Schema validation for TogoMedium SPARQLIST endpoints.

For each endpoint that has a matching schema file under test/schemas/,
hit the API with default parameters and validate the response against the schema.

Usage:
    BASE_URL=http://localhost:3000 pytest test/test_schemas.py -v

Endpoints without a schema file are reported as skipped, so the coverage
gap is visible. Endpoints listed in EXCLUDED are skipped silently
(mirrors test/api_test.py).
"""
from __future__ import annotations

import glob
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request

import jsonschema
import pytest

BASE_URL = os.environ.get("BASE_URL", "http://localhost:3000").rstrip("/")
REPO_DIR = os.path.join(os.path.dirname(__file__), "..", "repository")
SCHEMA_DIR = os.path.join(os.path.dirname(__file__), "schemas")

SPECIAL_DEFAULTS = {
    "gmdb_taxonomy_search_by_name": {"q": "Nocardioides"},
    "gmdb_taxonomy_gtdb_search_by_name": {"q": "Nocardioides"},
}

EXCLUDED_ENDPOINTS = {
    "gms_kegg_code_tid",
    "gms_by_kegg_tids_3",
}


def _parse_md_file(file_path: str) -> dict:
    """Extract endpoint name and default parameters from a SPARQList MD file."""
    endpoint = os.path.basename(file_path).replace(".md", "")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    parameters: dict[str, str | None] = {}
    section = re.search(r"## Parameters\s*\n(.*?)(?=\n##|\Z)", content, re.DOTALL)
    if section:
        for name, default in re.findall(
            r"\* `([^`]+)`[^\n]*\n(?:\s*\* default: ([^\n]+))?",
            section.group(1),
        ):
            parameters[name] = default.strip() if default else None

    return {"endpoint": endpoint, "parameters": parameters}


def _build_url(endpoint: str, parameters: dict[str, str | None]) -> str:
    url = f"{BASE_URL}/sparqlist/api/{endpoint}"
    query = {k: v for k, v in parameters.items() if v is not None}
    query.update(SPECIAL_DEFAULTS.get(endpoint, {}))
    if query:
        url += "?" + urllib.parse.urlencode(query)
    return url


def _fetch_json(url: str):
    with urllib.request.urlopen(url, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def _discover_cases():
    """Yield (endpoint_name, md_path, schema_path_or_None) for each MD file."""
    md_files = sorted(glob.glob(os.path.join(REPO_DIR, "*.md")))
    for md in md_files:
        name = os.path.basename(md).replace(".md", "")
        if name in EXCLUDED_ENDPOINTS:
            continue
        schema = os.path.join(SCHEMA_DIR, f"{name}.json")
        yield name, md, schema if os.path.exists(schema) else None


CASES = list(_discover_cases())


@pytest.mark.parametrize(
    "endpoint,md_path,schema_path",
    CASES,
    ids=[c[0] for c in CASES],
)
def test_response_matches_schema(endpoint, md_path, schema_path):
    if schema_path is None:
        pytest.skip(f"no schema for {endpoint} (add test/schemas/{endpoint}.json)")

    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    info = _parse_md_file(md_path)
    url = _build_url(info["endpoint"], info["parameters"])

    try:
        body = _fetch_json(url)
    except urllib.error.HTTPError as e:
        pytest.fail(f"HTTP {e.code} {e.reason} for {url}")
    except urllib.error.URLError as e:
        pytest.fail(f"connection error for {url}: {e}")
    except json.JSONDecodeError as e:
        pytest.fail(f"non-JSON response from {url}: {e}")

    try:
        jsonschema.validate(instance=body, schema=schema)
    except jsonschema.ValidationError as e:
        pytest.fail(
            f"schema mismatch for {endpoint}\n"
            f"  url: {url}\n"
            f"  path: {list(e.absolute_path)}\n"
            f"  message: {e.message}"
        )
