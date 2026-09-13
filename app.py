import json
from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from src.corporate_finance.core import analyze_dict, scenario_analysis
from src.corporate_finance.advanced import dupont_analysis, capital_intensity, working_capital_metrics, stress_test, peer_percentile, investment_screen

st.set_page_config(page_title="Corporate Finance Intelligence", page_icon="📈", layout="wide", initial_sidebar_state="expanded")
DATA = Path(__file__).parent / "data" / "top10_companies.json"

@st.cache_data
def load():
    rows = json.loads(DATA.read_text())['companies']
    out=[]
    for r in rows:
        a=analyze_dict(r)
        out.append({**r, **a['metrics'], 'risk_count':len(a['risk_flags']), 'health_score':a['health_score'], 'health_grade':a['health_grade']})
    return pd.DataFrame(out)

df=load()
metric_cols=['revenue_growth','ebitda_margin','ebit_margin','net_margin','roa','roe','current_ratio','quick_ratio','cash_ratio','debt_to_equity','debt_to_assets','net_debt_to_ebitda','interest_coverage','asset_turnover','operating_cash_flow_margin','free_cash_flow','fcf_margin','net_debt','health_score']
for c in metric_cols: df[c]=pd.to_numeric(df[c], errors='coerce')

st.markdown('# 📈 Corporate Finance Intelligence')
st.markdown('### Executive financial diagnostics • peer benchmarking • risk scoring • scenario analysis • capital efficiency')

with st.sidebar:
    st.header('🔎 Controls')
    selected=st.selectbox('Company', df.company.tolist())
    sectors=st.multiselect('Sector filter', sorted(df.sector.unique()), default=sorted(df.sector.unique()))
    view=st.radio('Analysis module', ['Executive Dashboard','Company Deep Dive','Peer Benchmark','Risk Matrix','Scenario Lab','Stress Testing','Capital & Working Capital','DuPont Analysis','Portfolio Screen','Data Explorer'])
    st.divider()
    st.caption('Demo portfolio project. Replace illustrative operating assumptions with audited filings before real-world use.')

company=df[df.company==selected].iloc[0]
raw=json.loads(DATA.read_text())['companies']
source=next(r for r in raw if r['company']==selected)
report=analyze_dict(source); m=report['metrics']

def pct(x): return 'N/A' if x is None else f'{x*100:.1f}%'
def mult(x): return 'N/A' if x is None else f'{x:.2f}x'

if view=='Executive Dashboard':
    st.subheader('Executive dashboard')
    k=st.columns(6)
    k[0].metric('Financial Health', f"{report['health_score']}/100", report['health_grade'])
    k[1].metric('Revenue', f"${company.revenue:,.0f}M", pct(m['revenue_growth']))
    k[2].metric('EBITDA Margin', pct(m['ebitda_margin']))
    k[3].metric('ROE', pct(m['roe']))
    k[4].metric('Net Debt / EBITDA', mult(m['net_debt_to_ebitda']))
    k[5].metric('Risk Flags', str(report['risk_summary']['count']))
    a,b=st.columns(2)
    with a:
        comp=pd.DataFrame({'Dimension':list(report['score_components'].keys()),'Score':list(report['score_components'].values())})
        st.plotly_chart(px.bar(comp,x='Score',y='Dimension',orientation='h',range_x=[0,100],text_auto='.0f',title='Health score composition'),use_container_width=True)
    with b:
        cf=pd.DataFrame({'Metric':['Debt','Cash','Net Debt','Operating CF','Capex','FCF'],'Value':[company.total_debt,company.cash,m['net_debt'],company.operating_cash_flow,company.capex,m['free_cash_flow']]})
        st.plotly_chart(px.bar(cf,x='Metric',y='Value',text_auto=',.0f',title='Capital & cash profile'),use_container_width=True)
    bench=df[df.sector.isin(sectors)].copy()
    a,b=st.columns(2)
    with a: st.plotly_chart(px.bar(bench.sort_values('health_score',ascending=False),x='company',y='health_score',color='sector',text='health_score',title='Peer financial health score',range_y=[0,100]),use_container_width=True)
    with b: st.plotly_chart(px.scatter(bench,x='revenue_growth',y='ebitda_margin',size='revenue',color='health_score',text='ticker',hover_name='company',title='Growth vs profitability'),use_container_width=True)
    screen=investment_screen(m)
    st.markdown('#### Automated fundamental screen')
    st.metric('Screen score', f"{screen['screen_score']}/100", screen['label'])
    if screen['positive_signals']: st.success('Positive signals: ' + ', '.join(screen['positive_signals']))
    if screen['negative_signals']: st.warning('Watch signals: ' + ', '.join(screen['negative_signals']))
    positives=[]
    if m['revenue_growth'] is not None and m['revenue_growth']>0: positives.append(f"revenue growth of {pct(m['revenue_growth'])}")
    if m['ebitda_margin'] is not None and m['ebitda_margin']>.20: positives.append(f"strong EBITDA margin of {pct(m['ebitda_margin'])}")
    if m['interest_coverage'] is not None and m['interest_coverage']>=5: positives.append(f"comfortable interest coverage of {mult(m['interest_coverage'])}")
    concerns=[f['message'] for f in report['risk_flags']]
    st.info(('Strengths: '+', '.join(positives)+'. ') if positives else 'Strengths: no standout positive signal under the configured rules. ' + ('Watch items: '+ ' '.join(concerns) if concerns else 'Watch items: none.'))

elif view=='Company Deep Dive':
    st.subheader(f"{selected} · {company.ticker}")
    k=st.columns(6)
    k[0].metric('Health',f"{report['health_score']}/100"); k[1].metric('Grade',report['health_grade']); k[2].metric('Growth',pct(m['revenue_growth'])); k[3].metric('EBITDA Margin',pct(m['ebitda_margin'])); k[4].metric('FCF',f"${m['free_cash_flow']:,.0f}M"); k[5].metric('ROA',pct(m['roa']))
    a,b=st.columns(2)
    with a:
        p=pd.DataFrame({'Metric':['EBITDA','EBIT','Net'],'Margin':[m['ebitda_margin']*100,m['ebit_margin']*100,m['net_margin']*100]}); st.plotly_chart(px.bar(p,x='Metric',y='Margin',text_auto='.1f',title='Profitability stack'),use_container_width=True)
    with b:
        p=pd.DataFrame({'Metric':['Current','Quick','Cash'],'Ratio':[m['current_ratio'],m['quick_ratio'],m['cash_ratio']]}); st.plotly_chart(px.bar(p,x='Metric',y='Ratio',text_auto='.2f',title='Liquidity profile'),use_container_width=True)
    a,b=st.columns(2)
    with a:
        p=pd.DataFrame({'Metric':['Debt / Equity','Net Debt / EBITDA','Interest Coverage'],'Multiple':[m['debt_to_equity'] or 0,m['net_debt_to_ebitda'] or 0,m['interest_coverage'] or 0]}); st.plotly_chart(px.bar(p,x='Metric',y='Multiple',text_auto='.2f',title='Leverage & coverage'),use_container_width=True)
    with b:
        p=pd.DataFrame({'Cash Flow':['Operating CF','Capex','Free CF'],'Value':[company.operating_cash_flow,company.capex,m['free_cash_flow']]}); st.plotly_chart(px.bar(p,x='Cash Flow',y='Value',text_auto=',.0f',title='Cash generation'),use_container_width=True)
    vals=[report['score_components'].get(k,0) for k in ['profitability','liquidity','coverage','leverage','cash_flow','growth']]; radar=['Profitability','Liquidity','Coverage','Leverage','Cash Flow','Growth']
    fig=go.Figure(go.Scatterpolar(r=vals+[vals[0]],theta=radar+[radar[0]],fill='toself',name=selected)); fig.update_layout(polar=dict(radialaxis=dict(range=[0,100])),showlegend=False,title='Financial health radar'); st.plotly_chart(fig,use_container_width=True)
    if report['risk_flags']:
        for f in report['risk_flags']: st.warning(f"**{f['code']}** — {f['message']}")
    else: st.success('🟢 No configured risk flags triggered.')

elif view=='Peer Benchmark':
    peer=df[df.sector.isin(sectors)].copy()
    metric=st.selectbox('Benchmark metric',['health_score','ebitda_margin','net_margin','roe','revenue_growth','current_ratio','net_debt_to_ebitda','interest_coverage','fcf_margin'])
    labels={'health_score':'Health Score','ebitda_margin':'EBITDA Margin','net_margin':'Net Margin','roe':'ROE','revenue_growth':'Revenue Growth','current_ratio':'Current Ratio','net_debt_to_ebitda':'Net Debt / EBITDA','interest_coverage':'Interest Coverage','fcf_margin':'FCF Margin'}
    peer=peer.sort_values(metric,ascending=metric=='net_debt_to_ebitda')
    peer['percentile']=peer[metric].apply(lambda x: peer_percentile(peer[metric].dropna().tolist(),x) if pd.notna(x) else None)
    st.plotly_chart(px.bar(peer,x='company',y=metric,color='sector',text_auto='.2f',title=f"{labels[metric]} — peer ranking"),use_container_width=True)
    st.plotly_chart(px.scatter(peer,x='revenue_growth',y='ebitda_margin',size='revenue',color='sector',text='ticker',hover_name='company',title='Growth vs profitability — peer map'),use_container_width=True)
    st.dataframe(peer[['company','ticker','sector','revenue','health_score','health_grade','percentile','revenue_growth','ebitda_margin','net_margin','roe','current_ratio','net_debt_to_ebitda','interest_coverage','free_cash_flow','risk_count']],use_container_width=True,hide_index=True)

elif view=='Risk Matrix':
    peer=df[df.sector.isin(sectors)].copy()
    fig=px.scatter(peer,x='net_debt_to_ebitda',y='interest_coverage',size='revenue',color='risk_count',text='ticker',hover_name='company',title='Leverage vs debt-service capacity'); fig.add_vline(x=4,line_dash='dash'); fig.add_hline(y=2,line_dash='dash'); st.plotly_chart(fig,use_container_width=True)
    st.caption('Lower leverage and stronger coverage generally indicate greater debt resilience. Thresholds are screening rules, not ratings.')
    risk=peer[['company','ticker','health_score','health_grade','net_debt_to_ebitda','interest_coverage','current_ratio','free_cash_flow','risk_count']].sort_values(['risk_count','health_score'],ascending=[False,True]); st.dataframe(risk,use_container_width=True,hide_index=True)

elif view=='Scenario Lab':
    st.subheader('Scenario & sensitivity laboratory')
    a,b,c=st.columns(3); rev=a.slider('Revenue change',-30,30,0,1)/100; mar=b.slider('EBITDA margin change (pp)',-10,10,0,0.5)/100; intr=c.slider('Interest expense change',-30,100,0,1)/100
    sc=scenario_analysis(source,rev,mar,intr); sm=sc['metrics']
    k=st.columns(5); k[0].metric('Scenario Health',f"{sc['health_score']}/100",f"{sc['health_score']-report['health_score']:+d}"); k[1].metric('EBITDA Margin',pct(sm['ebitda_margin'])); k[2].metric('Interest Coverage',mult(sm['interest_coverage'])); k[3].metric('FCF Margin',pct(sm['fcf_margin'])); k[4].metric('Risk Flags',str(len(sc['risk_flags'])))
    comp=pd.DataFrame({'Metric':['Health Score','EBITDA Margin','Interest Coverage','FCF Margin'],'Base':[report['health_score'],m['ebitda_margin']*100,m['interest_coverage'] or 0,m['fcf_margin']*100],'Scenario':[sc['health_score'],sm['ebitda_margin']*100,sm['interest_coverage'] or 0,sm['fcf_margin']*100]}); st.plotly_chart(px.bar(comp,x='Metric',y=['Base','Scenario'],barmode='group',title='Base vs scenario'),use_container_width=True)
    if sc['risk_flags']:
        for f in sc['risk_flags']: st.warning(f"**{f['code']}** — {f['message']}")
    else: st.success('Scenario produces no configured risk flags.')

elif view=='Stress Testing':
    st.subheader('📉 Multi-dimensional stress testing')
    st.caption('Grid-based sensitivity across revenue and EBITDA margin shocks. This is a transparent analytical stress test, not a forecast.')
    rev_shocks=st.multiselect('Revenue shocks',[-0.30,-0.20,-0.10,0.0,0.10,0.20],default=[-0.20,-0.10,0.0,0.10,0.20],format_func=lambda x:f'{x:+.0%}')
    mar_shocks=st.multiselect('Margin shocks',[-0.05,-0.02,0.0,0.02,0.05],default=[-0.05,-0.02,0.0,0.02,0.05],format_func=lambda x:f'{x:+.1%}')
    grid=stress_test(source,rev_shocks,mar_shocks)
    heat=pd.DataFrame(grid).pivot(index='margin_shock',columns='revenue_shock',values='ebitda_margin')*100
    heat.index=[f'{x:+.1%}' for x in heat.index]; heat.columns=[f'{x:+.0%}' for x in heat.columns]
    st.plotly_chart(px.imshow(heat,text_auto='.1f',aspect='auto',labels={'x':'Revenue shock','y':'Margin shock','color':'EBITDA margin %'},title='EBITDA margin sensitivity heatmap'),use_container_width=True)
    st.dataframe(pd.DataFrame(grid),use_container_width=True,hide_index=True)

elif view=='Capital & Working Capital':
    st.subheader('🏦 Capital efficiency & working capital')
    wc=working_capital_metrics(company.current_assets,company.current_liabilities,company.inventory,company.cash,company.revenue)
    cap=capital_intensity(company.revenue,company.total_assets,company.capex)
    k=st.columns(6); k[0].metric('Net Working Capital',f"${wc['net_working_capital']:,.0f}M"); k[1].metric('NWC / Revenue',pct(wc['nwc_to_revenue'])); k[2].metric('Working Capital Ratio',mult(wc['working_capital_ratio'])); k[3].metric('Asset Intensity',f"{cap['asset_intensity']:.2f}x"); k[4].metric('Capex / Revenue',pct(cap['capex_to_revenue'])); k[5].metric('Inventory Intensity',pct(wc['inventory_intensity']))
    a,b=st.columns(2)
    with a:
        p=pd.DataFrame({'Metric':['Assets','Revenue','Capex'],'Value':[company.total_assets,company.revenue,company.capex]}); st.plotly_chart(px.bar(p,x='Metric',y='Value',text_auto=',.0f',title='Capital deployment'),use_container_width=True)
    with b:
        p=pd.DataFrame({'Metric':['Current Assets','Current Liabilities','Inventory','Cash'],'Value':[company.current_assets,company.current_liabilities,company.inventory,company.cash]}); st.plotly_chart(px.bar(p,x='Metric',y='Value',text_auto=',.0f',title='Working capital composition'),use_container_width=True)
    st.json({'working_capital':wc,'capital_intensity':cap})

elif view=='DuPont Analysis':
    st.subheader('🧩 DuPont ROE decomposition')
    equity_multiplier=(company.total_assets/company.equity) if company.equity>0 else None
    dup=dupont_analysis(m['net_margin'],m['asset_turnover'],equity_multiplier)
    k=st.columns(4); k[0].metric('Net Margin',pct(m['net_margin'])); k[1].metric('Asset Turnover',mult(m['asset_turnover'])); k[2].metric('Equity Multiplier',mult(equity_multiplier)); k[3].metric('DuPont ROE',pct((dup['roe']/100) if dup['roe'] is not None else None))
    if dup['roe'] is not None:
        st.plotly_chart(px.bar(pd.DataFrame({'Driver':['Net Margin %','Asset Turnover','Equity Multiplier'],'Value':[dup['net_margin'],dup['asset_turnover'],dup['equity_multiplier']]}),x='Driver',y='Value',text_auto='.2f',title='Three-step ROE drivers'),use_container_width=True)
        st.info(f"ROE is decomposed as Net Margin × Asset Turnover × Equity Multiplier. The model's reconstructed ROE is {dup['roe']:.2f}%.")
    else: st.warning('DuPont ROE is not meaningful when book equity is non-positive.')

elif view=='Portfolio Screen':
    peer=df[df.sector.isin(sectors)].copy(); peer['risk_adjusted_score']=peer.health_score-peer.risk_count*3; peer['fcf_yield_proxy']=peer.free_cash_flow/peer.revenue; peer['capital_intensity']=peer.capex/peer.revenue
    st.subheader('Portfolio-style screening')
    st.plotly_chart(px.scatter(peer,x='fcf_yield_proxy',y='health_score',size='revenue',color='sector',text='ticker',hover_name='company',title='Cash generation vs financial health'),use_container_width=True)
    st.plotly_chart(px.bar(peer.sort_values('risk_adjusted_score',ascending=False),x='company',y='risk_adjusted_score',color='sector',text_auto='.0f',title='Risk-adjusted screening score'),use_container_width=True)
    st.dataframe(peer[['company','ticker','sector','health_score','health_grade','risk_count','risk_adjusted_score','fcf_yield_proxy','capital_intensity','net_debt_to_ebitda']],use_container_width=True,hide_index=True)

else:
    st.subheader('Data Explorer'); st.dataframe(df,use_container_width=True,hide_index=True); st.download_button('⬇ Download complete analysis CSV',df.to_csv(index=False).encode(), 'corporate_finance_analysis.csv','text/csv')

st.divider(); st.caption('Built with Python • Pandas • Plotly • Streamlit | Transparent analytical screening — not investment advice.')
