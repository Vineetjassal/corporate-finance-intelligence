import json
from pathlib import Path

import pandas as pd
import streamlit as st

from src.corporate_finance.core import analyze_dict

DATA_PATH = Path(__file__).parent / "data" / "top10_companies.json"

st.set_page_config(page_title="Corporate Finance Intelligence", page_icon="📊", layout="wide")

@st.cache_data
def load_rows():
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))["companies"]

rows = load_rows()
analyses = {r["company"]: analyze_dict(r) for r in rows}
records = []
for r in rows:
    m = analyses[r["company"]]["metrics"]
    records.append({"Company": r["company"], "Ticker": r["ticker"], "Sector": r["sector"], "Revenue": r["revenue"], "Revenue Growth": m["revenue_growth"], "EBITDA Margin": m["ebitda_margin"], "EBIT Margin": m["ebit_margin"], "Net Margin": m["net_margin"], "ROA": m["roa"], "ROE": m["roe"], "Current Ratio": m["current_ratio"], "Quick Ratio": m["quick_ratio"], "Debt / Equity": m["debt_to_equity"], "Net Debt / EBITDA": m["net_debt_to_ebitda"], "Interest Coverage": m["interest_coverage"], "FCF": m["free_cash_flow"], "FCF Margin": m["fcf_margin"], "Risk Flags": len(analyses[r["company"]]["risk_flags"])})
df = pd.DataFrame(records)

st.title("Corporate Finance Intelligence")
st.caption("Executive financial analysis • peer benchmarking • leverage & liquidity screening • explainable risk flags")

with st.sidebar:
    st.header("Analysis Controls")
    selected = st.selectbox("Company", [r["company"] for r in rows])
    sector_filter = st.multiselect("Sectors", sorted(df["Sector"].unique()), default=sorted(df["Sector"].unique()))
    metric = st.selectbox("Peer ranking metric", ["EBITDA Margin", "Net Margin", "ROE", "Revenue Growth", "Interest Coverage", "FCF Margin"])

company = df[df["Company"] == selected].iloc[0]
report = analyses[selected]
m = report["metrics"]

st.subheader(f"Executive view — {selected}")
cards = st.columns(5)
cards[0].metric("Revenue", f"{company['Revenue']:,.0f}")
cards[1].metric("Growth", f"{m['revenue_growth']*100:.1f}%" if m['revenue_growth'] is not None else "N/A")
cards[2].metric("EBITDA margin", f"{m['ebitda_margin']*100:.1f}%")
cards[3].metric("ROE", f"{m['roe']*100:.1f}%" if m['roe'] is not None else "N/A")
cards[4].metric("Risk flags", str(len(report["risk_flags"])), delta=report["risk_summary"]["status"], delta_color="inverse")

left, right = st.columns(2)
with left:
    st.subheader("Profitability profile")
    profitability = pd.DataFrame({"Margin": [m["ebitda_margin"]*100, m["ebit_margin"]*100, m["net_margin"]*100]}, index=["EBITDA", "EBIT", "Net"])
    st.bar_chart(profitability)
with right:
    st.subheader("Liquidity profile")
    liquidity = pd.DataFrame({"Ratio": [m["current_ratio"], m["quick_ratio"], m["cash_ratio"]]}, index=["Current", "Quick", "Cash"])
    st.bar_chart(liquidity)

left, right = st.columns(2)
with left:
    st.subheader("Leverage & debt service")
    leverage = pd.DataFrame({"Multiple": [m["debt_to_equity"] or 0, m["net_debt_to_ebitda"] or 0, m["interest_coverage"] or 0]}, index=["Debt / Equity", "Net Debt / EBITDA", "Interest Coverage"])
    st.bar_chart(leverage)
with right:
    st.subheader("Cash generation")
    cash = pd.DataFrame({"Value": [row["operating_cash_flow"], row["capex"], m["free_cash_flow"]]}, index=["Operating CF", "Capex", "Free CF"])
    st.bar_chart(cash)

st.divider()
st.header("Peer Benchmarking")
peer_df = df[df["Sector"].isin(sector_filter)].copy()
peer_df[metric] = peer_df[metric].fillna(0)
peer_df = peer_df.sort_values(metric, ascending=False)
st.bar_chart(peer_df.set_index("Company")[[metric]])

st.subheader("Peer scorecard")
display = peer_df[["Company", "Sector", "Revenue", "Revenue Growth", "EBITDA Margin", "Net Margin", "ROE", "Current Ratio", "Net Debt / EBITDA", "Interest Coverage", "FCF Margin", "Risk Flags"]].copy()
for col in ["Revenue Growth", "EBITDA Margin", "Net Margin", "ROE", "FCF Margin"]:
    display[col] = display[col].map(lambda x: None if pd.isna(x) else f"{x*100:.1f}%")
for col in ["Current Ratio", "Net Debt / EBITDA", "Interest Coverage"]:
    display[col] = display[col].map(lambda x: None if pd.isna(x) else f"{x:.2f}x")
st.dataframe(display, use_container_width=True, hide_index=True)

st.header("Risk & Credit-style Screening")
if report["risk_flags"]:
    for flag in report["risk_flags"]:
        icon = "🔴" if flag["severity"] == "elevated" else "🟠"
        st.warning(f"{icon} **{flag['code']}** — {flag['message']}")
else:
    st.success("🟢 No configured risk flags triggered.")

st.subheader("How to explain this project")
st.markdown("**1. Data → 2. Validation → 3. Financial ratios → 4. Peer benchmarking → 5. Risk rules → 6. Interactive decision dashboard.**")
st.markdown("The calculation engine is deterministic and explainable; the dashboard is a visualization layer. Demo operating metrics are illustrative assumptions and should be replaced with audited filings for real decisions.")

st.download_button("Download peer analysis CSV", peer_df.to_csv(index=False).encode("utf-8"), "peer_analysis.csv", "text/csv")
