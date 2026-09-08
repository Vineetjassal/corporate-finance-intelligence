# Corporate Finance Intelligence — Project Blueprint

## Objective
Build a practical, auditable corporate-finance intelligence toolkit that converts company financial statements and operating metrics into decision-ready analysis.

## Core capabilities
- Financial statement normalization
- Ratio and trend analysis
- Profitability, liquidity, leverage, efficiency, and cash-conversion metrics
- Debt-service and capital-structure assessment
- Explainable rule-based risk flags
- Reproducible CLI workflow with JSON output

## Architecture
`data/input` → `src` calculations → `reports` outputs

The first version is dependency-light and uses Python's standard library only.

## Metrics
**Profitability:** revenue growth, EBITDA margin, EBIT margin, net margin, ROA, ROE.

**Liquidity:** current ratio, quick ratio, cash ratio.

**Leverage / coverage:** debt-to-equity, debt-to-assets, net debt / EBITDA, interest coverage.

**Efficiency / cash flow:** asset turnover, operating cash-flow margin, free cash flow, FCF margin, cash conversion.

## Risk framework
Transparent deterministic rules:
- Interest coverage < 2.0x → elevated interest burden
- Net debt / EBITDA > 4.0x → elevated leverage
- Current ratio < 1.0x → liquidity pressure
- Negative free cash flow → cash-generation warning
- Falling revenue + falling margin → operating deterioration

This is an analytical toolkit, not investment advice or a credit decision engine.

## Validation
`python -m unittest discover -s tests -v`

`python -m src.corporate_finance.cli data/sample_company.json`

## Future extensions
CSV/Excel ingestion, peer benchmarking, historical time-series storage, PDF extraction, scenario analysis, dashboards, and an API layer.
