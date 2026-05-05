# =============================================================================
# 🚀 ASSERTIF CORRETORA - DASHBOARD FINANCEIRO PREMIUM
# =============================================================================
# Dashboard interativo com rankings, filtros e visualizações profissionais
# Versão: 2.1 PREMIUM - STREAMLIT + REPORTLAB (LANDSCAPE)
# Para rodar: streamlit run dashboard_assertif.py
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import warnings
from datetime import datetime
import base64
import os

# ReportLab imports para PDF
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

warnings.filterwarnings('ignore')

# =============================================================================
# 🎨 CONFIGURAÇÕES DE ESTILO PREMIUM
# =============================================================================

CORES = {
    'primaria': '#667eea',
    'secundaria': '#764ba2',
    'sucesso': '#28a745',
    'perigo': '#dc3545',
    'alerta': '#ffc107',
    'info': '#17a2b8',
    'escuro': '#1E3A5F',
    'claro': '#f8f9fa',
    'gradiente': ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe']
}

def formatar_moeda(valor):
    try:
        if pd.isna(valor) or valor == 0:
            return "R$ 0,00"
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return str(valor)

def criar_cartao_kpi_html(titulo, valor, subtitulo="", cor=CORES['primaria'], icone="📊"):
    html = f"""
    <div style="
        background: linear-gradient(135deg, {cor} 0%, {cor}cc 100%);
        padding: 25px 20px;
        border-radius: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 12px 40px rgba(0,0,0,0.25);
        margin: 12px;
        min-width: 220px;
        border: 1px solid rgba(255,255,255,0.2);
    ">
        <div style="font-size: 2.5rem; margin-bottom: 8px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">{icone}</div>
        <div style="font-size: 1rem; font-weight: 600; opacity: 1; margin-top: 8px; text-transform: uppercase; letter-spacing: 1px; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">{titulo}</div>
        <div style="font-size: 2rem; font-weight: 800; margin: 12px 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">{valor}</div>
        <div style="font-size: 0.9rem; font-weight: 500; opacity: 0.95; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">{subtitulo}</div>
    </div>
    """
    return html

# =============================================================================
# 📄 CLASSE PARA GERAÇÃO DE PDF COM REPORTLAB (OPTIMIZED LANDSCAPE)
# =============================================================================

class PDFDashboardGenerator:
    def __init__(self, filename="Assertif_Dashboard_Premium.pdf"):
        self.filename = filename
        self.styles = getSampleStyleSheet()
        self.largura_util = 27.7 * cm # A4 Landscape menos margens
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        self.styles.add(ParagraphStyle(
            name='MainTitle', parent=self.styles['Heading1'], fontSize=28,
            textColor=colors.white, alignment=TA_CENTER, spaceAfter=10, fontName='Helvetica-Bold'
        ))
        self.styles.add(ParagraphStyle(
            name='SubTitle', parent=self.styles['Normal'], fontSize=14,
            textColor=colors.white, alignment=TA_CENTER, spaceAfter=20, fontName='Helvetica'
        ))
        self.styles.add(ParagraphStyle(
            name='SectionTitle', parent=self.styles['Heading2'], fontSize=16,
            textColor=HexColor('#1E3A5F'), alignment=TA_LEFT, spaceAfter=12, spaceBefore=20, fontName='Helvetica-Bold'
        ))
    
    def _create_header_table(self):
        header_data = [
            [Paragraph("📊 ASSERTIF CORRETORA", self.styles['MainTitle'])],
            [Paragraph("Dashboard Financeiro Premium | Relatório de Resultados 2026", self.styles['SubTitle'])],
            [Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}", self.styles['SubTitle'])]
        ]
        header_table = Table(header_data, colWidths=[self.largura_util])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), HexColor('#667eea')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, 0), 20),
            ('BOTTOMPADDING', (0, -1), (-1, -1), 20),
            ('ROUNDEDCORNERS', [15, 15, 15, 15]),
        ]))
        return header_table
    
    def _create_kpi_table(self, kpis):
        kpi_data = []
        row = []
        col_width = self.largura_util / 4
        for i, kpi in enumerate(kpis):
            cell_content = f"""
            <para align="center">
            <font size="24">{kpi.get('icone', '📊')}</font><br/>
            <font size="10" color="white"><b>{kpi['titulo']}</b></font><br/>
            <font size="18" color="white"><b>{kpi['valor']}</b></font><br/>
            <font size="8" color="white">{kpi.get('subtitulo', '')}</font>
            </para>
            """
            row.append(Paragraph(cell_content, self.styles['Normal']))
            if (i + 1) % 4 == 0 or i == len(kpis) - 1:
                while len(row) < 4: row.append('')
                kpi_data.append(row)
                row = []
        
        kpi_table = Table(kpi_data, colWidths=[col_width] * 4)
        style_commands = [('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('TOPPADDING', (0, 0), (-1, -1), 15), ('BOTTOMPADDING', (0, 0), (-1, -1), 15)]
        cores_kpi = [HexColor('#667eea'), HexColor('#28a745'), HexColor('#dc3545'), HexColor('#764ba2')]
        for i in range(4):
            style_commands.append(('BACKGROUND', (i, 0), (i, 0), cores_kpi[i]))
        kpi_table.setStyle(TableStyle(style_commands))
        return kpi_table

    def _create_section_header(self, titulo, cor=HexColor('#667eea')):
        section_table = Table([[Paragraph(f"<font color='white'><b>{titulo}</b></font>", self.styles['Normal'])]], colWidths=[self.largura_util])
        section_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), cor), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('TOPPADDING', (0, 0), (-1, -1), 10), ('BOTTOMPADDING', (0, 0), (-1, -1), 10), ('LEFTPADDING', (0, 0), (-1, -1), 15)]))
        return section_table

    def _create_data_table(self, headers, data, col_widths=None):
        table_data = [headers] + data
        if col_widths is None: col_widths = [self.largura_util / len(headers)] * len(headers)
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        style = [
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#e8e8e8')),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]
        for i in range(1, len(table_data)):
            if i % 2 == 0: style.append(('BACKGROUND', (0, i), (-1, i), HexColor('#f8f9fa')))
        table.setStyle(TableStyle(style))
        return table

    def _create_resumo_executivo_table(self):
        data = [
            ['INDICADOR', 'VALOR'],
            ['💰 RECEITA BRUTA TOTAL', 'R$ 180.797,00'],
            ['📦 PRODUÇÃO DIRETA', ''],
            ['    Receita Bruta', 'R$ 180.522,00'],
            ['    Impostos Diretos', '(R$ 31.465,00)'],
            ['    Custo Operacional (D.A)', '(R$ 15.045,00)'],
            ['    Co-Corretagem', 'R$ 839,00'],
            ['    Rebate AAI', '(R$ 51.192,00)'],
            ['(=) Margem de Contribuição', 'R$ 83.658,00'],
            ['    Despesas', '(R$ 29.104,00)'],
            ['    Folha + Terceiros', '(R$ 16.946,00)'],
            ['EBITDA', 'R$ 37.608,00'],
            ['🎯 RESULTADO OPERACIONAL TOTAL', 'R$ 35.266,00'],
            ['📊 DISTRIBUIÇÃO DO RESULTADO', ''],
            ['    Distribuição Principal', 'R$ 24.575,00'],
            ['    Distribuição Secundária', 'R$ 10.691,00'],
        ]
        table = Table(data, colWidths=[self.largura_util * 0.7, self.largura_util * 0.3])
        style = [
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1E3A5F')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#e8e8e8')),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]
        # Destaques
        style.append(('BACKGROUND', (0, 12), (-1, 12), HexColor('#a5d6a7')))
        style.append(('FONTNAME', (0, 12), (-1, 12), 'Helvetica-Bold'))
        table.setStyle(TableStyle(style))
        return table

    def generate_pdf(self, df_seg=None, df_prod=None, df_orig=None, df_cli=None, df_cat=None):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=1*cm, leftMargin=1*cm, topMargin=1*cm, bottomMargin=1*cm)
        elements = []
        
        elements.append(self._create_header_table())
        elements.append(Spacer(1, 15))
        
        kpis = [
            {'titulo': 'FATURAMENTO YTD', 'valor': 'R$ 180.797', 'subtitulo': 'Jan - Abr 2026', 'icone': '💰'},
            {'titulo': 'RESULTADO TOTAL', 'valor': 'R$ 35.266', 'subtitulo': 'Lucro Operacional', 'icone': '📈'},
            {'titulo': 'DESPESAS', 'valor': 'R$ 29.104', 'subtitulo': 'Custo Operacional', 'icone': '💸'},
            {'titulo': 'EBITDA', 'valor': 'R$ 37.608', 'subtitulo': 'Performance', 'icone': '🎯'},
        ]
        elements.append(self._create_kpi_table(kpis))
        elements.append(Spacer(1, 15))
        
        elements.append(self._create_section_header("📋 RESUMO EXECUTIVO FINANCEIRO", HexColor('#1E3A5F')))
        elements.append(self._create_resumo_executivo_table())
        
        elements.append(PageBreak())
        
        elements.append(self._create_section_header("🏆 RANKING DE SEGURADORAS E CLIENTES", HexColor('#764ba2')))
        if df_seg is not None:
            seg_data = [[f"#{i+1}", str(r['Seguradora'])[:40], formatar_moeda(r['Total']), f"{r['% do Total']:.1f}%"] for i, (_, r) in enumerate(df_seg.head(10).iterrows())]
            elements.append(self._create_data_table(['Ranking', 'Seguradora', 'Comissão', '%'], seg_data))
        
        elements.append(Spacer(1, 15))
        
        elements.append(self._create_section_header("🤝 DISTRIBUIÇÃO DE RESULTADOS ACUMULADA", HexColor('#6f42c1')))
        dist_data = [['Distribuição Principal', 'R$ 24.575,00'], ['Distribuição Secundária', 'R$ 10.691,00'], ['TOTAL DISTRIBUÍDO', 'R$ 35.266,00']]
        elements.append(self._create_data_table(['Tipo de Distribuição', 'Valor'], dist_data))

        doc.build(elements)
        return buffer.getvalue()

# =============================================================================
# 🎯 APLICAÇÃO STREAMLIT PRINCIPAL
# =============================================================================

def main():
    st.set_page_config(page_title="Assertif Corretora - Dashboard Premium", page_icon="📊", layout="wide")
    
    st.markdown("""
    <style>
        .main-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 20px; text-align: center; margin-bottom: 30px; color: white; }
        .stMetric { background: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 5px solid #667eea; }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="main-header"><h1>📊 ASSERTIF CORRETORA</h1><h2>Gestão Financeira Estratégica</h2></div>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.header("📁 Upload")
        uploaded_file = st.file_uploader("Planilha Financeira", type=['xlsx'])
        st.markdown("---")
        st.info("💡 Versão 2.1 - Foco em Resultados Operacionais")

    # Mock/Data Processing Logic
    df_receitas_clean, df_seg, df_prod, df_orig, df_cli, df_cat = None, None, None, None, None, None
    
    if uploaded_file:
        dados = pd.read_excel(uploaded_file, sheet_name=None)
        df_receitas = dados.get('ASSERTIF DIRETO', pd.DataFrame())
        if not df_receitas.empty:
            col_comissao = df_receitas.columns[12]
            df_receitas[col_comissao] = pd.to_numeric(df_receitas[col_comissao].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
            df_seg = df_receitas.groupby(df_receitas.columns[4])[col_comissao].sum().reset_index()
            df_seg.columns = ['Seguradora', 'Total']
            df_seg['% do Total'] = (df_seg['Total'] / df_seg['Total'].sum() * 100)
            df_seg = df_seg.sort_values('Total', ascending=False)

    # --- KPIs ---
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.markdown(criar_cartao_kpi_html("FATURAMENTO", "R$ 180.797", "Total Bruto YTD", "#667eea", "💰"), unsafe_allow_html=True)
    with col2: st.markdown(criar_cartao_kpi_html("RESULTADO TOTAL", "R$ 35.266", "Lucro Operacional", "#28a745", "📈"), unsafe_allow_html=True)
    with col3: st.markdown(criar_cartao_kpi_html("DESPESAS", "R$ 29.104", "Custo Operacional", "#dc3545", "💸"), unsafe_allow_html=True)
    with col4: st.markdown(criar_cartao_kpi_html("EBITDA", "R$ 37.608", "Resultado Antes Juros", "#764ba2", "🎯"), unsafe_allow_html=True)

    # --- Gráficos de Distribuição ---
    st.markdown("### 🤝 Distribuição de Resultados")
    c1, c2 = st.columns(2)
    with c1:
        fig = px.pie(values=[24575, 10691], names=['Principal', 'Secundária'], color_discrete_sequence=['#667eea', '#f5576c'], hole=0.5)
        fig.update_layout(title="Divisão de Lucros")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        resumo_df = pd.DataFrame({
            'Categoria': ['Resultado Operacional', 'Distribuição Principal', 'Distribuição Secundária'],
            'Valor': [35266, 24575, 10691]
        })
        st.table(resumo_df)

    # --- Exportação ---
    st.markdown("---")
    if st.button("📄 GERAR RELATÓRIO EXECUTIVO PDF", type="primary"):
        gen = PDFDashboardGenerator()
        pdf = gen.generate_pdf(df_seg=df_seg)
        st.download_button("⬇️ Baixar Relatório Landscape", data=pdf, file_name="Relatorio_Assertif_2026.pdf", mime="application/pdf")

if __name__ == "__main__":
    main()
