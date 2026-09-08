# Corporate Finance Intelligence

An interactive, auditable corporate-finance intelligence toolkit for comparing major companies across profitability, liquidity, leverage, efficiency, cash flow and transparent risk flags.

## Dashboard

Run the interactive Streamlit dashboard:

```bash
pip install -r requirements.txt
streamlit run dashboard.py
```

The dashboard provides:
- Company selector across 10 large companies
- Executive KPI cards
- Profitability charts
- Liquidity and leverage charts
- Peer comparison table
- EBITDA-margin ranking
- Risk flags with explanations
- A reproducible underlying Python calculation engine

## CLI

```bash
python -m unittest discover -s tests -v
python -m src.corporate_finance.cli data/sample_company.json
python -m src.corporate_finance.cli data/sample_company.json --output reports/sample_report.json
```

## Data

`data/top10_companies.json` contains the demonstration universe. Company selection and headline revenue figures are based on the Fortune 500 2026 ranking. Metrics not directly available from that ranking are explicitly marked as illustrative demo assumptions so the dashboard can demonstrate the analytical workflow. Replace these with audited annual-report filings before using the tool for real investment, lending or credit decisions.

## Architecture

```text
Data JSON → FinancialSnapshot validation → Metric engine → Risk rules → CLI / Streamlit dashboard
```

## Project layout

```text
blueprint.md
README.md
requirements.txt
pyproject.toml
dashboard.py
data/
  README.md
  sample_company.json
  top10_companies.json
src/
  __init__.py
  corporate_finance/
    __init__.py
    core.py
    cli.py
tests/
  __init__.py
  test_core.py
  test_cli.py
reports/
  .gitkeep
```

## Design principles

- Dependency-light calculation engine.
- Deterministic and explainable financial metrics.
- Explicit handling of unavailable or zero-denominator ratios.
- Interactive visualization separated from the core analytical engine.
- Demo assumptions are clearly labeled rather than presented as audited facts.
- No investment advice or automated credit decision.
