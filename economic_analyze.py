import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import numpy as np
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io
import base64
import requests
import os

# Sahifa konfiguratsiyasi
st.set_page_config(
    page_title="Moliyaviy Tahlil Tizimi by SaidakbaR",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
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

# ============= OPENROUTER LLM FUNCTION =============
def call_openrouter_llm(prompt, max_tokens=2000):
    """Call OpenRouter API with DeepSeek R1T2 model"""
    try:
<<<<<<< HEAD
        api_key = os.getenv("OPENROUTER_API_KEY", "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")
=======
        api_key = os.getenv("OPENROUTER_API_KEY", "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")
>>>>>>> 86e4a52 (uzbek version)
        if not api_key:
            st.warning("OPENROUTER_API_KEY not configured. Please set environment variable.")
            return None
        # fetch tutorial then update
        headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://streamlit.io",
            "X-Title": "Financial Analysis AI Advisor"
        }
        
        data = {
            "model": "tngtech/deepseek-r1t2-chimera:free",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
        else:
            st.error(f"OpenRouter API error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Error calling OpenRouter API: {str(e)}")
        return None

# ============= CALCULATION FUNCTION =============
def calculate_financial_metrics(data):
    """Calculate all financial metrics and store in session_state"""
    revenue = data.get('revenue', 0)
    cogs = data.get('cogs', 0)
    operating_expenses = data.get('operating_expenses', 0)
    depreciation = data.get('depreciation', 0)
    interest_expense = data.get('interest_expense', 0)
    tax_expense = data.get('tax_expense', 0)
    operating_cash_flow = data.get('operating_cash_flow', 0)
    capex = data.get('capex', 0)
    dividends_paid = data.get('dividends_paid', 0)
    
    cash = data.get('cash', 0)
    marketable_securities = data.get('marketable_securities', 0)
    accounts_receivable = data.get('accounts_receivable', 0)
    inventory = data.get('inventory', 0)
    other_current_assets = data.get('other_current_assets', 0)
    total_assets = data.get('total_assets', 0)
    
    accounts_payable = data.get('accounts_payable', 0)
    short_term_debt = data.get('short_term_debt', 0)
    current_liabilities = data.get('current_liabilities', 0)
    long_term_debt = data.get('long_term_debt', 0)
    shareholders_equity = data.get('shareholders_equity', 0)
    
    shares_outstanding = data.get('shares_outstanding', 0)
    market_price_per_share = data.get('market_price_per_share', 0)
    
    prev_revenue = data.get('prev_revenue', revenue * 0.9 if revenue > 0 else 0)
    prev_net_income = data.get('prev_net_income', 0)
    prev_total_assets = data.get('prev_total_assets', total_assets * 0.93 if total_assets > 0 else 0)
    prev_equity = data.get('prev_equity', shareholders_equity * 0.94 if shareholders_equity > 0 else 0)
    prev_inventory = data.get('prev_inventory', inventory * 0.94 if inventory > 0 else 0)
    prev_ar = data.get('prev_ar', accounts_receivable * 0.92 if accounts_receivable > 0 else 0)
    prev_ap = data.get('prev_ap', accounts_payable * 0.95 if accounts_payable > 0 else 0)
    
    # Profitability calculations
    gross_profit = revenue - cogs
    gross_margin = (gross_profit / revenue * 100) if revenue > 0 else 0
    
    operating_income = revenue - cogs - operating_expenses
    operating_margin = (operating_income / revenue * 100) if revenue > 0 else 0
    
    ebitda = operating_income + depreciation
    ebitda_margin = (ebitda / revenue * 100) if revenue > 0 else 0
    
    net_income = operating_income - interest_expense - tax_expense
    net_margin = (net_income / revenue * 100) if revenue > 0 else 0
    
    # Average values
    avg_total_assets = (total_assets + prev_total_assets) / 2 if (total_assets + prev_total_assets) > 0 else 1
    avg_equity = (shareholders_equity + prev_equity) / 2 if (shareholders_equity + prev_equity) > 0 else 1
    avg_inventory = (inventory + prev_inventory) / 2 if (inventory + prev_inventory) > 0 else 1
    avg_ar = (accounts_receivable + prev_ar) / 2 if (accounts_receivable + prev_ar) > 0 else 1
    avg_ap = (accounts_payable + prev_ap) / 2 if (accounts_payable + prev_ap) > 0 else 1
    
    roa = (net_income / avg_total_assets * 100) if avg_total_assets > 0 else 0
    roe = (net_income / avg_equity * 100) if avg_equity > 0 else 0
    
    # Tax rate
    pretax_income = operating_income - interest_expense
    tax_rate = (tax_expense / pretax_income) if pretax_income > 0 else 0.2
    nopat = operating_income * (1 - tax_rate)
    
    total_debt = short_term_debt + long_term_debt
    invested_capital = total_debt + shareholders_equity - cash
    avg_invested_capital = invested_capital if invested_capital > 0 else 1
    roic = (nopat / avg_invested_capital * 100) if avg_invested_capital > 0 else 0
    
    # Liquidity
    current_assets = cash + marketable_securities + accounts_receivable + inventory + other_current_assets
    current_ratio = current_assets / current_liabilities if current_liabilities > 0 else 0
    quick_ratio = (current_assets - inventory) / current_liabilities if current_liabilities > 0 else 0
    cash_ratio = (cash + marketable_securities) / current_liabilities if current_liabilities > 0 else 0
    working_capital = current_assets - current_liabilities
    
    # Leverage
    debt_to_equity = total_debt / shareholders_equity if shareholders_equity > 0 else 0
    debt_to_assets = total_debt / total_assets if total_assets > 0 else 0
    equity_ratio = shareholders_equity / total_assets if total_assets > 0 else 0
    interest_coverage = operating_income / interest_expense if interest_expense > 0 else 0
    
    # Efficiency
    asset_turnover = revenue / avg_total_assets if avg_total_assets > 0 else 0
    inventory_turnover = cogs / avg_inventory if avg_inventory > 0 else 0
    dio = 365 / inventory_turnover if inventory_turnover > 0 else 0
    receivables_turnover = revenue / avg_ar if avg_ar > 0 else 0
    dso = 365 / receivables_turnover if receivables_turnover > 0 else 0
    payables_turnover = cogs / avg_ap if avg_ap > 0 else 0
    dpo = 365 / payables_turnover if payables_turnover > 0 else 0
    ccc = dio + dso - dpo
    
    # Market metrics
    eps = net_income / shares_outstanding if shares_outstanding > 0 else 0
    pe_ratio = market_price_per_share / eps if eps > 0 else 0
    book_value_per_share = shareholders_equity / shares_outstanding if shares_outstanding > 0 else 0
    pb_ratio = market_price_per_share / book_value_per_share if book_value_per_share > 0 else 0
    market_cap = market_price_per_share * shares_outstanding
    enterprise_value = market_cap + total_debt - cash
    ev_ebitda = enterprise_value / ebitda if ebitda > 0 else 0
    ev_sales = enterprise_value / revenue if revenue > 0 else 0
    
    # Cash flow
    fcff = operating_cash_flow - capex
    fcfe = net_income + depreciation - capex - working_capital
    ocf_margin = (operating_cash_flow / revenue * 100) if revenue > 0 else 0
    capex_to_sales = (capex / revenue * 100) if revenue > 0 else 0
    
    # Growth
    revenue_growth = ((revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
    net_income_growth = ((net_income - prev_net_income) / prev_net_income * 100) if prev_net_income > 0 else 0
    
    # EVA
    wacc = 0.08
    nopat_for_eva = operating_income * (1 - tax_rate)
    eva = nopat_for_eva - (wacc * avg_invested_capital)
    
    # Store all metrics
    metrics = {
        'gross_profit': gross_profit,
        'gross_margin': gross_margin,
        'operating_income': operating_income,
        'operating_margin': operating_margin,
        'ebitda': ebitda,
        'ebitda_margin': ebitda_margin,
        'net_income': net_income,
        'net_margin': net_margin,
        'avg_total_assets': avg_total_assets,
        'avg_equity': avg_equity,
        'roa': roa,
        'roe': roe,
        'roic': roic,
        'current_assets': current_assets,
        'current_ratio': current_ratio,
        'quick_ratio': quick_ratio,
        'cash_ratio': cash_ratio,
        'working_capital': working_capital,
        'total_debt': total_debt,
        'debt_to_equity': debt_to_equity,
        'debt_to_assets': debt_to_assets,
        'equity_ratio': equity_ratio,
        'interest_coverage': interest_coverage,
        'asset_turnover': asset_turnover,
        'inventory_turnover': inventory_turnover,
        'receivables_turnover': receivables_turnover,
        'dio': dio,
        'dso': dso,
        'dpo': dpo,
        'ccc': ccc,
        'eps': eps,
        'pe_ratio': pe_ratio,
        'pb_ratio': pb_ratio,
        'book_value_per_share': book_value_per_share,
        'market_cap': market_cap,
        'enterprise_value': enterprise_value,
        'ev_ebitda': ev_ebitda,
        'ev_sales': ev_sales,
        'fcff': fcff,
        'fcfe': fcfe,
        'ocf_margin': ocf_margin,
        'capex_to_sales': capex_to_sales,
        'revenue_growth': revenue_growth,
        'net_income_growth': net_income_growth,
        'eva': eva
    }
    
    st.session_state.calculated_metrics = metrics
    return metrics

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'financial_data' not in st.session_state:
    st.session_state.financial_data = {}
if 'analysis_started' not in st.session_state:
    st.session_state.analysis_started = False
if 'calculated_metrics' not in st.session_state:
    st.session_state.calculated_metrics = {}

# Asosiy sarlavha
st.markdown('<h1 class="main-header">📊 Moliyaviy tahlil tizimi by SaidakbaR</h1>', unsafe_allow_html=True)

# Yon panel
with st.sidebar:
    st.header("📋 Kompaniya Ma'lumotlari")
    company_name = st.text_input("Kompaniya nomi", "Mening Kompaniyam")
    fiscal_year = st.number_input("Moliyaviy yil", min_value=2000, max_value=2030, value=2024)
    fiscal_quarter = st.selectbox("Chorak", ["Yillik", "Q1", "Q2", "Q3", "Q4"])
    currency = st.selectbox("Valyuta", ["UZS", "USD", "EUR"])
    
    st.divider()
    st.subheader("📊 Tahlil Turi")
    analysis_type = st.radio(
        "Tahlil turini tanlang:",
        ["To'liq Tahlil", "Rentabellik", "Likvidlik", "Qarz Yuklama", "Samaradorlik", "Bozor Ko'rsatkichlari", "Pul Oqimi"]
    )

# Asosiy tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 Ma'lumotlarni Kiritish", "📊 Tahlil Natijalari", "📈 Grafiklar Tahlili", "📄 Hisobot", "🤖 AI Maslahatchi"])

with tab1:
    st.header("Moliyaviy Ma'lumotlarni Kiriting")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💰 Malumotlarni kiriting")
        revenue = st.number_input("Tushum (Savdo hajmi)", value=1000000.0, format="%.2f", key="revenue_input")
        cogs = st.number_input("Sotilgan mahsulot tannarxi", value=600000.0, format="%.2f", key="cogs_input")
        operating_expenses = st.number_input("Operatsion xarajatlar", value=200000.0, format="%.2f", key="opex_input")
        depreciation = st.number_input("Amortizatsiya", value=50000.0, format="%.2f", key="depreciation_input")
        interest_expense = st.number_input("Foiz xarajatlari", value=20000.0, format="%.2f", key="interest_input")
        tax_expense = st.number_input("Soliq xarajatlari", value=26000.0, format="%.2f", key="tax_input")
        
        st.subheader("💵 Pul Oqimi")
        operating_cash_flow = st.number_input("Operatsion pul oqimi", value=180000.0, format="%.2f", key="ocf_input")
        capex = st.number_input("Kapital xarajatlar", value=80000.0, format="%.2f", key="capex_input")
        dividends_paid = st.number_input("To'langan dividendlar", value=20000.0, format="%.2f", key="div_input")
    
    with col2:
        st.subheader("🏦 Balans")
        
        st.markdown("**Aktivlar**")
        cash = st.number_input("Naqd pul", value=150000.0, format="%.2f", key="cash_input")
        marketable_securities = st.number_input("Qisqa muddatli investitsiyalar", value=50000.0, format="%.2f", key="securities_input")
        accounts_receivable = st.number_input("Debitorlik qarz", value=120000.0, format="%.2f", key="ar_input")
        inventory = st.number_input("Tovar-moddiy zaxiralar", value=180000.0, format="%.2f", key="inventory_input")
        other_current_assets = st.number_input("Boshqa joriy aktivlar", value=30000.0, format="%.2f", key="other_assets_input")
        total_assets = st.number_input("Jami aktivlar", value=1500000.0, format="%.2f", key="total_assets_input")
        
        st.markdown("**Majburiyatlar**")
        accounts_payable = st.number_input("Kreditorlik qarz", value=100000.0, format="%.2f", key="ap_input")
        short_term_debt = st.number_input("Qisqa muddatli qarz", value=80000.0, format="%.2f", key="std_input")
        current_liabilities = st.number_input("Joriy majburiyatlar", value=250000.0, format="%.2f", key="cl_input")
        long_term_debt = st.number_input("Uzoq muddatli qarz", value=400000.0, format="%.2f", key="ltd_input")
        shareholders_equity = st.number_input("Xususiy kapital", value=850000.0, format="%.2f", key="equity_input")
        
        st.markdown("**Bozor Ma'lumotlari**")
        shares_outstanding = st.number_input("Aktsiyalar soni", value=100000.0, format="%.2f", key="shares_input")
        market_price_per_share = st.number_input("Aktsiya narxi", value=15.0, format="%.2f", key="price_input")
    
    with st.expander("📅 O'tgan Davr Ma'lumotlari"):
        col3, col4 = st.columns(2)
        with col3:
            prev_revenue = st.number_input("O'tgan davr tushumi", value=900000.0, format="%.2f", key="prev_rev_input")
            prev_net_income = st.number_input("O'tgan davr sof foydasi", value=80000.0, format="%.2f", key="prev_ni_input")
            prev_total_assets = st.number_input("O'tgan davr jami aktivlari", value=1400000.0, format="%.2f", key="prev_assets_input")
        with col4:
            prev_equity = st.number_input("O'tgan davr kapitali", value=800000.0, format="%.2f", key="prev_equity_input")
            prev_inventory = st.number_input("O'tgan davr zaxiralari", value=170000.0, format="%.2f", key="prev_inv_input")
            prev_ar = st.number_input("O'tgan davr debitor qarzi", value=110000.0, format="%.2f", key="prev_ar_input")
            prev_ap = st.number_input("O'tgan davr kreditor qarzi", value=95000.0, format="%.2f", key="prev_ap_input")
    
    # Store data
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
    
    st.divider()
    
    col_start1, col_start2, col_start3 = st.columns([1, 2, 1])
    with col_start2:
        if st.button("🚀 TAHLILNI BOSHLASH", key="start_analysis_btn", use_container_width=True):
            with st.spinner("Tahlil qilinmoqda..."):
                calculate_financial_metrics(st.session_state.financial_data)
                st.session_state.analysis_started = True
                st.success("✅ Tahlil tugallandi! Boshqa varaqlarni ko'ring.")
                st.balloons()

with tab2:
    st.header("📊 Moliyaviy Tahlil Natijalari")
    
    if not st.session_state.analysis_started:
        st.warning("⚠️ Iltimos, avval ma'lumotlarni kiriting va TAHLILNI BOSHLASH tugmasini bosing.")
        st.stop()
    
    metrics = st.session_state.calculated_metrics
    data = st.session_state.financial_data
    
    # Overall Score Section
    st.subheader("🎯 Umumiy Moliyaviy Sifat Balli")
    
    def calculate_score(value, thresholds, reverse=False):
        excellent, good, fair = thresholds
        if reverse:
            if value <= excellent: return 100
            elif value <= good: return 75
            elif value <= fair: return 50
            else: return 25
        else:
            if value >= excellent: return 100
            elif value >= good: return 75
            elif value >= fair: return 50
            else: return 25
    
    # Calculate category scores
    profitability_score = (
        calculate_score(metrics.get('gross_margin', 0), (40, 30, 20)) +
        calculate_score(metrics.get('operating_margin', 0), (20, 15, 10)) +
        calculate_score(metrics.get('net_margin', 0), (15, 10, 5)) +
        calculate_score(metrics.get('roe', 0), (20, 15, 10)) +
        calculate_score(metrics.get('roa', 0), (10, 7, 4))
    ) / 5
    
    liquidity_score = (
        calculate_score(metrics.get('current_ratio', 0), (2.0, 1.5, 1.0)) +
        calculate_score(metrics.get('quick_ratio', 0), (1.5, 1.0, 0.7)) +
        calculate_score(metrics.get('cash_ratio', 0), (0.5, 0.3, 0.1))
    ) / 3
    
    leverage_score = (
        calculate_score(metrics.get('debt_to_equity', 0), (0.5, 1.0, 2.0), reverse=True) +
        calculate_score(metrics.get('debt_to_assets', 0), (0.3, 0.5, 0.7), reverse=True) +
        calculate_score(metrics.get('interest_coverage', 0), (5, 3, 2))
    ) / 3
    
    efficiency_score = (
        calculate_score(metrics.get('asset_turnover', 0), (1.5, 1.0, 0.7)) +
        calculate_score(metrics.get('inventory_turnover', 0), (8, 6, 4)) +
        calculate_score(metrics.get('ccc', 0), (30, 60, 90), reverse=True)
    ) / 3
    
    growth_score = (
        calculate_score(metrics.get('revenue_growth', 0), (15, 10, 5)) +
        calculate_score(metrics.get('net_income_growth', 0), (20, 10, 5))
    ) / 2
    
    cashflow_score = (
        calculate_score(metrics.get('ocf_margin', 0), (20, 15, 10)) +
        (100 if metrics.get('fcff', 0) > 0 else 0)
    ) / 2
    
    overall_score = (profitability_score + liquidity_score + leverage_score + 
                    efficiency_score + growth_score + cashflow_score) / 6
    
    # Display scores
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 15px; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
            <h1 style='margin: 0; font-size: 3rem;'>{overall_score:.0f}</h1>
            <p style='margin: 5px 0; font-size: 1.2rem;'>UMUMIY BALL</p>
            <p style='margin: 0; font-size: 2rem;'>{'🌟' if overall_score >= 80 else '👍' if overall_score >= 60 else '⚠️'}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.metric("Rentabellik", f"{profitability_score:.0f}/100", 
                 delta="A'lo" if profitability_score >= 80 else "Yaxshi" if profitability_score >= 60 else "O'rtacha")
        st.metric("Likvidlik", f"{liquidity_score:.0f}/100",
                 delta="A'lo" if liquidity_score >= 80 else "Yaxshi" if liquidity_score >= 60 else "O'rtacha")
    
    with col3:
        st.metric("Moliyaviy Barqarorlik", f"{leverage_score:.0f}/100",
                 delta="A'lo" if leverage_score >= 80 else "Yaxshi" if leverage_score >= 60 else "O'rtacha")
        st.metric("Samaradorlik", f"{efficiency_score:.0f}/100",
                 delta="A'lo" if efficiency_score >= 80 else "Yaxshi" if efficiency_score >= 60 else "O'rtacha")
    
    with col4:
        st.metric("O'sish", f"{growth_score:.0f}/100",
                 delta="A'lo" if growth_score >= 80 else "Yaxshi" if growth_score >= 60 else "O'rtacha")
        st.metric("Pul Oqimi", f"{cashflow_score:.0f}/100",
                 delta="A'lo" if cashflow_score >= 80 else "Yaxshi" if cashflow_score >= 60 else "O'rtacha")
    
    st.divider()
    
    # Profitability Metrics
    if analysis_type in ["To'liq Tahlil", "Rentabellik"]:
        st.subheader("💰 Rentabellik Ko'rsatkichlari")
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric("Yalpi Foyda", f"{metrics.get('gross_profit', 0):,.0f} {data.get('currency', '')}", 
                   f"{metrics.get('gross_margin', 0):.1f}%")
        col2.metric("Operatsion Foyda", f"{metrics.get('operating_income', 0):,.0f} {data.get('currency', '')}", 
                   f"{metrics.get('operating_margin', 0):.1f}%")
        col3.metric("EBITDA", f"{metrics.get('ebitda', 0):,.0f} {data.get('currency', '')}", 
                   f"{metrics.get('ebitda_margin', 0):.1f}%")
        col4.metric("Sof Foyda", f"{metrics.get('net_income', 0):,.0f} {data.get('currency', '')}", 
                   f"{metrics.get('net_margin', 0):.1f}%")
        
        col5, col6, col7 = st.columns(3)
        col5.metric("ROA (Aktivlar Rentabelligi)", f"{metrics.get('roa', 0):.2f}%")
        col6.metric("ROE (Kapital Rentabelligi)", f"{metrics.get('roe', 0):.2f}%")
        col7.metric("ROIC (Investitsiya Rentabelligi)", f"{metrics.get('roic', 0):.2f}%")
    
    # Liquidity Metrics
    if analysis_type in ["To'liq Tahlil", "Likvidlik"]:
        st.subheader("💧 Likvidlik Ko'rsatkichlari")
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric("Joriy Likvidlik", f"{metrics.get('current_ratio', 0):.2f}")
        col2.metric("Tez Likvidlik", f"{metrics.get('quick_ratio', 0):.2f}")
        col3.metric("Absolut Likvidlik", f"{metrics.get('cash_ratio', 0):.2f}")
        col4.metric("Ishchi Kapital", f"{metrics.get('working_capital', 0):,.0f} {data.get('currency', '')}")
        
        if metrics.get('current_ratio', 0) > 1.5:
            st.success("✅ Likvidlik holati yaxshi")
        elif metrics.get('current_ratio', 0) > 1:
            st.warning("⚠️ Likvidlik qoniqarli, diqqat bilan kuzatish kerak")
        else:
            st.error("❌ Past likvidlik - choralar ko'rish zarur")
    
    # Leverage Metrics
    if analysis_type in ["To'liq Tahlil", "Qarz Yuklama"]:
        st.subheader("⚖️ Qarz Yuklama Ko'rsatkichlari")
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric("Qarz/Kapital", f"{metrics.get('debt_to_equity', 0):.2f}")
        col2.metric("Qarz/Aktivlar", f"{metrics.get('debt_to_assets', 0):.2f}")
        col3.metric("Kapital Nisbati", f"{metrics.get('equity_ratio', 0):.2f}")
        col4.metric("Foiz Qoplash", f"{metrics.get('interest_coverage', 0):.2f}x")
        
        if metrics.get('debt_to_equity', 0) > 2:
            st.warning("⚠️ Yuqori qarz yuklama - qarzni kamaytirish kerak")
        elif metrics.get('debt_to_equity', 0) < 0.5:
            st.success("✅ Konservativ qarz yuklama - kuchli pozitsiya")
    
    # Efficiency Metrics
    if analysis_type in ["To'liq Tahlil", "Samaradorlik"]:
        st.subheader("⚡ Samaradorlik Ko'rsatkichlari")
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric("Aktivlar Aylanmasi", f"{metrics.get('asset_turnover', 0):.2f}")
        col2.metric("Zaxiralar Aylanmasi", f"{metrics.get('inventory_turnover', 0):.2f}")
        col3.metric("Debitor Qarz Aylanmasi", f"{metrics.get('receivables_turnover', 0):.2f}")
        col4.metric("Pul Konversiya Davri", f"{metrics.get('ccc', 0):.0f} kun")
        
        col5, col6, col7 = st.columns(3)
        col5.metric("Zaxirada Saqlash (DIO)", f"{metrics.get('dio', 0):.0f} kun")
        col6.metric("To'lov Olish (DSO)", f"{metrics.get('dso', 0):.0f} kun")
        col7.metric("To'lov Qilish (DPO)", f"{metrics.get('dpo', 0):.0f} kun")
    
    # Market Metrics
    if analysis_type in ["To'liq Tahlil", "Bozor Ko'rsatkichlari"]:
        st.subheader("📈 Bozor Ko'rsatkichlari")
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric("EPS (Aktsiyaga Foyda)", f"{metrics.get('eps', 0):.2f} {data.get('currency', '')}")
        col2.metric("P/E (Narx/Foyda)", f"{metrics.get('pe_ratio', 0):.2f}")
        col3.metric("P/B (Narx/Balans)", f"{metrics.get('pb_ratio', 0):.2f}")
        col4.metric("Bozor Kapitalizatsiyasi", f"{metrics.get('market_cap', 0):,.0f} {data.get('currency', '')}")
        
        col5, col6 = st.columns(2)
        col5.metric("Korxona Qiymati", f"{metrics.get('enterprise_value', 0):,.0f} {data.get('currency', '')}")
        col6.metric("EV/EBITDA", f"{metrics.get('ev_ebitda', 0):.2f}")
    
    # Cash Flow Metrics
    if analysis_type in ["To'liq Tahlil", "Pul Oqimi"]:
        st.subheader("💵 Pul Oqimi Ko'rsatkichlari")
        col1, col2, col3 = st.columns(3)
        
        col1.metric("Erkin Pul Oqimi", f"{metrics.get('fcff', 0):,.0f} {data.get('currency', '')}")
        col2.metric("OCF Marjasi", f"{metrics.get('ocf_margin', 0):.1f}%")
        col3.metric("CapEx/Savdo", f"{metrics.get('capex_to_sales', 0):.1f}%")
        
        if metrics.get('fcff', 0) > 0:
            st.success("✅ Musbat erkin pul oqimi")
        else:
            st.warning("⚠️ Salbiy erkin pul oqimi - kapital taqsimotini ko'rib chiqish kerak")
    
    # Growth Metrics
    if analysis_type == "To'liq Tahlil":
        st.subheader("📊 O'sish Ko'rsatkichlari")
        col1, col2 = st.columns(2)
        
        col1.metric("Tushum O'sishi", f"{metrics.get('revenue_growth', 0):+.1f}%")
        col2.metric("Sof Foyda O'sishi", f"{metrics.get('net_income_growth', 0):+.1f}%")
        
        st.subheader("🔍 DuPont Tahlili (ROE)")
        net_margin = metrics.get('net_margin', 0) / 100
        asset_turnover = metrics.get('asset_turnover', 0)
        total_debt = metrics.get('total_debt', 0)
        shareholders_equity = data.get('shareholders_equity', 1)
        dupont_leverage = (total_debt + shareholders_equity) / shareholders_equity if shareholders_equity > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Sof Marja", f"{metrics.get('net_margin', 0):.2f}%")
        col2.metric("Aktivlar Aylanmasi", f"{asset_turnover:.2f}")
        col3.metric("Moliyaviy Leverage", f"{dupont_leverage:.2f}")
        
        st.info(f"ROE = {metrics.get('net_margin', 0):.2f}% × {asset_turnover:.2f} × {dupont_leverage:.2f} = {metrics.get('roe', 0):.2f}%")

with tab3:
    st.header("📈 Grafiklar Tahlili")
    
    if not st.session_state.analysis_started:
        st.warning("⚠️ Iltimos, avval tahlilni boshlang.")
        st.stop()
    
    metrics = st.session_state.calculated_metrics
    data = st.session_state.financial_data
    
    st.info("📐 **Asosiy Formulalar:** Sof Marja = (Sof Foyda / Tushum) × 100 | ROE = (Sof Foyda / Kapital) × 100 | Joriy Likvidlik = Joriy Aktivlar / Joriy Majburiyatlar")
    
    # Profitability Chart
    st.subheader("💰 Rentabellik Ko'rsatkichlari")
    fig_profitability = go.Figure()
    categories = ['Yalpi Marja', 'Operatsion Marja', 'EBITDA Marja', 'Sof Marja']
    values = [
        metrics.get('gross_margin', 0),
        metrics.get('operating_margin', 0),
        metrics.get('ebitda_margin', 0),
        metrics.get('net_margin', 0)
    ]
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
    
    # Liquidity and Leverage
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💧 Likvidlik Nisbatlari")
        fig_liquidity = go.Figure()
        fig_liquidity.add_trace(go.Bar(
            x=['Joriy Likvidlik', 'Tez Likvidlik', 'Absolut Likvidlik'],
            y=[
                metrics.get('current_ratio', 0),
                metrics.get('quick_ratio', 0),
                metrics.get('cash_ratio', 0)
            ],
            marker_color=['#17becf', '#bcbd22', '#9467bd'],
            text=[
                f"{metrics.get('current_ratio', 0):.2f}",
                f"{metrics.get('quick_ratio', 0):.2f}",
                f"{metrics.get('cash_ratio', 0):.2f}"
            ],
            textposition='auto'
        ))
        fig_liquidity.update_layout(title='Likvidlik Nisbatlari', height=350)
        st.plotly_chart(fig_liquidity, use_container_width=True)
    
    with col2:
        st.subheader("⚖️ Qarz Yuklama Nisbatlari")
        fig_leverage = go.Figure()
        fig_leverage.add_trace(go.Bar(
            x=['Qarz/Kapital', 'Qarz/Aktivlar', 'Kapital Nisbati'],
            y=[
                metrics.get('debt_to_equity', 0),
                metrics.get('debt_to_assets', 0),
                metrics.get('equity_ratio', 0)
            ],
            marker_color=['#e377c2', '#8c564b', '#7f7f7f'],
            text=[
                f"{metrics.get('debt_to_equity', 0):.2f}",
                f"{metrics.get('debt_to_assets', 0):.2f}",
                f"{metrics.get('equity_ratio', 0):.2f}"
            ],
            textposition='auto'
        ))
        fig_leverage.update_layout(title='Qarz Yuklama Nisbatlari', height=350)
        st.plotly_chart(fig_leverage, use_container_width=True)
    
    # Cash Conversion Cycle
    st.subheader("🔄 Pul Konversiya Davri")
    fig_ccc = go.Figure()
    fig_ccc.add_trace(go.Waterfall(
        x=['DIO', 'DSO', 'DPO', 'CCC'],
        y=[
            metrics.get('dio', 0),
            metrics.get('dso', 0),
            -metrics.get('dpo', 0),
            metrics.get('ccc', 0)
        ],
        measure=['relative', 'relative', 'relative', 'total'],
        text=[
            f"{metrics.get('dio', 0):.0f}",
            f"{metrics.get('dso', 0):.0f}",
            f"{-metrics.get('dpo', 0):.0f}",
            f"{metrics.get('ccc', 0):.0f}"
        ],
        textposition='outside',
        connector={"line": {"color": "rgb(63, 63, 63)"}}
    ))
    fig_ccc.update_layout(
        title='Pul Konversiya Davri (Kunlar)',
        yaxis_title='Kunlar',
        height=400
    )
    st.plotly_chart(fig_ccc, use_container_width=True)
    
    # Balance Sheet Composition
    st.subheader("🏦 Balans Tarkibi")
    col1, col2 = st.columns(2)
    
    with col1:
        current_assets = metrics.get('current_assets', 0)
        total_assets = data.get('total_assets', 1)
        fixed_assets = max(0, total_assets - current_assets)
        
        fig_assets = go.Figure(data=[go.Pie(
            labels=['Joriy Aktivlar', 'Asosiy Aktivlar'],
            values=[current_assets, fixed_assets],
            hole=.3
        )])
        fig_assets.update_layout(title='Aktivlar Tarkibi', height=350)
        st.plotly_chart(fig_assets, use_container_width=True)
    
    with col2:
        fig_liabilities = go.Figure(data=[go.Pie(
            labels=['Joriy Majburiyatlar', 'Uzoq Muddatli Qarz', 'Xususiy Kapital'],
            values=[
                data.get('current_liabilities', 0),
                data.get('long_term_debt', 0),
                data.get('shareholders_equity', 0)
            ],
            hole=.3
        )])
        fig_liabilities.update_layout(title='Majburiyatlar va Kapital', height=350)
        st.plotly_chart(fig_liabilities, use_container_width=True)
    
    # Trend Analysis
    st.subheader("📊 Trend Tahlili (3 Yillik)")
    fiscal_year = data.get('fiscal_year', 2024)
    years = [fiscal_year-2, fiscal_year-1, fiscal_year]
    
    revenue = data.get('revenue', 0)
    prev_revenue = data.get('prev_revenue', revenue * 0.9)
    revenue_trend = [prev_revenue * 0.9, prev_revenue, revenue]
    
    net_income = metrics.get('net_income', 0)
    prev_net_income = data.get('prev_net_income', net_income * 0.85)
    profit_trend = [prev_net_income * 0.85, prev_net_income, net_income]
    
    fig_trends = go.Figure()
    
    fig_trends.add_trace(go.Scatter(
        x=years, y=revenue_trend,
        mode='lines+markers',
        name='Tushum',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=10)
    ))
    
    fig_trends.add_trace(go.Scatter(
        x=years, y=profit_trend,
        mode='lines+markers',
        name='Sof Foyda',
        line=dict(color='#2ca02c', width=3),
        marker=dict(size=10)
    ))
    
    fig_trends.update_layout(
        title='Tushum va Foyda Trendi',
        xaxis_title='Yil',
        yaxis_title=f'Qiymat ({data.get("currency", "")})',
        hovermode='x unified',
        height=400
    )
    st.plotly_chart(fig_trends, use_container_width=True)
    
    # Waterfall Income Statement
    st.subheader("💧 Daromad Hisobi (Waterfall)")
    waterfall_data = [
        ('Tushum', revenue, 'relative'),
        ('Tannarx', -data.get('cogs', 0), 'relative'),
        ('Yalpi Foyda', metrics.get('gross_profit', 0), 'total'),
        ('Operatsion Xarajat', -data.get('operating_expenses', 0), 'relative'),
        ('EBIT', metrics.get('operating_income', 0), 'total'),
        ('Foiz', -data.get('interest_expense', 0), 'relative'),
        ('Soliq', -data.get('tax_expense', 0), 'relative'),
        ('Sof Foyda', net_income, 'total')
    ]
    
    fig_waterfall = go.Figure(go.Waterfall(
        name="Daromad Tahlili",
        orientation="v",
        measure=[item[2] for item in waterfall_data],
        x=[item[0] for item in waterfall_data],
        y=[item[1] for item in waterfall_data],
        text=[f"{item[1]:,.0f}" for item in waterfall_data],
        textposition="outside",
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        increasing={"marker": {"color": "#28a745"}},
        decreasing={"marker": {"color": "#dc3545"}},
        totals={"marker": {"color": "#1f77b4"}}
    ))
    
    fig_waterfall.update_layout(
        title="Tushumdan Sof Foydaga",
        showlegend=False,
        height=500,
        yaxis_title=f'Qiymat ({data.get("currency", "")})'
    )
    st.plotly_chart(fig_waterfall, use_container_width=True)
    
    # ROE Components (DuPont Analysis)
    st.subheader("🔍 DuPont ROE Tahlili")
    
    net_margin_val = metrics.get('net_margin', 0) / 100
    asset_turnover_val = metrics.get('asset_turnover', 0)
    total_debt = metrics.get('total_debt', 0)
    shareholders_equity = data.get('shareholders_equity', 1)
    equity_multiplier = (total_debt + shareholders_equity) / shareholders_equity if shareholders_equity > 0 else 1
    
    fig_dupont = go.Figure(data=[
        go.Bar(name='Sof Marja', x=['Komponent'], y=[net_margin_val * 100]),
        go.Bar(name='Aktivlar Aylanmasi', x=['Komponent'], y=[asset_turnover_val * 100]),
        go.Bar(name='Kapital Multiplikatori', x=['Komponent'], y=[equity_multiplier * 100])
    ])
    
    fig_dupont.update_layout(
        title='DuPont ROE Komponentlari',
        yaxis_title='Qiymat',
        barmode='group',
        height=400
    )
    st.plotly_chart(fig_dupont, use_container_width=True)

with tab4:
    st.header("📄 Moliyaviy Hisobot")
    
    if not st.session_state.analysis_started:
        st.warning("⚠️ Iltimos, avval tahlilni boshlang.")
        st.stop()
    
    metrics = st.session_state.calculated_metrics
    data = st.session_state.financial_data
    
    st.subheader(f"📊 {data.get('company_name', 'Kompaniya')}")
    st.write(f"**Moliyaviy Yil:** {data.get('fiscal_year', '')} | **Davr:** {data.get('fiscal_quarter', '')} | **Valyuta:** {data.get('currency', '')}")
    st.write(f"**Hisobot Sanasi:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    st.divider()
    
    # Executive Summary
    st.subheader("📊 Ijroiya Xulosasi")
    
    summary_data = {
        'Ko\'rsatkich': [
            'Tushum', 'Sof Foyda', 'EBITDA', 'ROE', 'ROA', 
            'Joriy Likvidlik', 'Qarz/Kapital', 'Erkin Pul Oqimi'
        ],
        'Qiymat': [
            f"{data.get('revenue', 0):,.0f} {data.get('currency', '')}",
            f"{metrics.get('net_income', 0):,.0f} {data.get('currency', '')}",
            f"{metrics.get('ebitda', 0):,.0f} {data.get('currency', '')}",
            f"{metrics.get('roe', 0):.2f}%",
            f"{metrics.get('roa', 0):.2f}%",
            f"{metrics.get('current_ratio', 0):.2f}",
            f"{metrics.get('debt_to_equity', 0):.2f}",
            f"{metrics.get('fcff', 0):,.0f} {data.get('currency', '')}"
        ],
        'Holat': [
            '✅ Yaxshi' if data.get('revenue', 0) > data.get('prev_revenue', 0) else '⚠️ Ko\'rib chiqish',
            '✅ Yaxshi' if metrics.get('net_income', 0) > 0 else '❌ Yomon',
            '✅ Yaxshi' if metrics.get('ebitda', 0) > 0 else '❌ Yomon',
            '✅ Yaxshi' if metrics.get('roe', 0) > 15 else '⚠️ O\'rtacha' if metrics.get('roe', 0) > 10 else '❌ Yomon',
            '✅ Yaxshi' if metrics.get('roa', 0) > 5 else '⚠️ O\'rtacha' if metrics.get('roa', 0) > 3 else '❌ Yomon',
            '✅ Yaxshi' if metrics.get('current_ratio', 0) > 1.5 else '⚠️ O\'rtacha' if metrics.get('current_ratio', 0) > 1 else '❌ Yomon',
            '✅ Yaxshi' if metrics.get('debt_to_equity', 0) < 1 else '⚠️ O\'rtacha' if metrics.get('debt_to_equity', 0) < 2 else '❌ Yuqori',
            '✅ Yaxshi' if metrics.get('fcff', 0) > 0 else '❌ Yomon'
        ]
    }
    
    st.dataframe(pd.DataFrame(summary_data), hide_index=True, use_container_width=True)
    
    st.divider()
    
    # Detailed Metrics Report
    st.subheader("📋 Batafsil Moliyaviy Ko'rsatkichlar")
    
    # Create comprehensive report
    report_data = []
    
    # Profitability
    report_data.extend([
        ('Rentabellik', 'Yalpi Marja', f'{metrics.get("gross_margin", 0):.2f}%', 'Yaxshi: > 40%'),
        ('Rentabellik', 'Operatsion Marja', f'{metrics.get("operating_margin", 0):.2f}%', 'Yaxshi: > 15%'),
        ('Rentabellik', 'EBITDA Marja', f'{metrics.get("ebitda_margin", 0):.2f}%', 'Yaxshi: > 20%'),
        ('Rentabellik', 'Sof Marja', f'{metrics.get("net_margin", 0):.2f}%', 'Yaxshi: > 10%'),
        ('Rentabellik', 'ROA', f'{metrics.get("roa", 0):.2f}%', 'Yaxshi: > 5%'),
        ('Rentabellik', 'ROE', f'{metrics.get("roe", 0):.2f}%', 'Yaxshi: > 15%'),
        ('Rentabellik', 'ROIC', f'{metrics.get("roic", 0):.2f}%', 'Yaxshi: > 10%'),
    ])
    
    # Liquidity
    report_data.extend([
        ('Likvidlik', 'Joriy Likvidlik', f'{metrics.get("current_ratio", 0):.2f}', 'Yaxshi: 1.5-3.0'),
        ('Likvidlik', 'Tez Likvidlik', f'{metrics.get("quick_ratio", 0):.2f}', 'Yaxshi: 1.0-2.0'),
        ('Likvidlik', 'Absolut Likvidlik', f'{metrics.get("cash_ratio", 0):.2f}', 'Yaxshi: 0.2-0.5'),
        ('Likvidlik', 'Ishchi Kapital', f'{metrics.get("working_capital", 0):,.0f} {data.get("currency", "")}', 'Musbat bo\'lishi kerak'),
    ])
    
    # Leverage
    report_data.extend([
        ('Qarz Yuklama', 'Qarz/Kapital', f'{metrics.get("debt_to_equity", 0):.2f}', 'Yaxshi: < 1.0'),
        ('Qarz Yuklama', 'Qarz/Aktivlar', f'{metrics.get("debt_to_assets", 0):.2f}', 'Yaxshi: < 0.5'),
        ('Qarz Yuklama', 'Foiz Qoplash', f'{metrics.get("interest_coverage", 0):.2f}x', 'Yaxshi: > 3.0'),
    ])
    
    # Efficiency
    report_data.extend([
        ('Samaradorlik', 'Aktivlar Aylanmasi', f'{metrics.get("asset_turnover", 0):.2f}', 'Yuqori yaxshi'),
        ('Samaradorlik', 'Zaxiralar Aylanmasi', f'{metrics.get("inventory_turnover", 0):.2f}', 'Yuqori yaxshi'),
        ('Samaradorlik', 'DIO', f'{metrics.get("dio", 0):.0f} kun', 'Past yaxshi'),
        ('Samaradorlik', 'DSO', f'{metrics.get("dso", 0):.0f} kun', 'Past yaxshi'),
        ('Samaradorlik', 'DPO', f'{metrics.get("dpo", 0):.0f} kun', 'Yuqori yaxshi'),
        ('Samaradorlik', 'CCC', f'{metrics.get("ccc", 0):.0f} kun', 'Past yaxshi'),
    ])
    
    # Market
    report_data.extend([
        ('Bozor', 'EPS', f'{metrics.get("eps", 0):.2f} {data.get("currency", "")}', 'Yuqori yaxshi'),
        ('Bozor', 'P/E', f'{metrics.get("pe_ratio", 0):.2f}', 'O\'rtacha: 15-25'),
        ('Bozor', 'P/B', f'{metrics.get("pb_ratio", 0):.2f}', 'O\'rtacha: 1.0-3.0'),
        ('Bozor', 'Bozor Kap.', f'{metrics.get("market_cap", 0):,.0f} {data.get("currency", "")}', 'Kompaniya qiymati'),
        ('Bozor', 'EV/EBITDA', f'{metrics.get("ev_ebitda", 0):.2f}', 'O\'rtacha: 8-15'),
    ])
    
    # Cash Flow
    report_data.extend([
        ('Pul Oqimi', 'Erkin Pul Oqimi', f'{metrics.get("fcff", 0):,.0f} {data.get("currency", "")}', 'Musbat bo\'lishi kerak'),
        ('Pul Oqimi', 'OCF Marja', f'{metrics.get("ocf_margin", 0):.2f}%', 'Yaxshi: > 15%'),
        ('Pul Oqimi', 'CapEx/Savdo', f'{metrics.get("capex_to_sales", 0):.2f}%', 'Sanoatga bog\'liq'),
    ])
    
    # Growth
    report_data.extend([
        ('O\'sish', 'Tushum O\'sishi', f'{metrics.get("revenue_growth", 0):+.2f}%', 'Musbat yaxshi'),
        ('O\'sish', 'Sof Foyda O\'sishi', f'{metrics.get("net_income_growth", 0):+.2f}%', 'Musbat yaxshi'),
    ])
    
    report_df = pd.DataFrame(report_data, columns=['Kategoriya', 'Ko\'rsatkich', 'Qiymat', 'Mezon'])
    st.dataframe(report_df, hide_index=True, use_container_width=True)
    
    st.divider()
    
    # Recommendations
    st.subheader("💡 Asosiy Tavsiyalar")
    
    recommendations = []
    
    net_margin = metrics.get('net_margin', 0)
    if net_margin < 5:
        recommendations.append("**⚠️ Past Sof Marja** - Xarajatlarni kamaytirish va operatsion samaradorlikni oshirish kerak")
    elif net_margin > 15:
        recommendations.append("**✅ A'lo Sof Marja** - Kompaniya kuchli rentabellikni ko'rsatmoqda")
    
    current_ratio = metrics.get('current_ratio', 0)
    if current_ratio < 1:
        recommendations.append("**❌ Likvidlik Xavfi** - Likvidlik holatini yaxshilash uchun zudlik bilan choralar ko'rish kerak")
    elif current_ratio > 3:
        recommendations.append("**⚠️ Ortiqcha Likvidlik** - Ishchi kapitalning optimal taqsimlanishini ko'rib chiqing")
    else:
        recommendations.append("**✅ Sog'lom Likvidlik** - Joriy likvidlik holati yetarli")
    
    debt_to_equity = metrics.get('debt_to_equity', 0)
    if debt_to_equity > 2:
        recommendations.append("**⚠️ Yuqori Qarz Yuklama** - Moliyaviy xavfni kamaytirish uchun qarzni qaytarish strategiyasini ko'rib chiqing")
    elif debt_to_equity < 0.5:
        recommendations.append("**✅ Konservativ Kapital Tuzilmasi** - Kuchli moliyaviy barqarorlik")
    
    roe = metrics.get('roe', 0)
    if roe > 15:
        recommendations.append("**✅ Kuchli ROE** - Kompaniya aktsionerlar kapitalidan samarali foydalanmoqda")
    elif roe < 8:
        recommendations.append("**⚠️ Past ROE** - Kapital samaradorligini oshirishga e'tibor bering")
    
    fcff = metrics.get('fcff', 0)
    if fcff < 0:
        recommendations.append("**❌ Salbiy Erkin Pul Oqimi** - Kapital taqsimoti va operatsion samaradorlikni ko'rib chiqing")
    else:
        recommendations.append("**✅ Musbat Erkin Pul Oqimi** - Kompaniya yetarli pul ishlab chiqarmoqda")
    
    for rec in recommendations:
        st.write(rec)
    
    st.divider()
    
    # Download Options
    st.subheader("📥 Hisobotni Yuklab Olish")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        csv = report_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📊 CSV Yuklab Olish",
            data=csv,
            file_name=f"{data.get('company_name', 'kompaniya')}_hisobot_{data.get('fiscal_year', '')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        # Create Excel file
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            report_df.to_excel(writer, sheet_name='Moliyaviy Hisobot', index=False)
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Xulosa', index=False)
        excel_data = output.getvalue()
        
        st.download_button(
            label="📈 Excel Yuklab Olish",
            data=excel_data,
            file_name=f"{data.get('company_name', 'kompaniya')}_hisobot_{data.get('fiscal_year', '')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with col3:
        st.button("📄 PDF Yaratish", use_container_width=True, help="PDF yaratish funksiyasi tez orada")

with tab5:
    st.header("🤖 AI Financial Advisor")
    
    if not st.session_state.analysis_started:
        st.warning("⚠️ Please start analysis first.")
        st.stop()
    
    metrics = st.session_state.calculated_metrics
    data = st.session_state.financial_data
    
    st.markdown("### 💡 Strategic Recommendations")
    
    # Generate recommendations based on metrics
    def generate_recommendations():
        recs = []
        
        net_margin = metrics.get('net_margin', 0)
        roe = metrics.get('roe', 0)
        current_ratio = metrics.get('current_ratio', 0)
        debt_to_equity = metrics.get('debt_to_equity', 0)
        fcff = metrics.get('fcff', 0)
        revenue_growth = metrics.get('revenue_growth', 0)
        
        # Profitability
        if net_margin < 5:
            recs.append({
                'category': '💰 Cost Reduction Strategy',
                'priority': 'HIGH',
                'strategy': 'Improve profitability through cost optimization',
                'actions': [
                    'Conduct comprehensive expense analysis across all departments',
                    'Identify and eliminate operational inefficiencies',
                    'Negotiate better terms with suppliers',
                    'Automate repetitive processes',
                    f'Target: Increase net margin to 8-12% within 12 months'
                ]
            })
        elif net_margin > 15:
            recs.append({
                'category': '🚀 Growth Strategy',
                'priority': 'HIGH',
                'strategy': 'Leverage strong profitability for expansion',
                'actions': [
                    'Invest in R&D for new product development',
                    'Explore new market opportunities',
                    'Strengthen marketing and sales efforts',
                    'Consider strategic partnerships or acquisitions',
                    'Reinvest profits into business growth'
                ]
            })
        
        # Liquidity
        if current_ratio < 1.5:
            recs.append({
                'category': '💧 Liquidity Improvement',
                'priority': 'CRITICAL',
                'strategy': 'Strengthen liquidity position urgently',
                'actions': [
                    'Accelerate accounts receivable collection',
                    'Reduce inventory levels by 10-15%',
                    'Negotiate extended payment terms with suppliers',
                    'Consider short-term financing options',
                    'Target: Achieve current ratio of 1.8+ within 6 months'
                ]
            })
        
        # Leverage
        if debt_to_equity > 1.5:
            recs.append({
                'category': '⚖️ Debt Reduction Plan',
                'priority': 'HIGH',
                'strategy': 'Reduce financial risk through deleveraging',
                'actions': [
                    f'Debt reduction plan: Decrease D/E from {debt_to_equity:.2f} to 1.0 (24 months)',
                    'Prioritize paying off high-interest debt first',
                    'Consider refinancing at lower rates',
                    'Allocate OCF to debt repayment',
                    'Review asset sales if necessary'
                ]
            })
        
        # Cash Flow
        if fcff < 0:
            recs.append({
                'category': '💵 Cash Flow Enhancement',
                'priority': 'HIGH',
                'strategy': 'Improve cash generation capability',
                'actions': [
                    'Review and defer non-essential capital expenditures',
                    'Increase operating cash flow by 15-20%',
                    'Optimize working capital management',
                    'Focus on cash-generating projects',
                    'Target: Achieve positive FCF within 12 months'
                ]
            })
        
        # Growth
        if revenue_growth < 0:
            recs.append({
                'category': '📈 Revenue Recovery',
                'priority': 'HIGH',
                'strategy': 'Address declining revenue trends',
                'actions': [
                    'Analyze market trends and competitive position',
                    'Develop customer retention program',
                    'Launch new products/services',
                    'Increase market share through targeted marketing',
                    'Explore new customer segments or geographies'
                ]
            })
        
        # Strategic Vision
        recs.append({
            'category': '🎯 Strategic Vision (3-Year Plan)',
            'priority': 'CRITICAL',
            'strategy': 'Comprehensive growth roadmap and strategic planning',
            'actions': [
                f'Year 1: Stabilize core business and improve profitability (Target: {min(net_margin + 2, 20):.0f}% net margin)',
                f'Year 2: Invest in growth initiatives (Target: {data.get("revenue", 0) * 1.25:,.0f} revenue)',
                f'Year 3: Scale operations and market expansion (Target: {data.get("revenue", 0) * 1.60:,.0f} revenue)',
                'Establish quarterly KPIs and milestones',
                'Develop contingency plans for market uncertainties'
            ]
        })
        
        return recs
    
    recommendations = generate_recommendations()
    
    # Display recommendations
    for rec in recommendations:
        with st.expander(f"{rec['category']} - Priority: {rec['priority']}", expanded=True):
            st.markdown(f"**Strategy:** {rec['strategy']}")
            st.markdown("**Action Items:**")
            for action in rec['actions']:
                st.markdown(f"• {action}")
    
    st.divider()
    
    # AI Advisor Section
    st.markdown("### 🤖 AI-Powered Deep Analysis")
    
    st.info("""
    **Using OpenRouter AI** to provide intelligent financial insights based on your data.
    The AI will analyze your metrics and provide personalized recommendations.
    """)
    
    if st.button("🔍 AI dan maslahat oling", key="ai_advisor_button", use_container_width=True):
        with st.spinner("🤖 AI is analyzing your financial data..."):
            
            # Prepare context IN UZBEK
            ai_context = f"""
Siz Moliyaviy Tahlil bo'yicha Mutaxassissiz. Quyida kompaniyaning moliyaviy ma'lumotlari berilgan.
Iltimos, barcha javoblarni faqat O'ZBEK TILIDA bering.

**ASOSIY MA'LUMOTLAR:**
- Kompaniya: {data.get('company_name', 'Noma\'lum')}
- Moliyaviy Yil: {data.get('fiscal_year', 'N/A')}
- Valyuta: {data.get('currency', 'USD')}

**DAROMAD VA FOYDALAR:**
- Umumiy Daromad (Tushum): {data.get('revenue', 0):,.0f} {data.get('currency', 'USD')}
- Sof Foyda: {metrics.get('net_income', 0):,.0f} {data.get('currency', 'USD')}
- Sof Marja: {metrics.get('net_margin', 0):.2f}%
- EBITDA: {metrics.get('ebitda', 0):,.0f} {data.get('currency', 'USD')}

**RENTABELLIK:**
- ROE (Kapital Rentabelligi): {metrics.get('roe', 0):.2f}%
- ROA (Aktivlar Rentabelligi): {metrics.get('roa', 0):.2f}%

**LIKVIDLIK VA MOLIYAVIY BARQARORLIK:**
- Joriy Likvidlik Nisbati: {metrics.get('current_ratio', 0):.2f}
- Qarz/Kapital Nisbati: {metrics.get('debt_to_equity', 0):.2f}

**PUL OQIMI:**
- Operatsion Pul Oqimi: {data.get('operating_cash_flow', 0):,.0f} {data.get('currency', 'USD')}
- Erkin Pul Oqimi (FCFF): {metrics.get('fcff', 0):,.0f} {data.get('currency', 'USD')}

**O'SISH:**
- Tushum O'sishi: {metrics.get('revenue_growth', 0):.2f}%

MUHIM: Barcha javoblaringizni faqat O'ZBEK TILIDA yozing!

Iltimos, quyidagi bo'limlar bo'yicha batafsil tahlil va maslahatlar bering (O'zbek tilida):

1. HOZIRGI MOLIYAVIY HOLAT: Kompaniyaning asosiy kuchli va zaif tomonlarini tahlil qiling
2. ASOSIY MUAMMOLAR: Agar muammolar bo'lsa, ularni aniqlang va hal qilish yo'llarini tavsiya qiling
3. STRATEGIK TAVSIYALAR: Kompaniyaning o'sishi va rentabelligini oshirish uchun aniq tavsiyalar bering
4. MOLIYAVIY MAQSADLAR: 12, 24 va 36 oylik maqsadlarni belgilang
5. XAVF FAKTORLARI: Moliyaviy holat bilan bog'liq asosiy xavflarni aniqlang

Javobingiz aniq, konkret va amaliy bo'lishi kerak. O'ZBEK TILIDA yozing!
"""
            
            ai_response = call_openrouter_llm(ai_context, max_tokens=3000)
            
            if ai_response:
                st.markdown("#### 🤖 AI Analysis & Recommendations:")
                st.markdown(ai_response)
                
                # Save to session state
                st.session_state.ai_advice = ai_response
                
                st.success("✅ AI analysis complete!")
            else:
                st.error("❌ Unable to connect to AI advisor. Please check your OpenRouter API key configuration.")
    
    # Display saved advice
    if "ai_advice" in st.session_state and st.session_state.ai_advice:
        with st.expander("📝 View Previous AI Analysis", expanded=False):
            st.markdown(st.session_state.ai_advice)
    
    st.divider()
    
    # Financial Health Summary
    st.markdown("### 📊 Financial Health Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ✅ Strengths")
        strengths = []
        
        if metrics.get('net_margin', 0) > 15:
            strengths.append("• Excellent profitability indicators")
        if metrics.get('roe', 0) > 15:
            strengths.append("• High return on equity")
        if 1.5 <= metrics.get('current_ratio', 0) <= 3:
            strengths.append("• Optimal liquidity position")
        if metrics.get('debt_to_equity', 0) < 1:
            strengths.append("• Low leverage - strong financial stability")
        if metrics.get('fcff', 0) > 0:
            strengths.append("• Positive free cash flow")
        if metrics.get('revenue_growth', 0) > 10:
            strengths.append("• Strong revenue growth")
        
        if strengths:
            for strength in strengths:
                st.markdown(strength)
        else:
            st.markdown("*No major strengths identified*")
    
    with col2:
        st.markdown("#### ⚠️ Areas for Improvement")
        weaknesses = []
        
        if metrics.get('net_margin', 0) < 5:
            weaknesses.append("• Low net margin - cost reduction needed")
        if metrics.get('roe', 0) < 10:
            weaknesses.append("• Low ROE - improve capital efficiency")
        if metrics.get('current_ratio', 0) < 1:
            weaknesses.append("• Liquidity risk - improve short-term position")
        if metrics.get('debt_to_equity', 0) > 2:
            weaknesses.append("• High leverage - debt reduction plan required")
        if metrics.get('fcff', 0) < 0:
            weaknesses.append("• Negative cash flow - improve operations")
        if metrics.get('revenue_growth', 0) < 0:
            weaknesses.append("• Revenue decline - market strategy review needed")
        
        if weaknesses:
            for weakness in weaknesses:
                st.markdown(weakness)
        else:
            st.markdown("*No major weaknesses identified*")
    
    st.divider()
    
    # Overall Assessment
    st.markdown("### 🎯 Overall Assessment")
    
    total_issues = len([w for w in [
        metrics.get('net_margin', 0) < 5,
        metrics.get('roe', 0) < 10,
        metrics.get('current_ratio', 0) < 1,
        metrics.get('debt_to_equity', 0) > 2,
        metrics.get('fcff', 0) < 0,
        metrics.get('revenue_growth', 0) < 0
    ] if w])
    
    if total_issues == 0:
        st.success("🌟 **Excellent Position:** Your company is in strong financial health. Continue current strategy and focus on sustainable growth.")
    elif total_issues <= 2:
        st.info("👍 **Good Position:** Financial metrics are satisfactory. Implement recommendations to further strengthen position.")
    elif total_issues <= 4:
        st.warning("⚠️ **Moderate Issues:** Several areas need attention. Prioritize HIGH priority strategies from recommendations above.")
    else:
        st.error("🔴 **Critical Issues:** Multiple serious problems detected. Immediate action required on CRITICAL priority items.")

st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>Financial Analysis System v1.0 | © 2024</p>
</div>
<<<<<<< HEAD
""", unsafe_allow_html=True)
=======
""", unsafe_allow_html=True)
>>>>>>> 86e4a52 (uzbek version)
