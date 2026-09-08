"""Core financial metrics and transparent risk rules."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Optional


def _ratio(numerator: float, denominator: float) -> Optional[float]:
    if denominator == 0:
        return None
    return numerator / denominator


def _margin(value: float, revenue: float) -> Optional[float]:
    return _ratio(value, revenue)


def _round(value: Optional[float], digits: int = 4) -> Optional[float]:
    return None if value is None else round(value, digits)


@dataclass(frozen=True)
class FinancialSnapshot:
    company: str
    period: str
    revenue: float
    previous_revenue: Optional[float]
    ebitda: float
    ebit: float
    net_income: float
    total_assets: float
    equity: float
    current_assets: float
    current_liabilities: float
    inventory: float
    cash: float
    total_debt: float
    operating_cash_flow: float
    capex: float
    interest_expense: float

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FinancialSnapshot":
        required = [
            "company", "period", "revenue", "ebitda", "ebit", "net_income",
            "total_assets", "equity", "current_assets", "current_liabilities",
            "inventory", "cash", "total_debt", "operating_cash_flow", "capex",
            "interest_expense",
        ]
        missing = [key for key in required if key not in data]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")
        numeric = [key for key in required if key not in {"company", "period"}]
        values = {key: data[key] for key in required}
        values["previous_revenue"] = data.get("previous_revenue")
        for key in numeric:
            try:
                values[key] = float(values[key])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Field '{key}' must be numeric") from exc
        if values["previous_revenue"] is not None:
            try:
                values["previous_revenue"] = float(values["previous_revenue"])
            except (TypeError, ValueError) as exc:
                raise ValueError("Field 'previous_revenue' must be numeric") from exc
        if values["revenue"] < 0 or values["total_assets"] < 0 or values["equity"] < 0:
            raise ValueError("Revenue, total assets, and equity cannot be negative")
        return cls(**values)


def analyze(snapshot: FinancialSnapshot) -> dict[str, Any]:
    s = snapshot
    fcf = s.operating_cash_flow - s.capex
    net_debt = s.total_debt - s.cash
    revenue_growth = _ratio(s.revenue - s.previous_revenue, s.previous_revenue) if s.previous_revenue is not None else None
    ebitda_margin = _margin(s.ebitda, s.revenue)
    ebit_margin = _margin(s.ebit, s.revenue)
    net_margin = _margin(s.net_income, s.revenue)
    current_ratio = _ratio(s.current_assets, s.current_liabilities)
    quick_ratio = _ratio(s.current_assets - s.inventory, s.current_liabilities)
    cash_ratio = _ratio(s.cash, s.current_liabilities)
    debt_to_equity = _ratio(s.total_debt, s.equity)
    debt_to_assets = _ratio(s.total_debt, s.total_assets)
    net_debt_to_ebitda = _ratio(net_debt, s.ebitda)
    interest_coverage = _ratio(s.ebit, s.interest_expense)
    asset_turnover = _ratio(s.revenue, s.total_assets)
    ocf_margin = _margin(s.operating_cash_flow, s.revenue)
    fcf_margin = _margin(fcf, s.revenue)
    roa = _ratio(s.net_income, s.total_assets)
    roe = _ratio(s.net_income, s.equity)

    risks: list[dict[str, Any]] = []
    if interest_coverage is not None and interest_coverage < 2.0:
        risks.append({"code": "INTEREST_BURDEN", "severity": "elevated", "message": "Interest coverage is below 2.0x."})
    if net_debt_to_ebitda is not None and net_debt_to_ebitda > 4.0:
        risks.append({"code": "LEVERAGE", "severity": "elevated", "message": "Net debt / EBITDA is above 4.0x."})
    if current_ratio is not None and current_ratio < 1.0:
        risks.append({"code": "LIQUIDITY", "severity": "elevated", "message": "Current ratio is below 1.0x."})
    if fcf < 0:
        risks.append({"code": "CASH_GENERATION", "severity": "warning", "message": "Free cash flow is negative."})
    if revenue_growth is not None and revenue_growth < 0 and ebitda_margin is not None and ebitda_margin < 0:
        risks.append({"code": "OPERATING_DETERIORATION", "severity": "warning", "message": "Revenue and EBITDA margin are both deteriorating."})

    metrics = {
        "revenue_growth": revenue_growth,
        "ebitda_margin": ebitda_margin,
        "ebit_margin": ebit_margin,
        "net_margin": net_margin,
        "roa": roa,
        "roe": roe,
        "current_ratio": current_ratio,
        "quick_ratio": quick_ratio,
        "cash_ratio": cash_ratio,
        "debt_to_equity": debt_to_equity,
        "debt_to_assets": debt_to_assets,
        "net_debt_to_ebitda": net_debt_to_ebitda,
        "interest_coverage": interest_coverage,
        "asset_turnover": asset_turnover,
        "operating_cash_flow_margin": ocf_margin,
        "free_cash_flow": fcf,
        "fcf_margin": fcf_margin,
        "net_debt": net_debt,
    }
    metrics = {key: _round(value) for key, value in metrics.items()}
    return {
        "company": s.company,
        "period": s.period,
        "metrics": metrics,
        "risk_flags": risks,
        "risk_summary": {"count": len(risks), "status": "elevated" if risks else "normal"},
    }


def analyze_dict(data: dict[str, Any]) -> dict[str, Any]:
    return analyze(FinancialSnapshot.from_dict(data))


def snapshot_dict(snapshot: FinancialSnapshot) -> dict[str, Any]:
    return asdict(snapshot)
