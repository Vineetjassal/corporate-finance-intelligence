import json
from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from src.corporate_finance.core import analyze_dict

st.set_page_config(page_title="Corporate Finance Intelligence", page_icon="📈", layout="wide", initial_sidebar_state="expanded")
DATA = Path(__file__).parent / "data" / "top10_companies.json"

@st.cache_data
def load():
    rows = json.loads(DATA.read_text())['companies']
    out=[]
    for r in rows:
        m=analyze_dict(r)['metrics']; out.append({**r, **m, 'risk_count':len(analyze_dict(r)['risk_flags'])})
    return pd.DataFrame(out)

df=load()
for c in ['revenue_growth','ebitda_margin','ebit_margin','net_margin','roa','roe','current_ratio','quick_ratio','cash_ratio','debt_to_equity','debt_to_assets','net_debt_to_ebitda','interest_coverage','asset_turnover','operating_cash_flow_margin','free_cash_flow','fcf_margin','net_debt']:
    df[c]=pd.to_numeric(df[c], errors='coerce')

st.markdown('# 📈 Corporate Finance Intelligence')
st.markdown('### Financial health • peer benchmarking • cash-flow analysis • explainable risk screening')

with st.sidebar:
    st.header('🔎 Controls')
    selected=st.selectbox('Company', df.company.tolist())
    sectors=st.multiselect('Sector filter', sorted(df.sector.unique()), default=sorted(df.sector.unique()))
    view=st.radio('View', ['Company Deep Dive','Peer Benchmark','Risk Matrix','Data Explorer'])
    st.divider(); st.caption('Demo portfolio project — replace illustrative metrics with audited filings for real decisions.')

company=df[df.company==selected].iloc[0]
report=analyze_dict(company.to_dict()); m=report['metrics']

if view=='Company Deep Dive':
    st.subheader(f"{selected}  ·  {company.ticker}")
    k=st.columns(6)
    k[0].metric('Revenue', f"{company.revenue:,.0f}")
    k[1].metric('Growth', f"{m['revenue_growth']*100:.1f}%")
    k[2].metric('EBITDA margin', f"{m['ebitda_margin']*100:.1f}%")
    k[3].metric('ROE', 'N/A' if m['roe'] is None else f"{m['roe']*100:.1f}%")
    k[4].metric('Net debt / EBITDA', 'N/A' if m['net_debt_to_ebitda'] is None else f"{m['net_debt_to_ebitda']:.2f}x")
    k[5].metric('Risk flags', str(report['risk_summary']['count']))

    a,b=st.columns(2)
    with a:
        st.markdown('#### Profitability margins')
        p=pd.DataFrame({'Metric':['EBITDA','EBIT','Net'], 'Margin':[m['ebitda_margin']*100,m['ebit_margin']*100,m['net_margin']*100]})
        st.plotly_chart(px.bar(p,x='Metric',y='Margin',text_auto='.1f',title='Profitability stack'), use_container_width=True)
    with b:
        st.markdown('#### Liquidity')
        p=pd.DataFrame({'Metric':['Current','Quick','Cash'], 'Ratio':[m['current_ratio'],m['quick_ratio'],m['cash_ratio']]})
        st.plotly_chart(px.bar(p,x='Metric',y='Ratio',text_auto='.2f',title='Liquidity ratios'), use_container_width=True)
    a,b=st.columns(2)
    with a:
        p=pd.DataFrame({'Metric':['Debt / Equity','Net Debt / EBITDA','Interest Coverage'], 'Multiple':[m['debt_to_equity'] or 0,m['net_debt_to_ebitda'] or 0,m['interest_coverage'] or 0]})
        st.plotly_chart(px.bar(p,x='Metric',y='Multiple',text_auto='.2f',title='Leverage & coverage'), use_container_width=True)
    with b:
        p=pd.DataFrame({'Cash Flow':['Operating CF','Capex','Free CF'], 'Value':[company.operating_cash_flow,company.capex,m['free_cash_flow']]})
        st.plotly_chart(px.bar(p,x='Cash Flow',y='Value',text_auto=',.0f',title='Cash generation'), use_container_width=True)
    st.markdown('#### Financial health radar')
    radar_metrics=['ebitda_margin','net_margin','current_ratio','interest_coverage','fcf_margin']
    vals=[]
    for x in radar_metrics: vals.append(float(m[x] or 0))
    # normalized to peer max for visual comparability
    maxes=[max(abs(df[x].dropna().max()),1e-9) for x in radar_metrics]
    norm=[min(abs(v)/mx,1) for v,mx in zip(vals,maxes)]
    fig=go.Figure(go.Scatterpolar(r=norm+[norm[0]],theta=radar_metrics+[radar_metrics[0]],fill='toself',name=selected))
    fig.update_layout(polar=dict(radialaxis=dict(range=[0,1])), showlegend=False)
    st.plotly_chart(fig,use_container_width=True)
    st.markdown('#### Explainable risk assessment')
    if report['risk_flags']:
        for f in report['risk_flags']: st.warning(f"**{f['code']}** — {f['message']}")
    else: st.success('🟢 No configured risk flags triggered.')

elif view=='Peer Benchmark':
    peer=df[df.sector.isin(sectors)].copy()
    metric=st.selectbox('Benchmark metric',['ebitda_margin','net_margin','roe','revenue_growth','current_ratio','net_debt_to_ebitda','interest_coverage','fcf_margin'])
    labels={'ebitda_margin':'EBITDA Margin','net_margin':'Net Margin','roe':'ROE','revenue_growth':'Revenue Growth','current_ratio':'Current Ratio','net_debt_to_ebitda':'Net Debt / EBITDA','interest_coverage':'Interest Coverage','fcf_margin':'FCF Margin'}
    peer=peer.sort_values(metric,ascending=metric not in ['net_debt_to_ebitda'])
    st.plotly_chart(px.bar(peer,x='company',y=metric,color='sector',text_auto='.2f',title=f"{labels[metric]} — peer ranking"),use_container_width=True)
    st.plotly_chart(px.scatter(peer,x='revenue_growth',y='ebitda_margin',size='revenue',color='sector',text='ticker',hover_name='company',title='Growth vs profitability — peer map'),use_container_width=True)
    st.dataframe(peer[['company','ticker','sector','revenue','revenue_growth','ebitda_margin','net_margin','roe','current_ratio','net_debt_to_ebitda','interest_coverage','free_cash_flow','risk_count']],use_container_width=True,hide_index=True)

elif view=='Risk Matrix':
    peer=df[df.sector.isin(sectors)].copy()
    st.subheader('Risk matrix')
    fig=px.scatter(peer,x='net_debt_to_ebitda',y='interest_coverage',size='revenue',color='risk_count',text='ticker',hover_name='company',title='Leverage vs debt-service capacity')
    fig.add_vline(x=4,line_dash='dash'); fig.add_hline(y=2,line_dash='dash')
    st.plotly_chart(fig,use_container_width=True)
    st.markdown('**Interpretation:** upper-left is generally stronger (lower leverage, stronger coverage); lower-right deserves closer review.')
    risk=peer[['company','ticker','net_debt_to_ebitda','interest_coverage','current_ratio','free_cash_flow','risk_count']].sort_values('risk_count',ascending=False)
    st.dataframe(risk,use_container_width=True,hide_index=True)

else:
    st.subheader('Data Explorer')
    st.dataframe(df,use_container_width=True,hide_index=True)
    st.download_button('⬇ Download complete analysis CSV',df.to_csv(index=False).encode(), 'corporate_finance_analysis.csv','text/csv')

st.divider(); st.caption('Built with Python • Pandas • Plotly • Streamlit | Analytical screening only — not investment advice.')
