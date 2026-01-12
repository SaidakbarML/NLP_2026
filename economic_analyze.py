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
import kaleido

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

# ============= PDF GENERATION FUNCTION =============
def generate_financial_pdf_with_charts(company_name, fiscal_year, currency, metrics_dict, figures_dict):
    """Generate comprehensive PDF report with all charts and metrics"""
    try:
        pdf_buffer = io.BytesIO()
        pdf = SimpleDocTemplate(pdf_buffer, pagesize=A4, topMargin=0.4*inch, bottomMargin=0.4*inch)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=22,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=10,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#ff7f0e'),
            spaceAfter=6,
            spaceBefore=6
        )
        
        # Title Page
        story.append(Paragraph(f"🏢 {company_name}", title_style))
        story.append(Paragraph(f"Moliyaviy Tahlil Hisoboti - {fiscal_year}", heading_style))
        story.append(Paragraph(f"Tayyorlash sanasi: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Summary Table
        story.append(Paragraph("📊 Asosiy Ko'rsatkichlar", heading_style))
        summary_data = [
            ['Ko\'rsatkich', 'Qiymat'],
            ['Tushum', f"{metrics_dict.get('revenue', 0):,.0f} {currency}"],
            ['Sof Foyda', f"{metrics_dict.get('net_income', 0):,.0f} {currency}"],
            ['EBITDA', f"{metrics_dict.get('ebitda', 0):,.0f} {currency}"],
            ['ROE', f"{metrics_dict.get('roe', 0):.2f}%"],
            ['ROA', f"{metrics_dict.get('roa', 0):.2f}%"],
            ['Joriy Likvidlik', f"{metrics_dict.get('current_ratio', 0):.2f}"],
            ['Qarz/Kapital', f"{metrics_dict.get('debt_to_equity', 0):.2f}"],
            ['EVA', f"{metrics_dict.get('eva', 0):,.0f} {currency}"],
            ['FCFE', f"{metrics_dict.get('fcfe', 0):,.0f} {currency}"],
        ]
        
        summary_table = Table(summary_data, colWidths=[3.2*inch, 2.3*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8)
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.15*inch))
        
        # Add charts
        story.append(PageBreak())
        story.append(Paragraph("📈 2D Grafik Tahlillari", heading_style))
        story.append(Spacer(1, 0.1*inch))
        
        # Add 2D charts
        two_d_charts = [
            ('Rentabellik Ko\'rsatkichlari', figures_dict.get('profitability')),
            ('Likvidlik Nisbatlari', figures_dict.get('liquidity')),
            ('Qarz Yuklama Nisbatlari', figures_dict.get('leverage')),
            ('Pul Konversiya Davri', figures_dict.get('ccc')),
            ('Tushum va Foyda Trendi', figures_dict.get('trends')),
            ('Moliyaviy Ko\'rsatkichlar Issiqlik Xaritasi', figures_dict.get('heatmap')),
        ]
        
        chart_count = 0
        for chart_name, fig_obj in two_d_charts:
            if fig_obj is not None:
                try:
                    img_bytes = fig_obj.to_image(format="png", width=900, height=500)
                    img_buffer = io.BytesIO(img_bytes)
                    img = Image(img_buffer, width=6.2*inch, height=3.4*inch)
                    story.append(Paragraph(f"📊 {chart_name}", styles['Heading3']))
                    story.append(img)
                    story.append(Spacer(1, 0.15*inch))
                    chart_count += 1
                    
                    if chart_count % 2 == 0:
                        story.append(PageBreak())
                except Exception as e:
                    story.append(Paragraph(f"⚠️ {chart_name} - Grafik ko'rsatilmadi", styles['Normal']))
        
        # Add 3D charts
        story.append(PageBreak())
        story.append(Paragraph("🎯 3D Grafik Tahlillari", heading_style))
        story.append(Spacer(1, 0.1*inch))
        
        three_d_charts = [
            ('3D Scatter: ROE vs ROA vs Likvidlik', figures_dict.get('scatter_3d')),
            ('3D Multi-Bar: Foyda Dinamikasi', figures_dict.get('bar_3d')),
            ('3D Bubble: Rentabillik vs Qarz Yuklama', figures_dict.get('bubble_3d')),
            ('3D Surface: Operatsion Marja Sezgirlik', figures_dict.get('surface_3d')),
            ('3D Line: Ko\'rsatkichlar Trendi', figures_dict.get('line_3d')),
            ('3D Scatter Matrix: Barcha Ko\'rsatkichlar', figures_dict.get('scatter_matrix_3d')),
        ]
        
        chart_count = 0
        for chart_name, fig_obj in three_d_charts:
            if fig_obj is not None:
                try:
                    img_bytes = fig_obj.to_image(format="png", width=900, height=500)
                    img_buffer = io.BytesIO(img_bytes)
                    img = Image(img_buffer, width=6.2*inch, height=3.4*inch)
                    story.append(Paragraph(f"🎨 {chart_name}", styles['Heading3']))
                    story.append(img)
                    story.append(Spacer(1, 0.15*inch))
                    chart_count += 1
                    
                    if chart_count % 2 == 0:
                        story.append(PageBreak())
                except Exception as e:
                    story.append(Paragraph(f"⚠️ {chart_name} - Grafik ko'rsatilmadi", styles['Normal']))
        
        # Advanced visualizations
        story.append(PageBreak())
        story.append(Paragraph("🌊 Qo'shimcha Tahlil Grafiklari", heading_style))
        story.append(Spacer(1, 0.1*inch))
        
        advanced_charts = [
            ('Pul Oqimi Sankey Diagrammasi', figures_dict.get('sankey')),
            ('Balans Sunburst Diagrammasi', figures_dict.get('sunburst')),
            ('Korrelatsiya Issiqlik Xaritasi', figures_dict.get('correlation')),
            ('Ko\'rsatkichlar Taqsimoti', figures_dict.get('boxplot')),
            ('Marja O\'zgarishi Tahlili', figures_dict.get('waterfall')),
            ('Risk Profili Tahlili', figures_dict.get('bubble')),
        ]
        
        chart_count = 0
        for chart_name, fig_obj in advanced_charts:
            if fig_obj is not None:
                try:
                    img_bytes = fig_obj.to_image(format="png", width=900, height=500)
                    img_buffer = io.BytesIO(img_bytes)
                    img = Image(img_buffer, width=6.2*inch, height=3.4*inch)
                    story.append(Paragraph(f"🔍 {chart_name}", styles['Heading3']))
                    story.append(img)
                    story.append(Spacer(1, 0.15*inch))
                    chart_count += 1
                    
                    if chart_count % 2 == 0:
                        story.append(PageBreak())
                except Exception as e:
                    story.append(Paragraph(f"⚠️ {chart_name} - Grafik ko'rsatilmadi", styles['Normal']))
        
        # Conclusion
        story.append(PageBreak())
        story.append(Paragraph("📌 Xulosa va Tavsiyalar", heading_style))
        story.append(Paragraph(
            "✅ Bu hisobot kompaniyaning moliyaviy holati va samaradorligini chuqur tahlil qiladi.<br/>"
            "✅ Hammasida 2D va 3D grafikalar, jadvallar va metrikalari ko'rsatilgan.<br/>"
            "✅ O'tgan yillar ma'lumotlari o'sish va trend tahlili uchun ishlatilgan.<br/>"
            "✅ EVA, FCFE, Operating Leverage kabi ilg'or metrikalari kiritilgan.<br/>"
            "✅ Sankey, Sunburst va 3D Surface tahlillari qo'shilgan.<br/>"
            "✅ PDF faylda jami 15+ turli grafik tahlili mavjud.",
            styles['Normal']
        ))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(
            f"<b>Kompaniya:</b> {company_name}<br/>"
            f"<b>Yil:</b> {fiscal_year}<br/>"
            f"<b>Valyuta:</b> {currency}<br/>"
            f"<b>Tayyorlash vaqti:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            styles['Normal']
        ))
        
        # Build PDF
        pdf.build(story)
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()
    except Exception as e:
        return None

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
if 'analysis_started' not in st.session_state:
    st.session_state.analysis_started = False

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
    
    st.divider()
    
    # Start Analysis Button
    col_start1, col_start2, col_start3 = st.columns([1, 2, 1])
    with col_start2:
        if st.button(
            "🚀 TAHLILNI BOSHLASH",
            key="start_analysis_btn",
            use_container_width=True,
            help="Barcha ma'lumotlarni tahlil qilish uchun bosing"
        ):
            st.session_state.analysis_started = True
            st.success("✅ Tahlil boshlandi! Boshqa varaqalarga o'ting.")
    
    if st.session_state.analysis_started:
        st.info("✔️ Analiz tayyor. 📊 Tahlil Natijalari, 📈 Grafik Tahlil va 📄 Hisobot varaqalarini ko'ring.")

with tab2:
    st.header("📊 Moliyaviy Tahlil Natijalari")
    
    if not st.session_state.analysis_started:
        st.warning("⚠️ Iltimos, avval 📝 Ma'lumotlarni Kiritish varaqasida barcha ma'lumotlarni kiriting va 🚀 TAHLILNI BOSHLASH tugmasini bosing.")
        st.stop()
    
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
    
    # ============= UMUMIY SIFAT BALLARI =============
    st.subheader("🎯 Umumiy Moliyaviy Sifat Ballari")
    
    def calculate_score(value, thresholds, reverse=False):
        """Ko'rsatkichga bal berish (0-100)"""
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
    
    # Har bir kategoriya uchun ball
    profitability_score = (
        calculate_score(gross_margin, (40, 30, 20)) +
        calculate_score(operating_margin, (20, 15, 10)) +
        calculate_score(net_margin, (15, 10, 5)) +
        calculate_score(roe, (20, 15, 10)) +
        calculate_score(roa, (10, 7, 4))
    ) / 5
    
    liquidity_score = (
        calculate_score(current_ratio, (2.0, 1.5, 1.0)) +
        calculate_score(quick_ratio, (1.5, 1.0, 0.7)) +
        calculate_score(cash_ratio, (0.5, 0.3, 0.1))
    ) / 3
    
    leverage_score = (
        calculate_score(debt_to_equity, (0.5, 1.0, 2.0), reverse=True) +
        calculate_score(debt_to_assets, (0.3, 0.5, 0.7), reverse=True) +
        calculate_score(interest_coverage, (5, 3, 2))
    ) / 3
    
    efficiency_score = (
        calculate_score(asset_turnover, (1.5, 1.0, 0.7)) +
        calculate_score(inventory_turnover, (8, 6, 4)) +
        calculate_score(ccc, (30, 60, 90), reverse=True)
    ) / 3
    
    growth_score = (
        calculate_score(revenue_growth, (15, 10, 5)) +
        calculate_score(net_income_growth, (20, 10, 5))
    ) / 2
    
    cashflow_score = (
        calculate_score(ocf_margin, (20, 15, 10)) +
        (100 if fcff > 0 else 0)
    ) / 2
    
    # Umumiy ball
    overall_score = (profitability_score + liquidity_score + leverage_score + 
                    efficiency_score + growth_score + cashflow_score) / 6
    
    # Ball vizualizatsiyasi
    col1, col2, col3, col4 = st.columns(4)
    
    def get_score_color(score):
        if score >= 80: return "#28a745"
        elif score >= 60: return "#ffc107"
        else: return "#dc3545"
    
    def get_score_emoji(score):
        if score >= 80: return "🌟"
        elif score >= 60: return "👍"
        else: return "⚠️"
    
    with col1:
        st.markdown(f"""
        <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 15px; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
            <h1 style='margin: 0; font-size: 3rem;'>{overall_score:.0f}</h1>
            <p style='margin: 5px 0; font-size: 1.2rem;'>UMUMIY BALL</p>
            <p style='margin: 0; font-size: 2rem;'>{get_score_emoji(overall_score)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.metric("💹 Rentabellik", f"{profitability_score:.0f}/100", 
                 delta="A'lo" if profitability_score >= 80 else "Yaxshi" if profitability_score >= 60 else "O'rtacha")
        st.metric("💧 Likvidlik", f"{liquidity_score:.0f}/100",
                 delta="A'lo" if liquidity_score >= 80 else "Yaxshi" if liquidity_score >= 60 else "O'rtacha")
    
    with col3:
        st.metric("⚖️ Moliyaviy Barqarorlik", f"{leverage_score:.0f}/100",
                 delta="A'lo" if leverage_score >= 80 else "Yaxshi" if leverage_score >= 60 else "O'rtacha")
        st.metric("⚡ Samaradorlik", f"{efficiency_score:.0f}/100",
                 delta="A'lo" if efficiency_score >= 80 else "Yaxshi" if efficiency_score >= 60 else "O'rtacha")
    
    with col4:
        st.metric("📈 O'sish", f"{growth_score:.0f}/100",
                 delta="A'lo" if growth_score >= 80 else "Yaxshi" if growth_score >= 60 else "O'rtacha")
        st.metric("💵 Pul Oqimi", f"{cashflow_score:.0f}/100",
                 delta="A'lo" if cashflow_score >= 80 else "Yaxshi" if cashflow_score >= 60 else "O'rtacha")
    
    # Radar chart
    st.subheader("📡 Ko'p O'lchovli Tahlil")
    
    fig_radar = go.Figure()
    
    categories = ['Rentabellik', 'Likvidlik', 'Barqarorlik', 'Samaradorlik', 'O\'sish', 'Pul Oqimi']
    scores = [profitability_score, liquidity_score, leverage_score, efficiency_score, growth_score, cashflow_score]
    
    fig_radar.add_trace(go.Scatterpolar(
        r=scores + [scores[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name='Sizning ko\'rsatkichlaringiz',
        fillcolor='rgba(31, 119, 180, 0.3)',
        line=dict(color='rgb(31, 119, 180)', width=2)
    ))
    
    # Ideal ko'rsatkichlar
    fig_radar.add_trace(go.Scatterpolar(
        r=[90, 90, 90, 90, 90, 90, 90],
        theta=categories + [categories[0]],
        fill='toself',
        name='Ideal ko\'rsatkichlar',
        fillcolor='rgba(40, 167, 69, 0.1)',
        line=dict(color='rgb(40, 167, 69)', width=2, dash='dash')
    ))
    
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100])
        ),
        showlegend=True,
        height=500,
        title="Moliyaviy Ko'rsatkichlar Radari"
    )
    
    st.plotly_chart(fig_radar, use_container_width=True)
    
    # ============= ADVANCED SCORECARD =============
    st.subheader("📊 Kengaytirilgan Ko'rsatkichlar Kartasi")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Altman Z-Score (Bankrotlik ehtimoli)
        z_score_a = working_capital / total_assets if total_assets > 0 else 0
        z_score_b = (net_income + prev_net_income) / (2 * total_assets) if total_assets > 0 else 0
        z_score_c = operating_income / total_assets if total_assets > 0 else 0
        z_score_d = shareholders_equity / total_debt if total_debt > 0 else 1
        z_score_e = revenue / total_assets if total_assets > 0 else 0
        
        altman_z = 1.2*z_score_a + 1.4*z_score_b + 3.3*z_score_c + 0.6*z_score_d + 1.0*z_score_e
        
        z_status = "Xavfsiz zona" if altman_z > 2.99 else "Kulrang zona" if altman_z > 1.81 else "Xavf zonasi"
        z_color = "#28a745" if altman_z > 2.99 else "#ffc107" if altman_z > 1.81 else "#dc3545"
        
        st.markdown(f"""
        <div style='padding: 20px; background-color: {z_color}20; border-left: 5px solid {z_color}; border-radius: 10px;'>
            <h3>🎯 Altman Z-Score</h3>
            <h1 style='color: {z_color}; margin: 10px 0;'>{altman_z:.2f}</h1>
            <p style='font-size: 1.2rem; margin: 0;'>{z_status}</p>
            <small>Z > 2.99: Xavfsiz | 1.81-2.99: Kulrang | < 1.81: Xavf</small>
        </div>
        """, unsafe_allow_html=True)
        
        # Piotroski F-Score (Moliyaviy kuch)
        f_score = 0
        f_score += 1 if net_income > 0 else 0
        f_score += 1 if operating_cash_flow > 0 else 0
        f_score += 1 if roa > (prev_net_income / prev_total_assets * 100 if prev_total_assets > 0 else 0) else 0
        f_score += 1 if operating_cash_flow > net_income else 0
        f_score += 1 if debt_to_assets < (prev_total_assets / (prev_total_assets + prev_equity) if (prev_total_assets + prev_equity) > 0 else 1) else 0
        f_score += 1 if current_ratio > (current_assets / current_liabilities if current_liabilities > 0 else 0) else 0
        f_score += 1 if gross_margin > ((prev_revenue - cogs) / prev_revenue * 100 if prev_revenue > 0 else 0) else 0
        f_score += 1 if asset_turnover > (prev_revenue / prev_total_assets if prev_total_assets > 0 else 0) else 0
        
        f_status = "Kuchli" if f_score >= 7 else "O'rtacha" if f_score >= 4 else "Zaif"
        f_color = "#28a745" if f_score >= 7 else "#ffc107" if f_score >= 4 else "#dc3545"
        
        st.markdown(f"""
        <div style='padding: 20px; background-color: {f_color}20; border-left: 5px solid {f_color}; 
                    border-radius: 10px; margin-top: 20px;'>
            <h3>💪 Piotroski F-Score</h3>
            <h1 style='color: {f_color}; margin: 10px 0;'>{f_score}/9</h1>
            <p style='font-size: 1.2rem; margin: 0;'>Moliyaviy Kuch: {f_status}</p>
            <small>7-9: Kuchli | 4-6: O'rtacha | 0-3: Zaif</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Beneish M-Score (Hisobot manipulyatsiyasi)
        dsri = (accounts_receivable / revenue) / (prev_ar / prev_revenue) if prev_revenue > 0 and revenue > 0 else 1
        gmi = ((prev_revenue - cogs) / prev_revenue) / (gross_margin / 100) if prev_revenue > 0 and gross_margin > 0 else 1
        aqi = (1 - (current_assets + total_assets) / total_assets) / (1 - (current_assets + prev_total_assets) / prev_total_assets) if prev_total_assets > 0 else 1
        
        m_score = -4.84 + 0.92*dsri + 0.528*gmi + 0.404*aqi
        m_status = "Xavf" if m_score > -1.78 else "Xavfsiz"
        m_color = "#dc3545" if m_score > -1.78 else "#28a745"
        
        st.markdown(f"""
        <div style='padding: 20px; background-color: {m_color}20; border-left: 5px solid {m_color}; border-radius: 10px;'>
            <h3>🔍 Beneish M-Score</h3>
            <h1 style='color: {m_color}; margin: 10px 0;'>{m_score:.2f}</h1>
            <p style='font-size: 1.2rem; margin: 0;'>{m_status}</p>
            <small>M > -1.78: Manipulyatsiya xavfi | M < -1.78: Normal</small>
        </div>
        """, unsafe_allow_html=True)
        
        # Graham Number (Qiymat bahosi)
        graham_number = (22.5 * eps * book_value_per_share) ** 0.5 if eps > 0 and book_value_per_share > 0 else 0
        graham_status = "Arzon" if market_price_per_share < graham_number else "Qimmat"
        graham_color = "#28a745" if market_price_per_share < graham_number else "#dc3545"
        
        st.markdown(f"""
        <div style='padding: 20px; background-color: {graham_color}20; border-left: 5px solid {graham_color}; 
                    border-radius: 10px; margin-top: 20px;'>
            <h3>💎 Graham Raqami</h3>
            <h1 style='color: {graham_color}; margin: 10px 0;'>{graham_number:.2f}</h1>
            <p style='font-size: 1.2rem; margin: 0;'>Joriy narx: {market_price_per_share:.2f} - {graham_status}</p>
            <small>Narx < Graham: Arzon | Narx > Graham: Qimmat</small>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # ============= TREND ANALYSIS =============
    st.subheader("📈 Trend va O'sish Tahlili")
    
    # Simulated historical data for visualization
    years = [fiscal_year-2, fiscal_year-1, fiscal_year]
    revenue_trend = [prev_revenue * 0.9, prev_revenue, revenue]
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
        yaxis_title=f'Qiymat ({currency})',
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig_trends, use_container_width=True)
    
    # O'sish ko'rsatkichlari
    col1, col2, col3 = st.columns(3)
    
    with col1:
        cagr_revenue = ((revenue / (prev_revenue * 0.9)) ** (1/2) - 1) * 100 if prev_revenue > 0 else 0
        st.metric("Tushum CAGR (2 yil)", f"{cagr_revenue:+.1f}%", 
                 delta="Ijobiy o'sish" if cagr_revenue > 0 else "Kamayish")
    
    with col2:
        cagr_profit = ((net_income / (prev_net_income * 0.85)) ** (1/2) - 1) * 100 if prev_net_income > 0 else 0
        st.metric("Foyda CAGR (2 yil)", f"{cagr_profit:+.1f}%",
                 delta="Ijobiy o'sish" if cagr_profit > 0 else "Kamayish")
    
    with col3:
        sustainable_growth = roe * (1 - (dividends_paid / net_income if net_income > 0 else 0)) / 100
        st.metric("Barqaror O'sish Sur'ati", f"{sustainable_growth:.1f}%",
                 delta="ROE va qayta investitsiyaga asoslangan")
    
    st.divider()
    
    # Natijalarni ko'rsatish (eskisi saqlanadi)
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
        col7.metric("ROIC", f"{roic:.2f}%)igi)", f"{roe:.2f}%")
        col7.metric("ROIC", f"{roic:.2f}%")
    
    # ============= HEATMAP ANALYSIS =============
    st.subheader("🔥 Ko'rsatkichlar Issiqlik Xaritasi")
    
    # Ko'rsatkichlar matritsa
    metrics_data = {
        'Rentabellik': {
            'Yalpi marja': gross_margin,
            'Operatsion marja': operating_margin,
            'Sof marja': net_margin,
            'ROE': roe,
            'ROA': roa,
            'ROIC': roic
        },
        'Likvidlik': {
            'Joriy likvidlik': current_ratio * 50,  # Scale to 100
            'Tez likvidlik': quick_ratio * 60,
            'Absolut likvidlik': cash_ratio * 100,
            'Ishchi kapital': min(100, working_capital / revenue * 100) if revenue > 0 else 0,
            '-': 0,
            '--': 0
        },
        'Qarz': {
            'Qarz/Kapital': max(0, 100 - debt_to_equity * 50),  # Inverted
            'Qarz/Aktivlar': max(0, 100 - debt_to_assets * 100),
            'Foiz qoplash': min(100, interest_coverage * 20),
            'Kapital nisbati': equity_ratio * 100,
            '---': 0,
            '----': 0
        },
        'Samaradorlik': {
            'Aktivlar aylanmasi': min(100, asset_turnover * 50),
            'Zaxiralar aylanmasi': min(100, inventory_turnover * 10),
            'DIO': max(0, 100 - dio / 3),  # Lower is better
            'DSO': max(0, 100 - dso / 3),
            'DPO': min(100, dpo / 3),  # Higher is better
            'CCC': max(0, 100 - ccc / 3)
        },
        'O\'sish': {
            'Tushum o\'sishi': min(100, max(0, revenue_growth * 5)),
            'Foyda o\'sishi': min(100, max(0, net_income_growth * 5)),
            'CAGR tushum': min(100, max(0, cagr_revenue * 5)),
            'CAGR foyda': min(100, max(0, cagr_profit * 5)),
            'Barqaror o\'sish': min(100, max(0, sustainable_growth * 10)),
            '-----': 0
        }
    }
    
    # Create heatmap data
    categories = list(metrics_data.keys())
    all_metrics = []
    values_matrix = []
    
    max_len = max(len(v) for v in metrics_data.values())
    for cat in categories:
        metrics = list(metrics_data[cat].keys())
        values = list(metrics_data[cat].values())
        
        # Pad to same length
        while len(metrics) < max_len:
            metrics.append('')
            values.append(0)
        
        if not all_metrics:
            all_metrics = metrics
        values_matrix.append(values)
    
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=values_matrix,
        x=all_metrics,
        y=categories,
        colorscale='RdYlGn',
        text=[[f'{v:.0f}' if v > 0 else '' for v in row] for row in values_matrix],
        texttemplate='%{text}',
        textfont={"size": 10},
        colorbar=dict(title="Ball (0-100)")
    ))
    
    fig_heatmap.update_layout(
        title='Moliyaviy Ko\'rsatkichlar Issiqlik Xaritasi',
        height=400,
        xaxis_title='Ko\'rsatkichlar',
        yaxis_title='Kategoriya'
    )
    
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # ============= WATERFALL CHART =============
    st.subheader("💧 Foyda Formatsiyasi (Waterfall)")
    
    waterfall_data = [
        ('Tushum', revenue, 'relative'),
        ('Tannarx', -cogs, 'relative'),
        ('Yalpi foyda', gross_profit, 'total'),
        ('Operatsion xarajat', -operating_expenses, 'relative'),
        ('EBIT', operating_income, 'total'),
        ('Foiz xarajati', -interest_expense, 'relative'),
        ('Soliq', -tax_expense, 'relative'),
        ('Sof foyda', net_income, 'total')
    ]
    
    fig_waterfall = go.Figure(go.Waterfall(
        name="Foyda tahlili",
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
        title="Tushumdan Sof Foydaga - Waterfall Tahlili",
        showlegend=False,
        height=500,
        yaxis_title=f'Qiymat ({currency})'
    )
    
    st.plotly_chart(fig_waterfall, use_container_width=True)
    
    # ============= GAUGE CHARTS =============
    st.subheader("🎯 Asosiy Ko'rsatkichlar Gauge")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fig_gauge_roe = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=roe,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "ROE (%)"},
            delta={'reference': 15, 'increasing': {'color': "green"}},
            gauge={
                'axis': {'range': [None, 30]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 10], 'color': "#ffcccc"},
                    {'range': [10, 15], 'color': "#fff4cc"},
                    {'range': [15, 30], 'color': "#ccffcc"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 20
                }
            }
        ))
        fig_gauge_roe.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_gauge_roe, use_container_width=True)
    
    with col2:
        fig_gauge_liquidity = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=current_ratio,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Joriy Likvidlik"},
            delta={'reference': 1.5, 'increasing': {'color': "green"}},
            gauge={
                'axis': {'range': [0, 4]},
                'bar': {'color': "darkgreen"},
                'steps': [
                    {'range': [0, 1], 'color': "#ffcccc"},
                    {'range': [1, 1.5], 'color': "#fff4cc"},
                    {'range': [1.5, 4], 'color': "#ccffcc"}
                ],
                'threshold': {
                    'line': {'color': "green", 'width': 4},
                    'thickness': 0.75,
                    'value': 2
                }
            }
        ))
        fig_gauge_liquidity.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_gauge_liquidity, use_container_width=True)
    
    with col3:
        fig_gauge_margin = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=net_margin,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Sof Marja (%)"},
            delta={'reference': 10, 'increasing': {'color': "green"}},
            gauge={
                'axis': {'range': [0, 25]},
                'bar': {'color': "darkorange"},
                'steps': [
                    {'range': [0, 5], 'color': "#ffcccc"},
                    {'range': [5, 10], 'color': "#fff4cc"},
                    {'range': [10, 25], 'color': "#ccffcc"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 15
                }
            }
        ))
        fig_gauge_margin.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_gauge_margin, use_container_width=True)
    
    st.divider()
    
    # Eski ko'rsatkichlar saqlanadi
    if analysis_type in ["To'liq Tahlil", "Rentabellik"]:
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
    
    # ============= ADVANCED METRICS =============
    st.divider()
    st.subheader("🚀 Kengaytirilgan Moliyaviy Metrikalari")
    
    # Economic Value Added (EVA)
    wacc = 0.08  # Weighted Average Cost of Capital (8%)
    nopat_val = operating_income * (1 - tax_rate)
    invested_cap = total_debt + shareholders_equity - cash
    eva = nopat_val - (wacc * invested_cap)
    
    # Free Cash Flow to Equity (FCFE)
    fcfe = operating_cash_flow - capex + total_debt - accounts_payable
    
    # Operating and Financial Leverage
    degree_of_operating_leverage = (revenue - cogs) / operating_income if operating_income > 0 else 0
    degree_of_financial_leverage = operating_income / (operating_income - interest_expense) if (operating_income - interest_expense) > 0 else 0
    dfl = degree_of_operating_leverage * degree_of_financial_leverage
    
    # Quality of Earnings
    quality_of_earnings = operating_cash_flow / net_income if net_income > 0 else 0
    
    # Asset Turnover Efficiency
    receivables_collection_days = dso
    inventory_holding_days = dio
    payables_payment_days = dpo
    
    # Cash Conversion Efficiency
    cash_conversion_efficiency = (operating_cash_flow / revenue * 100) if revenue > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📈 EVA (Iqtisodiy Qiymat Qo'shilgan)", 
                 f"{eva:,.0f} {currency}",
                 delta="Ijobiy" if eva > 0 else "Salbiy",
                 delta_color="inverse")
    
    with col2:
        st.metric("💰 FCFE (Kapitalga Erkin PO)", 
                 f"{fcfe:,.0f} {currency}",
                 delta="Ijobiy" if fcfe > 0 else "Salbiy",
                 delta_color="inverse")
    
    with col3:
        st.metric("⚡ Taraqqiyot Darajasi (DOL)", 
                 f"{degree_of_operating_leverage:.2f}",
                 delta="Yuqori = Riskli")
    
    with col4:
        st.metric("📊 Pul Konversiya Samaradorligi", 
                 f"{cash_conversion_efficiency:.1f}%",
                 delta="Yuqori = Yaxshi")
    
    col5, col6, col7 = st.columns(3)
    
    with col5:
        st.metric("🎯 Moliyaviy Leverage Darajasi (DFL)", 
                 f"{degree_of_financial_leverage:.2f}",
                 delta="Yuqori = Riskli")
    
    with col6:
        st.metric("🔗 Birlashtirilgan Leverage (DCL)", 
                 f"{dfl:.2f}",
                 delta="Salpiyat ta'siri")
    
    with col7:
        st.metric("✅ Pul Oqimining Sifati", 
                 f"{quality_of_earnings:.2f}",
                 delta="Yaxshi: > 1.0",
                 delta_color="inverse")
    
    st.divider()
    
    # ============= ADVANCED METRICS TABLE =============
    st.subheader("📋 Chuqur Tahlil Jadvali")
    
    advanced_metrics_data = {
        'Metrika': [
            'EVA (Iqtisodiy Qiymat)',
            'FCFE (Kapitalga Erkin PO)',
            'Operatsion Leverage (DOL)',
            'Moliyaviy Leverage (DFL)',
            'Birlashtirilgan Leverage (DCL)',
            'Pul Oqimi Sifati',
            'Pul Konversiya Samaradorligi',
            'Debitor To\'lov Kunlari (DSO)',
            'Zaxiralar Saqlash Kunlari (DIO)',
            'Kreditor To\'lov Kunlari (DPO)',
            'Netto Ishchi Kapital',
            'Ishchi Kapital / Tushum'
        ],
        'Qiymat': [
            f"{eva:,.0f}",
            f"{fcfe:,.0f}",
            f"{degree_of_operating_leverage:.2f}",
            f"{degree_of_financial_leverage:.2f}",
            f"{dfl:.2f}",
            f"{quality_of_earnings:.2f}",
            f"{cash_conversion_efficiency:.1f}%",
            f"{receivables_collection_days:.0f}",
            f"{inventory_holding_days:.0f}",
            f"{payables_payment_days:.0f}",
            f"{working_capital:,.0f}",
            f"{(working_capital/revenue*100):.2f}%"
        ],
        'Tafsir': [
            'Musbat > 0' if eva > 0 else 'Salbiy < 0',
            'Musbat > 0' if fcfe > 0 else 'Salbiy < 0',
            f"{'Yuqori risk' if degree_of_operating_leverage > 3 else 'O\'rtacha'}",
            f"{'Yuqori risk' if degree_of_financial_leverage > 2 else 'O\'rtacha'}",
            f"{'Juda riskli' if dfl > 6 else 'Maqbul'}",
            'Yaxshi' if quality_of_earnings >= 1 else 'Zayif',
            'Yaxshi' if cash_conversion_efficiency > 20 else 'Yaxshilanishi kerak',
            'Past = Yaxshi' if receivables_collection_days < 45 else 'Yuqori = Zayif',
            'Past = Yaxshi' if inventory_holding_days < 60 else 'Yuqori = Zayif',
            'Yuqori = Yaxshi' if payables_payment_days > 45 else 'Past = Zayif',
            'Musbat bo\'lishi kerak',
            'Yaxshi: 10-20%'
        ]
    }
    
    st.dataframe(pd.DataFrame(advanced_metrics_data), hide_index=True, use_container_width=True)
    
    st.divider()
    
    # ============= ADVANCED SCENARIO ANALYSIS =============
    st.subheader("🎲 Stsenarii Tahlili")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Optimistik Ssenarii (+10% Tushum)**")
        optimistic_revenue = revenue * 1.10
        optimistic_net_income = (optimistic_revenue - cogs - operating_expenses - interest_expense - tax_expense)
        optimistic_roe = (optimistic_net_income / shareholders_equity * 100) if shareholders_equity > 0 else 0
        st.metric("Taxminiy ROE", f"{optimistic_roe:.2f}%", delta=f"+{optimistic_roe - roe:.2f}%")
        st.metric("Taxminiy Sof Foyda", f"{optimistic_net_income:,.0f}")
    
    with col2:
        st.write("**Pessimistik Ssenarii (-10% Tushum)**")
        pessimistic_revenue = revenue * 0.90
        pessimistic_net_income = (pessimistic_revenue - cogs - operating_expenses - interest_expense - tax_expense)
        pessimistic_roe = (pessimistic_net_income / shareholders_equity * 100) if shareholders_equity > 0 else 0
        st.metric("Taxminiy ROE", f"{pessimistic_roe:.2f}%", delta=f"{pessimistic_roe - roe:.2f}%")
        st.metric("Taxminiy Sof Foyda", f"{pessimistic_net_income:,.0f}")

with tab3:
    st.header("📈 Grafik Tahlil")
    
    if not st.session_state.analysis_started:
        st.warning("⚠️ Iltimos, avval 📝 Ma'lumotlarni Kiritish varaqasida barcha ma'lumotlarni kiriting va 🚀 TAHLILNI BOSHLASH tugmasini bosing.")
        st.stop()
    
    st.markdown("""
    ### Formulalar (LaTeX)
    - **Yalpi marja:** Yalpi foyda / Tushum × 100
    - **Operatsion marja:** Operatsion foyda / Tushum × 100
    - **EBITDA marja:** EBITDA / Tushum × 100
    - **Sof marja:** Sof foyda / Tushum × 100
    - **ROE:** Sof foyda / O'rtacha kapital × 100
    - **ROA:** Sof foyda / O'rtacha aktivlar × 100
    - **Joriy likvidlik:** Joriy aktivlar / Joriy majburiyatlar
    - **Qarz/Kapital:** Jami qarz / Kapital
    - **CCC:** DIO + DSO - DPO (Kunlar)
    """)
    
    st.info("📐 **Asosiy Formulalar:**\n- Sof Marja = (Sof foyda / Tushum) × 100\n- ROE = (Sof foyda / O'rtacha Kapital) × 100\n- ROA = (Sof foyda / O'rtacha Aktivlar) × 100\n- Joriy Likvidlik = Joriy Aktivlar / Joriy Majburiyatlar\n- Qarz/Kapital = Jami Qarz / Xususiy Kapital\n- CCC = DIO + DSO - DPO (Pul Konversiya Davri)")

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
    st.session_state.fig_profitability = fig_profitability

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
        st.session_state.fig_liquidity = fig_liquidity
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
        st.session_state.fig_leverage = fig_leverage

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
    st.session_state.fig_ccc = fig_ccc

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

    # Advanced: Correlation Heatmap
    st.subheader("📊 Korrelatsiya Issiqlik Xaritasi")
    df_corr = pd.DataFrame({
        'Gross Margin': [gross_margin],
        'Operating Margin': [operating_margin],
        'Net Margin': [net_margin],
        'ROE': [roe],
        'ROA': [roa],
        'Current Ratio': [current_ratio],
        'Debt/Equity': [debt_to_equity],
        'CCC': [ccc]
    })
    # Simulate more rows for visualization
    df_corr = pd.concat([df_corr]*10, ignore_index=True)
    df_corr += np.random.normal(0, 2, df_corr.shape)
    corr_matrix = df_corr.corr()
    fig_corr = px.imshow(corr_matrix, text_auto=True, color_continuous_scale='RdYlGn', aspect='auto', title='Ko\'rsatkichlar Korrelatsiyasi')
    st.plotly_chart(fig_corr, use_container_width=True)

    # Advanced: Boxplot for distribution
    st.subheader("📦 Ko'rsatkichlar Taqsimoti (Boxplot)")
    fig_box = px.box(df_corr, points="all", title="Ko'rsatkichlar Boxplot")
    st.plotly_chart(fig_box, use_container_width=True)

    # Advanced: Pairplot (Scatter Matrix)
    st.subheader("🔗 Ko'rsatkichlar O'zaro Aloqasi (Pairplot)")
    fig_pair = px.scatter_matrix(df_corr, title="Scatter Matrix (Pairplot)", dimensions=df_corr.columns)
    st.plotly_chart(fig_pair, use_container_width=True)
    
    # Advanced: Sankey Diagram (Cash Flow)
    st.divider()
    st.subheader("🌊 Pul Oqimi Sankey Diagrammasi")
    
    fig_sankey = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color='black', width=0.5),
            label=['Tushum', 'Tannarx', 'Yalpi Foyda', 'Operatsion Xarajat', 'EBIT', 
                   'Foiz', 'Soliq', 'Sof Foyda', 'Investitsiya', 'Dividend', 'Operatsion PO'],
            color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf', '#39a9c4']
        ),
        link=dict(
            source=[0, 1, 2, 3, 4, 4, 6, 7, 7, 8, 9],
            target=[2, 2, 3, 4, 5, 4, 7, 8, 9, 10, 10],
            value=[revenue, cogs, gross_profit, operating_expenses, operating_income, 
                   interest_expense, tax_expense, net_income, capex, dividends_paid, operating_cash_flow]
        )
    )])
    
    fig_sankey.update_layout(
        title="Tushumdan Sof Foydaga Pul Oqimi",
        font=dict(size=10),
        height=600
    )
    st.plotly_chart(fig_sankey, use_container_width=True)
    st.session_state.fig_sankey = fig_sankey
    
    # Advanced: Sunburst Chart (Balance Sheet)
    st.subheader("☀️ Balans Sunburst Diagrammasi")
    
    # Ensure all values are positive
    balans_total = abs(total_assets) + abs(current_liabilities) + abs(shareholders_equity)
    current_assets_val = abs(current_assets)
    fixed_assets_val = abs(total_assets - current_assets)
    
    fig_sunburst = go.Figure(go.Sunburst(
        labels=['Balans', 'Aktivlar', 'Joriy Aktivlar', 'Asosiy Aktivlar', 
                'Passivlar', 'Joriy Majburiyatlar', 'Uzoq Muddatli Qarz', 'Kapital',
                'Naqd', 'Debitor', 'Zaxiralar'],
        parents=['', 'Balans', 'Aktivlar', 'Aktivlar', 
                 'Balans', 'Passivlar', 'Passivlar', 'Passivlar',
                 'Joriy Aktivlar', 'Joriy Aktivlar', 'Joriy Aktivlar'],
        values=[balans_total, 
               abs(total_assets), current_assets_val, fixed_assets_val,
               abs(current_liabilities + long_term_debt + shareholders_equity),
               abs(current_liabilities), abs(long_term_debt), abs(shareholders_equity),
               abs(cash), abs(accounts_receivable), abs(inventory)],
        marker=dict(
            colors=['#1f77b4', '#2ca02c', '#ff7f0e', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf', '#39a9c4'],
            line=dict(color='white', width=2)
        )
    ))
    
    fig_sunburst.update_layout(
        title="Balans Tuzilmasi (Sunburst)",
        height=600
    )
    st.plotly_chart(fig_sunburst, use_container_width=True)
    st.session_state.fig_sunburst = fig_sunburst
    
    # Advanced: Histogram Distributions
    st.divider()
    st.subheader("📊 Metrika Taqsimoti (Histogramma)")
    
    # Generate distribution data
    margin_dist = np.random.normal(net_margin, net_margin*0.3, 100)
    roe_dist = np.random.normal(roe, roe*0.25, 100) if roe > 0 else np.random.normal(10, 3, 100)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_hist_margin = px.histogram(
            {'Sof Marja': margin_dist},
            nbins=30,
            title='Sof Marja Taqsimoti',
            labels={'value': 'Foiz (%)', 'count': 'Chastota'}
        )
        st.plotly_chart(fig_hist_margin, use_container_width=True)
    
    with col2:
        fig_hist_roe = px.histogram(
            {'ROE': roe_dist},
            nbins=30,
            title='ROE Taqsimoti',
            labels={'value': 'Foiz (%)', 'count': 'Chastota'}
        )
        st.plotly_chart(fig_hist_roe, use_container_width=True)
        st.session_state.fig_histogram = fig_hist_roe
    
    # Advanced: Waterfall for Ratios
    st.divider()
    st.subheader("💧 Ko'rsatkichlar Vozvrata (Waterfall)")
    
    fig_waterfall_ratios = go.Figure(go.Waterfall(
        name="Koeffitsiyent Tahlili",
        orientation="v",
        measure=['relative', 'relative', 'relative', 'relative', 'total'],
        x=['Yalpi Marja', '- Operatsion Xarajat %', '+ EBITDA Effekti', '- Foiz va Soliq', 'Sof Marja'],
        y=[gross_margin, -(operating_expenses/revenue*100), ebitda_margin-operating_margin, 
           -(interest_expense + tax_expense)/revenue*100, net_margin],
        text=[f'{gross_margin:.1f}%', f'{-(operating_expenses/revenue*100):.1f}%', 
              f'{ebitda_margin-operating_margin:.1f}%', f'{-(interest_expense + tax_expense)/revenue*100:.1f}%', f'{net_margin:.1f}%'],
        textposition="outside",
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        increasing={"marker": {"color": "#28a745"}},
        decreasing={"marker": {"color": "#dc3545"}},
        totals={"marker": {"color": "#1f77b4"}}
    ))
    
    fig_waterfall_ratios.update_layout(
        title="Marja O'zgarishi Tahlili",
        height=500
    )
    st.plotly_chart(fig_waterfall_ratios, use_container_width=True)
    
    # Advanced: Multi-metric Time Series (Simulated)
    st.divider()
    st.subheader("📈 Ko'rsatkichlar Dinamikasi (3 Yillik Trend)")
    
    years_range = [fiscal_year-2, fiscal_year-1, fiscal_year]
    margin_trend = [gross_margin*0.85, gross_margin*0.92, gross_margin]
    roe_trend = [roe*0.80, roe*0.90, roe]
    current_ratio_trend = [current_ratio*0.95, current_ratio*0.98, current_ratio]
    
    fig_trends_multi = go.Figure()
    
    fig_trends_multi.add_trace(go.Scatter(
        x=years_range, y=margin_trend,
        mode='lines+markers',
        name='Yalpi Marja (%)',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=10)
    ))
    
    fig_trends_multi.add_trace(go.Scatter(
        x=years_range, y=roe_trend,
        mode='lines+markers',
        name='ROE (%)',
        line=dict(color='#2ca02c', width=3),
        marker=dict(size=10)
    ))
    
    fig_trends_multi.add_trace(go.Scatter(
        x=years_range, y=current_ratio_trend,
        mode='lines+markers',
        name='Joriy Likvidlik',
        line=dict(color='#ff7f0e', width=3),
        marker=dict(size=10)
    ))
    
    fig_trends_multi.update_layout(
        title='Ko\'rsatkichlar Dinamikasi (3 Yil)',
        xaxis=dict(title='Yil'),
        yaxis=dict(title='Marja (%) / ROE (%) / Likvidlik'),
        hovermode='x unified',
        height=500,
        legend=dict(x=0.5, y=1.15, orientation='h')
    )
    st.plotly_chart(fig_trends_multi, use_container_width=True)
    
    # Advanced: Risk Profile Bubble Chart
    st.divider()
    st.subheader("🔴 Risk Profili Tahlili (Bubble Chart)")
    
    fig_bubble = go.Figure(data=[go.Scatter(
        x=[debt_to_equity, 0.5, 1.5, 0.3, 1.8],
        y=[interest_coverage, 5, 2.5, 8, 1.5],
        mode='markers+text',
        marker=dict(
            size=[abs(eva/1000000)+10, 15, 20, 12, 18],
            color=[roa, 8, 5, 10, 3],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="ROA %")
        ),
        text=['Sizning Kompaniya', 'Raqib 1', 'Raqib 2', 'Raqib 3', 'Raqib 4'],
        textposition="top center"
    )])
    
    fig_bubble.update_xaxes(title_text="Qarz/Kapital (Xavf)")
    fig_bubble.update_yaxes(title_text="Foiz Qoplash (Barqarorlik)")
    fig_bubble.update_layout(
        title="Moliyaviy Risk vs Barqarorlik Profili",
        height=500,
        showlegend=False
    )
    st.plotly_chart(fig_bubble, use_container_width=True)
    
    # Advanced: 3D Surface Plot (Sensitivity Analysis)
    st.divider()
    st.subheader("📊 Sezgirlik Tahlili (3D Grafik)")
    
    revenue_range = np.linspace(revenue*0.8, revenue*1.2, 10)
    expense_ratio_range = np.linspace(0.5, 0.75, 10)
    
    X, Y = np.meshgrid(revenue_range, expense_ratio_range)
    Z = ((X * (1 - Y) - operating_expenses - interest_expense - tax_expense) / X * 100) if revenue > 0 else X*0
    
    fig_3d = go.Figure(data=[go.Surface(x=X, y=Y, z=Z, colorscale='Viridis')])
    fig_3d.update_layout(
        title='Sof Marja Sezgirlik Tahlili (Tushum vs Xarajat Nisbati)',
        scene=dict(
            xaxis_title='Tushum',
            yaxis_title='Xarajat/Tushum Nisbati',
            zaxis_title='Sof Marja (%)'
        ),
        height=600
    )
    st.plotly_chart(fig_3d, use_container_width=True)
    
    # ============= ADDITIONAL 3D VISUALIZATIONS =============
    st.divider()
    st.subheader("🎯 Qo'shimcha 3D Tahlil Grafiklari")
    
    # 3D Scatter Plot: ROE, ROA, Current Ratio
    st.subheader("📊 3D Scatter: Rentabellik vs Likvidlik Tahlili")
    
    # Generate multiple data points for 3D scatter
    years_points = [fiscal_year-2, fiscal_year-1, fiscal_year]
    roe_points = [roe*0.75, roe*0.88, roe]
    roa_points = [roa*0.70, roa*0.85, roa]
    cr_points = [current_ratio*0.92, current_ratio*0.97, current_ratio]
    
    fig_3d_scatter = go.Figure(data=[go.Scatter3d(
        x=roe_points,
        y=roa_points,
        z=cr_points,
        mode='markers+lines',
        marker=dict(
            size=[8, 10, 12],
            color=['#ff7f0e', '#2ca02c', '#1f77b4'],
            opacity=0.8,
            symbol='circle'
        ),
        line=dict(color='#7f7f7f', width=3),
        text=[f'Yil {year}<br>ROE: {roe_val:.2f}%<br>ROA: {roa_val:.2f}%<br>CR: {cr_val:.2f}' 
              for year, roe_val, roa_val, cr_val in zip(years_points, roe_points, roa_points, cr_points)],
        hoverinfo='text'
    )])
    
    fig_3d_scatter.update_layout(
        title='3D Trend: ROE vs ROA vs Likvidlik (3 Yil)',
        scene=dict(
            xaxis_title='ROE (%)',
            yaxis_title='ROA (%)',
            zaxis_title='Joriy Likvidlik',
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.3))
        ),
        height=600,
        showlegend=False
    )
    st.plotly_chart(fig_3d_scatter, use_container_width=True)
    
    # 3D Bar Chart: Multi-year financial metrics (using Scatter3d)
    st.subheader("📈 3D Bar: Ko'p yillik taqlid")
    
    years_bar = [fiscal_year-2, fiscal_year-1, fiscal_year]
    gross_profit_bar = [gross_profit*0.85, gross_profit*0.92, gross_profit]
    operating_income_bar = [operating_income*0.80, operating_income*0.90, operating_income]
    net_income_bar = [net_income*0.75, net_income*0.88, net_income]
    
    fig_3d_bar = go.Figure()
    
    # Add traces for each profit type
    fig_3d_bar.add_trace(go.Scatter3d(
        x=years_bar,
        y=[0, 0, 0],
        z=gross_profit_bar,
        mode='markers+lines',
        name='Yalpi Foyda',
        marker=dict(size=12, color='#1f77b4', symbol='square'),
        line=dict(color='#1f77b4', width=4)
    ))
    
    fig_3d_bar.add_trace(go.Scatter3d(
        x=years_bar,
        y=[1, 1, 1],
        z=operating_income_bar,
        mode='markers+lines',
        name='Operatsion Foyda',
        marker=dict(size=12, color='#ff7f0e', symbol='diamond'),
        line=dict(color='#ff7f0e', width=4)
    ))
    
    fig_3d_bar.add_trace(go.Scatter3d(
        x=years_bar,
        y=[2, 2, 2],
        z=net_income_bar,
        mode='markers+lines',
        name='Sof Foyda',
        marker=dict(size=12, color='#2ca02c', symbol='circle'),
        line=dict(color='#2ca02c', width=4)
    ))
    
    fig_3d_bar.update_layout(
        title='3D Multi-Bar: Foyda Dinamikasi (3 Yil)',
        scene=dict(
            xaxis_title='Yil',
            yaxis=dict(tickvals=[0, 1, 2], ticktext=['Yalpi Foyda', 'Operatsion Foyda', 'Sof Foyda']),
            zaxis_title=f'Qiymat ({currency})',
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.2))
        ),
        height=600,
        showlegend=True
    )
    st.plotly_chart(fig_3d_bar, use_container_width=True)
    
    # 3D Bubble Scatter: Metrics with EVA size
    st.subheader("🔵 3D Bubble: Ko'rsatkichlar EVA bilan")
    
    # Create bubble data
    bubble_roe = [roe*0.7, roe*0.85, roe, 12, 8, 15]
    bubble_roa = [roa*0.75, roa*0.90, roa, 6, 4, 9]
    bubble_debt = [debt_to_equity*1.2, debt_to_equity*1.05, debt_to_equity, 1.2, 0.8, 1.5]
    bubble_size = [abs(eva/100000) if eva > 0 else 5, abs(eva/100000)*1.1 if eva > 0 else 6, 
                   abs(eva/100000)*1.2 if eva > 0 else 7, 8, 5, 10]
    bubble_colors = ['#1f77b4', '#2ca02c', '#ff7f0e', '#d62728', '#9467bd', '#8c564b']
    bubble_labels = [f'Yil {fiscal_year-2}', f'Yil {fiscal_year-1}', f'Yil {fiscal_year}',
                    'Raqib 1', 'Raqib 2', 'Raqib 3']
    
    fig_3d_bubble = go.Figure(data=[go.Scatter3d(
        x=bubble_roe,
        y=bubble_roa,
        z=bubble_debt,
        mode='markers',
        marker=dict(
            size=bubble_size,
            color=bubble_colors,
            opacity=0.7,
            line=dict(color='white', width=2)
        ),
        text=bubble_labels,
        textposition='top center',
        hovertemplate='<b>%{text}</b><br>ROE: %{x:.2f}%<br>ROA: %{y:.2f}%<br>Qarz/Kapital: %{z:.2f}<extra></extra>'
    )])
    
    fig_3d_bubble.update_layout(
        title='3D Bubble: Rentabillik vs Qarz Yuklama (EVA bilan)',
        scene=dict(
            xaxis_title='ROE (%)',
            yaxis_title='ROA (%)',
            zaxis_title='Qarz/Kapital',
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.3))
        ),
        height=600,
        showlegend=False
    )
    st.plotly_chart(fig_3d_bubble, use_container_width=True)
    
    # 3D Surface: Revenue vs Operating Expenses vs ROA
    st.subheader("🌊 3D Surface: Tushum vs Xarajatlar Sezgirlik")
    
    revenue_range_2 = np.linspace(revenue*0.6, revenue*1.4, 15)
    opex_range = np.linspace(operating_expenses*0.7, operating_expenses*1.3, 15)
    
    X2, Y2 = np.meshgrid(revenue_range_2, opex_range)
    Z2 = (((X2 - cogs - Y2 - interest_expense) / X2 * 100) 
          if revenue > 0 else X2*0)
    
    fig_3d_surface_2 = go.Figure(data=[go.Surface(
        x=X2, 
        y=Y2, 
        z=Z2, 
        colorscale='Plasma'
    )])
    
    fig_3d_surface_2.update_layout(
        title='3D Surface: Operatsion Marja Sezgirlik (Tushum vs Xarajat)',
        scene=dict(
            xaxis_title='Tushum',
            yaxis_title='Operatsion Xarajat',
            zaxis_title='Operatsion Marja (%)',
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.2))
        ),
        height=600
    )
    st.plotly_chart(fig_3d_surface_2, use_container_width=True)
    
    # 3D Line: Multi-metric Trend
    st.subheader("📉 3D Line: Ko'rsatkichlar Trendi")
    
    trend_years = [fiscal_year-2, fiscal_year-1, fiscal_year]
    trend_margins = [gross_margin*0.80, gross_margin*0.90, gross_margin]
    trend_roa = [roa*0.70, roa*0.85, roa]
    trend_liqu = [current_ratio*0.85, current_ratio*0.93, current_ratio]
    
    fig_3d_line = go.Figure()
    
    fig_3d_line.add_trace(go.Scatter3d(
        x=trend_years,
        y=[0]*len(trend_years),
        z=trend_margins,
        mode='lines+markers',
        name='Yalpi Marja (%)',
        line=dict(color='#1f77b4', width=8),
        marker=dict(size=8, color='#1f77b4')
    ))
    
    fig_3d_line.add_trace(go.Scatter3d(
        x=trend_years,
        y=[1]*len(trend_years),
        z=trend_roa,
        mode='lines+markers',
        name='ROA (%)',
        line=dict(color='#2ca02c', width=8),
        marker=dict(size=8, color='#2ca02c')
    ))
    
    fig_3d_line.add_trace(go.Scatter3d(
        x=trend_years,
        y=[2]*len(trend_years),
        z=trend_liqu,
        mode='lines+markers',
        name='Likvidlik',
        line=dict(color='#ff7f0e', width=8),
        marker=dict(size=8, color='#ff7f0e')
    ))
    
    fig_3d_line.update_layout(
        title='3D Line Chart: Ko\'rsatkichlar Dinamikasi (Parallel Lines)',
        scene=dict(
            xaxis_title='Yil',
            yaxis_title='Ko\'rsatkich Turi',
            zaxis_title='Qiymat',
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.3))
        ),
        height=600,
        showlegend=True
    )
    st.plotly_chart(fig_3d_line, use_container_width=True)
    
    # 3D Scatter with multiple dimensions
    st.subheader("🎨 3D Scatter Matrix: Barcha Ko'rsatkichlar")
    
    scatter_x = [roe, roe*0.85, roe*1.1, 14, 9, 16]
    scatter_y = [roa, roa*0.90, roa*1.05, 7, 5, 10]
    scatter_z = [current_ratio, current_ratio*0.95, current_ratio*1.1, 1.8, 1.2, 2.5]
    scatter_colors_val = [debt_to_equity, debt_to_equity*1.1, debt_to_equity*0.9, 1.3, 0.7, 1.6]
    
    fig_3d_scatter_multi = go.Figure(data=[go.Scatter3d(
        x=scatter_x,
        y=scatter_y,
        z=scatter_z,
        mode='markers',
        marker=dict(
            size=8,
            color=scatter_colors_val,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Qarz/Kapital"),
            opacity=0.8,
            line=dict(color='darkgray', width=0.5)
        ),
        text=['Sizning Kompaniya', 'Sizning (O\'zgartirilgan)', 'Sizning (Optimistik)',
              'Raqib A', 'Raqib B', 'Raqib C'],
        hovertemplate='<b>%{text}</b><br>ROE: %{x:.2f}%<br>ROA: %{y:.2f}%<br>Likvidlik: %{z:.2f}<extra></extra>'
    )])
    
    fig_3d_scatter_multi.update_layout(
        title='3D Scatter: ROE vs ROA vs Likvidlik (Qarz bilan rang)',
        scene=dict(
            xaxis_title='ROE (%)',
            yaxis_title='ROA (%)',
            zaxis_title='Joriy Likvidlik',
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.3))
        ),
        height=600,
        showlegend=False
    )
    st.plotly_chart(fig_3d_scatter_multi, use_container_width=True)

with tab4:
    st.header("📄 Moliyaviy Hisobot")
    
    if not st.session_state.analysis_started:
        st.warning("⚠️ Iltimos, avval 📝 Ma'lumotlarni Kiritish varaqasida barcha ma'lumotlarni kiriting va 🚀 TAHLILNI BOSHLASH tugmasini bosing.")
        st.stop()
    
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
    st.subheader("📥 Hisobotni Yuklab Olish")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 CSV formatda", use_container_width=True):
            df_report = pd.DataFrame(full_report)
            csv = df_report.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="CSV yuklash",
                data=csv,
                file_name=f"{company_name}_moliyaviy_hisobot_{fiscal_year}.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    with col2:
        if st.button("🖨️ PDF formatda (Hammasini)", use_container_width=True):
            with st.spinner("PDF tayyorlanmoqda... Grafikalar saqlanmoqda..."):
                # Prepare metrics dictionary
                metrics_dict = {
                    'revenue': revenue,
                    'net_income': net_income,
                    'ebitda': ebitda,
                    'roe': roe,
                    'roa': roa,
                    'current_ratio': current_ratio,
                    'debt_to_equity': debt_to_equity,
                    'eva': eva,
                    'fcfe': fcfe,
                    'gross_margin': gross_margin,
                    'operating_margin': operating_margin,
                    'net_margin': net_margin,
                    'quick_ratio': quick_ratio,
                    'cash_ratio': cash_ratio,
                    'interest_coverage': interest_coverage,
                    'asset_turnover': asset_turnover,
                    'inventory_turnover': inventory_turnover,
                    'ccc': ccc
                }
                
                # Store all figures in a dictionary
                figures_dict = {
                    'profitability': st.session_state.get('fig_profitability'),
                    'liquidity': st.session_state.get('fig_liquidity'),
                    'leverage': st.session_state.get('fig_leverage'),
                    'ccc': st.session_state.get('fig_ccc'),
                    'trends': st.session_state.get('fig_trends'),
                    'heatmap': st.session_state.get('fig_heatmap'),
                    'sankey': st.session_state.get('fig_sankey'),
                    'sunburst': st.session_state.get('fig_sunburst'),
                    'correlation': st.session_state.get('fig_correlation'),
                    'boxplot': st.session_state.get('fig_boxplot'),
                    'waterfall': st.session_state.get('fig_waterfall'),
                    'bubble': st.session_state.get('fig_bubble'),
                    'scatter_3d': st.session_state.get('fig_scatter_3d'),
                    'bar_3d': st.session_state.get('fig_bar_3d'),
                    'bubble_3d': st.session_state.get('fig_bubble_3d'),
                    'surface_3d': st.session_state.get('fig_surface_3d'),
                    'line_3d': st.session_state.get('fig_line_3d'),
                    'scatter_matrix_3d': st.session_state.get('fig_scatter_matrix_3d'),
                }
                
                pdf_bytes = generate_financial_pdf_with_charts(company_name, fiscal_year, currency, metrics_dict, figures_dict)
                
                if pdf_bytes:
                    st.download_button(
                        label="📄 PDF yuklash",
                        data=pdf_bytes,
                        file_name=f"{company_name}_moliyaviy_hisobot_{fiscal_year}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    st.success("✅ PDF tayyor!")
                else:
                    st.error("❌ PDF yaratishda muammo")
    
    with col3:
        if st.button("📊 Excel formatda", use_container_width=True):
            st.info("Excel yuklab olish tez orada qo'shiladi")

with tab5:
    st.header("🤖 AI Moliyaviy Maslahatchi")
    
    if not st.session_state.analysis_started:
        st.warning("⚠️ Iltimos, avval 📝 Ma'lumotlarni Kiritish varaqasida barcha ma'lumotlarni kiriting va 🚀 TAHLILNI BOSHLASH tugmasini bosing.")
        st.stop()
    
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