"""Core financial metrics, transparent risk rules, and scenario analytics."""

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
        if values["revenue"] < 0 or values["total_assets"] < 0:
            raise ValueError("Revenue and total assets cannot be negative")
        return cls(**values)


def _score_component(value: Optional[float], good: float, bad: float, higher_is_better: bool = True) -> Optional[float]:
    """Map a metric to a 0-100 score using transparent linear interpolation."""
    if value is None:
        return None
    if higher_is_better:
        if value >= good:
            return 100.0
        if value <= bad:
            return 0.0
        return 100.0 * (value - bad) / (good - bad)
    if value <= good:
        return 100.0
    if value >= bad:
        return 0.0
    return 100.0 * (bad - value) / (bad - good)


def _health_score(metrics: dict[str, Optional[float]], risk_flags: list[dict[str, Any]]) -> tuple[int, str, dict[str, float]]:
    """Weighted screening score; thresholds are deliberately explainable, not a credit rating."""
    components = {
        "profitability": _score_component(metrics["ebitda_margin"], 0.25, 0.05),
        "liquidity": _score_component(metrics["current_ratio"], 2.0, 0.75),
        "coverage": _score_component(metrics["interest_coverage"], 8.0, 1.0),
        "leverage": _score_component(metrics["net_debt_to_ebitda"], 0.0, 6.0, False),
        "cash_flow": _score_component(metrics["fcf_margin"], 0.15, -0.05),
        "growth": _score_component(metrics["revenue_growth"], 0.15, -0.10),
    }
    available = {k: v for k, v in components.items() if v is not None}
    weights = {"profitability": .20, "liquidity": .15, "coverage": .20, "leverage": .20, "cash_flow": .15, "growth": .10}
    total_weight = sum(weights[k] for k in available)
    raw = sum(available[k] * weights[k] for k in available) / total_weight if total_weight else 0.0
    penalty = min(25, len(risk_flags) * 5)
    score = max(0, min(100, round(raw - penalty)))
    grade = "A" if score >= 80 else "B" if score >= 65 else "C" if score >= 50 else "D" if score >= 35 else "E"
    return score, grade, {k: round(v, 1) for k, v in available.items()}


def analyze(snapshot: FinancialSnapshot) -> dict[str, Any]:
    s = snapshot
    fcf = s.operating_cash_flow - s.capex
    net_debt = s.total_debt - s.cash
    revenue_growth = _ratio(s.revenue - s.previous_revenue, s.previous_revenue) if s.previous_revenue not in (None, 0) else None
    ebitda_margin = _margin(s.ebitda, s.revenue)
    ebit_margin = _margin(s.ebit, s.revenue)
    net_margin = _margin(s.net_income, s.revenue)
    current_ratio = _ratio(s.current_assets, s.current_liabilities)
    quick_ratio = _ratio(s.current_assets - s.inventory, s.current_liabilities)
    cash_ratio = _ratio(s.cash, s.current_liabilities)
    debt_to_equity = _ratio(s.total_debt, s.equity) if s.equity > 0 else None
    debt_to_assets = _ratio(s.total_debt, s.total_assets)
    net_debt_to_ebitda = _ratio(net_debt, s.ebitda) if s.ebitda > 0 else None
    interest_coverage = _ratio(s.ebit, s.interest_expense) if s.interest_expense > 0 else None
    asset_turnover = _ratio(s.revenue, s.total_assets)
    ocf_margin = _margin(s.operating_cash_flow, s.revenue)
    fcf_margin = _margin(fcf, s.revenue)
    roa = _ratio(s.net_income, s.total_assets)
    roe = _ratio(s.net_income, s.equity) if s.equity > 0 else None

    risks: list[dict[str, Any]] = []
    if interest_coverage is not None and interest_coverage < 2.0:
        risks.append({"code": "INTEREST_BURDEN", "severity": "high", "message": "Interest coverage is below 2.0x."})
    if net_debt_to_ebitda is not None and net_debt_to_ebitda > 4.0:
        risks.append({"code": "LEVERAGE", "severity": "high", "message": "Net debt / EBITDA is above 4.0x."})
    if current_ratio is not None and current_ratio < 1.0:
        risks.append({"code": "LIQUIDITY", "severity": "high", "message": "Current ratio is below 1.0x."})
    if fcf < 0:
        risks.append({"code": "CASH_GENERATION", "severity": "medium", "message": "Free cash flow is negative."})
    if s.equity < 0:
        risks.append({"code": "NEGATIVE_EQUITY", "severity": "high", "message": "Book equity is negative; debt/equity and ROE are not meaningful."})
    if revenue_growth is not None and revenue_growth < 0:
        risks.append({"code": "REVENUE_DECLINE", "severity": "medium", "message": "Revenue declined versus the prior period."})

    metrics = {
        "revenue_growth": revenue_growth, "ebitda_margin": ebitda_margin, "ebit_margin": ebit_margin,
        "net_margin": net_margin, "roa": roa, "roe": roe, "current_ratio": current_ratio,
        "quick_ratio": quick_ratio, "cash_ratio": cash_ratio, "debt_to_equity": debt_to_equity,
        "debt_to_assets": debt_to_assets, "net_debt_to_ebitda": net_debt_to_ebitda,
        "interest_coverage": interest_coverage, "asset_turnover": asset_turnover,
        "operating_cash_flow_margin": ocf_margin, "free_cash_flow": fcf,
        "fcf_margin": fcf_margin, "net_debt": net_debt,
    }
    metrics = {key: _round(value) for key, value in metrics.items()}
    score, grade, score_components = _health_score(metrics, risks)
    return {
        "company": s.company, "period": s.period, "metrics": metrics, "risk_flags": risks,
        "risk_summary": {"count": len(risks), "status": "elevated" if risks else "normal"},
        "health_score": score, "health_grade": grade, "score_components": score_components,
    }


def scenario_analysis(data: dict[str, Any], revenue_change: float = 0.0, margin_change: float = 0.0, interest_change: float = 0.0) -> dict[str, Any]:
    """Run a simple sensitivity case without mutating the source snapshot.

    revenue_change and margin_change are decimal changes (0.10 = +10%, 0.02 = +2 percentage points).
    """
    s = FinancialSnapshot.from_dict(data)
    new_revenue = s.revenue * (1 + revenue_change)
    new_ebitda_margin = (s.ebitda / s.revenue if s.revenue else 0) + margin_change
    new_ebitda = new_revenue * new_ebitda_margin
    new_interest = s.interest_expense * (1 + interest_change)
    new_ebit = new_ebitda * (s.ebit / s.ebitda) if s.ebitda else new_ebitda
    case = asdict(s)
    case.update({"revenue": new_revenue, "ebitda": new_ebitda, "ebit": new_ebit, "interest_expense": new_interest})
    result = analyze_dict(case)
    result["scenario"] = {"revenue_change": revenue_change, "margin_change": margin_change, "interest_change": interest_change}
    return result


def analyze_dict(data: dict[str, Any]) -> dict[str, Any]:
    return analyze(FinancialSnapshot.from_dict(data))


def snapshot_dict(snapshot: FinancialSnapshot) -> dict[str, Any]:
    return asdict(snapshot)
