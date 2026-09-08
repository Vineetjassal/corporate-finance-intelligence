import json
from pathlib import Path

import streamlit as st

from src.corporate_finance.core import analyze_dict

DATA_PATH = Path(__file__).parent / "data" / "top10_companies.json"

st.set_page_config(page_title="Corporate Finance Intelligence", page_icon="📊", layout="wide")

@st.cache_data
def load_data():
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))["companies"]

companies = load_data()
analyses = {row["company"]: analyze_dict(row) for row in companies}

st.title("Corporate Finance Intelligence")
st.caption("Interactive multi-company financial analysis and transparent risk screening")

selected = st.selectbox("Select company", [x["company"] for x in companies])
row = next(x for x in companies if x["company"] == selected)
report = analyses[selected]
m = report["metrics"]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Revenue", f"{row['revenue']:,.0f}")
c2.metric("EBITDA margin", f"{m['ebitda_margin']*100:.1f}%")
c3.metric("ROE", "N/A" if m["roe"] is None else f"{m['roe']*100:.1f}%")
c4.metric("Net debt / EBITDA", "N/A" if m["net_debt_to_ebitda"] is None else f"{m['net_debt_to_ebitda']:.2f}x")

st.subheader("Profitability")
st.bar_chart({"EBITDA margin": m["ebitda_margin"] * 100, "EBIT margin": m["ebit_margin"] * 100, "Net margin": m["net_margin"] * 100})

st.subheader("Liquidity and leverage")
col1, col2 = st.columns(2)
with col1:
    st.bar_chart({"Current ratio": m["current_ratio"], "Quick ratio": m["quick_ratio"], "Cash ratio": m["cash_ratio"]})
with col2:
    st.bar_chart({"Debt / equity": m["debt_to_equity"], "Debt / assets": m["debt_to_assets"], "Interest coverage": m["interest_coverage"]})

st.subheader("Peer comparison")
peer_rows = []
for name, analysis in analyses.items():
    pm = analysis["metrics"]
    peer_rows.append({"Company": name, "EBITDA margin (%)": round(pm["ebitda_margin"] * 100, 2), "ROE (%)": None if pm["roe"] is None else round(pm["roe"] * 100, 2), "Net debt / EBITDA": pm["net_debt_to_ebitda"], "Interest coverage": pm["interest_coverage"]})
peer_rows.sort(key=lambda x: x["EBITDA margin (%)"], reverse=True)
st.dataframe(peer_rows, use_container_width=True, hide_index=True)

st.subheader("EBITDA margin — top 10")
st.bar_chart({x["Company"]: x["EBITDA margin (%)"] for x in peer_rows})

st.subheader("Risk flags")
flags = report["risk_flags"]
if flags:
    for flag in flags:
        st.warning(f"**{flag['code']}** — {flag['message']}")
else:
    st.success("No configured risk flags triggered.")

st.info("Demo dataset: company selection is based on Fortune 500 2026 ranking; operating metrics not directly sourced from that ranking are illustrative assumptions for dashboard demonstration. Replace with audited filings before decision use.")
