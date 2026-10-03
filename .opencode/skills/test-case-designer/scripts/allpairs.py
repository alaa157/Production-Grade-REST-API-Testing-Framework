#!/usr/bin/env python3
"""
allpairs.py — Pairwise test combination generator for test-case-designer skill.

Usage:
    python allpairs.py --input '{"parameters": {"browser": ["Chrome", "Firefox"], "os": ["Win", "Mac"]}}'

Output:
    Markdown table to stdout with one row per generated test combination.
"""

import argparse
import json
import sys

try:
    from allpairspy import AllPairs
except ImportError:
    print(
        "⚠️  allpairspy not installed. Run: pip install allpairspy",
        file=sys.stderr,
    )
    sys.exit(1)


def generate(parameters: dict) -> list[dict]:
    """Run AllPairs algorithm and return list of combination dicts."""
    param_names = list(parameters.keys())
    param_values = [parameters[k] for k in param_names]

    combinations = []
    for i, pair in enumerate(AllPairs(param_values), start=1):
        row = {"Case": str(i)}
        # allpairspy >= 2.5 yields plain lists; older versions yielded objects with .test_vector
        test_vector = pair if isinstance(pair, list) else pair.test_vector
        for name, value in zip(param_names, test_vector):
            row[name] = str(value)
        combinations.append(row)
    return combinations


def to_markdown(combinations: list[dict]) -> str:
    """Render combination list as a Markdown table."""
    if not combinations:
        return "_No combinations generated._"

    headers = list(combinations[0].keys())
    col_widths = {h: max(len(h), max(len(row[h]) for row in combinations)) for h in headers}

    def fmt_row(row: dict) -> str:
        return "| " + " | ".join(row[h].ljust(col_widths[h]) for h in headers) + " |"

    separator = "| " + " | ".join("-" * col_widths[h] for h in headers) + " |"
    header_row = fmt_row({h: h for h in headers})

    lines = [header_row, separator] + [fmt_row(row) for row in combinations]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Pairwise test combination generator")
    parser.add_argument(
        "--input",
        required=True,
        help='JSON string: {"parameters": {"param1": ["v1","v2"], ...}}',
    )
    args = parser.parse_args()

    try:
        data = json.loads(args.input)
    except json.JSONDecodeError as e:
        print(f"⚠️  Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    if "parameters" not in data or not isinstance(data["parameters"], dict):
        print('⚠️  Input must have a "parameters" key with a dict value.', file=sys.stderr)
        sys.exit(1)

    parameters = data["parameters"]
    if len(parameters) < 2:
        print("⚠️  At least 2 parameters are required for pairwise testing.", file=sys.stderr)
        sys.exit(1)

    combinations = generate(parameters)
    print(to_markdown(combinations))


if __name__ == "__main__":
    main()
