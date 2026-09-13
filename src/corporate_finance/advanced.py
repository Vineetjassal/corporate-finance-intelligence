"""Advanced corporate-finance analytics for portfolio screening and scenario analysis."""
from __future__ import annotations
from typing import Any


def _pct(x: float | None) -> float | None:
    return None if x is None else round(x * 100, 2)


def dupont_analysis(net_margin: float | None, asset_turnover: float | None, equity_multiplier: float | None) -> dict[str, Any]:
    """Three-step DuPont decomposition: ROE = margin × turnover × leverage."""
    roe = None if None in (net_margin, asset_turnover, equity_multiplier) else net_margin * asset_turnover * equity_multiplier
    return {"net_margin": _pct(net_margin), "asset_turnover": asset_turnover, "equity_multiplier": equity_multiplier, "roe": _pct(roe)}


def capital_intensity(revenue: float, total_assets: float, capex: float) -> dict[str, float | None]:
    return {
        "asset_intensity": round(total_assets / revenue, 4) if revenue else None,
        "capex_to_revenue": round(capex / revenue, 4) if revenue else None,
        "capex_to_assets": round(capex / total_assets, 4) if total_assets else None,
    }


def working_capital_metrics(current_assets: float, current_liabilities: float, inventory: float, cash: float, revenue: float) -> dict[str, float | None]:
    nwc = current_assets - current_liabilities
    return {
        "net_working_capital": round(nwc, 2),
        "nwc_to_revenue": round(nwc / revenue, 4) if revenue else None,
        "working_capital_ratio": round(current_assets / current_liabilities, 4) if current_liabilities else None,
        "cash_conversion_proxy": round((nwc / revenue) * 365, 1) if revenue else None,
        "inventory_intensity": round(inventory / revenue, 4) if revenue else None,
        "cash_intensity": round(cash / revenue, 4) if revenue else None,
    }


def stress_test(snapshot: dict[str, Any], revenue_shocks: list[float] | None = None, margin_shocks: list[float] | None = None) -> list[dict[str, float]]:
    """Generate a grid of revenue/margin stress cases using the source snapshot."""
    revenue_shocks = revenue_shocks or [-0.20, -0.10, 0.0, 0.10, 0.20]
    margin_shocks = margin_shocks or [-0.05, -0.02, 0.0, 0.02, 0.05]
    base_revenue = float(snapshot["revenue"])
    base_margin = float(snapshot["ebitda"]) / base_revenue if base_revenue else 0.0
    out = []
    for rs in revenue_shocks:
        for ms in margin_shocks:
            revenue = base_revenue * (1 + rs)
            ebitda = revenue * max(0, base_margin + ms)
            out.append({"revenue_shock": rs, "margin_shock": ms, "revenue": round(revenue, 2), "ebitda": round(ebitda, 2), "ebitda_margin": round(ebitda / revenue, 4) if revenue else 0})
    return out


def peer_percentile(values: list[float], value: float) -> float:
    if not values:
        return 50.0
    below = sum(v <= value for v in values)
    return round(100 * below / len(values), 1)


def investment_screen(metrics: dict[str, Any]) -> dict[str, Any]:
    """Non-advisory screening label based on transparent fundamental signals."""
    positives, negatives = [], []
    if (metrics.get("revenue_growth") or 0) > 0.10: positives.append("strong growth")
    if (metrics.get("ebitda_margin") or 0) > 0.20: positives.append("strong operating margin")
    if (metrics.get("fcf_margin") or 0) > 0.10: positives.append("healthy free-cash-flow margin")
    if metrics.get("net_debt_to_ebitda") is not None and metrics["net_debt_to_ebitda"] < 2: positives.append("moderate leverage")
    if (metrics.get("current_ratio") or 0) < 1: negatives.append("tight liquidity")
    if metrics.get("net_debt_to_ebitda") is not None and metrics["net_debt_to_ebitda"] > 4: negatives.append("high leverage")
    if (metrics.get("interest_coverage") or 99) < 2: negatives.append("weak interest coverage")
    if (metrics.get("free_cash_flow") or 0) < 0: negatives.append("negative free cash flow")
    score = max(0, min(100, 50 + 10 * len(positives) - 12 * len(negatives)))
    label = "Strong fundamentals" if score >= 75 else "Watchlist" if score >= 50 else "High risk"
    return {"screen_score": score, "label": label, "positive_signals": positives, "negative_signals": negatives}
