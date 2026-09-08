# Corporate Finance Intelligence

A dependency-light Python toolkit for auditable corporate-finance analysis. It turns a normalized company financial snapshot into profitability, liquidity, leverage, efficiency, cash-flow metrics and transparent risk flags.

## Quick start

```bash
python -m unittest discover -s tests -v
python -m src.corporate_finance.cli data/sample_company.json
```

The CLI prints a JSON report and can also write it to a file:

```bash
python -m src.corporate_finance.cli data/sample_company.json --output reports/sample_report.json
```

## Input

See `data/sample_company.json`. Monetary values are assumed to use the same unit (for example, INR crore or USD million).

Required fields are documented in `src/corporate_finance/core.py` and validated before calculations run.

## Project layout

```text
blueprint.md
README.md
pyproject.toml
src/corporate_finance/
  __init__.py
  core.py
  cli.py
data/sample_company.json
reports/.gitkeep
tests/test_core.py
```

## Design principles

- Standard-library only for the first release.
- Deterministic calculations and explainable risk rules.
- Explicit handling of unavailable or zero-denominator ratios.
- JSON output suitable for downstream automation.
- No investment advice and no automated credit decision.
