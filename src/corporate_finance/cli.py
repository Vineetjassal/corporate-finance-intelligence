"""Command-line interface for Corporate Finance Intelligence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import analyze_dict


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze a corporate financial snapshot.")
    parser.add_argument("input", type=Path, help="Path to a JSON financial snapshot")
    parser.add_argument("--output", type=Path, help="Optional path for the JSON report")
    args = parser.parse_args()

    try:
        data = json.loads(args.input.read_text(encoding="utf-8"))
        report = analyze_dict(data)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))

    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
