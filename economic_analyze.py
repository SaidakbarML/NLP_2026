import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import numpy as np

# Sahifa konfiguratsiyasi
st.set_page_config(
    page_title="Moliyaviy Tahlil Tizimi",
    page_icon="💼",
    layout="wide"
)

# CSS stillari
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .positive {
        color: #28a745;
    }
    .negative {
        color: #dc3545;
    }
    .neutral {
        color: #ffc107;
    }
</style>
""", unsafe_allow_html=True)

# Asosiy sarlavha
st.markdown('<h1 class="main-header">💼 Moliyaviy Tahlil va Hisobot Tizimi</h1>', unsafe_allow_html=True)

# Yon panel - Kompaniya ma'lumotlari
with st.sidebar:
    st.header("🏢 Kompaniya Ma'lumotlari")
    company_name = st.text_input("Kompaniya nomi", "Mening Kompaniyam")
    fiscal_year = st.number_input("Moliyaviy yil", min_value=2000, max_value=2030, value=2024)
    fiscal_quarter = st.selectbox("Chorak", ["Yillik", "Q1", "Q2", "Q3", "Q4"])
    currency = st.selectbox("Valyuta", ["UZS", "USD", "EUR"])
    
    st.divider()
    st.subheader("📊 Tahlil turini tanlang")
    analysis_type = st.radio(
        "Tahlil turi:",
        ["To'liq Tahlil", "Rentabellik", "Likvidlik", "Qarz Yuklama", "Samaradorlik", "Bozor Ko'rsatkichlari", "Pul Oqimi"]
    )

# Session state for chat
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'financial_data' not in st.session_state:
    st.session_state.financial_data = {}

# Asosiy kontent
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 Ma'lumotlarni Kiritish", "📊 Tahlil Natijalari", "📈 Grafik Tahlil", "📄 Hisobot", "🤖 AI Maslahatchi"])

with tab1:
    st.header("Moliyaviy Ma'lumotlarni Kiriting")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💰 Daromad Hisoboti")
        revenue = st.number_input("Tushum (Savdo hajmi)", value=1000000.0, format="%.2f")
        cogs = st.number_input("Sotilgan mahsulot tannarxi", value=600000.0, format="%.2f")
        operating_expenses = st.number_input("Operatsion xarajatlar", value=200000.0, format="%.2f")
        depreciation = st.number_input("Amortizatsiya", value=50000.0, format="%.2f")
        interest_expense = st.number_input("Foiz xarajatlari", value=20000.0, format="%.2f")
        tax_expense = st.number_input("Soliq xarajatlari", value=26000.0, format="%.2f")
        
        st.subheader("💵 Pul Oqimi")
        operating_cash_flow = st.number_input("Operatsion pul oqimi", value=180000.0, format="%.2f")
        capex = st.number_input("Kapital xarajatlar", value=80000.0, format="%.2f")
        dividends_paid = st.number_input("To'langan dividendlar", value=20000.0, format="%.2f")
    
    with col2:
        st.subheader("🏦 Balans")
        
        st.markdown("**Aktivlar**")
        cash = st.number_input("Naqd pul", value=150000.0, format="%.2f")
        marketable_securities = st.number_input("Qisqa muddatli investitsiyalar", value=50000.0, format="%.2f")
        accounts_receivable = st.number_input("Debitorlik qarz", value=120000.0, format="%.2f")
        inventory = st.number_input("Tovar-moddiy zaxiralar", value=180000.0, format="%.2f")
        other_current_assets = st.number_input("Boshqa joriy aktivlar", value=30000.0, format="%.2f")
        total_assets = st.number_input("Jami aktivlar", value=1500000.0, format="%.2f")
        
        st.markdown("**Majburiyatlar**")
        accounts_payable = st.number_input("Kreditorlik qarz", value=100000.0, format="%.2f")
        short_term_debt = st.number_input("Qisqa muddatli qarz", value=80000.0, format="%.2f")
        current_liabilities = st.number_input("Joriy majburiyatlar", value=250000.0, format="%.2f")
        long_term_debt = st.number_input("Uzoq muddatli qarz", value=400000.0, format="%.2f")
        shareholders_equity = st.number_input("Xususiy kapital", value=850000.0, format="%.2f")
        
        st.markdown("**Bozor Ma'lumotlari**")
        shares_outstanding = st.number_input("Aktsiyalar soni", value=100000.0, format="%.2f")
        market_price_per_share = st.number_input("Aktsiya narxi", value=15.0, format="%.2f")
    
    # O'tgan davr ma'lumotlari
    with st.expander("📅 O'tgan Davr Ma'lumotlari (O'sish hisobi uchun)"):
        col3, col4 = st.columns(2)
        with col3:
            prev_revenue = st.number_input("O'tgan davr tushumi", value=900000.0, format="%.2f")
            prev_net_income = st.number_input("O'tgan davr sof foydasi", value=80000.0, format="%.2f")
            prev_total_assets = st.number_input("O'tgan davr jami aktivlari", value=1400000.0, format="%.2f")
        with col4:
            prev_equity = st.number_input("O'tgan davr kapitali", value=800000.0, format="%.2f")
            prev_inventory = st.number_input("O'tgan davr zaxiralari", value=170000.0, format="%.2f")
            prev_ar = st.number_input("O'tgan davr debitor qarzi", value=110000.0, format="%.2f")
            prev_ap = st.number_input("O'tgan davr kreditor qarzi", value=95000.0, format="%.2f")
    
    # Ma'lumotlarni saqlash
    st.session_state.financial_data = {
        'company_name': company_name,
        'fiscal_year': fiscal_year,
        'fiscal_quarter': fiscal_quarter,
        'currency': currency,
        'revenue': revenue,
        'cogs': cogs,
        'operating_expenses': operating_expenses,
        'depreciation': depreciation,
        'interest_expense': interest_expense,
        'tax_expense': tax_expense,
        'operating_cash_flow': operating_cash_flow,
        'capex': capex,
        'dividends_paid': dividends_paid,
        'cash': cash,
        'marketable_securities': marketable_securities,
        'accounts_receivable': accounts_receivable,
        'inventory': inventory,
        'other_current_assets': other_current_assets,
        'total_assets': total_assets,
        'accounts_payable': accounts_payable,
        'short_term_debt': short_term_debt,
        'current_liabilities': current_liabilities,
        'long_term_debt': long_term_debt,
        'shareholders_equity': shareholders_equity,
        'shares_outstanding': shares_outstanding,
        'market_price_per_share': market_price_per_share,
        'prev_revenue': prev_revenue,
        'prev_net_income': prev_net_income,
        'prev_total_assets': prev_total_assets,
        'prev_equity': prev_equity,
        'prev_inventory': prev_inventory,
        'prev_ar': prev_ar,
        'prev_ap': prev_ap
    }

with tab2:
    st.header("📊 Moliyaviy Tahlil Natijalari")
    
    # Hisoblar
    gross_profit = revenue - cogs
    gross_margin = (gross_profit / revenue * 100) if revenue > 0 else 0
    
    operating_income = revenue - cogs - operating_expenses
    operating_margin = (operating_income / revenue * 100) if revenue > 0 else 0
    
    ebitda = operating_income + depreciation
    ebitda_margin = (ebitda / revenue * 100) if revenue > 0 else 0
    
    net_income = operating_income - interest_expense - tax_expense
    net_margin = (net_income / revenue * 100) if revenue > 0 else 0
    
    # O'rtacha qiymatlar
    avg_total_assets = (total_assets + prev_total_assets) / 2
    avg_equity = (shareholders_equity + prev_equity) / 2
    avg_inventory = (inventory + prev_inventory) / 2
    avg_ar = (accounts_receivable + prev_ar) / 2
    avg_ap = (accounts_payable + prev_ap) / 2
    
    roa = (net_income / avg_total_assets * 100) if avg_total_assets > 0 else 0
    roe = (net_income / avg_equity * 100) if avg_equity > 0 else 0
    
    # Tax rate
    pretax_income = operating_income - interest_expense
    tax_rate = (tax_expense / pretax_income) if pretax_income > 0 else 0.2
    nopat = operating_income * (1 - tax_rate)
    
    total_debt = short_term_debt + long_term_debt
    invested_capital = total_debt + shareholders_equity - cash
    avg_invested_capital = invested_capital
    roic = (nopat / avg_invested_capital * 100) if avg_invested_capital > 0 else 0
    
    # Likvidlik
    current_assets = cash + marketable_securities + accounts_receivable + inventory + other_current_assets
    current_ratio = current_assets / current_liabilities if current_liabilities > 0 else 0
    quick_ratio = (current_assets - inventory) / current_liabilities if current_liabilities > 0 else 0
    cash_ratio = (cash + marketable_securities) / current_liabilities if current_liabilities > 0 else 0
    working_capital = current_assets - current_liabilities
    
    # Qarz yuklama
    debt_to_equity = total_debt / shareholders_equity if shareholders_equity > 0 else 0
    debt_to_assets = total_debt / total_assets if total_assets > 0 else 0
    equity_ratio = shareholders_equity / total_assets if total_assets > 0 else 0
    interest_coverage = operating_income / interest_expense if interest_expense > 0 else 0
    
    # Samaradorlik
    asset_turnover = revenue / avg_total_assets if avg_total_assets > 0 else 0
    inventory_turnover = cogs / avg_inventory if avg_inventory > 0 else 0
    dio = 365 / inventory_turnover if inventory_turnover > 0 else 0
    receivables_turnover = revenue / avg_ar if avg_ar > 0 else 0
    dso = 365 / receivables_turnover if receivables_turnover > 0 else 0
    payables_turnover = cogs / avg_ap if avg_ap > 0 else 0
    dpo = 365 / payables_turnover if payables_turnover > 0 else 0
    ccc = dio + dso - dpo
    
    # Bozor ko'rsatkichlari
    eps = net_income / shares_outstanding if shares_outstanding > 0 else 0
    pe_ratio = market_price_per_share / eps if eps > 0 else 0
    book_value_per_share = shareholders_equity / shares_outstanding if shares_outstanding > 0 else 0
    pb_ratio = market_price_per_share / book_value_per_share if book_value_per_share > 0 else 0
    market_cap = market_price_per_share * shares_outstanding
    enterprise_value = market_cap + total_debt - cash
    ev_ebitda = enterprise_value / ebitda if ebitda > 0 else 0
    ev_sales = enterprise_value / revenue if revenue > 0 else 0
    
    # Pul oqimi
    fcff = operating_cash_flow - capex
    ocf_margin = (operating_cash_flow / revenue * 100) if revenue > 0 else 0
    capex_to_sales = (capex / revenue * 100) if revenue > 0 else 0
    
    # O'sish
    revenue_growth = ((revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
    net_income_growth = ((net_income - prev_net_income) / prev_net_income * 100) if prev_net_income > 0 else 0
    
    # Natijalarni ko'rsatish
    if analysis_type in ["To'liq Tahlil", "Rentabellik"]:
        st.subheader("💹 Rentabellik Ko'rsatkichlari")
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric("Yalpi foyda", f"{gross_profit:,.0f} {currency}", f"{gross_margin:.1f}%")
        col2.metric("Operatsion foyda", f"{operating_income:,.0f} {currency}", f"{operating_margin:.1f}%")
        col3.metric("EBITDA", f"{ebitda:,.0f} {currency}", f"{ebitda_margin:.1f}%")
        col4.metric("Sof foyda", f"{net_income:,.0f} {currency}", f"{net_margin:.1f}%")
        
        col5, col6, col7 = st.columns(3)
        col5.metric("ROA (Aktivlar rentabelligi)", f"{roa:.2f}%")
        col6.metric("ROE (Kapital rentabelligi)", f"{roe:.2f}%")
        col7.metric("ROIC", f"{roic:.2f}%")
    
    if analysis_type in ["To'liq Tahlil", "Likvidlik"]:
        st.subheader("💧 Likvidlik Ko'rsatkichlari")
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric("Joriy likvidlik", f"{current_ratio:.2f}")
        col2.metric("Tez likvidlik", f"{quick_ratio:.2f}")
        col3.metric("Absolut likvidlik", f"{cash_ratio:.2f}")
        col4.metric("Ishchi kapital", f"{working_capital:,.0f} {currency}")
        
        st.info("✅ Yaxshi: Joriy likvidlik > 1.5, Tez likvidlik > 1.0")
    
    if analysis_type in ["To'liq Tahlil", "Qarz Yuklama"]:
        st.subheader("⚖️ Qarz Yuklama Ko'rsatkichlari")
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric("Qarz/Kapital", f"{debt_to_equity:.2f}")
        col2.metric("Qarz/Aktivlar", f"{debt_to_assets:.2f}")
        col3.metric("Kapital nisbati", f"{equity_ratio:.2f}")
        col4.metric("Foiz qoplash", f"{interest_coverage:.2f}x")
        
        if debt_to_equity > 2:
            st.warning("⚠️ Yuqori qarz yuklama - Qarz/Kapital > 2")
        elif debt_to_equity < 0.5:
            st.success("✅ Past qarz yuklama - Qarz/Kapital < 0.5")
    
    if analysis_type in ["To'liq Tahlil", "Samaradorlik"]:
        st.subheader("⚡ Samaradorlik Ko'rsatkichlari")
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric("Aktivlar aylanmasi", f"{asset_turnover:.2f}")
        col2.metric("Zaxiralar aylanmasi", f"{inventory_turnover:.2f}")
        col3.metric("Debitor qarz aylanmasi", f"{receivables_turnover:.2f}")
        col4.metric("Pul konversiya davri", f"{ccc:.0f} kun")
        
        col5, col6, col7 = st.columns(3)
        col5.metric("Zaxiralarda saqlash (DIO)", f"{dio:.0f} kun")
        col6.metric("To'lov olish (DSO)", f"{dso:.0f} kun")
        col7.metric("To'lov qilish (DPO)", f"{dpo:.0f} kun")
    
    if analysis_type in ["To'liq Tahlil", "Bozor Ko'rsatkichlari"]:
        st.subheader("📈 Bozor Ko'rsatkichlari")
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric("EPS (Aktsiyaga foyda)", f"{eps:.2f} {currency}")
        col2.metric("P/E (Narx/Foyda)", f"{pe_ratio:.2f}")
        col3.metric("P/B (Narx/Balans)", f"{pb_ratio:.2f}")
        col4.metric("Bozor kapitalizatsiyasi", f"{market_cap:,.0f} {currency}")
        
        col5, col6 = st.columns(2)
        col5.metric("Enterprise Value", f"{enterprise_value:,.0f} {currency}")
        col6.metric("EV/EBITDA", f"{ev_ebitda:.2f}")
    
    if analysis_type in ["To'liq Tahlil", "Pul Oqimi"]:
        st.subheader("💵 Pul Oqimi Ko'rsatkichlari")
        col1, col2, col3 = st.columns(3)
        
        col1.metric("Erkin pul oqimi", f"{fcff:,.0f} {currency}")
        col2.metric("Operatsion pul oqimi marjasi", f"{ocf_margin:.1f}%")
        col3.metric("CapEx/Savdo", f"{capex_to_sales:.1f}%")
    
    if analysis_type == "To'liq Tahlil":
        st.subheader("📊 O'sish Ko'rsatkichlari")
        col1, col2 = st.columns(2)
        
        col1.metric("Tushum o'sishi", f"{revenue_growth:+.1f}%")
        col2.metric("Foyda o'sishi", f"{net_income_growth:+.1f}%")
        
        st.subheader("🔍 DuPont Tahlili (ROE)")
        dupont_margin = net_margin / 100
        dupont_turnover = asset_turnover
        dupont_leverage = total_assets / shareholders_equity if shareholders_equity > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Sof marja", f"{net_margin:.2f}%")
        col2.metric("Aktivlar aylanmasi", f"{asset_turnover:.2f}")
        col3.metric("Moliyaviy leverage", f"{dupont_leverage:.2f}")
        
        st.info(f"ROE = {net_margin:.2f}% × {asset_turnover:.2f} × {dupont_leverage:.2f} = {roe:.2f}%")

with tab3:
    st.header("📈 Grafik Tahlil")
    
    # Rentabellik grafigi
    fig_profitability = go.Figure()
    categories = ['Yalpi marja', 'Operatsion marja', 'EBITDA marja', 'Sof marja']
    values = [gross_margin, operating_margin, ebitda_margin, net_margin]
    
    fig_profitability.add_trace(go.Bar(
        x=categories,
        y=values,
        marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'],
        text=[f'{v:.1f}%' for v in values],
        textposition='auto',
    ))
    fig_profitability.update_layout(
        title='Rentabellik Ko\'rsatkichlari',
        yaxis_title='Foiz (%)',
        height=400
    )
    st.plotly_chart(fig_profitability, use_container_width=True)
    
    # Likvidlik va Qarz yuklamasi
    col1, col2 = st.columns(2)
    
    with col1:
        fig_liquidity = go.Figure()
        fig_liquidity.add_trace(go.Bar(
            x=['Joriy likvidlik', 'Tez likvidlik', 'Absolut likvidlik'],
            y=[current_ratio, quick_ratio, cash_ratio],
            marker_color=['#17becf', '#bcbd22', '#9467bd'],
            text=[f'{current_ratio:.2f}', f'{quick_ratio:.2f}', f'{cash_ratio:.2f}'],
            textposition='auto'
        ))
        fig_liquidity.update_layout(title='Likvidlik Nisbatlari', height=350)
        st.plotly_chart(fig_liquidity, use_container_width=True)
    
    with col2:
        fig_leverage = go.Figure()
        fig_leverage.add_trace(go.Bar(
            x=['Qarz/Kapital', 'Qarz/Aktivlar', 'Kapital/Aktivlar'],
            y=[debt_to_equity, debt_to_assets, equity_ratio],
            marker_color=['#e377c2', '#8c564b', '#7f7f7f'],
            text=[f'{debt_to_equity:.2f}', f'{debt_to_assets:.2f}', f'{equity_ratio:.2f}'],
            textposition='auto'
        ))
        fig_leverage.update_layout(title='Qarz Yuklama Nisbatlari', height=350)
        st.plotly_chart(fig_leverage, use_container_width=True)
    
    # Pul konversiya davri
    fig_ccc = go.Figure()
    fig_ccc.add_trace(go.Waterfall(
        x=['DIO', 'DSO', 'DPO', 'CCC'],
        y=[dio, dso, -dpo, ccc],
        measure=['relative', 'relative', 'relative', 'total'],
        text=[f'{dio:.0f}', f'{dso:.0f}', f'{-dpo:.0f}', f'{ccc:.0f}'],
        textposition='outside',
        connector={"line": {"color": "rgb(63, 63, 63)"}}
    ))
    fig_ccc.update_layout(
        title='Pul Konversiya Davri (Cash Conversion Cycle)',
        yaxis_title='Kunlar',
        height=400
    )
    st.plotly_chart(fig_ccc, use_container_width=True)
    
    # Balans tarkibi
    col1, col2 = st.columns(2)
    
    with col1:
        fig_assets = go.Figure(data=[go.Pie(
            labels=['Joriy aktivlar', 'Asosiy aktivlar'],
            values=[current_assets, total_assets - current_assets],
            hole=.3
        )])
        fig_assets.update_layout(title='Aktivlar Tarkibi', height=350)
        st.plotly_chart(fig_assets, use_container_width=True)
    
    with col2:
        fig_liabilities = go.Figure(data=[go.Pie(
            labels=['Joriy majburiyatlar', 'Uzoq muddatli qarz', 'Xususiy kapital'],
            values=[current_liabilities, long_term_debt, shareholders_equity],
            hole=.3
        )])
        fig_liabilities.update_layout(title='Passivlar Tarkibi', height=350)
        st.plotly_chart(fig_liabilities, use_container_width=True)

with tab4:
    st.header("📄 Moliyaviy Hisobot")
    
    st.subheader(f"🏢 {company_name}")
    st.write(f"**Moliyaviy yil:** {fiscal_year} | **Davr:** {fiscal_quarter} | **Valyuta:** {currency}")
    st.write(f"**Hisobot sanasi:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    st.divider()
    
    # Umumiy xulosa
    st.subheader("📋 Umumiy Xulosa")
    
    summary_data = {
        'Ko\'rsatkich': [
            'Tushum', 'Sof foyda', 'EBITDA', 'ROE', 'ROA', 
            'Joriy likvidlik', 'Qarz/Kapital', 'Erkin pul oqimi'
        ],
        'Qiymat': [
            f"{revenue:,.0f} {currency}",
            f"{net_income:,.0f} {currency}",
            f"{ebitda:,.0f} {currency}",
            f"{roe:.2f}%",
            f"{roa:.2f}%",
            f"{current_ratio:.2f}",
            f"{debt_to_equity:.2f}",
            f"{fcff:,.0f} {currency}"
        ],
        'Baholash': [
            '✅' if revenue > prev_revenue else '⚠️',
            '✅' if net_income > 0 else '❌',
            '✅' if ebitda > 0 else '❌',
            '✅' if roe > 15 else '⚠️' if roe > 10 else '❌',
            '✅' if roa > 5 else '⚠️' if roa > 3 else '❌',
            '✅' if current_ratio > 1.5 else '⚠️' if current_ratio > 1 else '❌',
            '✅' if debt_to_equity < 1 else '⚠️' if debt_to_equity < 2 else '❌',
            '✅' if fcff > 0 else '❌'
        ]
    }
    
    st.dataframe(pd.DataFrame(summary_data), hide_index=True, use_container_width=True)
    
    # To'liq hisobot
    st.subheader("📊 Batafsil Moliyaviy Ko'rsatkichlar")
    
    full_report = {
        'Kategoriya': [],
        'Ko\'rsatkich': [],
        'Qiymat': [],
        'Izoh': []
    }
    
    # Rentabellik
    profitability_items = [
        ('Rentabellik', 'Yalpi marja', f'{gross_margin:.2f}%', 'Yaxshi: > 40%'),
        ('Rentabellik', 'Operatsion marja', f'{operating_margin:.2f}%', 'Yaxshi: > 15%'),
        ('Rentabellik', 'EBITDA marja', f'{ebitda_margin:.2f}%', 'Yaxshi: > 20%'),
        ('Rentabellik', 'Sof marja', f'{net_margin:.2f}%', 'Yaxshi: > 10%'),
        ('Rentabellik', 'ROA', f'{roa:.2f}%', 'Yaxshi: > 5%'),
        ('Rentabellik', 'ROE', f'{roe:.2f}%', 'Yaxshi: > 15%'),
        ('Rentabellik', 'ROIC', f'{roic:.2f}%', 'Yaxshi: > 10%'),
    ]
    
    # Likvidlik
    liquidity_items = [
        ('Likvidlik', 'Joriy likvidlik', f'{current_ratio:.2f}', 'Yaxshi: 1.5-3.0'),
        ('Likvidlik', 'Tez likvidlik', f'{quick_ratio:.2f}', 'Yaxshi: 1.0-2.0'),
        ('Likvidlik', 'Absolut likvidlik', f'{cash_ratio:.2f}', 'Yaxshi: 0.2-0.5'),
        ('Likvidlik', 'Ishchi kapital', f'{working_capital:,.0f} {currency}', 'Musbat bo\'lishi kerak'),
    ]
    
    # Qarz yuklama
    leverage_items = [
        ('Qarz yuklama', 'Qarz/Kapital', f'{debt_to_equity:.2f}', 'Yaxshi: < 1.0'),
        ('Qarz yuklama', 'Qarz/Aktivlar', f'{debt_to_assets:.2f}', 'Yaxshi: < 0.5'),
        ('Qarz yuklama', 'Foiz qoplash', f'{interest_coverage:.2f}x', 'Yaxshi: > 3.0'),
    ]
    
    # Samaradorlik
    efficiency_items = [
        ('Samaradorlik', 'Aktivlar aylanmasi', f'{asset_turnover:.2f}', 'Yuqori = yaxshi'),
        ('Samaradorlik', 'Zaxiralar aylanmasi', f'{inventory_turnover:.2f}', 'Yuqori = yaxshi'),
        ('Samaradorlik', 'DIO', f'{dio:.0f} kun', 'Past = yaxshi'),
        ('Samaradorlik', 'DSO', f'{dso:.0f} kun', 'Past = yaxshi'),
        ('Samaradorlik', 'DPO', f'{dpo:.0f} kun', 'Yuqori = yaxshi'),
        ('Samaradorlik', 'CCC', f'{ccc:.0f} kun', 'Past = yaxshi'),
    ]
    
    # Bozor
    market_items = [
        ('Bozor', 'EPS', f'{eps:.2f} {currency}', 'Yuqori = yaxshi'),
        ('Bozor', 'P/E', f'{pe_ratio:.2f}', 'O\'rtacha: 15-25'),
        ('Bozor', 'P/B', f'{pb_ratio:.2f}', 'O\'rtacha: 1.0-3.0'),
        ('Bozor', 'Bozor kap.', f'{market_cap:,.0f} {currency}', 'Kompaniya qiymati'),
        ('Bozor', 'EV/EBITDA', f'{ev_ebitda:.2f}', 'O\'rtacha: 8-15'),
    ]
    
    # Pul oqimi
    cashflow_items = [
        ('Pul oqimi', 'Erkin pul oqimi', f'{fcff:,.0f} {currency}', 'Musbat bo\'lishi kerak'),
        ('Pul oqimi', 'OCF marja', f'{ocf_margin:.2f}%', 'Yaxshi: > 15%'),
        ('Pul oqimi', 'CapEx/Savdo', f'{capex_to_sales:.2f}%', 'Sanoatga bog\'liq'),
    ]
    
    # O'sish
    growth_items = [
        ('O\'sish', 'Tushum o\'sishi', f'{revenue_growth:+.2f}%', 'Musbat = yaxshi'),
        ('O\'sish', 'Foyda o\'sishi', f'{net_income_growth:+.2f}%', 'Musbat = yaxshi'),
    ]
    
    all_items = profitability_items + liquidity_items + leverage_items + efficiency_items + market_items + cashflow_items + growth_items
    
    for item in all_items:
        full_report['Kategoriya'].append(item[0])
        full_report['Ko\'rsatkich'].append(item[1])
        full_report['Qiymat'].append(item[2])
        full_report['Izoh'].append(item[3])
    
    st.dataframe(pd.DataFrame(full_report), hide_index=True, use_container_width=True)
    
    # Tavsiyalar
    st.subheader("💡 Tavsiyalar va Xulosalar")
    
    recommendations = []
    
    if net_margin < 5:
        recommendations.append("⚠️ **Sof marja past** - Xarajatlarni kamaytirish va samaradorlikni oshirish kerak")
    elif net_margin > 15:
        recommendations.append("✅ **A'lo sof marja** - Kompaniya yuqori rentabellikka ega")
    
    if current_ratio < 1:
        recommendations.append("❌ **Likvidlik xavfi** - Joriy majburiyatlarni qoplash uchun resurslar yetarli emas")
    elif current_ratio > 3:
        recommendations.append("⚠️ **Ortiqcha likvidlik** - Resurslar samarasiz ishlatilmoqda")
    else:
        recommendations.append("✅ **Maqbul likvidlik** - Likvidlik holati yaxshi")
    
    if debt_to_equity > 2:
        recommendations.append("❌ **Yuqori qarz yuklama** - Moliyaviy xavf yuqori, qarzni kamaytirish kerak")
    elif debt_to_equity < 0.5:
        recommendations.append("✅ **Past qarz yuklama** - Moliyaviy barqarorlik yuqori")
    
    if roe > 15:
        recommendations.append("✅ **Yuqori ROE** - Kompaniya kapitalni samarali ishlatmoqda")
    elif roe < 8:
        recommendations.append("⚠️ **Past ROE** - Kapital samaradorligini oshirish kerak")
    
    if fcff < 0:
        recommendations.append("❌ **Salbiy erkin pul oqimi** - Pul oqimini yaxshilash zarur")
    else:
        recommendations.append("✅ **Musbat erkin pul oqimi** - Kompaniya pul ishlab chiqarmoqda")
    
    if ccc > 90:
        recommendations.append("⚠️ **Uzoq pul konversiya davri** - Ishchi kapitalni boshqarishni yaxshilash kerak")
    elif ccc < 30:
        recommendations.append("✅ **Qisqa pul konversiya davri** - Samarali ishchi kapital boshqaruvi")
    
    if interest_coverage < 2:
        recommendations.append("❌ **Past foiz qoplash** - Foiz to'lashda qiyinchiliklar bo'lishi mumkin")
    elif interest_coverage > 5:
        recommendations.append("✅ **Yuqori foiz qoplash** - Qarz xizmatida muammo yo'q")
    
    for rec in recommendations:
        st.write(rec)
    
    # Hisobotni yuklab olish
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 CSV formatda yuklab olish", use_container_width=True):
            df_report = pd.DataFrame(full_report)
            csv = df_report.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="CSV faylni yuklab olish",
                data=csv,
                file_name=f"{company_name}_moliyaviy_hisobot_{fiscal_year}.csv",
                mime="text/csv",
            )
    
    with col2:
        if st.button("📊 Excel formatda yuklab olish", use_container_width=True):
            st.info("Excel yuklab olish tez orada qo'shiladi")
    
    with col3:
        if st.button("🖨️ PDF formatda yuklab olish", use_container_width=True):
            st.info("PDF yuklab olish tez orada qo'shiladi")

with tab5:
    st.header("🤖 AI Moliyaviy Maslahatchi")
    st.write("Men sizning moliyaviy ko'rsatkichlaringiz haqida savollaringizga javob bera olaman!")
    
    # AI Maslahatchi funksiyasi
    def get_financial_context():
        """Joriy moliyaviy ma'lumotlarni kontekst sifatida tayyorlash"""
        if not st.session_state.financial_data:
            return "Ma'lumot kiritilmagan"
        
        data = st.session_state.financial_data
        
        # Hisoblar
        gross_profit = data.get('revenue', 0) - data.get('cogs', 0)
        gross_margin = (gross_profit / data.get('revenue', 1) * 100) if data.get('revenue', 0) > 0 else 0
        
        operating_income = data.get('revenue', 0) - data.get('cogs', 0) - data.get('operating_expenses', 0)
        operating_margin = (operating_income / data.get('revenue', 1) * 100) if data.get('revenue', 0) > 0 else 0
        
        ebitda = operating_income + data.get('depreciation', 0)
        ebitda_margin = (ebitda / data.get('revenue', 1) * 100) if data.get('revenue', 0) > 0 else 0
        
        net_income = operating_income - data.get('interest_expense', 0) - data.get('tax_expense', 0)
        net_margin = (net_income / data.get('revenue', 1) * 100) if data.get('revenue', 0) > 0 else 0
        
        avg_assets = (data.get('total_assets', 0) + data.get('prev_total_assets', 0)) / 2
        avg_equity = (data.get('shareholders_equity', 0) + data.get('prev_equity', 0)) / 2
        
        roa = (net_income / avg_assets * 100) if avg_assets > 0 else 0
        roe = (net_income / avg_equity * 100) if avg_equity > 0 else 0
        
        current_assets = (data.get('cash', 0) + data.get('marketable_securities', 0) + 
                         data.get('accounts_receivable', 0) + data.get('inventory', 0) + 
                         data.get('other_current_assets', 0))
        current_ratio = current_assets / data.get('current_liabilities', 1) if data.get('current_liabilities', 0) > 0 else 0
        
        total_debt = data.get('short_term_debt', 0) + data.get('long_term_debt', 0)
        debt_to_equity = total_debt / data.get('shareholders_equity', 1) if data.get('shareholders_equity', 0) > 0 else 0
        
        fcff = data.get('operating_cash_flow', 0) - data.get('capex', 0)
        
        context = f"""
Kompaniya: {data.get('company_name', 'N/A')}
Yil: {data.get('fiscal_year', 'N/A')}
Davr: {data.get('fiscal_quarter', 'N/A')}
Valyuta: {data.get('currency', 'N/A')}

ASOSIY MOLIYAVIY KO'RSATKICHLAR:
- Tushum: {data.get('revenue', 0):,.0f} {data.get('currency', '')}
- Sof foyda: {net_income:,.0f} {data.get('currency', '')}
- EBITDA: {ebitda:,.0f} {data.get('currency', '')}

RENTABELLIK:
- Yalpi marja: {gross_margin:.2f}%
- Operatsion marja: {operating_margin:.2f}%
- EBITDA marja: {ebitda_margin:.2f}%
- Sof marja: {net_margin:.2f}%
- ROE: {roe:.2f}%
- ROA: {roa:.2f}%

LIKVIDLIK VA QARZ:
- Joriy likvidlik: {current_ratio:.2f}
- Qarz/Kapital: {debt_to_equity:.2f}
- Jami qarz: {total_debt:,.0f} {data.get('currency', '')}

PUL OQIMI:
- Operatsion pul oqimi: {data.get('operating_cash_flow', 0):,.0f} {data.get('currency', '')}
- Erkin pul oqimi: {fcff:,.0f} {data.get('currency', '')}
- Kapital xarajatlar: {data.get('capex', 0):,.0f} {data.get('currency', '')}

BALANS:
- Jami aktivlar: {data.get('total_assets', 0):,.0f} {data.get('currency', '')}
- Xususiy kapital: {data.get('shareholders_equity', 0):,.0f} {data.get('currency', '')}
- Naqd pul: {data.get('cash', 0):,.0f} {data.get('currency', '')}
"""
        return context
    
    def get_ai_response(user_question, context):
        """AI javobini generatsiya qilish - oddiy qoidalar asosida"""
        question_lower = user_question.lower()
        
        # Umumiy savollar
        if any(word in question_lower for word in ['salom', 'assalom', 'hello', 'hi']):
            return "Assalom alaykum! Men sizning moliyaviy maslahatchi botingizman. Kompaniyangizning moliyaviy ko'rsatkichlari haqida savollar berishingiz mumkin. Masalan: 'Kompaniyamning rentabelligi qanday?', 'Likvidlik holatim yaxshimi?', 'Qanday tavsiyalar bera olasiz?'"
        
        # Rentabellik haqida
        if any(word in question_lower for word in ['rentabellik', 'foyda', 'marja', 'roe', 'roa', 'daromad']):
            data = st.session_state.financial_data
            if not data:
                return "Iltimos, avval moliyaviy ma'lumotlarni kiriting."
            
            revenue = data.get('revenue', 0)
            cogs = data.get('cogs', 0)
            operating_expenses = data.get('operating_expenses', 0)
            interest_expense = data.get('interest_expense', 0)
            tax_expense = data.get('tax_expense', 0)
            
            gross_profit = revenue - cogs
            gross_margin = (gross_profit / revenue * 100) if revenue > 0 else 0
            operating_income = revenue - cogs - operating_expenses
            net_income = operating_income - interest_expense - tax_expense
            net_margin = (net_income / revenue * 100) if revenue > 0 else 0
            
            avg_assets = (data.get('total_assets', 0) + data.get('prev_total_assets', 0)) / 2
            avg_equity = (data.get('shareholders_equity', 0) + data.get('prev_equity', 0)) / 2
            roa = (net_income / avg_assets * 100) if avg_assets > 0 else 0
            roe = (net_income / avg_equity * 100) if avg_equity > 0 else 0
            
            response = f"""📊 **RENTABELLIK TAHLILI:**

Kompaniyangizning rentabellik ko'rsatkichlari:

💰 **Marja ko'rsatkichlari:**
- Yalpi marja: {gross_margin:.2f}% {"✅ Yaxshi" if gross_margin > 40 else "⚠️ O'rtacha" if gross_margin > 25 else "❌ Past"}
- Sof marja: {net_margin:.2f}% {"✅ Yaxshi" if net_margin > 10 else "⚠️ O'rtacha" if net_margin > 5 else "❌ Past"}

📈 **Rentabellik nisbatlari:**
- ROE (Kapital rentabelligi): {roe:.2f}% {"✅ A'lo" if roe > 15 else "⚠️ O'rtacha" if roe > 10 else "❌ Past"}
- ROA (Aktivlar rentabelligi): {roa:.2f}% {"✅ Yaxshi" if roa > 5 else "⚠️ O'rtacha" if roa > 3 else "❌ Past"}

💡 **Tavsiyalar:**
"""
            if net_margin < 5:
                response += "\n- ⚠️ Sof marja juda past. Xarajatlarni kamaytirish va narxlash strategiyasini ko'rib chiqing."
            if roe < 10:
                response += "\n- ⚠️ ROE past. Kapitalni samarali ishlatish yo'llarini qidiring."
            if gross_margin < 25:
                response += "\n- ⚠️ Yalpi marja past. Ta'minot zanjiri xarajatlarini optimallashtiring."
            if net_margin > 10 and roe > 15:
                response += "\n- ✅ Rentabellik ko'rsatkichlaringiz a'lo darajada!"
            
            return response
        
        # Likvidlik haqida
        if any(word in question_lower for word in ['likvidlik', 'naqd', 'to\'lov', 'qarz', 'majburiyat']):
            data = st.session_state.financial_data
            if not data:
                return "Iltimos, avval moliyaviy ma'lumotlarni kiriting."
            
            current_assets = (data.get('cash', 0) + data.get('marketable_securities', 0) + 
                            data.get('accounts_receivable', 0) + data.get('inventory', 0) + 
                            data.get('other_current_assets', 0))
            current_liabilities = data.get('current_liabilities', 1)
            current_ratio = current_assets / current_liabilities if current_liabilities > 0 else 0
            quick_ratio = (current_assets - data.get('inventory', 0)) / current_liabilities if current_liabilities > 0 else 0
            
            total_debt = data.get('short_term_debt', 0) + data.get('long_term_debt', 0)
            debt_to_equity = total_debt / data.get('shareholders_equity', 1) if data.get('shareholders_equity', 0) > 0 else 0
            
            response = f"""💧 **LIKVIDLIK VA QARZ TAHLILI:**

**Likvidlik nisbatlari:**
- Joriy likvidlik: {current_ratio:.2f} {"✅ Yaxshi" if current_ratio > 1.5 else "⚠️ O'rtacha" if current_ratio > 1 else "❌ Xavfli"}
- Tez likvidlik: {quick_ratio:.2f} {"✅ Yaxshi" if quick_ratio > 1 else "⚠️ Past"}

**Qarz yuklama:**
- Qarz/Kapital: {debt_to_equity:.2f} {"✅ Maqbul" if debt_to_equity < 1 else "⚠️ O'rtacha" if debt_to_equity < 2 else "❌ Yuqori"}
- Jami qarz: {total_debt:,.0f} {data.get('currency', '')}

💡 **Tavsiyalar:**
"""
            if current_ratio < 1:
                response += "\n- ❌ Likvidlik xavfi! Qisqa muddatli majburiyatlarni qoplash uchun resurslar yetarli emas."
            elif current_ratio > 3:
                response += "\n- ⚠️ Ortiqcha likvidlik. Resurslarni samarali investitsiya qiling."
            else:
                response += "\n- ✅ Likvidlik holati yaxshi."
            
            if debt_to_equity > 2:
                response += "\n- ❌ Qarz yuklama juda yuqori! Qarzni kamaytirish rejasini tuzing."
            elif debt_to_equity < 0.5:
                response += "\n- ✅ Moliyaviy barqarorlik yuqori."
            
            return response
        
        # Pul oqimi haqida
        if any(word in question_lower for word in ['pul oqimi', 'cash flow', 'naqd pul', 'fcf']):
            data = st.session_state.financial_data
            if not data:
                return "Iltimos, avval moliyaviy ma'lumotlarni kiriting."
            
            ocf = data.get('operating_cash_flow', 0)
            capex = data.get('capex', 0)
            fcff = ocf - capex
            revenue = data.get('revenue', 1)
            ocf_margin = (ocf / revenue * 100) if revenue > 0 else 0
            
            response = f"""💵 **PUL OQIMI TAHLILI:**

**Pul oqimi ko'rsatkichlari:**
- Operatsion pul oqimi: {ocf:,.0f} {data.get('currency', '')} {"✅" if ocf > 0 else "❌"}
- Kapital xarajatlar: {capex:,.0f} {data.get('currency', '')}
- Erkin pul oqimi (FCF): {fcff:,.0f} {data.get('currency', '')} {"✅" if fcff > 0 else "❌"}
- OCF marja: {ocf_margin:.2f}% {"✅ Yaxshi" if ocf_margin > 15 else "⚠️ O'rtacha" if ocf_margin > 10 else "❌ Past"}

💡 **Tavsiyalar:**
"""
            if fcff < 0:
                response += "\n- ❌ Salbiy erkin pul oqimi! Kompaniya pul sarflayapti, daromad keltirayotgan emas."
                response += "\n- Xarajatlarni kamaytiring yoki tushumni oshiring."
            else:
                response += "\n- ✅ Musbat erkin pul oqimi - bu yaxshi belgi!"
            
            if ocf_margin < 10:
                response += "\n- ⚠️ OCF marja past. Operatsion samaradorlikni oshiring."
            
            return response
        
        # Tavsiyalar
        if any(word in question_lower for word in ['tavsiya', 'maslahat', 'nima qilish', 'yaxshilash']):
            data = st.session_state.financial_data
            if not data:
                return "Iltimos, avval moliyaviy ma'lumotlarni kiriting."
            
            # Barcha asosiy ko'rsatkichlarni hisoblash
            revenue = data.get('revenue', 0)
            cogs = data.get('cogs', 0)
            operating_expenses = data.get('operating_expenses', 0)
            operating_income = revenue - cogs - operating_expenses
            net_income = operating_income - data.get('interest_expense', 0) - data.get('tax_expense', 0)
            net_margin = (net_income / revenue * 100) if revenue > 0 else 0
            
            avg_equity = (data.get('shareholders_equity', 0) + data.get('prev_equity', 0)) / 2
            roe = (net_income / avg_equity * 100) if avg_equity > 0 else 0
            
            current_assets = (data.get('cash', 0) + data.get('marketable_securities', 0) + 
                            data.get('accounts_receivable', 0) + data.get('inventory', 0) + 
                            data.get('other_current_assets', 0))
            current_ratio = current_assets / data.get('current_liabilities', 1) if data.get('current_liabilities', 0) > 0 else 0
            
            total_debt = data.get('short_term_debt', 0) + data.get('long_term_debt', 0)
            debt_to_equity = total_debt / data.get('shareholders_equity', 1) if data.get('shareholders_equity', 0) > 0 else 0
            
            fcff = data.get('operating_cash_flow', 0) - data.get('capex', 0)
            
            response = f"""💡 **KOMPANIYA UCHUN SHAXSIY TAVSIYALAR:**

📊 **Umumiy holat:**
"""
            
            # Asosiy muammolar va tavsiyalar
            issues = []
            suggestions = []
            strengths = []
            
            if net_margin < 5:
                issues.append("Sof marja juda past")
                suggestions.append("Xarajatlarni qisqartiring, operatsion samaradorlikni oshiring")
            elif net_margin > 15:
                strengths.append("A'lo rentabellik ko'rsatkichlari")
            
            if roe < 10:
                issues.append("ROE past - kapital samarasiz ishlatilmoqda")
                suggestions.append("Rentabellikni oshiring yoki ortiqcha kapitalni qaytaring")
            elif roe > 15:
                strengths.append("Yuqori kapital rentabelligi")
            
            if current_ratio < 1:
                issues.append("Likvidlik xavfi mavjud")
                suggestions.append("Qisqa muddatli qarzni kamaytiring yoki joriy aktivlarni oshiring")
            elif current_ratio > 3:
                issues.append("Ortiqcha likvidlik")
                suggestions.append("Naqd pulni samarali investitsiya qiling")
            else:
                strengths.append("Maqbul likvidlik darajasi")
            
            if debt_to_equity > 2:
                issues.append("Yuqori qarz yuklama - moliyaviy xavf")
                suggestions.append("Qarzni qaytarish rejasini tuzing, yangi qarz olishdan saqlaning")
            elif debt_to_equity < 0.5:
                strengths.append("Barqaror moliyaviy holat")
            
            if fcff < 0:
                issues.append("Salbiy erkin pul oqimi")
                suggestions.append("Pul oqimini yaxshilash uchun operatsion xarajatlarni optimallashtiring")
            else:
                strengths.append("Musbat pul oqimi")
            
            # Kuchli tomonlar
            if strengths:
                response += "\n\n✅ **Kuchli tomonlaringiz:**\n"
                for strength in strengths:
                    response += f"- {strength}\n"
            
            # Muammolar
            if issues:
                response += "\n\n⚠️ **E'tibor talab etadigan sohalar:**\n"
                for issue in issues:
                    response += f"- {issue}\n"
            
            # Tavsiyalar
            if suggestions:
                response += "\n\n💡 **Tavsiyalar:**\n"
                for i, suggestion in enumerate(suggestions, 1):
                    response += f"{i}. {suggestion}\n"
            
            # Umumiy xulosa
            if len(issues) == 0:
                response += "\n\n🎉 **Umumiy xulosa:** Kompaniyangiz yaxshi holatda! Hozirgi strategiyangizni davom ettiring."
            elif len(issues) <= 2:
                response += "\n\n📌 **Umumiy xulosa:** Ba'zi sohalarni yaxshilash kerak, lekin umumiy holat qoniqarli."
            else:
                response += "\n\n⚠️ **Umumiy xulosa:** Jiddiy e'tibor talab qiladigan bir nechta muammolar mavjud. Tezkor choralar ko'ring."
            
            return response
        
        # Solishtirish
        if any(word in question_lower for word in ['solishtir', 'benchmark', 'o\'rtacha', 'standart']):
            return """📊 **SANOAT O'RTACHA KO'RSATKICHLARI:**

**Rentabellik (o'rtacha):**
- Sof marja: 8-12%
- ROE: 12-18%
- ROA: 5-8%

**Likvidlik (maqbul):**
- Joriy likvidlik: 1.5-2.5
- Tez likvidlik: 1.0-1.5

**Qarz yuklama (maqbul):**
- Qarz/Kapital: 0.5-1.5
- Foiz qoplash: > 3.0

💡 Sizning ko'rsatkichlaringizni bu qiymatlar bilan solishtiring. Har bir sanoatning o'z xususiyatlari bor, shuning uchun aniq solishtirish uchun o'z sanoatingizning benchmark ko'rsatkichlarini toping."""
        
        # Yo'riqnoma
        if any(word in question_lower for word in ['yordam', 'qanday', 'nima', 'help', 'qo\'llanma']):
            return """🤖 **AI MASLAHATCHI YO'RIQNOMASI:**

Men sizga quyidagi mavzularda yordam bera olaman:

1️⃣ **Rentabellik tahlili:**
   - "Rentabelligim qanday?"
   - "Foydam yaxshimi?"
   - "ROE haqida tushuntir"

2️⃣ **Likvidlik va qarz:**
   - "Likvidlik holatim qanday?"
   - "Qarzlarim ko'pmi?"
   - "To'lov qobiliyatim yaxshimi?"

3️⃣ **Pul oqimi:**
   - "Pul oqimim qanday?"
   - "Erkin pul oqimi nima?"

4️⃣ **Umumiy tavsiyalar:**
   - "Qanday tavsiyalar bera olasiz?"
   - "Kompaniyamni yaxshilash uchun nima qilishim kerak?"

5️⃣ **Solishtirish:**
   - "Mening ko'rsatkichlarimni solishtir"
   - "Sanoat o'rtacha ko'rsatkichlari qanday?"

📌 Shunchaki savolingizni yozing va men sizga batafsil javob beraman!"""
        
        # Default javob
        return """Men sizning savolingizni to'liq tushunmadim. Quyidagi mavzularda yordam bera olaman:

- Rentabellik tahlili
- Likvidlik va qarz holati
- Pul oqimi
- Umumiy tavsiyalar
- Sanoat bilan solishtirish

"Yordam" deb yozing, to'liq yo'riqnomani ko'rish uchun."""
    
    # Chat UI
    st.markdown("### 💬 Suhbat")
    
    # Chat history
    chat_container = st.container()
    with chat_container:
        for i, chat in enumerate(st.session_state.chat_history):
            if chat['role'] == 'user':
                st.markdown(f"""
                <div style='background-color: #e3f2fd; padding: 10px; border-radius: 10px; margin: 5px 0;'>
                    <strong>Siz:</strong> {chat['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='background-color: #f5f5f5; padding: 10px; border-radius: 10px; margin: 5px 0;'>
                    <strong>🤖 AI Maslahatchi:</strong><br>{chat['content']}
                </div>
                """, unsafe_allow_html=True)
    
    # User input
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input("Savolingizni yozing...", key="user_input", label_visibility="collapsed", 
                                    placeholder="Masalan: Kompaniyamning rentabelligi qanday?")
    with col2:
        send_button = st.button("📤 Yuborish", use_container_width=True)
    
    # Quick questions
    st.markdown("**💡 Tez savollar:**")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 Rentabellik", use_container_width=True):
            user_input = "Kompaniyamning rentabelligi qanday?"
            send_button = True
    
    with col2:
        if st.button("💧 Likvidlik", use_container_width=True):
            user_input = "Likvidlik holatim qanday?"
            send_button = True
    
    with col3:
        if st.button("💵 Pul oqimi", use_container_width=True):
            user_input = "Pul oqimim haqida ma'lumot ber"
            send_button = True
    
    with col4:
        if st.button("💡 Tavsiyalar", use_container_width=True):
            user_input = "Qanday tavsiyalar bera olasiz?"
            send_button = True
    
    # Process message
    if send_button and user_input:
        # Add user message
        st.session_state.chat_history.append({
            'role': 'user',
            'content': user_input
        })
        
        # Get AI response
        context = get_financial_context()
        ai_response = get_ai_response(user_input, context)
        
        # Add AI response
        st.session_state.chat_history.append({
            'role': 'assistant',
            'content': ai_response
        })
        
        # Rerun to update chat
        st.rerun()
    
    # Clear chat button
    if st.button("🗑️ Suhbatni tozalash"):
        st.session_state.chat_history = []
        st.rerun()
    
    # Info box
    with st.expander("ℹ️ AI Maslahatchi haqida"):
        st.markdown("""
        **AI Moliyaviy Maslahatchi** sizning moliyaviy ma'lumotlaringizni tahlil qilib, 
        to'g'ridan-to'g'ri savollaringizga javob beradi.
        
        **Qanday ishlaydi:**
        1. Siz "Ma'lumotlarni Kiritish" tabida kompaniya ma'lumotlarini kiritasiz
        2. AI Maslahatchi bu ma'lumotlarni tahlil qiladi
        3. Siz savol berasiz (masalan: "Rentabelligim yaxshimi?")
        4. AI sizga batafsil javob va tavsiyalar beradi
        
        **Xususiyatlar:**
        - ✅ Uzbek tilida to'liq qo'llab-quvvatlash
        - ✅ Shaxsiylashtirilgan tavsiyalar
        - ✅ Oddiy va tushunarli tushuntirishlar
        - ✅ Sanoat standartlari bilan solishtirish
        - ✅ Amaliy maslahatlar
        """)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p><strong>Moliyaviy Tahlil Tizimi</strong> | Barcha huquqlar himoyalangan © 2024</p>
    <p style='font-size: 0.9em;'>Bu tizim kompaniyalarning moliyaviy holatini baholash va qarorlar qabul qilishda yordam berish uchun ishlab chiqilgan</p>
    <p style='font-size: 0.8em;'>⚠️ Diqqat: Bu ma'lumotlar faqat tahlil maqsadida. Investitsiya qarorlari qabul qilishdan oldin professional maslahatchi bilan maslahatlashing</p>
</div>
""", unsafe_allow_html=True)

# Qo'shimcha funksiyalar - Qirg'oqda
with st.sidebar:
    st.divider()
    st.subheader("📚 Qo'llanma")
    
    with st.expander("Ko'rsatkichlar haqida"):
        st.markdown("""
        **Rentabellik:**
        - Yalpi marja: (Tushum - Tannarx) / Tushum
        - ROE: Sof foyda / O'rtacha kapital
        - ROA: Sof foyda / O'rtacha aktivlar
        
        **Likvidlik:**
        - Joriy: Joriy aktivlar / Joriy majburiyatlar
        - Tez: (Joriy aktivlar - Zaxiralar) / Joriy majburiyatlar
        
        **Qarz yuklama:**
        - Qarz/Kapital: Jami qarz / Xususiy kapital
        - Foiz qoplash: EBIT / Foiz xarajatlari
        """)
    
    with st.expander("Benchmark qiymatlari"):
        st.markdown("""
        **Yaxshi ko'rsatkichlar:**
        - ROE: > 15%
        - ROA: > 5%
        - Joriy likvidlik: 1.5 - 3.0
        - Qarz/Kapital: < 1.0
        - EBITDA marja: > 20%
        - Foiz qoplash: > 3.0
        
        **Sanoatga bog'liq:**
        - Zaxiralar aylanmasi
        - Aktivlar aylanmasi
        - P/E nisbati
        """)
    
    with st.expander("Maslahatlar"):
        st.markdown("""
        1. **Aniq ma'lumot kiriting** - Natijalar kiritilgan ma'lumotlarga bog'liq
        2. **O'tgan davr bilan solishtiring** - Trendlarni kuzating
        3. **Sanoat o'rtacha ko'rsatkichlari bilan solishtiring**
        4. **Bir nechta ko'rsatkichni birgalikda tahlil qiling**
        5. **Moliyaviy konsultant bilan maslahatlashing**
        """)
    
    st.divider()
    
    # Ma'lumotlarni tozalash
    if st.button("🗑️ Barcha ma'lumotlarni tozalash", use_container_width=True):
        st.rerun()
    
    # Versiya
    st.caption("Versiya 1.0.0")
    st.caption("Oxirgi yangilanish: 2024")