# Corporate Finance Intelligence

A recruiter-ready corporate-finance analytics platform built with **Python, Pandas, NumPy, Plotly and Streamlit**. It turns financial statement inputs into transparent ratios, risk flags, a 0–100 financial-health score, peer benchmarking and interactive what-if scenarios.

## What this project demonstrates

- Financial statement normalization and validation
- Profitability, liquidity, leverage, coverage, efficiency and cash-flow analytics
- Explainable rule-based financial risk screening
- Weighted financial-health score with component-level attribution
- Peer benchmarking and portfolio-style screening
- Leverage vs interest-coverage risk mapping
- Interactive scenario/sensitivity analysis
- Downloadable analysis dataset
- Unit-tested calculation engine with edge-case handling
- Separate analytical core from presentation layer

## Dashboard modules

The main `app.py` dashboard contains:

1. **Executive Dashboard** — health score, grade, KPI cards, peer ranking, growth/profitability map and analyst-style takeaway.
2. **Company Deep Dive** — profitability stack, liquidity, leverage, cash generation and health radar.
3. **Peer Benchmark** — compare companies across key financial metrics.
4. **Risk Matrix** — visualize leverage against interest-coverage capacity with configurable screening thresholds.
5. **Scenario Lab** — stress revenue, EBITDA margin and interest expense and compare the resulting health profile with the base case.
6. **Portfolio Screen** — risk-adjusted screening score, FCF yield proxy and capital-intensity view.
7. **Data Explorer** — inspect and export the complete analytical dataset.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Run tests:

```bash
python -m unittest discover -s tests -v
```

Run the CLI:

```bash
python -m src.corporate_finance.cli data/sample_company.json
python -m src.corporate_finance.cli data/sample_company.json --output reports/sample_report.json
```

## Analytical framework

### Profitability
Revenue growth, EBITDA margin, EBIT margin, net margin, ROA and ROE.

### Liquidity
Current ratio, quick ratio and cash ratio.

### Capital structure & debt service
Debt/equity, debt/assets, net debt/EBITDA and interest coverage.

### Cash generation & efficiency
Operating cash-flow margin, free cash flow, FCF margin and asset turnover.

### Risk rules
The engine transparently flags conditions such as weak interest coverage, high net leverage, weak liquidity, negative FCF, negative equity and revenue decline.

### Financial health score
A 0–100 screening score combines profitability, liquidity, debt coverage, leverage, cash flow and growth. Each component is independently visible so the result is explainable rather than a black-box prediction.

### Scenario engine
The scenario model changes revenue, EBITDA margin and interest expense without mutating source data, then reruns the complete analytical engine. This makes the dashboard useful for sensitivity analysis rather than only static ratio reporting.

## Data

`data/top10_companies.json` contains a demonstration universe of 10 large companies. Company selection and headline revenue figures are based on the Fortune 500 2026 ranking. Metrics not directly available from that ranking are explicitly marked as illustrative demo assumptions so the dashboard can demonstrate the analytical workflow. Replace these assumptions with audited annual-report filings before real investment, lending or credit decisions.

## Architecture

```text
JSON / future CSV-XLSX ingestion
        ↓
FinancialSnapshot validation
        ↓
Metric calculation engine
        ↓
Risk rules + health scoring
        ↓
Scenario engine / peer analytics
        ↓
CLI + Streamlit + downloadable outputs
```

## Project layout

```text
blueprint.md
README.md
requirements.txt
pyproject.toml
app.py
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
docs/
  index.html
.github/workflows/
  test.yml
  pages.yml
```

## Engineering principles

- Deterministic and explainable calculations
- Explicit handling of unavailable ratios and zero denominators
- Negative equity handled safely instead of crashing the analytical pipeline
- Presentation logic separated from the calculation engine
- Automated tests for core metrics, risk rules, scenarios and edge cases
- Demo assumptions clearly labeled rather than presented as audited facts
- Designed as analytical screening, not investment advice

## Roadmap

- Import audited 10-K/annual-report data from CSV/XLSX
- Multi-year time-series trend analysis
- DuPont ROE decomposition
- Altman-style distress indicators
- Working-capital and cash-conversion-cycle analysis
- Valuation module (P/E, EV/EBITDA, FCF yield) when market data is supplied
- Automated PDF/Excel report generation
- Production deployment with scheduled data refresh
