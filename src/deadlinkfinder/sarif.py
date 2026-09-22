"""SARIF v2.1.0 generator for DeadLinkFinder.

Enables native GitHub Code Scanning Alerts integration for documentation links.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .verifier import BrokenLink, VerificationReport

SARIF_SCHEMA = "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json"
TOOL_VERSION = "0.2.0"

RULES = [
    {
        "id": "DLF-001",
        "name": "Broken Local File Link",
        "shortDescription": {"text": "Target local file does not exist"},
        "fullDescription": {"text": "A markdown link or image points to a relative file path that does not exist in the repository."},
        "defaultConfiguration": {"level": "error"},
        "help": {
            "text": "Ensure the referenced file exists or update the path.",
            "markdown": "### Remediation\nEnsure the referenced relative file exists at the specified path or update the relative link.",
        },
        "properties": {"tags": ["documentation", "links", "markdown"]},
    },
    {
        "id": "DLF-002",
        "name": "Missing Anchor Slug",
        "shortDescription": {"text": "Target heading anchor not found"},
        "fullDescription": {"text": "A markdown link points to an anchor (#section) that does not exist in the target document."},
        "defaultConfiguration": {"level": "warning"},
        "help": {
            "text": "Verify the heading text in the target document to ensure the anchor slug matches.",
            "markdown": "### Remediation\nVerify the heading text in the target document to ensure the anchor slug matches.",
        },
        "properties": {"tags": ["documentation", "anchors", "markdown"]},
    },
    {
        "id": "DLF-003",
        "name": "Broken External URL",
        "shortDescription": {"text": "External URL returned an error or timed out"},
        "fullDescription": {"text": "An external HTTP/HTTPS link returned an HTTP error status (>= 400) or could not be reached."},
        "defaultConfiguration": {"level": "warning"},
        "help": {
            "text": "Check if the remote page was moved, deleted, or requires authentication.",
            "markdown": "### Remediation\nCheck if the remote page was moved, deleted, or requires authentication.",
        },
        "properties": {"tags": ["documentation", "external-links", "web"]},
    },
]


def generate_sarif(report: VerificationReport) -> dict[str, Any]:
    """Convert verification report into a SARIF v2.1.0 compliant dictionary."""
    results: list[dict[str, Any]] = []

    for b in report.broken_links:
        ref = b.reference
        uri = ref.source_file.replace("\\", "/").lstrip("./")
        level = "error" if b.rule_id == "DLF-001" else "warning"

        msg = f"{b.rule_name}: {b.reason} ('{ref.raw_target}')."
        if b.suggestion:
            msg += f" Did you mean '{b.suggestion}'?"

        result = {
            "ruleId": b.rule_id,
            "level": level,
            "message": {"text": msg},
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {
                            "uri": uri,
                            "uriBaseId": "%SRCROOT%",
                        },
                        "region": {
                            "startLine": ref.line_number,
                            "startColumn": 1,
                        },
                    }
                }
            ],
            "properties": {
                "target": ref.raw_target,
                "isImage": ref.is_image,
                "suggestion": b.suggestion,
            },
        }
        results.append(result)

    return {
        "$schema": SARIF_SCHEMA,
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "DeadLinkFinder",
                        "semanticVersion": TOOL_VERSION,
                        "informationUri": "https://github.com/umutgungorr/deadlinkfinder",
                        "rules": RULES,
                    }
                },
                "results": results,
            }
        ],
    }


def to_sarif_json(report: VerificationReport, indent: int = 2) -> str:
    """Format report as SARIF v2.1.0 JSON string."""
    return json.dumps(generate_sarif(report), indent=indent)
