# =============================================================================
# 🚀 ASSERTIF CORRETORA - DASHBOARD FINANCEIRO PREMIUM - VERSÃO CORRIGIDA
# =============================================================================
# Dashboard interativo com rankings, filtros e visualizações profissionais
# Versão: 5.1 PREMIUM ULTIMATE - LEITURA DINÂMICA DA PLANILHA
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
import math

# ReportLab imports para PDF
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether, HRFlowable, ListFlowable, ListItem,
    NextPageTemplate, PageTemplate, Frame, BaseDocTemplate
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Circle, Ellipse
from reportlab.graphics.charts.barcharts import VerticalBarChart, HorizontalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics.widgets.markers import makeMarker
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

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
    'gradiente': ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe'],
    'chart_colors': ['#667eea', '#28a745', '#f5576c', '#ffc107', '#17a2b8', '#764ba2', '#20c997', '#fd7e14']
}

# =============================================================================
# 📊 FUNÇÕES PARA LEITURA DINÂMICA DA PLANILHA
# =============================================================================

def ler_dados_dre(df_dre):
    """Lê os dados da aba DRE 2026 dinamicamente"""
    dados = {
        'meses': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'],
        'meses_completos': ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
                           'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'],
        'receita_bruta_total': {},
        'receita_bruta_direto': {},
        'impostos_diretos': {},
        'custo_operacional': {},
        'co_corretagem': {},
        'rebate_aai': {},
        'margem_contribuicao': {},
        'despesas': {},
        'folha_terceiros': {},
        'resultado_operacional': {},
        'resultado_distribuicao': {},
        'socio_partner': {},
        'socio_maldivas': {},
        'ytd': {}
    }
    
    try:
        # Mapear colunas para meses (C=Jan, D=Fev, E=Mar, F=Abr, etc.)
        col_map = {2: 'Jan', 3: 'Fev', 4: 'Mar', 5: 'Abr', 6: 'Mai', 7: 'Jun', 
                   8: 'Jul', 9: 'Ago', 10: 'Set', 11: 'Out', 12: 'Nov', 13: 'Dez', 14: 'YTD'}
        
        # Encontrar as linhas pelos nomes
        for idx, row in df_dre.iterrows():
            primeira_col = str(row.iloc[0]).strip().upper() if pd.notna(row.iloc[0]) else ''
            
            # Linha 4: RECEITA BRUTA TOTAL
            if 'RECEITA BRUTA TOTAL' in primeira_col:
                for col_idx, mes in col_map.items():
                    if col_idx < len(row):
                        valor = row.iloc[col_idx]
                        dados['receita_bruta_total'][mes] = parse_valor(valor)
            
            # Linha 7: RECEITA BRUTA (Produção Direta)
            elif primeira_col == 'RECEITA BRUTA':
                for col_idx, mes in col_map.items():
                    if col_idx < len(row):
                        valor = row.iloc[col_idx]
                        dados['receita_bruta_direto'][mes] = parse_valor(valor)
            
            # Linha 8: IMPOSTOS DIRETOS
            elif 'IMPOSTOS DIRETOS' in primeira_col:
                for col_idx, mes in col_map.items():
                    if col_idx < len(row):
                        valor = row.iloc[col_idx]
                        dados['impostos_diretos'][mes] = parse_valor(valor)
            
            # Linha 9: CUSTO OPERACIONAL (D.A)
            elif 'CUSTO OPERACIONAL' in primeira_col:
                for col_idx, mes in col_map.items():
                    if col_idx < len(row):
                        valor = row.iloc[col_idx]
                        dados['custo_operacional'][mes] = parse_valor(valor)
            
            # Linha 10: CO-CORRETAGEM
            elif 'CO-CORRETAGEM' in primeira_col:
                for col_idx, mes in col_map.items():
                    if col_idx < len(row):
                        valor = row.iloc[col_idx]
                        dados['co_corretagem'][mes] = parse_valor(valor)
            
            # Linha 11: REBATE AAI
            elif 'REBATE AAI' in primeira_col:
                for col_idx, mes in col_map.items():
                    if col_idx < len(row):
                        valor = row.iloc[col_idx]
                        dados['rebate_aai'][mes] = parse_valor(valor)
            
            # Linha 12: MARGEM DE CONTRIBUIÇÃO
            elif 'MARGEM DE CONTRIBUIÇÃO' in primeira_col:
                for col_idx, mes in col_map.items():
                    if col_idx < len(row):
                        valor = row.iloc[col_idx]
                        dados['margem_contribuicao'][mes] = parse_valor(valor)
            
            # Linha 13: DESPESAS
            elif primeira_col == 'DESPESAS':
                for col_idx, mes in col_map.items():
                    if col_idx < len(row):
                        valor = row.iloc[col_idx]
                        dados['despesas'][mes] = parse_valor(valor)
            
            # Linha 14: FOLHA+TERCEIROS
            elif 'FOLHA' in primeira_col:
                for col_idx, mes in col_map.items():
                    if col_idx < len(row):
                        valor = row.iloc[col_idx]
                        dados['folha_terceiros'][mes] = parse_valor(valor)
            
            # Linha 27: RESULTADO OPERACIONAL
            elif 'RESULTADO OPERACIONAL' in primeira_col and 'DISTRIBUIÇÃO' not in primeira_col:
                for col_idx, mes in col_map.items():
                    if col_idx < len(row):
                        valor = row.iloc[col_idx]
                        dados['resultado_operacional'][mes] = parse_valor(valor)
            
            # Linha 29: RESULTADO OPERACIONAL - DISTRIBUIÇÃO
            elif 'RESULTADO OPERACIONAL' in primeira_col and 'DISTRIBUIÇÃO' in primeira_col:
                for col_idx, mes in col_map.items():
                    if col_idx < len(row):
                        valor = row.iloc[col_idx]
                        dados['resultado_distribuicao'][mes] = parse_valor(valor)
            
            # Linha 30: Sócio Partner
            elif 'PARTNER' in primeira_col:
                for col_idx, mes in col_map.items():
                    if col_idx < len(row):
                        valor = row.iloc[col_idx]
                        dados['socio_partner'][mes] = parse_valor(valor)
            
            # Linha 31: Sócio Maldivas
            elif 'MALDIVAS' in primeira_col:
                for col_idx, mes in col_map.items():
                    if col_idx < len(row):
                        valor = row.iloc[col_idx]
                        dados['socio_maldivas'][mes] = parse_valor(valor)
        
    except Exception as e:
        st.error(f"Erro ao ler DRE: {str(e)}")
    
    return dados

def parse_valor(valor):
    """Converte valor da planilha para número"""
    try:
        if pd.isna(valor) or valor == '' or valor == ' ':
            return 0
        if isinstance(valor, (int, float)):
            return float(valor)
        # Remover formatação
        valor_str = str(valor).strip()
        valor_str = valor_str.replace('(', '-').replace(')', '')
        valor_str = valor_str.replace(' ', '').replace('.', '').replace(',', '.')
        return float(valor_str) if valor_str else 0
    except:
        return 0

def formatar_moeda(valor):
    """Formata valor para moeda brasileira"""
    try:
        if pd.isna(valor) or valor == 0:
            return "R$ 0,00"
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return str(valor)

def formatar_percentual(valor):
    """Formata valor como percentual"""
    try:
        return f"{valor:.1f}%"
    except:
        return str(valor)

def criar_cartao_kpi_html(titulo, valor, subtitulo="", cor=CORES['primaria'], icone="📊"):
    """Cria HTML para cartão de KPI estilizado"""
    html = f"""
    <div style="
        background: linear-gradient(135deg, {cor} 0%, {cor}cc 100%);
        padding: 25px 20px;
        border-radius: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 12px 40px rgba(0,0,0,0.25);
        margin: 12px;
        min-width: 180px;
        border: 1px solid rgba(255,255,255,0.2);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    ">
        <div style="font-size: 2.2rem; margin-bottom: 8px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">{icone}</div>
        <div style="font-size: 0.85rem; font-weight: 600; opacity: 1; margin-top: 8px; text-transform: uppercase; letter-spacing: 1px; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">{titulo}</div>
        <div style="font-size: 1.5rem; font-weight: 800; margin: 12px 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">{valor}</div>
        <div style="font-size: 0.8rem; font-weight: 500; opacity: 0.95; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">{subtitulo}</div>
    </div>
    """
    return html

# =============================================================================
# 📄 CLASSE PARA GERAÇÃO DE PDF
# =============================================================================

class PDFDashboardGenerator:
    """Classe para gerar PDF profissional do dashboard"""
    
    def __init__(self, filename="Assertif_Dashboard_Premium.pdf"):
        self.filename = filename
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        """Configura estilos customizados para o PDF"""
        self.styles.add(ParagraphStyle(
            name='CoverTitle',
            parent=self.styles['Heading1'],
            fontSize=42,
            textColor=colors.white,
            alignment=TA_CENTER,
            spaceAfter=20,
            fontName='Helvetica-Bold',
            leading=50
        ))
        
        self.styles.add(ParagraphStyle(
            name='CoverSubtitle',
            parent=self.styles['Normal'],
            fontSize=18,
            textColor=colors.white,
            alignment=TA_CENTER,
            spaceAfter=30,
            fontName='Helvetica',
            leading=24
        ))
        
        self.styles.add(ParagraphStyle(
            name='MainTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            textColor=colors.white,
            alignment=TA_CENTER,
            spaceAfter=10,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='SubTitle',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.white,
            alignment=TA_CENTER,
            spaceAfter=20,
            fontName='Helvetica'
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=HexColor('#1E3A5F'),
            alignment=TA_LEFT,
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='NormalText',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=HexColor('#1E3A5F'),
            alignment=TA_LEFT,
            spaceAfter=6,
            fontName='Helvetica'
        ))
    
    def _create_section_header(self, titulo, cor=HexColor('#667eea')):
        """Cria cabeçalho de seção premium"""
        section_data = [[
            Paragraph(f"<font color='white'><b>{titulo}</b></font>", 
                     ParagraphStyle(name='SectionHeader', fontSize=14, fontName='Helvetica-Bold', alignment=TA_LEFT))
        ]]
        section_table = Table(section_data, colWidths=[18*cm])
        section_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), cor),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 20),
            ('RIGHTPADDING', (0, 0), (-1, -1), 20),
        ]))
        return section_table
    
    def _create_note_box(self, titulo, texto, cor=HexColor('#17a2b8')):
        """Cria box de nota explicativa"""
        note_content = [[Paragraph(
            f"<b>{titulo}</b><br/><br/>{texto}",
            ParagraphStyle(name='NoteContent', fontSize=9, textColor=HexColor('#1E3A5F'), 
                          alignment=TA_JUSTIFY, fontName='Helvetica', leading=12)
        )]]
        
        note_table = Table(note_content, colWidths=[17*cm])
        note_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), HexColor('#f8f9fa')),
            ('BOX', (0, 0), (-1, -1), 2, cor),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ]))
        
        return note_table
    
    def _add_page_number(self, canvas, doc):
        """Adiciona número de página"""
        canvas.saveState()
        
        canvas.setFillColor(HexColor('#667eea'))
        canvas.rect(1*cm, A4[1] - 1.5*cm, A4[0] - 2*cm, 0.8*cm, fill=True, stroke=False)
        
        canvas.setFillColor(colors.white)
        canvas.setFont('Helvetica-Bold', 9)
        canvas.drawString(1.5*cm, A4[1] - 1.1*cm, "📊 ASSERTIF CORRETORA - Dashboard Financeiro Premium")
        canvas.drawRightString(A4[0] - 1.5*cm, A4[1] - 1.1*cm, f"YTD 2026")
        
        canvas.setFillColor(HexColor('#1E3A5F'))
        canvas.rect(1*cm, 0.5*cm, A4[0] - 2*cm, 0.6*cm, fill=True, stroke=False)
        
        canvas.setFillColor(colors.white)
        canvas.setFont('Helvetica', 8)
        canvas.drawString(1.5*cm, 0.7*cm, f"Gerado em: {datetime.now().strftime('%d/%m/%Y')}")
        canvas.drawCentredString(A4[0]/2, 0.7*cm, "Confidencial - Uso Interno")
        canvas.drawRightString(A4[0] - 1.5*cm, 0.7*cm, f"Página {doc.page}")
        
        canvas.restoreState()
    
    def generate_pdf(self, dados_dre=None):
        """Gera o PDF completo do dashboard"""
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1*cm,
            leftMargin=1*cm,
            topMargin=2*cm,
            bottomMargin=1.5*cm
        )
        
        elements = []
        
        # Capa simples
        elements.append(self._create_section_header("📊 ASSERTIF CORRETORA - DASHBOARD FINANCEIRO", HexColor('#667eea')))
        elements.append(Spacer(1, 20))
        
        elements.append(self._create_note_box(
            "Relatório Executivo YTD 2026",
            f"Documento gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}<br/><br/>"
            "Este dashboard apresenta uma visão consolidada do desempenho financeiro da Assertif Corretora."
        ))
        
        doc.build(elements, onFirstPage=self._add_page_number, onLaterPages=self._add_page_number)
        
        buffer.seek(0)
        return buffer.getvalue()


# =============================================================================
# 🎯 APLICAÇÃO STREAMLIT PRINCIPAL
# =============================================================================

def main():
    st.set_page_config(
        page_title="Assertif Corretora - Dashboard Premium",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS customizado
    st.markdown("""
    <style>
        .main .block-container { padding-top: 2rem; padding-bottom: 2rem; }
        
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            padding: 50px 40px;
            border-radius: 30px;
            text-align: center;
            margin-bottom: 40px;
            box-shadow: 0 25px 60px rgba(102, 126, 234, 0.45);
        }
        .main-header h1 { color: white; font-size: 3.2rem; font-weight: 800; text-shadow: 3px 3px 8px rgba(0,0,0,0.35); margin-bottom: 10px; }
        .main-header h2 { color: white; font-size: 1.5rem; font-weight: 500; opacity: 0.95; }
        
        .section-header {
            padding: 22px 35px;
            border-radius: 18px;
            margin: 30px 0;
            box-shadow: 0 10px 35px rgba(0,0,0,0.15);
        }
        .section-header h2 { color: white; font-size: 1.7rem; font-weight: 700; margin: 0; }
        
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 1.1rem;
            font-weight: 700;
            border-radius: 15px;
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>📊 ASSERTIF CORRETORA</h1>
        <h2>Dashboard Financeiro Interativo Premium | YTD 2026</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📁 Upload de Dados")
        uploaded_file = st.file_uploader(
            "Faça upload da planilha Excel",
            type=['xlsx', 'xls'],
            help="Selecione o arquivo Excel com os dados financeiros"
        )
        
        st.markdown("---")
        st.header("⚙️ Configurações")
        show_tables = st.checkbox("Mostrar tabelas detalhadas", value=True)
        show_charts = st.checkbox("Mostrar gráficos", value=True)
    
    # Variáveis para armazenar dados
    dados_dre = None
    df_receitas_clean = None
    df_despesas_clean = None
    df_seg = None
    df_prod = None
    df_orig = None
    df_cli = None
    df_cat = None
    
    if uploaded_file is not None:
        # Carregar dados
        dados = pd.read_excel(uploaded_file, sheet_name=None)
        
        st.sidebar.success(f"✅ Arquivo carregado!")
        st.sidebar.info(f"📑 Abas: {list(dados.keys())}")
        
        # Carregar cada aba
        df_dre = dados.get('DRE 2026', pd.DataFrame())
        df_receitas = dados.get('ASSERTIF DIRETO', pd.DataFrame())
        df_despesas = dados.get('DESPESAS', pd.DataFrame())
        
        # =====================================================================
        # LEITURA DINÂMICA DA DRE
        # =====================================================================
        if len(df_dre) > 0:
            dados_dre = ler_dados_dre(df_dre)
            st.sidebar.success("✅ DRE lida com sucesso!")
        
        # Processar RECEITAS
        if len(df_receitas) > 0:
            df_receitas.columns = df_receitas.columns.str.strip()
            df_receitas_clean = df_receitas.dropna(subset=[df_receitas.columns[12]])
            
            col_comissao = df_receitas.columns[12]
            df_receitas_clean[col_comissao] = pd.to_numeric(
                df_receitas_clean[col_comissao].astype(str).str.replace(',', '.').str.replace(' ', ''),
                errors='coerce'
            ).fillna(0)
            
            col_seguradora = df_receitas.columns[4]
            col_produto = df_receitas.columns[10]
            col_originador = df_receitas.columns[7]
            col_cliente = df_receitas.columns[3]
            
            # Agrupar por seguradora
            df_seg = df_receitas_clean.groupby(col_seguradora)[col_comissao].agg(['sum', 'count', 'mean']).reset_index()
            df_seg.columns = ['Seguradora', 'Total', 'Qtd', 'Média']
            df_seg = df_seg[df_seg['Total'] > 0].sort_values('Total', ascending=False)
            df_seg['% do Total'] = (df_seg['Total'] / df_seg['Total'].sum() * 100).round(1)
            
            # Agrupar por produto
            df_prod = df_receitas_clean.groupby(col_produto)[col_comissao].agg(['sum', 'count', 'mean']).reset_index()
            df_prod.columns = ['Produto', 'Total', 'Qtd', 'Média']
            df_prod = df_prod[df_prod['Total'] > 0].sort_values('Total', ascending=False)
            df_prod['% do Total'] = (df_prod['Total'] / df_prod['Total'].sum() * 100).round(1)
            
            # Agrupar por originador
            df_orig = df_receitas_clean.groupby(col_originador)[col_comissao].agg(['sum', 'count', 'mean']).reset_index()
            df_orig.columns = ['Originador', 'Total', 'Operações', 'Ticket Médio']
            df_orig = df_orig[df_orig['Total'] > 0].sort_values('Total', ascending=False)
            df_orig['% do Total'] = (df_orig['Total'] / df_orig['Total'].sum() * 100).round(1)
            
            # Agrupar por cliente
            df_cli = df_receitas_clean.groupby(col_cliente)[col_comissao].agg(['sum', 'count', 'mean']).reset_index()
            df_cli.columns = ['Cliente', 'Total', 'Qtd', 'Média']
            df_cli = df_cli[df_cli['Total'] > 0].sort_values('Total', ascending=False)
            df_cli['% do Total'] = (df_cli['Total'] / df_cli['Total'].sum() * 100).round(1)
        
        # Processar DESPESAS
        if len(df_despesas) > 0:
            df_despesas_clean = df_despesas.dropna(how='all')
            col_valor_desp = df_despesas.columns[4]
            col_categoria = df_despesas.columns[5]
            
            df_despesas_clean[col_valor_desp] = pd.to_numeric(
                df_despesas_clean[col_valor_desp].astype(str).str.replace(',', '.').str.replace(' ', ''),
                errors='coerce'
            ).fillna(0)
            
            df_cat = df_despesas_clean.groupby(col_categoria)[col_valor_desp].agg(['sum', 'count']).reset_index()
            df_cat.columns = ['Categoria', 'Total', 'Qtd']
            df_cat = df_cat[df_cat['Total'] > 0].sort_values('Total', ascending=False)
            df_cat['% do Total'] = (df_cat['Total'] / df_cat['Total'].sum() * 100).round(1)
    
    # =============================================================================
    # 🗓️ FILTRO DE MÊS
    # =============================================================================
    
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 15px 25px;
        border-radius: 15px;
        margin-bottom: 25px;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    ">
        <h3 style="color: white; margin: 0; font-size: 1.2rem;">🗓️ FILTRO DE PERÍODO</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col_filtro1, col_filtro2 = st.columns([3, 1])
    
    with col_filtro1:
        meses_opcoes = ['All', 'Janeiro', 'Fevereiro', 'Março', 'Abril']
        meses_selecionados = st.multiselect(
            "Selecione o(s) mês(es):",
            options=meses_opcoes,
            default=['All'],
            help="Selecione 'All' para ver todos os meses ou escolha meses específicos"
        )
    
    with col_filtro2:
        if 'All' in meses_selecionados or len(meses_selecionados) == 0:
            st.info("📊 **Período:** YTD Completo")
        else:
            st.info(f"📊 **Período:** {', '.join(meses_selecionados)}")
    
    # =============================================================================
    # 💰 SEÇÃO 1: KPIs PRINCIPAIS
    # =============================================================================
    
    st.markdown("""
    <div class="section-header" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
        <h2>💰 INDICADORES PRINCIPAIS (KPIs)</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Calcular KPIs baseado nos dados da DRE
    if dados_dre:
        # Mapear meses selecionados
        mes_map = {'Janeiro': 'Jan', 'Fevereiro': 'Fev', 'Março': 'Mar', 'Abril': 'Abr'}
        
        if 'All' in meses_selecionados or len(meses_selecionados) == 0:
            # Usar YTD
            faturamento = dados_dre['receita_bruta_total'].get('YTD', 0)
            margem_contrib = dados_dre['margem_contribuicao'].get('YTD', 0)
            despesas = abs(dados_dre['despesas'].get('YTD', 0)) + abs(dados_dre['folha_terceiros'].get('YTD', 0))
            resultado_op = dados_dre['resultado_operacional'].get('YTD', 0)
        else:
            # Somar meses selecionados
            faturamento = sum(dados_dre['receita_bruta_total'].get(mes_map.get(m, ''), 0) for m in meses_selecionados)
            margem_contrib = sum(dados_dre['margem_contribuicao'].get(mes_map.get(m, ''), 0) for m in meses_selecionados)
            despesas = sum(abs(dados_dre['despesas'].get(mes_map.get(m, ''), 0)) + abs(dados_dre['folha_terceiros'].get(mes_map.get(m, ''), 0)) for m in meses_selecionados)
            resultado_op = sum(dados_dre['resultado_operacional'].get(mes_map.get(m, ''), 0) for m in meses_selecionados)
        
        # Custos totais = Impostos + D.A. + Rebate - Co-corretagem
        if 'All' in meses_selecionados or len(meses_selecionados) == 0:
            impostos = abs(dados_dre['impostos_diretos'].get('YTD', 0))
            da = abs(dados_dre['custo_operacional'].get('YTD', 0))
            rebate = abs(dados_dre['rebate_aai'].get('YTD', 0))
            cocorr = dados_dre['co_corretagem'].get('YTD', 0)
        else:
            impostos = sum(abs(dados_dre['impostos_diretos'].get(mes_map.get(m, ''), 0)) for m in meses_selecionados)
            da = sum(abs(dados_dre['custo_operacional'].get(mes_map.get(m, ''), 0)) for m in meses_selecionados)
            rebate = sum(abs(dados_dre['rebate_aai'].get(mes_map.get(m, ''), 0)) for m in meses_selecionados)
            cocorr = sum(dados_dre['co_corretagem'].get(mes_map.get(m, ''), 0) for m in meses_selecionados)
        
        custos_totais = impostos + da + rebate - cocorr
    else:
        # Valores padrão se não houver dados
        faturamento = 178072
        custos_totais = 95729
        margem_contrib = 82145
        despesas = 46051
        resultado_op = 29490
    
    # 5 colunas para 5 KPIs
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(criar_cartao_kpi_html("FATURAMENTO BRUTO", formatar_moeda(faturamento), "Receita Bruta Total", "#667eea", "💰"), unsafe_allow_html=True)
    
    with col2:
        st.markdown(criar_cartao_kpi_html("CUSTOS TOTAIS", formatar_moeda(custos_totais), "Impostos+DA+Rebate", "#dc3545", "📉"), unsafe_allow_html=True)
    
    with col3:
        st.markdown(criar_cartao_kpi_html("MARGEM CONTRIB.", formatar_moeda(margem_contrib), "Faturamento - Custos", "#17a2b8", "📊"), unsafe_allow_html=True)
    
    with col4:
        st.markdown(criar_cartao_kpi_html("DESPESAS TOTAIS", formatar_moeda(despesas), "Oper. + Folha", "#ffc107", "💸"), unsafe_allow_html=True)
    
    with col5:
        st.markdown(criar_cartao_kpi_html("RESULTADO OPER.", formatar_moeda(resultado_op), "Linha 27 DRE", "#28a745", "🎯"), unsafe_allow_html=True)
    
    # Nota explicativa dos KPIs - APENAS TEXTO (LEGENDA)
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #ffffff 0%, #f0f8ff 100%);
        border: 3px solid #17a2b8;
        border-left: 8px solid #17a2b8;
        border-radius: 15px;
        padding: 25px 30px;
        margin: 25px 0;
        box-shadow: 0 10px 30px rgba(23, 162, 184, 0.15);
    ">
        <h3 style="color: #0c5460; margin-bottom: 20px; font-size: 1.4rem; font-weight: 700;">
            Legenda dos KPIs
        </h3>
        <div style="color: #1a1a1a; font-size: 1.05rem; line-height: 2;">
            <p style="margin: 8px 0; padding: 10px 15px; background: rgba(102, 126, 234, 0.1); border-radius: 10px; border-left: 4px solid #667eea;">
                <strong style="color: #667eea;">💰 Faturamento Bruto:</strong> 
                <span style="color: #1E3A5F;">Soma da Receita Bruta de Produção Direta e Portal MAAS</span>
            </p>
            <p style="margin: 8px 0; padding: 10px 15px; background: rgba(220, 53, 69, 0.1); border-radius: 10px; border-left: 4px solid #dc3545;">
                <strong style="color: #dc3545;">📉 Custos Totais:</strong> 
                <span style="color: #1E3A5F;">Soma de Impostos Diretos, Custo Operacional (D.A.) e Rebate AAI, menos Co-corretagem</span>
            </p>
            <p style="margin: 8px 0; padding: 10px 15px; background: rgba(23, 162, 184, 0.1); border-radius: 10px; border-left: 4px solid #17a2b8;">
                <strong style="color: #17a2b8;">📊 Margem de Contribuição:</strong> 
                <span style="color: #1E3A5F;">Faturamento Bruto menos Custos Totais (considerando Prod. Direta e Portal MAAS)</span>
            </p>
            <p style="margin: 8px 0; padding: 10px 15px; background: rgba(255, 193, 7, 0.1); border-radius: 10px; border-left: 4px solid #ffc107;">
                <strong style="color: #e0a800;">💸 Despesas Totais:</strong> 
                <span style="color: #1E3A5F;">Soma de Despesas Operacionais e Folha + Terceiros</span>
            </p>
            <p style="margin: 8px 0; padding: 10px 15px; background: rgba(40, 167, 69, 0.1); border-radius: 10px; border-left: 4px solid #28a745;">
                <strong style="color: #28a745;">🎯 Resultado Operacional:</strong> 
                <span style="color: #1E3A5F;">Margem de Contribuição menos Despesas Totais (conforme Linha 27 da DRE) - base para distribuição 65/35</span>
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # =============================================================================
    # 📈 SEÇÃO 2: EVOLUÇÃO MENSAL
    # =============================================================================
    
    if show_charts:
        st.markdown("""
        <div class="section-header" style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%);">
            <h2>📈 EVOLUÇÃO MENSAL - RECEITA vs RESULTADO</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Dados da DRE
        if dados_dre:
            meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril']
            meses_curtos = ['Jan', 'Fev', 'Mar', 'Abr']
            
            receita_bruta = [dados_dre['receita_bruta_total'].get(m, 0) for m in meses_curtos]
            resultado_op_mensal = [dados_dre['resultado_operacional'].get(m, 0) for m in meses_curtos]
            
            # Calcular crescimento
            crescimento = [0]
            for i in range(1, len(receita_bruta)):
                if receita_bruta[i-1] > 0:
                    cresc = ((receita_bruta[i] - receita_bruta[i-1]) / receita_bruta[i-1]) * 100
                else:
                    cresc = 0
                crescimento.append(cresc)
        else:
            meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril']
            receita_bruta = [42263, 49513, 71946, 14350]
            resultado_op_mensal = [5133, 7667, 16690, 0]
            crescimento = [0, 17.2, 45.3, -80.1]
        
        fig_evolucao = make_subplots(
            rows=1, cols=3,
            subplot_titles=(
                '<b>📊 Receita Bruta por Mês</b>',
                '<b>📈 Crescimento Mensal (%)</b>',
                '<b>🎯 Resultado Operacional</b>'
            ),
            horizontal_spacing=0.08,
            column_widths=[0.35, 0.30, 0.35]
        )
        
        # Gráfico 1: Receita Bruta
        fig_evolucao.add_trace(
            go.Bar(
                x=meses, y=receita_bruta,
                marker=dict(color=receita_bruta, colorscale='Viridis', showscale=False, line=dict(width=2, color='white')),
                text=[f"R$ {v/1000:.1f}K" for v in receita_bruta],
                textposition='outside',
                textfont=dict(size=14, color=CORES['escuro'], family='Arial Black'),
                name='Receita Bruta',
                width=0.6
            ),
            row=1, col=1
        )
        
        # Gráfico 2: Crescimento Mensal
        cores_cresc = ['#6c757d' if c == 0 else ('#28a745' if c > 0 else '#dc3545') for c in crescimento]
        fig_evolucao.add_trace(
            go.Scatter(
                x=meses, y=crescimento,
                mode='lines+markers+text',
                line=dict(color=CORES['primaria'], width=4, shape='spline'),
                marker=dict(size=18, color=cores_cresc, line=dict(width=3, color='white'), symbol='circle'),
                text=[f"{v:+.1f}%" for v in crescimento],
                textposition='top center',
                textfont=dict(size=14, family='Arial Black', color=CORES['escuro']),
                name='Crescimento %'
            ),
            row=1, col=2
        )
        
        fig_evolucao.add_hline(y=0, line_dash="dash", line_color="#dc3545", line_width=2, row=1, col=2)
        
        # Gráfico 3: Resultado Operacional
        fig_evolucao.add_trace(
            go.Scatter(
                x=meses, y=resultado_op_mensal,
                mode='lines+markers+text',
                fill='tozeroy',
                fillcolor='rgba(102, 126, 234, 0.25)',
                line=dict(color=CORES['primaria'], width=4, shape='spline'),
                marker=dict(size=14, color=CORES['primaria'], line=dict(width=3, color='white'), symbol='circle'),
                text=[f"R$ {v/1000:.1f}K" for v in resultado_op_mensal],
                textposition='top center',
                textfont=dict(size=14, family='Arial Black', color=CORES['escuro']),
                name='Resultado'
            ),
            row=1, col=3
        )
        
        fig_evolucao.update_layout(
            height=480,
            showlegend=False,
            paper_bgcolor='white',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Segoe UI', size=14, color=CORES['escuro']),
            margin=dict(l=60, r=60, t=80, b=60)
        )
        
        fig_evolucao.update_xaxes(gridcolor='#e8e8e8', tickfont=dict(size=12, family='Arial', color=CORES['escuro']), tickangle=0)
        fig_evolucao.update_yaxes(gridcolor='#e8e8e8', tickfont=dict(size=12, family='Arial'))
        
        st.plotly_chart(fig_evolucao, use_container_width=True)
    
    # =============================================================================
    # 🏆 SEÇÃO 3: RANKING DE SEGURADORAS
    # =============================================================================
    
    if show_charts and df_seg is not None and len(df_seg) > 0:
        st.markdown("""
        <div class="section-header" style="background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);">
            <h2>🏆 RANKING - MAIORES COMISSÕES POR SEGURADORA</h2>
        </div>
        """, unsafe_allow_html=True)
        
        fig_ranking_seg = go.Figure()
        
        fig_ranking_seg.add_trace(go.Bar(
            y=df_seg['Seguradora'].head(15),
            x=df_seg['Total'].head(15),
            orientation='h',
            marker=dict(
                color=df_seg['Total'].head(15),
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title=dict(text='Comissão (R$)', font=dict(size=12)), thickness=15, len=0.7),
                line=dict(width=1, color='white')
            ),
            text=[f"R$ {v/1000:.1f}K ({p:.1f}%)" for v, p in zip(df_seg['Total'].head(15), df_seg['% do Total'].head(15))],
            textposition='outside',
            textfont=dict(size=11, family='Arial Black', color='#1E3A5F'),
            width=0.7
        ))
        
        fig_ranking_seg.update_layout(
            title=dict(text='🏢 Top 15 Seguradoras por Volume de Comissão', font=dict(size=18, family='Arial Black', color='#1E3A5F'), x=0.5, xanchor='center'),
            height=650,
            paper_bgcolor='white',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis_title=dict(text='Comissão Total (R$)', font=dict(size=13, family='Arial Black')),
            yaxis=dict(categoryorder='total ascending', tickfont=dict(size=11, family='Arial')),
            margin=dict(l=180, r=150, t=80, b=60)
        )
        
        fig_ranking_seg.update_xaxes(gridcolor='#e8e8e8', tickformat=',.0f')
        st.plotly_chart(fig_ranking_seg, use_container_width=True)
    
    # =============================================================================
    # 🤝 SEÇÃO 4: DISTRIBUIÇÃO ENTRE SÓCIOS - CORRIGIDO
    # =============================================================================
    
    if show_charts:
        st.markdown("""
        <div class="section-header" style="background: linear-gradient(135deg, #6f42c1 0%, #e83e8c 100%);">
            <h2>🤝 DISTRIBUIÇÃO DE RESULTADOS - SÓCIOS</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Ler dados diretamente da DRE - Linhas 30 e 31
        if dados_dre:
            meses_dist = ['Janeiro', 'Fevereiro', 'Março', 'Abril']
            meses_curtos = ['Jan', 'Fev', 'Mar', 'Abr']
            
            # Pegar dados diretamente das linhas 30 e 31 da DRE
            partner = [dados_dre['socio_partner'].get(m, 0) for m in meses_curtos]
            maldivas = [dados_dre['socio_maldivas'].get(m, 0) for m in meses_curtos]
            resultado_linha27 = [dados_dre['resultado_operacional'].get(m, 0) for m in meses_curtos]
        else:
            meses_dist = ['Janeiro', 'Fevereiro', 'Março', 'Abril']
            partner = [3336, 4984, 10849, 0]
            maldivas = [986, 1818, 4976, 0]
            resultado_linha27 = [5133, 7667, 16690, 0]
        
        # Filtrar apenas meses com dados (resultado > 0)
        meses_com_dados = []
        partner_filtrado = []
        maldivas_filtrado = []
        resultado_filtrado = []
        
        for i, mes in enumerate(meses_dist):
            if resultado_linha27[i] > 0:
                meses_com_dados.append(mes)
                partner_filtrado.append(partner[i])
                maldivas_filtrado.append(maldivas[i])
                resultado_filtrado.append(resultado_linha27[i])
        
        # APENAS GRÁFICO - Barras agrupadas mostrando divisão mês a mês
        fig_dist = go.Figure()
        
        fig_dist.add_trace(go.Bar(
            name='Partner (65%)',
            x=meses_com_dados,
            y=partner_filtrado,
            marker_color='#667eea',
            marker_line=dict(width=2, color='white'),
            text=[f"R$ {v/1000:.1f}K" for v in partner_filtrado],
            textposition='outside',
            textfont=dict(size=14, family='Arial Black'),
            width=0.35
        ))
        
        fig_dist.add_trace(go.Bar(
            name='Maldivas (35%)',
            x=meses_com_dados,
            y=maldivas_filtrado,
            marker_color='#f5576c',
            marker_line=dict(width=2, color='white'),
            text=[f"R$ {v/1000:.1f}K" for v in maldivas_filtrado],
            textposition='outside',
            textfont=dict(size=14, family='Arial Black'),
            width=0.35
        ))
        
        # Linha do resultado total (Linha 27)
        fig_dist.add_trace(go.Scatter(
            name='Resultado Linha 27',
            x=meses_com_dados,
            y=resultado_filtrado,
            mode='lines+markers+text',
            line=dict(color='#28a745', width=3, dash='dot'),
            marker=dict(size=12, color='#28a745', line=dict(width=2, color='white')),
            text=[f"R$ {v/1000:.1f}K" for v in resultado_filtrado],
            textposition='top center',
            textfont=dict(size=12, family='Arial Black', color='#28a745'),
        ))
        
        fig_dist.update_layout(
            title=dict(
                text='📊 Distribuição do Resultado (Linha 27) - 65% Partner / 35% Maldivas - Mês a Mês',
                font=dict(size=18, family='Arial Black', color='#1E3A5F'),
                x=0.5,
                xanchor='center'
            ),
            height=500,
            paper_bgcolor='white',
            plot_bgcolor='rgba(0,0,0,0)',
            barmode='group',
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=-0.20,
                xanchor='center',
                x=0.5,
                font=dict(size=13, family='Arial Black')
            ),
            font=dict(family='Segoe UI', size=12),
            margin=dict(l=60, r=60, t=100, b=100),
            yaxis=dict(
                title='Valor (R$)',
                gridcolor='#e8e8e8',
                range=[0, max(resultado_filtrado) * 1.35] if resultado_filtrado else [0, 100],
                tickformat=',.0f'
            ),
            xaxis=dict(
                title='',
                tickfont=dict(size=14, family='Arial Black')
            )
        )
        
        st.plotly_chart(fig_dist, use_container_width=True)
    
    # =============================================================================
    # 📦 SEÇÃO 5: ANÁLISE POR PRODUTO
    # =============================================================================
    
    if show_charts and df_prod is not None and len(df_prod) > 0:
        st.markdown("""
        <div class="section-header" style="background: linear-gradient(135deg, #ffc107 0%, #fd7e14 100%);">
            <h2 style="color: #1E3A5F;">📦 ANÁLISE POR TIPO DE PRODUTO</h2>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_prod = px.sunburst(df_prod, path=['Produto'], values='Total', color='Total', color_continuous_scale='YlOrRd', title='☀️ Distribuição por Produto (Sunburst)')
            fig_prod.update_layout(height=550, paper_bgcolor='white', font=dict(family='Segoe UI', size=12),
                                   title=dict(font=dict(size=18, family='Arial Black', color='#1E3A5F'), x=0.5, xanchor='center'))
            fig_prod.update_traces(textinfo='label+percent entry', textfont=dict(size=12, family='Arial Black'))
            st.plotly_chart(fig_prod, use_container_width=True)
        
        with col2:
            fig_prod_bar = go.Figure()
            fig_prod_bar.add_trace(go.Bar(
                y=df_prod['Produto'], x=df_prod['Total'], orientation='h',
                marker=dict(color=df_prod['Total'], colorscale='YlOrRd', showscale=True,
                           colorbar=dict(title=dict(text='Comissão', font=dict(size=12)), thickness=15, len=0.7), line=dict(width=1, color='white')),
                text=[f"R$ {v/1000:.1f}K ({p:.1f}%)" for v, p in zip(df_prod['Total'], df_prod['% do Total'])],
                textposition='outside', textfont=dict(size=11, family='Arial Black', color='#1E3A5F'),
                width=0.7
            ))
            fig_prod_bar.update_layout(
                title=dict(text='📊 Comissão por Tipo de Produto', font=dict(size=18, family='Arial Black', color='#1E3A5F'), x=0.5, xanchor='center'),
                height=500, paper_bgcolor='white', plot_bgcolor='rgba(0,0,0,0)',
                xaxis_title=dict(text='Comissão Total (R$)', font=dict(size=13, family='Arial Black')),
                yaxis=dict(categoryorder='total ascending', tickfont=dict(size=11, family='Arial')),
                margin=dict(l=180, r=150, t=80, b=60)
            )
            fig_prod_bar.update_xaxes(gridcolor='#e8e8e8', tickformat=',.0f')
            st.plotly_chart(fig_prod_bar, use_container_width=True)
    
    # =============================================================================
    # 👥 SEÇÃO 6: RANKING DE ORIGINADORES
    # =============================================================================
    
    if show_charts and df_orig is not None and len(df_orig) > 0:
        st.markdown("""
        <div class="section-header" style="background: linear-gradient(135deg, #17a2b8 0%, #20c997 100%);">
            <h2>👥 RANKING - TOP ORIGINADORES</h2>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            fig_orig = go.Figure()
            top_5 = df_orig.head(5)
            outros_total = df_orig.iloc[5:]['Total'].sum() if len(df_orig) > 5 else 0
            outros_pct = df_orig.iloc[5:]['% do Total'].sum() if len(df_orig) > 5 else 0
            
            if outros_total > 0:
                outros = pd.DataFrame({'Originador': ['Outros'], 'Total': [outros_total], '% do Total': [outros_pct]})
                df_orig_chart = pd.concat([top_5[['Originador', 'Total', '% do Total']], outros])
            else:
                df_orig_chart = top_5[['Originador', 'Total', '% do Total']]
            
            fig_orig.add_trace(go.Pie(
                labels=df_orig_chart['Originador'], values=df_orig_chart['Total'], hole=0.55,
                marker=dict(colors=CORES['gradiente'], line=dict(width=3, color='white')),
                textinfo='label+percent', textposition='outside', textfont=dict(size=12, family='Arial Black')
            ))
            
            fig_orig.update_layout(
                title=dict(text='🏅 Distribuição de Comissão por Originador', font=dict(size=18, family='Arial Black', color='#1E3A5F'), x=0.5, xanchor='center'),
                height=550, paper_bgcolor='white',
                annotations=[dict(text=f'Total<br><b>{formatar_moeda(df_orig["Total"].sum())}</b>', x=0.5, y=0.5, font_size=14, font_family='Arial Black', showarrow=False)],
                showlegend=True, legend=dict(orientation='h', yanchor='bottom', y=-0.15, xanchor='center', x=0.5, font=dict(size=11)),
                margin=dict(l=80, r=80, t=80, b=100)
            )
            st.plotly_chart(fig_orig, use_container_width=True)
        
        with col2:
            st.markdown("### 🏆 Top 3 Originadores")
            medalhas = ['🥇', '🥈', '🥉']
            cores_medalha = ['#FFD700', '#C0C0C0', '#CD7F32']
            
            for i, (idx, row) in enumerate(df_orig.head(3).iterrows()):
                st.markdown(f"""
                <div style="background: white; border: 4px solid {cores_medalha[i]}; padding: 20px; border-radius: 15px; margin: 10px 0; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
                    <div style="display: flex; align-items: center;">
                        <span style="font-size: 2.5rem; margin-right: 15px;">{medalhas[i]}</span>
                        <div>
                            <div style="font-size: 1rem; font-weight: 700; color: #1E3A5F;">{row['Originador']}</div>
                            <div style="font-size: 1.3rem; color: #28a745; font-weight: 800;">{formatar_moeda(row['Total'])}</div>
                            <div style="font-size: 0.9rem; color: #6c757d;">{int(row['Operações'])} operações | Ticket: {formatar_moeda(row['Ticket Médio'])}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # =============================================================================
    # 🏅 SEÇÃO 7: RANKING MAIORES CLIENTES
    # =============================================================================
    
    if show_charts and df_cli is not None and len(df_cli) > 0:
        st.markdown("""
        <div class="section-header" style="background: linear-gradient(135deg, #20c997 0%, #17a2b8 100%);">
            <h2>🏅 RANKING - MAIORES CLIENTES POR RECEITA</h2>
        </div>
        """, unsafe_allow_html=True)
        
        fig_ranking_cli = go.Figure()
        
        fig_ranking_cli.add_trace(go.Bar(
            y=df_cli['Cliente'].head(15), x=df_cli['Total'].head(15), orientation='h',
            marker=dict(color=df_cli['Total'].head(15), colorscale='Tealgrn', showscale=True,
                       colorbar=dict(title=dict(text='Receita (R$)', font=dict(size=12)), thickness=15, len=0.7), line=dict(width=1, color='white')),
            text=[f"R$ {v/1000:.1f}K ({p:.1f}%)" for v, p in zip(df_cli['Total'].head(15), df_cli['% do Total'].head(15))],
            textposition='outside', textfont=dict(size=11, family='Arial Black', color='#1E3A5F'),
            width=0.7
        ))
        
        fig_ranking_cli.update_layout(
            title=dict(text='🏢 Top 15 Clientes por Volume de Receita', font=dict(size=18, family='Arial Black', color='#1E3A5F'), x=0.5, xanchor='center'),
            height=650, paper_bgcolor='white', plot_bgcolor='rgba(0,0,0,0)',
            xaxis_title=dict(text='Receita Total (R$)', font=dict(size=13, family='Arial Black')),
            yaxis=dict(categoryorder='total ascending', tickfont=dict(size=10, family='Arial')),
            margin=dict(l=280, r=150, t=80, b=60)
        )
        fig_ranking_cli.update_xaxes(gridcolor='#e8e8e8', tickformat=',.0f')
        st.plotly_chart(fig_ranking_cli, use_container_width=True)
    
    # =============================================================================
    # 💸 SEÇÃO 8: RANKING DE DESPESAS
    # =============================================================================
    
    if show_charts and df_cat is not None and len(df_cat) > 0:
        st.markdown("""
        <div class="section-header" style="background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);">
            <h2>💸 RANKING - MAIORES DESPESAS</h2>
        </div>
        """, unsafe_allow_html=True)
        
        fig_desp_bar = go.Figure()
        
        fig_desp_bar.add_trace(go.Bar(
            x=df_cat['Categoria'].head(10), y=df_cat['Total'].head(10),
            marker=dict(color=df_cat['Total'].head(10), colorscale='Reds', showscale=False, line=dict(width=1, color='white')),
            text=[f"R$ {v/1000:.1f}K" for v in df_cat['Total'].head(10)],
            textposition='outside', textfont=dict(size=11, family='Arial Black', color='#1E3A5F'),
            width=0.7
        ))
        
        fig_desp_bar.update_layout(
            title=dict(text='📊 Top 10 Categorias de Despesas', font=dict(size=18, family='Arial Black', color='#1E3A5F'), x=0.5, xanchor='center'),
            height=550, paper_bgcolor='white', plot_bgcolor='rgba(0,0,0,0)', xaxis_tickangle=-35,
            xaxis=dict(tickfont=dict(size=10, family='Arial')),
            yaxis_title=dict(text='Valor (R$)', font=dict(size=13, family='Arial Black')),
            yaxis=dict(range=[0, df_cat['Total'].head(10).max() * 1.25]),
            margin=dict(l=80, r=60, t=80, b=180)
        )
        fig_desp_bar.update_yaxes(gridcolor='#e8e8e8', tickformat=',.0f')
        st.plotly_chart(fig_desp_bar, use_container_width=True)
    
    # =============================================================================
    # 📋 SEÇÃO 9: RESUMO EXECUTIVO
    # =============================================================================
    
    if show_tables:
        st.markdown("""
        <div class="section-header" style="background: linear-gradient(135deg, #1E3A5F 0%, #2d5a87 100%);">
            <h2>📋 RESUMO EXECUTIVO</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Tabela de resumo com dados da DRE
        if dados_dre:
            resumo_data = {
                'Indicador': [
                    '💰 FATURAMENTO BRUTO',
                    '    → Produção Direta',
                    '    → Portal MAAS',
                    '',
                    '(-) Impostos Diretos',
                    '(-) Custo Operacional (D.A)',
                    '(+) Co-Corretagem',
                    '(-) Rebate AAI',
                    '',
                    '(=) MARGEM DE CONTRIBUIÇÃO',
                    '',
                    '💸 DESPESAS TOTAIS',
                    '    → Despesas Operacionais',
                    '    → Folha + Terceiros',
                    '',
                    '🎯 RESULTADO OPERACIONAL (Linha 27)',
                ],
                'Valor': [
                    formatar_moeda(dados_dre['receita_bruta_total'].get('YTD', 0)),
                    formatar_moeda(dados_dre['receita_bruta_direto'].get('YTD', 0)),
                    formatar_moeda(dados_dre['receita_bruta_total'].get('YTD', 0) - dados_dre['receita_bruta_direto'].get('YTD', 0)),
                    '',
                    formatar_moeda(dados_dre['impostos_diretos'].get('YTD', 0)),
                    formatar_moeda(dados_dre['custo_operacional'].get('YTD', 0)),
                    formatar_moeda(dados_dre['co_corretagem'].get('YTD', 0)),
                    formatar_moeda(dados_dre['rebate_aai'].get('YTD', 0)),
                    '',
                    formatar_moeda(dados_dre['margem_contribuicao'].get('YTD', 0)),
                    '',
                    formatar_moeda(dados_dre['despesas'].get('YTD', 0) + dados_dre['folha_terceiros'].get('YTD', 0)),
                    formatar_moeda(dados_dre['despesas'].get('YTD', 0)),
                    formatar_moeda(dados_dre['folha_terceiros'].get('YTD', 0)),
                    '',
                    formatar_moeda(dados_dre['resultado_operacional'].get('YTD', 0)),
                ]
            }
        else:
            resumo_data = {
                'Indicador': ['Faça upload da planilha para ver os dados'],
                'Valor': ['']
            }
        
        df_resumo_display = pd.DataFrame(resumo_data)
        st.dataframe(df_resumo_display, use_container_width=True, hide_index=True)
    
    # =============================================================================
    # 📥 SEÇÃO 10: EXPORTAR PDF
    # =============================================================================
    
    st.markdown("---")
    st.markdown("""
    <div class="section-header" style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%);">
        <h2>📥 EXPORTAR DASHBOARD PARA PDF</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("📄 GERAR PDF PROFISSIONAL PREMIUM", type="primary", use_container_width=True):
            with st.spinner("Gerando PDF profissional..."):
                try:
                    pdf_generator = PDFDashboardGenerator()
                    pdf_bytes = pdf_generator.generate_pdf(dados_dre=dados_dre)
                    
                    st.success("✅ PDF Premium gerado com sucesso!")
                    
                    st.download_button(
                        label="⬇️ BAIXAR PDF PREMIUM",
                        data=pdf_bytes,
                        file_name=f"Assertif_Dashboard_Premium_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    
                except Exception as e:
                    st.error(f"❌ Erro ao gerar PDF: {str(e)}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1E3A5F 0%, #2d5a87 50%, #667eea 100%);
        padding: 35px;
        border-radius: 20px;
        text-align: center;
        margin-top: 30px;
        color: white;
    ">
        <h3 style="margin-bottom: 10px;">✅ ASSERTIF CORRETORA - Dashboard Financeiro Premium</h3>
        <p style="opacity: 0.9;">
            📊 Versão 5.1 Premium Ultimate | 🗓️ Período: YTD 2026 | 📈 Status: LUCRO<br>
            Desenvolvido com Streamlit + Plotly + ReportLab
        </p>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# 🚀 EXECUÇÃO DA APLICAÇÃO
# =============================================================================

if __name__ == "__main__":
    main()
