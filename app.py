# =============================================================================
# 🚀 ASSERTIF CORRETORA - DASHBOARD FINANCEIRO PREMIUM - VERSÃO OSCAR
# =============================================================================
# Dashboard interativo com rankings, filtros e visualizações profissionais
# Versão: 6.0 PREMIUM ULTIMATE OSCAR EDITION
# Para rodar: streamlit run dashboard_assertif.py
# =============================================================================

# ARQUIVO: dashboard_assertif.py

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
# 🎨 CONFIGURAÇÕES DE ESTILO PREMIUM - PALETA AZUL MALDIVAS
# =============================================================================

# Paleta de cores profissional - Tons de Azul Maldivas Holding
CORES = {
    'primaria': '#0a1628',
    'secundaria': '#1a3a5c',
    'sucesso': '#00d4aa',
    'perigo': '#ff6b6b',
    'alerta': '#feca57',
    'info': '#2e86ab',
    'escuro': '#0a1628',
    'claro': '#f8f9fa',
    'ouro': '#ffd700',
    'prata': '#c0c0c0',
    'bronze': '#cd7f32',
    'azul_claro': '#7dd3fc',
    'gradiente': ['#0a1628', '#1a3a5c', '#2e86ab', '#4ea8de', '#7dd3fc', '#bae6fd'],
    'chart_colors': ['#0a1628', '#1a3a5c', '#2e86ab', '#4ea8de', '#00d4aa', '#7dd3fc', '#bae6fd', '#e0f2fe']
}

# Paletas para gráficos
PALETA_SEQUENCIAL = px.colors.sequential.Viridis
PALETA_QUALITATIVA = px.colors.qualitative.Set2
PALETA_DIVERGENTE = px.colors.diverging.RdYlGn

# =============================================================================
# 📊 DADOS MENSAIS DA DRE - ESTRUTURA ATUALIZADA AUTOMATICAMENTE
# =============================================================================

DADOS_MENSAIS = {
    'Janeiro': {
        'receita_bruta': 42263,
        'custos_totais': 21890,
        'margem_contrib': 20373,
        'despesas': 15240,
        'resultado_op': 5133
    },
    'Fevereiro': {
        'receita_bruta': 49513,
        'custos_totais': 26782,
        'margem_contrib': 22732,
        'despesas': 15065,
        'resultado_op': 7667
    },
    'Março': {
        'receita_bruta': 71946,
        'custos_totais': 39509,
        'margem_contrib': 32436,
        'despesas': 15746,
        'resultado_op': 16690
    },
    'Abril': {
        'receita_bruta': 17075,
        'custos_totais': 8758,
        'margem_contrib': 8317,
        'despesas': 17017,
        'resultado_op': -8699
    }
}

# =============================================================================
# 📊 FUNÇÕES AUXILIARES PREMIUM
# =============================================================================

def formatar_moeda(valor):
    """Formata valor para moeda brasileira"""
    try:
        if pd.isna(valor) or valor == 0:
            return "R$ 0,00"
        if valor < 0:
            return f"-R$ {abs(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return str(valor)

def formatar_percentual(valor):
    """Formata valor como percentual"""
    try:
        return f"{valor:.1f}%"
    except:
        return str(valor)

def calcular_dados_filtrados(meses_selecionados, dados_mensais_atual=None):
    """Calcula os totais baseado nos meses selecionados"""
    dados_para_usar = dados_mensais_atual if dados_mensais_atual is not None else DADOS_MENSAIS
    
    if 'All' in meses_selecionados or len(meses_selecionados) == 0:
        meses_selecionados = list(dados_para_usar.keys())
    
    totais = {
        'receita_bruta': 0,
        'custos_totais': 0,
        'margem_contrib': 0,
        'despesas': 0,
        'resultado_op': 0
    }
    
    for mes in meses_selecionados:
        if mes in dados_para_usar:
            for key in totais:
                totais[key] += dados_para_usar[mes][key]
    
    return totais, meses_selecionados


def extrair_dados_dre(df_dre):
    """
    🎯 FUNÇÃO INOVADORA E PRECISA PARA EXTRAIR DADOS DA DRE 2026
    """
    dados_extraidos = {}
    
    meses_colunas = {
        1: 'Janeiro',
        2: 'Fevereiro', 
        3: 'Março',
        4: 'Abril',
        5: 'Maio',
        6: 'Junho',
        7: 'Julho',
        8: 'Agosto',
        9: 'Setembro',
        10: 'Outubro',
        11: 'Novembro',
        12: 'Dezembro'
    }
    
    linhas_encontradas = {
        'receita_bruta_total': None,
        'impostos_diretos': None,
        'custo_op_da': None,
        'co_corretagem': None,
        'rebate_aai': None,
        'margem_contrib_direta': None,
        'despesas': None,
        'folha_terceiros': None,
        'margem_contrib_maas': None,
        'resultado_op': None
    }
    
    try:
        if hasattr(df_dre, 'values'):
            dados = df_dre.values
        else:
            dados = df_dre
        
        for idx, row in enumerate(dados):
            if len(row) > 0:
                texto_celula = str(row[0]).strip().upper() if row[0] is not None else ""
                
                if 'RECEITA BRUTA TOTAL' in texto_celula and 'MAAS' in texto_celula:
                    linhas_encontradas['receita_bruta_total'] = idx
                
                elif texto_celula == 'IMPOSTOS DIRETOS' or texto_celula.startswith('IMPOSTOS DIRETOS'):
                    if linhas_encontradas['impostos_diretos'] is None:
                        linhas_encontradas['impostos_diretos'] = idx
                
                elif 'CUSTO OPERACIONAL' in texto_celula and 'D.A' in texto_celula:
                    if linhas_encontradas['custo_op_da'] is None:
                        linhas_encontradas['custo_op_da'] = idx
                
                elif texto_celula == 'CO-CORRETAGEM' or texto_celula.startswith('CO-CORRETAGEM'):
                    linhas_encontradas['co_corretagem'] = idx
                
                elif texto_celula == 'REBATE AAI' or texto_celula.startswith('REBATE AAI'):
                    if linhas_encontradas['rebate_aai'] is None:
                        linhas_encontradas['rebate_aai'] = idx
                
                elif 'MARGEM DE CONTRIBUIÇÃO' in texto_celula:
                    if linhas_encontradas['margem_contrib_direta'] is None:
                        linhas_encontradas['margem_contrib_direta'] = idx
                    elif linhas_encontradas['margem_contrib_maas'] is None:
                        linhas_encontradas['margem_contrib_maas'] = idx
                
                elif texto_celula == 'DESPESAS' or texto_celula == 'DESPESAS ':
                    if linhas_encontradas['despesas'] is None:
                        linhas_encontradas['despesas'] = idx
                
                elif 'FOLHA' in texto_celula and 'TERCEIROS' in texto_celula:
                    if linhas_encontradas['folha_terceiros'] is None:
                        linhas_encontradas['folha_terceiros'] = idx
                
                elif texto_celula == 'RESULTADO OPERACIONAL' or texto_celula.startswith('RESULTADO OPERACIONAL'):
                    if 'DISTRIBUIÇÃO' not in texto_celula and 'DISTRIBUI' not in texto_celula:
                        linhas_encontradas['resultado_op'] = idx
        
        def get_valor(linha_idx, col_idx):
            try:
                if linha_idx is None:
                    return 0
                if linha_idx < len(dados) and col_idx < len(dados[linha_idx]):
                    val = dados[linha_idx][col_idx]
                    
                    if val is None or val == '' or val == ' ':
                        return 0
                    
                    if isinstance(val, (int, float)):
                        if pd.isna(val):
                            return 0
                        return float(val)
                    
                    val_str = str(val).strip()
                    
                    is_negative = False
                    if val_str.startswith('(') and val_str.endswith(')'):
                        is_negative = True
                        val_str = val_str[1:-1]
                    
                    val_str = val_str.replace('R$', '').replace(' ', '').strip()
                    
                    if '.' in val_str and ',' in val_str:
                        val_str = val_str.replace('.', '').replace(',', '.')
                    elif ',' in val_str:
                        val_str = val_str.replace(',', '.')
                    
                    if val_str == '' or val_str == '-':
                        return 0
                    
                    valor = float(val_str)
                    return -valor if is_negative else valor
                return 0
            except (ValueError, TypeError) as e:
                return 0
        
        for col_idx, mes_nome in meses_colunas.items():
            if col_idx >= len(dados[0]):
                continue
            
            receita_bruta = get_valor(linhas_encontradas['receita_bruta_total'], col_idx)
            
            if receita_bruta > 0:
                impostos = abs(get_valor(linhas_encontradas['impostos_diretos'], col_idx))
                custo_da = abs(get_valor(linhas_encontradas['custo_op_da'], col_idx))
                co_corretagem = abs(get_valor(linhas_encontradas['co_corretagem'], col_idx))
                rebate = abs(get_valor(linhas_encontradas['rebate_aai'], col_idx))
                
                margem_direta = get_valor(linhas_encontradas['margem_contrib_direta'], col_idx)
                margem_maas = get_valor(linhas_encontradas['margem_contrib_maas'], col_idx)
                margem_contrib = margem_direta + margem_maas
                
                despesas_op = abs(get_valor(linhas_encontradas['despesas'], col_idx))
                folha_terceiros = abs(get_valor(linhas_encontradas['folha_terceiros'], col_idx))
                despesas_total = despesas_op + folha_terceiros
                
                resultado_op = get_valor(linhas_encontradas['resultado_op'], col_idx)
                
                custos_totais = impostos + custo_da + rebate - co_corretagem
                
                dados_extraidos[mes_nome] = {
                    'receita_bruta': round(receita_bruta, 2),
                    'custos_totais': round(custos_totais, 2),
                    'margem_contrib': round(margem_contrib, 2),
                    'despesas': round(despesas_total, 2),
                    'resultado_op': round(resultado_op, 2)
                }
        
        return dados_extraidos if dados_extraidos else None
        
    except Exception as e:
        print(f"❌ Erro ao extrair dados DRE: {e}")
        return None


def criar_cartao_kpi_html(titulo, valor, subtitulo="", cor=CORES['primaria'], icone="📊", tamanho="normal"):
    """Cria HTML para cartão de KPI estilizado - VERSÃO AZUL MALDIVAS - SEM SUBTÍTULO"""
    
    # Tamanhos responsivos
    if tamanho == "grande":
        padding = "35px 25px"
        icone_size = "3rem"
        titulo_size = "1.1rem"
        valor_size = "2.2rem"
        min_height = "200px"
    else:
        padding = "30px 20px"
        icone_size = "2.8rem"
        titulo_size = "0.95rem"
        valor_size = "1.9rem"
        min_height = "180px"
    
    html = f"""
    <div style="
        background: linear-gradient(145deg, {cor} 0%, {cor}dd 50%, {cor}bb 100%);
        padding: {padding};
        border-radius: 24px;
        color: white;
        text-align: center;
        box-shadow: 
            0 20px 60px rgba(0,0,0,0.3),
            0 8px 25px {cor}40,
            inset 0 1px 0 rgba(255,255,255,0.2);
        margin: 10px 5px;
        min-height: {min_height};
        border: 1px solid rgba(255,255,255,0.15);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    ">
        <div style="
            position: absolute;
            top: -30%;
            right: -30%;
            width: 150px;
            height: 150px;
            background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 70%);
            border-radius: 50%;
        "></div>
        <div style="
            font-size: {icone_size}; 
            margin-bottom: 15px; 
            text-shadow: 3px 3px 6px rgba(0,0,0,0.4);
            filter: drop-shadow(0 4px 8px rgba(0,0,0,0.3));
            position: relative;
            z-index: 1;
        ">{icone}</div>
        <div style="
            font-size: {titulo_size}; 
            font-weight: 700; 
            opacity: 1; 
            margin-top: 5px; 
            text-transform: uppercase; 
            letter-spacing: 2px; 
            text-shadow: 2px 2px 4px rgba(0,0,0,0.4);
            position: relative;
            z-index: 1;
        ">{titulo}</div>
        <div style="
            font-size: {valor_size}; 
            font-weight: 900; 
            margin: 18px 0; 
            text-shadow: 3px 3px 6px rgba(0,0,0,0.4);
            letter-spacing: 1px;
            position: relative;
            z-index: 1;
        ">{valor}</div>
    </div>
    """
    return html


# =============================================================================
# 📄 CLASSE PARA GERAÇÃO DE PDF COM REPORTLAB - VERSÃO AZUL MALDIVAS
# =============================================================================

class PDFDashboardGenerator:
    """Classe para gerar PDF profissional do dashboard - Versão Azul Maldivas"""
    
    def __init__(self, filename="Assertif_Dashboard_Premium.pdf"):
        self.filename = filename
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        self.page_number = 0
        self.total_pages = 0
        
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
            textColor=HexColor('#0a1628'),
            alignment=TA_LEFT,
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='NormalText',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=HexColor('#0a1628'),
            alignment=TA_LEFT,
            spaceAfter=6,
            fontName='Helvetica'
        ))
        
        self.styles.add(ParagraphStyle(
            name='TOCEntry',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=HexColor('#0a1628'),
            alignment=TA_LEFT,
            spaceAfter=8,
            fontName='Helvetica',
            leftIndent=20
        ))
        
        self.styles.add(ParagraphStyle(
            name='NoteStyle',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=HexColor('#6c757d'),
            alignment=TA_JUSTIFY,
            spaceAfter=6,
            fontName='Helvetica-Oblique',
            leftIndent=10,
            rightIndent=10
        ))
        
        self.styles.add(ParagraphStyle(
            name='PositiveValue',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=HexColor('#00d4aa'),
            alignment=TA_RIGHT,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='NegativeValue',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=HexColor('#ff6b6b'),
            alignment=TA_RIGHT,
            fontName='Helvetica-Bold'
        ))
    
    def _create_cover_page(self):
        """Cria página de capa profissional - SEM EMOJIS"""
        elements = []
        
        elements.append(Spacer(1, 3*cm))
        
        # Título principal sem emoji
        cover_content = [
            [Paragraph("<font size='48' color='white'><b>ASSERTIF CORRETORA</b></font>", 
                      ParagraphStyle(name='CoverMain', alignment=TA_CENTER, fontSize=48, fontName='Helvetica-Bold'))],
            [Spacer(1, 0.3*cm)],
            [Paragraph("<font size='36' color='white'><b>DE SEGUROS</b></font>", 
                      ParagraphStyle(name='CoverMain2', alignment=TA_CENTER, fontSize=36, fontName='Helvetica-Bold'))],
            [Spacer(1, 1*cm)],
            [Paragraph("_" * 50, 
                      ParagraphStyle(name='LineCover', alignment=TA_CENTER, textColor=colors.white, fontSize=14))],
            [Spacer(1, 1*cm)],
            [Paragraph("<font size='22' color='white'>Dashboard Financeiro</font>", 
                      ParagraphStyle(name='CoverSub1', alignment=TA_CENTER, fontSize=22, fontName='Helvetica'))],
            [Spacer(1, 0.3*cm)],
            [Paragraph("<font size='16' color='white'>Relatorio Executivo | YTD 2026</font>", 
                      ParagraphStyle(name='CoverSub2', alignment=TA_CENTER, fontSize=16, fontName='Helvetica'))],
            [Spacer(1, 2*cm)],
            [Paragraph("<font size='14' color='white'>Periodo: Janeiro a Abril de 2026</font>", 
                      ParagraphStyle(name='CoverInfo', alignment=TA_CENTER, fontSize=14, fontName='Helvetica'))],
            [Spacer(1, 0.5*cm)],
            [Paragraph("<font size='14' color='#00d4aa'><b>Status: LUCRO | Margem: 17%</b></font>", 
                      ParagraphStyle(name='CoverInfo2', alignment=TA_CENTER, fontSize=14, fontName='Helvetica-Bold'))],
            [Spacer(1, 2*cm)],
            [Paragraph(f"<font size='11' color='white'>Gerado em: {datetime.now().strftime('%d/%m/%Y as %H:%M')}</font>", 
                      ParagraphStyle(name='CoverDate', alignment=TA_CENTER, fontSize=11, fontName='Helvetica'))],
        ]
        
        cover_table = Table([[item[0]] for item in cover_content], colWidths=[18*cm])
        cover_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), HexColor('#0a1628')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 30),
            ('RIGHTPADDING', (0, 0), (-1, -1), 30),
        ]))
        
        elements.append(cover_table)
        elements.append(Spacer(1, 1*cm))
        
        # Tabela de resumo sem emojis
        info_data = [
            ['FATURAMENTO YTD', 'R$ 178.072,00', 'MARGEM CONTRIBUICAO', 'R$ 82.343,00'],
            ['DESPESAS TOTAIS', 'R$ 46.050,00', 'RESULTADO OPERACIONAL', 'R$ 29.490,00'],
        ]
        
        info_table = Table(info_data, colWidths=[5*cm, 4*cm, 5*cm, 4*cm])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), HexColor('#f8f9fa')),
            ('TEXTCOLOR', (0, 0), (0, -1), HexColor('#0a1628')),
            ('TEXTCOLOR', (2, 0), (2, -1), HexColor('#0a1628')),
            ('TEXTCOLOR', (1, 0), (1, -1), HexColor('#00d4aa')),
            ('TEXTCOLOR', (3, 0), (3, -1), HexColor('#00d4aa')),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
            ('FONTNAME', (3, 0), (3, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#e8e8e8')),
            ('BOX', (0, 0), (-1, -1), 2, HexColor('#0a1628')),
        ]))
        
        elements.append(info_table)
        elements.append(PageBreak())
        
        return elements
    
    def _create_table_of_contents(self):
        """Cria sumário/índice do documento - SEM EMOJIS"""
        elements = []
        
        toc_header = [[Paragraph("<font color='white'><b>SUMARIO</b></font>", 
                                 ParagraphStyle(name='TOCHeader', alignment=TA_CENTER, fontSize=20, fontName='Helvetica-Bold'))]]
        toc_header_table = Table(toc_header, colWidths=[18*cm])
        toc_header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), HexColor('#0a1628')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 20),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
        ]))
        
        elements.append(toc_header_table)
        elements.append(Spacer(1, 1*cm))
        
        toc_items = [
            ('1.', 'Indicadores Principais (KPIs)', '3'),
            ('2.', 'Evolucao Mensal - Receita vs Resultado', '3'),
            ('3.', 'Ranking - Maiores Comissoes por Seguradora', '4'),
            ('4.', 'Distribuicao de Resultados - Socios', '4'),
            ('5.', 'Ranking - Top Originadores', '5'),
            ('6.', 'Ranking - Maiores Clientes', '5'),
            ('7.', 'Analise por Tipo de Produto', '6'),
            ('8.', 'Ranking - Maiores Despesas', '6'),
            ('9.', 'Resumo Executivo - DRE Completo', '7'),
            ('10.', 'Analise Grafica Consolidada', '8'),
            ('11.', 'Notas e Observacoes', '9'),
        ]
        
        toc_data = []
        for num, titulo, pagina in toc_items:
            toc_data.append([
                Paragraph(f"<b>{num}</b>", ParagraphStyle(name='TOCNum', fontSize=12, textColor=HexColor('#1a3a5c'), fontName='Helvetica-Bold')),
                Paragraph(titulo, ParagraphStyle(name='TOCTitle', fontSize=12, textColor=HexColor('#0a1628'), fontName='Helvetica')),
                Paragraph(f"<b>{pagina}</b>", ParagraphStyle(name='TOCPage', fontSize=12, textColor=HexColor('#6c757d'), alignment=TA_RIGHT, fontName='Helvetica-Bold')),
            ])
        
        toc_table = Table(toc_data, colWidths=[1.5*cm, 13.5*cm, 3*cm])
        toc_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LINEBELOW', (0, 0), (-1, -2), 0.5, HexColor('#e8e8e8')),
            ('LINEBELOW', (0, -1), (-1, -1), 2, HexColor('#1a3a5c')),
        ]))
        
        elements.append(toc_table)
        elements.append(Spacer(1, 2*cm))
        
        info_box = [[Paragraph(
            "<b>Sobre este Relatorio</b><br/><br/>"
            "Este dashboard apresenta uma visao consolidada do desempenho financeiro da Assertif Corretora "
            "no periodo de Janeiro a Abril de 2026. Os dados incluem analise de receitas por seguradora, "
            "produto, originador e cliente, alem da distribuicao de resultados entre os socios e "
            "evolucao mensal dos principais indicadores.",
            ParagraphStyle(name='InfoBox', fontSize=10, textColor=HexColor('#0a1628'), 
                          alignment=TA_JUSTIFY, fontName='Helvetica', leading=14)
        )]]
        
        info_box_table = Table(info_box, colWidths=[17*cm])
        info_box_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), HexColor('#e8f4f8')),
            ('BOX', (0, 0), (-1, -1), 2, HexColor('#2e86ab')),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ]))
        
        elements.append(info_box_table)
        elements.append(PageBreak())
        
        return elements
    
    def _create_section_header(self, titulo, cor=HexColor('#0a1628'), icone=""):
        """Cria cabeçalho de seção premium - SEM EMOJIS"""
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
    
    def _create_kpi_cards(self, kpis):
        """Cria cards de KPIs com visual premium - SEM EMOJIS"""
        kpi_cells = []
        
        cores_kpi = [
            HexColor('#0a1628'),
            HexColor('#ff6b6b'),
            HexColor('#2e86ab'),
            HexColor('#feca57'),
            HexColor('#00d4aa'),
        ]
        
        for i, kpi in enumerate(kpis):
            cor = cores_kpi[i % len(cores_kpi)]
            
            card_content = [
                [Paragraph(f"<font size='8' color='white'><b>{kpi['titulo']}</b></font>", 
                          ParagraphStyle(name=f'KPITitle{i}', alignment=TA_CENTER))],
                [Spacer(1, 0.3*cm)],
                [Paragraph(f"<font size='16' color='white'><b>{kpi['valor']}</b></font>", 
                          ParagraphStyle(name=f'KPIValue{i}', alignment=TA_CENTER))],
            ]
            
            card_table = Table(card_content, colWidths=[3.4*cm])
            card_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), cor),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ]))
            
            kpi_cells.append(card_table)
        
        kpi_row = Table([kpi_cells], colWidths=[3.6*cm] * 5)
        kpi_row.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        return kpi_row
    
    def _create_line_chart(self, data, labels, title, width=450, height=200):
        """Cria gráfico de linha"""
        drawing = Drawing(width, height)
        
        drawing.add(Rect(0, 0, width, height, fillColor=HexColor('#f8f9fa'), strokeColor=None))
        
        lc = HorizontalLineChart()
        lc.x = 50
        lc.y = 40
        lc.height = height - 80
        lc.width = width - 100
        lc.data = [data]
        lc.categoryAxis.categoryNames = labels
        lc.categoryAxis.labels.fontName = 'Helvetica'
        lc.categoryAxis.labels.fontSize = 9
        lc.valueAxis.valueMin = 0
        lc.valueAxis.valueMax = max(data) * 1.2 if data else 100
        lc.valueAxis.labels.fontName = 'Helvetica'
        lc.valueAxis.labels.fontSize = 8
        lc.lines[0].strokeColor = HexColor('#0a1628')
        lc.lines[0].strokeWidth = 3
        lc.lines[0].symbol = makeMarker('Circle')
        lc.lines[0].symbol.fillColor = HexColor('#1a3a5c')
        lc.lines[0].symbol.strokeColor = colors.white
        lc.lines[0].symbol.strokeWidth = 2
        lc.lines[0].symbol.size = 8
        
        drawing.add(lc)
        
        drawing.add(String(width/2, height - 15, title, 
                          fontName='Helvetica-Bold', fontSize=11, textAnchor='middle',
                          fillColor=HexColor('#0a1628')))
        
        return drawing
    
    def _create_data_table(self, headers, data, col_widths=None, highlight_rows=None):
        """Cria tabela de dados formatada premium"""
        table_data = [headers] + data
        
        if col_widths is None:
            col_widths = [18*cm / len(headers)] * len(headers)
        
        table = Table(table_data, colWidths=col_widths)
        
        style_commands = [
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#0a1628')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#e8e8e8')),
            ('BOX', (0, 0), (-1, -1), 1.5, HexColor('#0a1628')),
        ]
        
        for i in range(1, len(table_data)):
            if i % 2 == 0:
                style_commands.append(('BACKGROUND', (0, i), (-1, i), HexColor('#f8f9fa')))
            else:
                style_commands.append(('BACKGROUND', (0, i), (-1, i), colors.white))
        
        if highlight_rows:
            for row_idx, cor in highlight_rows.items():
                if row_idx < len(table_data):
                    style_commands.append(('BACKGROUND', (0, row_idx), (-1, row_idx), cor))
                    style_commands.append(('FONTNAME', (0, row_idx), (-1, row_idx), 'Helvetica-Bold'))
        
        table.setStyle(TableStyle(style_commands))
        
        return table
    
    def _create_note_box(self, titulo, texto, cor=HexColor('#2e86ab')):
        """Cria box de nota explicativa - SEM EMOJIS"""
        note_content = [[Paragraph(
            f"<b>{titulo}</b><br/><br/>{texto}",
            ParagraphStyle(name='NoteContent', fontSize=9, textColor=HexColor('#0a1628'), 
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
    
    def _create_footer(self):
        """Cria rodapé do documento - SEM EMOJIS"""
        footer_data = [[
            Paragraph(
                "<font color='white'><b>ASSERTIF CORRETORA - Dashboard Financeiro</b><br/>"
                f"Versao 6.0 | Periodo: Janeiro a Abril 2026 | Status: LUCRO<br/>"
                f"Documento gerado automaticamente em {datetime.now().strftime('%d/%m/%Y as %H:%M')}</font>",
                ParagraphStyle(
                    name='FooterStyle',
                    parent=self.styles['Normal'],
                    fontSize=10,
                    textColor=colors.white,
                    alignment=TA_CENTER,
                )
            )
        ]]
        
        footer_table = Table(footer_data, colWidths=[18*cm])
        footer_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), HexColor('#0a1628')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 20),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
            ('LEFTPADDING', (0, 0), (-1, -1), 20),
            ('RIGHTPADDING', (0, 0), (-1, -1), 20),
        ]))
        
        return footer_table
    
    def _add_page_number(self, canvas, doc):
        """Adiciona número de página e cabeçalho/rodapé em cada página - SEM EMOJIS"""
        canvas.saveState()
        
        canvas.setFillColor(HexColor('#0a1628'))
        canvas.rect(1*cm, A4[1] - 1.5*cm, A4[0] - 2*cm, 0.8*cm, fill=True, stroke=False)
        
        canvas.setFillColor(colors.white)
        canvas.setFont('Helvetica-Bold', 9)
        canvas.drawString(1.5*cm, A4[1] - 1.1*cm, "ASSERTIF CORRETORA - Dashboard Financeiro")
        canvas.drawRightString(A4[0] - 1.5*cm, A4[1] - 1.1*cm, f"YTD 2026")
        
        canvas.setFillColor(HexColor('#0a1628'))
        canvas.rect(1*cm, 0.5*cm, A4[0] - 2*cm, 0.6*cm, fill=True, stroke=False)
        
        canvas.setFillColor(colors.white)
        canvas.setFont('Helvetica', 8)
        canvas.drawString(1.5*cm, 0.7*cm, f"Gerado em: {datetime.now().strftime('%d/%m/%Y')}")
        canvas.drawCentredString(A4[0]/2, 0.7*cm, "Confidencial - Uso Interno")
        canvas.drawRightString(A4[0] - 1.5*cm, 0.7*cm, f"Pagina {doc.page}")
        
        canvas.restoreState()
    
    def generate_pdf(self, df_receitas_clean=None, df_despesas_clean=None, df_seg=None, 
                     df_prod=None, df_orig=None, df_cli=None, df_cat=None):
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
        
        elements.extend(self._create_cover_page())
        elements.extend(self._create_table_of_contents())
        
        elements.append(self._create_section_header("INDICADORES PRINCIPAIS (KPIs)", HexColor('#0a1628')))
        elements.append(Spacer(1, 15))
        
        kpis = [
            {'titulo': 'FATURAMENTO', 'valor': 'R$ 178.072,00'},
            {'titulo': 'CUSTOS TOTAIS', 'valor': 'R$ 95.729,00'},
            {'titulo': 'MARGEM CONTRIB.', 'valor': 'R$ 82.343,00'},
            {'titulo': 'DESPESAS', 'valor': 'R$ 46.050,00'},
            {'titulo': 'RESULTADO', 'valor': 'R$ 29.490,00'},
        ]
        elements.append(self._create_kpi_cards(kpis))
        elements.append(Spacer(1, 20))
        
        elements.append(self._create_note_box(
            "Legenda dos KPIs",
            "<b>Faturamento Bruto:</b> Soma da Receita Bruta de Producao Direta e Portal MAAS<br/><br/>"
            "<b>Custos Totais:</b> Soma de Impostos Diretos, Custo Operacional (D.A.) e Rebate AAI, menos Co-corretagem<br/><br/>"
            "<b>Margem de Contribuicao:</b> Faturamento Bruto menos Custos Totais<br/><br/>"
            "<b>Despesas Totais:</b> Soma de Despesas Operacionais e Folha + Terceiros<br/><br/>"
            "<b>Resultado Operacional:</b> Margem de Contribuicao menos Despesas Totais"
        ))
        elements.append(Spacer(1, 20))
        
        elements.append(self._create_section_header("EVOLUCAO MENSAL - RECEITA vs RESULTADO", HexColor('#1a3a5c')))
        elements.append(Spacer(1, 15))
        
        meses = ['Jan', 'Fev', 'Mar', 'Abr']
        receita_bruta = [42263, 49513, 71946, 14350]
        
        elements.append(self._create_line_chart(receita_bruta, meses, 'Evolucao da Receita Bruta Mensal (R$)', width=500, height=180))
        elements.append(Spacer(1, 15))
        
        evolucao_headers = ['Mes', 'Receita Bruta', 'Var. %', 'Resultado Op.', 'Margem']
        evolucao_data = [
            ['Janeiro', 'R$ 42.263,00', '-', 'R$ 5.133,00', '12,1%'],
            ['Fevereiro', 'R$ 49.513,00', '+17,2%', 'R$ 7.667,00', '15,5%'],
            ['Marco', 'R$ 71.946,00', '+45,3%', 'R$ 16.690,00', '23,2%'],
            ['Abril', 'R$ 14.350,00', '-80,1%', 'R$ 0,00', '0,0%'],
        ]
        elements.append(self._create_data_table(evolucao_headers, evolucao_data, 
                                                 [3*cm, 4*cm, 3*cm, 4*cm, 3*cm],
                                                 highlight_rows={4: HexColor('#ffe6e6')}))
        
        elements.append(PageBreak())
        
        elements.append(Spacer(1, 30))
        elements.append(self._create_footer())
        
        doc.build(elements, onFirstPage=self._add_page_number, onLaterPages=self._add_page_number)
        
        buffer.seek(0)
        return buffer.getvalue()


# =============================================================================
# 🎯 APLICAÇÃO STREAMLIT PRINCIPAL - VERSÃO AZUL MALDIVAS
# =============================================================================

def main():
    # Configuração da página
    st.set_page_config(
        page_title="Assertif Corretora - Dashboard Financeiro",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS customizado - PALETA AZUL MALDIVAS
    st.markdown("""
    <style>
        /* ========================================
           🎬 ASSERTIF DASHBOARD - AZUL MALDIVAS
           ======================================== */
        
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
        
        /* Reset e Base */
        * {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        .main .block-container {
            padding: 2rem 3rem;
            max-width: 1400px;
        }
        
        /* ========================================
           🎨 HEADER PRINCIPAL - AZUL MALDIVAS
           ======================================== */
        .main-header {
            background: linear-gradient(135deg, 
                #0a1628 0%, 
                #1a3a5c 25%, 
                #2e86ab 50%, 
                #1a3a5c 75%, 
                #0a1628 100%);
            background-size: 400% 400%;
            animation: gradientShift 8s ease infinite;
            padding: 60px 50px;
            border-radius: 32px;
            text-align: center;
            margin-bottom: 50px;
            box-shadow: 
                0 30px 80px rgba(10, 22, 40, 0.5),
                0 15px 40px rgba(26, 58, 92, 0.3),
                inset 0 2px 0 rgba(255,255,255,0.25);
            border: 2px solid rgba(255,255,255,0.2);
            position: relative;
            overflow: hidden;
        }
        
        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        .main-header::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 60%);
            animation: pulse 4s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); opacity: 0.5; }
            50% { transform: scale(1.1); opacity: 0.8; }
        }
        
        .main-header h1 {
            color: white;
            font-size: 3.8rem;
            font-weight: 900;
            text-shadow: 
                4px 4px 12px rgba(0,0,0,0.4),
                0 0 40px rgba(255,255,255,0.2);
            margin-bottom: 15px;
            position: relative;
            z-index: 1;
            letter-spacing: -1px;
        }
        
        .main-header h2 {
            color: white;
            font-size: 1.6rem;
            font-weight: 500;
            opacity: 0.95;
            position: relative;
            z-index: 1;
            text-shadow: 2px 2px 8px rgba(0,0,0,0.3);
        }
        
        .main-header .badge {
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 10px 25px;
            border-radius: 50px;
            margin-top: 20px;
            font-size: 1rem;
            font-weight: 600;
            color: white;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.3);
        }
        
        /* ========================================
           📊 SEÇÕES - VISUAL AZUL MALDIVAS
           ======================================== */
        .section-header {
            padding: 28px 40px;
            border-radius: 20px;
            margin: 40px 0 25px 0;
            box-shadow: 
                0 15px 45px rgba(0,0,0,0.15),
                0 5px 20px rgba(0,0,0,0.1);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        
        .section-header::after {
            content: '';
            position: absolute;
            top: 0;
            right: 0;
            width: 200px;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1));
        }
        
        .section-header:hover {
            transform: translateY(-5px);
            box-shadow: 
                0 25px 60px rgba(0,0,0,0.2),
                0 10px 30px rgba(0,0,0,0.15);
        }
        
        .section-header h2 {
            color: white;
            font-size: 1.9rem;
            font-weight: 800;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            position: relative;
            z-index: 1;
            letter-spacing: -0.5px;
        }
        
        /* ========================================
           💳 CARDS DE MÉTRICAS - AZUL MALDIVAS
           ======================================== */
        .stMetric {
            background: linear-gradient(145deg, #0a1628 0%, #0a1628dd 100%);
            padding: 30px;
            border-radius: 24px;
            color: white;
            box-shadow: 
                0 20px 50px rgba(10, 22, 40, 0.35),
                inset 0 1px 0 rgba(255,255,255,0.2);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            border: 1px solid rgba(255,255,255,0.15);
        }
        
        .stMetric:hover {
            transform: translateY(-8px) scale(1.02);
            box-shadow: 
                0 30px 70px rgba(10, 22, 40, 0.45),
                inset 0 1px 0 rgba(255,255,255,0.3);
        }
        
        /* ========================================
           📈 TABELAS - DESIGN ELEGANTE
           ======================================== */
        .stDataFrame {
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 
                0 15px 40px rgba(0,0,0,0.1),
                0 5px 15px rgba(0,0,0,0.05);
            border: 1px solid rgba(10, 22, 40, 0.2);
        }
        
        .stDataFrame table {
            font-size: 14px !important;
        }
        
        .stDataFrame th {
            background: linear-gradient(135deg, #0a1628 0%, #1a3a5c 100%) !important;
            color: white !important;
            font-weight: 700 !important;
            padding: 18px 15px !important;
            font-size: 14px !important;
        }
        
        .stDataFrame td {
            padding: 15px !important;
            font-size: 14px !important;
        }
        
        /* ========================================
           🔘 BOTÕES - CALL TO ACTION
           ======================================== */
        .stButton > button {
            background: linear-gradient(135deg, #0a1628 0%, #1a3a5c 100%);
            color: white;
            border: none;
            padding: 18px 50px;
            font-size: 1.2rem;
            font-weight: 800;
            border-radius: 16px;
            box-shadow: 
                0 15px 40px rgba(10, 22, 40, 0.45),
                inset 0 1px 0 rgba(255,255,255,0.2);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .stButton > button:hover {
            transform: translateY(-5px) scale(1.02);
            box-shadow: 
                0 25px 60px rgba(10, 22, 40, 0.55),
                inset 0 1px 0 rgba(255,255,255,0.3);
        }
        
        .stButton > button:active {
            transform: translateY(-2px);
        }
        
        /* ========================================
           📊 GRÁFICOS PLOTLY - CONTAINER
           ======================================== */
        .js-plotly-plot {
            border-radius: 20px;
            box-shadow: 
                0 15px 45px rgba(0,0,0,0.1),
                0 5px 20px rgba(0,0,0,0.05);
            background: white;
            padding: 10px;
        }
        
        /* ========================================
           ℹ️ INFO BOXES - PREMIUM STYLE
           ======================================== */
        .stAlert {
            border-radius: 16px;
            border-left-width: 6px;
            padding: 20px;
            font-size: 15px;
        }
        
        /* ========================================
           📋 EXPANDERS - ELEGANT STYLE
           ======================================== */
        .streamlit-expanderHeader {
            font-weight: 700;
            font-size: 1.15rem;
            color: #0a1628;
            padding: 15px 0;
        }
        
        /* ========================================
           🗂️ SIDEBAR - CLEAN DESIGN
           ======================================== */
        .css-1d391kg {
            background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
        }
        
        .sidebar .sidebar-content {
            padding: 20px;
        }
        
        /* ========================================
           🎯 FILTRO DE PERÍODO - DESTAQUE
           ======================================== */
        .filtro-periodo {
            background: linear-gradient(135deg, #0a1628 0%, #1a3a5c 100%);
            padding: 25px 35px;
            border-radius: 20px;
            margin-bottom: 35px;
            box-shadow: 
                0 15px 45px rgba(10, 22, 40, 0.35),
                inset 0 1px 0 rgba(255,255,255,0.2);
        }
        
        /* ========================================
           📝 LEGENDA DOS KPIs - BOX PREMIUM
           ======================================== */
        .legenda-box {
            background: linear-gradient(135deg, #ffffff 0%, #f0f8ff 100%);
            border: 3px solid #2e86ab;
            border-left: 10px solid #2e86ab;
            border-radius: 20px;
            padding: 35px 40px;
            margin: 35px 0;
            box-shadow: 
                0 15px 40px rgba(46, 134, 171, 0.15),
                0 5px 15px rgba(0,0,0,0.05);
        }
        
        .legenda-box h3 {
            color: #0a1628;
            margin-bottom: 25px;
            font-size: 1.5rem;
            font-weight: 800;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .legenda-item {
            margin: 12px 0;
            padding: 15px 20px;
            border-radius: 14px;
            border-left: 5px solid;
            font-size: 1.1rem;
            line-height: 1.6;
            transition: all 0.3s ease;
        }
        
        .legenda-item:hover {
            transform: translateX(5px);
        }
        
        /* ========================================
           🏆 RANKING CARDS - TOP 3
           ======================================== */
        .ranking-card {
            background: white;
            border-radius: 20px;
            padding: 25px;
            margin: 15px 0;
            box-shadow: 
                0 10px 30px rgba(0,0,0,0.1),
                0 5px 15px rgba(0,0,0,0.05);
            border: 3px solid;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .ranking-card:hover {
            transform: translateY(-5px) scale(1.02);
        }
        
        .ranking-card.ouro { border-color: #ffd700; }
        .ranking-card.prata { border-color: #c0c0c0; }
        .ranking-card.bronze { border-color: #cd7f32; }
        
        /* ========================================
           📱 RESPONSIVIDADE
           ======================================== */
        @media (max-width: 768px) {
            .main-header h1 { font-size: 2.5rem; }
            .main-header h2 { font-size: 1.2rem; }
            .section-header h2 { font-size: 1.4rem; }
        }
        
        /* ========================================
           ✨ ANIMAÇÕES SUAVES
           ======================================== */
        * {
            transition: background-color 0.3s ease, 
                        border-color 0.3s ease,
                        box-shadow 0.3s ease;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # =========================================================================
    # 🎬 HEADER PRINCIPAL - AZUL MALDIVAS
    # =========================================================================
    st.markdown("""
    <div class="main-header">
        <h1>🏆 ASSERTIF CORRETORA</h1>
        <h2>Dashboard Financeiro</h2>
        <div class="badge">📊 YTD Janeiro - Abril 2026 • Versão 6.0</div>
    </div>
    """, unsafe_allow_html=True)
    
    # =========================================================================
    # 📂 SIDEBAR PREMIUM
    # =========================================================================
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 20px 0;">
            <span style="font-size: 3rem;">📊</span>
            <h2 style="color: #0a1628; margin: 15px 0 5px 0; font-weight: 800;">ASSERTIF</h2>
            <p style="color: #6c757d; font-size: 0.9rem;">Dashboard Premium</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("### 📁 Upload de Dados")
        uploaded_file = st.file_uploader(
            "Arraste sua planilha Excel aqui",
            type=['xlsx', 'xls'],
            help="Selecione o arquivo Excel com os dados financeiros",
            key="file_uploader"
        )
        
        st.markdown("---")
        
        st.markdown("### ⚙️ Configurações de Exibição")
        show_tables = st.checkbox("📋 Mostrar tabelas detalhadas", value=True)
        show_charts = st.checkbox("📈 Mostrar gráficos", value=True)
        
        st.markdown("---")
        
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #0a162822 0%, #1a3a5c22 100%);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            margin-top: 20px;
        ">
            <p style="font-size: 0.85rem; color: #0a1628; margin: 0; font-weight: 600;">
                ✨ Versão Premium<br/>
                <span style="font-size: 0.75rem; color: #6c757d;">v6.0 • Maio 2026</span>
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # =========================================================================
    # 🗓️ FILTRO DE PERÍODO - PREMIUM
    # =========================================================================
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #0a1628 0%, #1a3a5c 100%);
        padding: 20px 35px;
        border-radius: 20px;
        margin-bottom: 35px;
        box-shadow: 0 15px 45px rgba(10, 22, 40, 0.35);
    ">
        <h3 style="color: white; margin: 0; font-size: 1.4rem; font-weight: 700;">
            🗓️ SELECIONE O PERÍODO DE ANÁLISE
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    col_filtro1, col_filtro2 = st.columns([3, 1])
    
    with col_filtro1:
        meses_opcoes = ['All', 'Janeiro', 'Fevereiro', 'Março', 'Abril']
        meses_selecionados = st.multiselect(
            "Selecione o(s) mês(es) para análise:",
            options=meses_opcoes,
            default=['All'],
            help="Selecione 'All' para ver todos os meses ou escolha meses específicos"
        )
    
    with col_filtro2:
        if 'All' in meses_selecionados or len(meses_selecionados) == 0:
            st.success("📊 **YTD Completo**")
        else:
            st.info(f"📊 **{', '.join(meses_selecionados)}**")
    
    # =========================================================================
    # 📊 PROCESSAMENTO DOS DADOS
    # =========================================================================
    df_receitas_clean = None
    df_despesas_clean = None
    df_seg = None
    df_prod = None
    df_orig = None
    df_cli = None
    df_cat = None
    dados_mensais_atual = DADOS_MENSAIS.copy()
    
    if uploaded_file is not None:
        dados = pd.read_excel(uploaded_file, sheet_name=None)
        
        st.sidebar.success(f"✅ Arquivo carregado com sucesso!")
        st.sidebar.info(f"📑 Abas encontradas: {len(dados.keys())}")
        
        df_dre = dados.get('DRE 2026', pd.DataFrame())
        df_receitas = dados.get('ASSERTIF DIRETO', pd.DataFrame())
        df_despesas = dados.get('DESPESAS', pd.DataFrame())
        
        if len(df_dre) > 0:
            dados_extraidos = extrair_dados_dre(df_dre)
            if dados_extraidos:
                dados_mensais_atual = dados_extraidos
                st.sidebar.success("✅ Dados da DRE extraídos!")
        
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
            
            df_seg = df_receitas_clean.groupby(col_seguradora)[col_comissao].agg(['sum', 'count', 'mean']).reset_index()
            df_seg.columns = ['Seguradora', 'Total', 'Qtd', 'Média']
            df_seg = df_seg[df_seg['Total'] > 0].sort_values('Total', ascending=False)
            df_seg['% do Total'] = (df_seg['Total'] / df_seg['Total'].sum() * 100).round(1)
            
            df_prod = df_receitas_clean.groupby(col_produto)[col_comissao].agg(['sum', 'count', 'mean']).reset_index()
            df_prod.columns = ['Produto', 'Total', 'Qtd', 'Média']
            df_prod = df_prod[df_prod['Total'] > 0].sort_values('Total', ascending=False)
            df_prod['% do Total'] = (df_prod['Total'] / df_prod['Total'].sum() * 100).round(1)
            
            df_orig = df_receitas_clean.groupby(col_originador)[col_comissao].agg(['sum', 'count', 'mean']).reset_index()
            df_orig.columns = ['Originador', 'Total', 'Operações', 'Ticket Médio']
            df_orig = df_orig[df_orig['Total'] > 0].sort_values('Total', ascending=False)
            df_orig['% do Total'] = (df_orig['Total'] / df_orig['Total'].sum() * 100).round(1)
            
            df_cli = df_receitas_clean.groupby(col_cliente)[col_comissao].agg(['sum', 'count', 'mean']).reset_index()
            df_cli.columns = ['Cliente', 'Total', 'Qtd', 'Média']
            df_cli = df_cli[df_cli['Total'] > 0].sort_values('Total', ascending=False)
            df_cli['% do Total'] = (df_cli['Total'] / df_cli['Total'].sum() * 100).round(1)
        
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
    
    # Calcular dados filtrados
    totais, meses_ativos = calcular_dados_filtrados(meses_selecionados, dados_mensais_atual)
    
    # =========================================================================
    # 💰 SEÇÃO 1: KPIs PRINCIPAIS - AZUL MALDIVAS (SEM SUBTÍTULO)
    # =========================================================================
    st.markdown("""
    <div class="section-header" style="background: linear-gradient(135deg, #0a1628 0%, #1a3a5c 100%);">
        <h2>💰 INDICADORES PRINCIPAIS (KPIs)</h2>
    </div>
    """, unsafe_allow_html=True)
    
    faturamento = totais['receita_bruta']
    custos_totais = totais['custos_totais']
    margem_contrib = totais['margem_contrib']
    despesas_total = totais['despesas']
    resultado_op = totais['resultado_op']
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(criar_cartao_kpi_html(
            "FATURAMENTO", 
            formatar_moeda(faturamento), 
            "", 
            "#0a1628", 
            "💰"
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(criar_cartao_kpi_html(
            "CUSTOS TOTAIS", 
            formatar_moeda(custos_totais), 
            "", 
            "#ff6b6b", 
            "📉"
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(criar_cartao_kpi_html(
            "MARGEM CONTRIB.", 
            formatar_moeda(margem_contrib), 
            "", 
            "#2e86ab", 
            "📊"
        ), unsafe_allow_html=True)
    
    with col4:
        st.markdown(criar_cartao_kpi_html(
            "DESPESAS TOTAIS", 
            formatar_moeda(despesas_total), 
            "", 
            "#feca57", 
            "💸"
        ), unsafe_allow_html=True)
    
    with col5:
        cor_resultado = "#00d4aa" if resultado_op >= 0 else "#ff6b6b"
        icone_resultado = "🎯" if resultado_op >= 0 else "⚠️"
        st.markdown(criar_cartao_kpi_html(
            "RESULTADO OPER.", 
            formatar_moeda(resultado_op), 
            "", 
            cor_resultado, 
            icone_resultado
        ), unsafe_allow_html=True)
    
    # =========================================================================
    # 📌 LEGENDA DOS KPIs - BOX PREMIUM
    # =========================================================================
    st.markdown("""
    <div class="legenda-box">
        <h3>📌 Legenda dos Indicadores</h3>
        <div style="color: #0a1628; font-size: 1.1rem; line-height: 2.2;">
            <div class="legenda-item" style="background: rgba(10, 22, 40, 0.1); border-color: #0a1628;">
                <strong style="color: #0a1628;">💰 Faturamento Bruto:</strong> 
                <span>Soma da Receita Bruta de Produção Direta e Portal MAAS</span>
            </div>
            <div class="legenda-item" style="background: rgba(255, 107, 107, 0.1); border-color: #ff6b6b;">
                <strong style="color: #ff6b6b;">📉 Custos Totais:</strong> 
                <span>Impostos Diretos + Custo Operacional (D.A.) + Rebate AAI - Co-corretagem</span>
            </div>
            <div class="legenda-item" style="background: rgba(46, 134, 171, 0.1); border-color: #2e86ab;">
                <strong style="color: #2e86ab;">📊 Margem de Contribuição:</strong> 
                <span>Faturamento Bruto menos Custos Totais (Prod. Direta + Portal MAAS)</span>
            </div>
            <div class="legenda-item" style="background: rgba(254, 202, 87, 0.1); border-color: #feca57;">
                <strong style="color: #e0a800;">💸 Despesas Totais:</strong> 
                <span>Despesas Operacionais + Folha + Terceiros</span>
            </div>
            <div class="legenda-item" style="background: rgba(0, 212, 170, 0.1); border-color: #00d4aa;">
                <strong style="color: #00d4aa;">🎯 Resultado Operacional:</strong> 
                <span>Margem de Contribuição - Despesas • Base para distribuição 65/35</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # =========================================================================
    # 📈 SEÇÃO 2: EVOLUÇÃO MENSAL - GRÁFICOS AZUL CLARO
    # =========================================================================
    if show_charts:
        st.markdown("""
        <div class="section-header" style="background: linear-gradient(135deg, #1a3a5c 0%, #2e86ab 100%);">
            <h2>📈 EVOLUÇÃO MENSAL - RECEITA vs RESULTADO</h2>
        </div>
        """, unsafe_allow_html=True)
        
        meses = list(dados_mensais_atual.keys())
        receita_bruta = [dados_mensais_atual[m]['receita_bruta'] for m in meses]
        resultado_op_mensal = [dados_mensais_atual[m]['resultado_op'] for m in meses]
        
        # Crescimento mensal da RECEITA (não do resultado)
        crescimento = [0]
        for i in range(1, len(receita_bruta)):
            if receita_bruta[i-1] > 0:
                cresc = ((receita_bruta[i] - receita_bruta[i-1]) / receita_bruta[i-1]) * 100
            else:
                cresc = 0
            crescimento.append(round(cresc, 1))
        
        # Cor azul claro uniforme para todos os gráficos
        azul_claro = '#7dd3fc'
        
        fig_evolucao = make_subplots(
            rows=1, cols=3,
            subplot_titles=(
                '<b>📊 Receita Bruta por Mês</b>',
                '<b>📈 Crescimento Mensal da Receita (%)</b>',
                '<b>🎯 Resultado Operacional</b>'
            ),
            horizontal_spacing=0.08,
            column_widths=[0.35, 0.30, 0.35]
        )
        
        # Gráfico 1: Receita Bruta - Azul Claro
        fig_evolucao.add_trace(
            go.Bar(
                x=meses, y=receita_bruta,
                marker=dict(
                    color=azul_claro,
                    line=dict(width=3, color='white'),
                    cornerradius=8
                ),
                text=[f"R$ {v/1000:.1f}K" for v in receita_bruta],
                textposition='outside',
                textfont=dict(size=16, color='#0a1628', family='Arial Black'),
                name='Receita Bruta',
                hovertemplate='<b>%{x}</b><br>Receita: R$ %{y:,.0f}<extra></extra>',
                width=0.6
            ),
            row=1, col=1
        )
        
        # Gráfico 2: Crescimento Mensal da Receita - Azul Claro
        fig_evolucao.add_trace(
            go.Scatter(
                x=meses, y=crescimento,
                mode='lines+markers+text',
                line=dict(color=azul_claro, width=5, shape='spline'),
                marker=dict(size=22, color=azul_claro, line=dict(width=4, color='white'), symbol='circle'),
                text=[f"{v:+.1f}%" for v in crescimento],
                textposition='top center',
                textfont=dict(size=15, family='Arial Black', color='#0a1628'),
                name='Crescimento %',
                hovertemplate='<b>%{x}</b><br>Crescimento: %{y:+.1f}%<extra></extra>'
            ),
            row=1, col=2
        )
        
        fig_evolucao.add_hline(y=0, line_dash="dash", line_color="#ff6b6b", line_width=3, row=1, col=2)
        
        # Gráfico 3: Resultado Operacional - Azul Claro
        fig_evolucao.add_trace(
            go.Bar(
                x=meses, y=resultado_op_mensal,
                marker=dict(
                    color=azul_claro,
                    line=dict(width=3, color='white'),
                    cornerradius=8
                ),
                text=[f"R$ {v/1000:.1f}K" for v in resultado_op_mensal],
                textposition='outside',
                textfont=dict(size=16, family='Arial Black', color='#0a1628'),
                name='Resultado',
                hovertemplate='<b>%{x}</b><br>Resultado: R$ %{y:,.0f}<extra></extra>',
                width=0.6
            ),
            row=1, col=3
        )
        
        fig_evolucao.add_hline(y=0, line_dash="solid", line_color="#ff6b6b", line_width=3, row=1, col=3)
        
        fig_evolucao.update_layout(
            height=550,
            showlegend=False,
            paper_bgcolor='white',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter, Segoe UI', size=14, color='#0a1628'),
            hoverlabel=dict(bgcolor='white', font_size=15, bordercolor='#1a3a5c'),
            margin=dict(l=70, r=70, t=100, b=70)
        )
        
        fig_evolucao.update_xaxes(
            gridcolor='#e8e8e8', 
            tickfont=dict(size=14, family='Inter', color='#0a1628'), 
            tickangle=0
        )
        fig_evolucao.update_yaxes(
            gridcolor='#e8e8e8', 
            tickfont=dict(size=13, family='Inter')
        )
        
        st.plotly_chart(fig_evolucao, use_container_width=True)
    
    # =========================================================================
    # 🏆 SEÇÃO 3: RANKING DE SEGURADORAS
    # =========================================================================
    if show_charts and df_seg is not None and len(df_seg) > 0:
        st.markdown("""
        <div class="section-header" style="background: linear-gradient(135deg, #1a3a5c 0%, #0a1628 100%);">
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
                colorscale=[[0, '#4ea8de'], [0.5, '#2e86ab'], [1, '#0a1628']],
                showscale=True,
                colorbar=dict(
                    title=dict(text='Comissão (R$)', font=dict(size=13, family='Inter')), 
                    thickness=18, 
                    len=0.7
                ),
                line=dict(width=2, color='white'),
                cornerradius=6
            ),
            text=[f"R$ {v/1000:.1f}K ({p:.1f}%)" for v, p in zip(df_seg['Total'].head(15), df_seg['% do Total'].head(15))],
            textposition='outside',
            textfont=dict(size=13, family='Inter', color='#0a1628', weight='bold'),
            hovertemplate='<b>%{y}</b><br>Comissão: R$ %{x:,.2f}<extra></extra>',
            width=0.7
        ))
        
        fig_ranking_seg.update_layout(
            title=dict(
                text='🏢 Top 15 Seguradoras por Volume de Comissão', 
                font=dict(size=22, family='Inter', color='#0a1628', weight='bold'), 
                x=0.5, 
                xanchor='center'
            ),
            height=700,
            paper_bgcolor='white',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis_title=dict(text='Comissão Total (R$)', font=dict(size=15, family='Inter', weight='bold')),
            yaxis=dict(categoryorder='total ascending', tickfont=dict(size=13, family='Inter')),
            font=dict(family='Inter', size=13),
            margin=dict(l=200, r=180, t=100, b=70)
        )
        
        fig_ranking_seg.update_xaxes(gridcolor='#e8e8e8', tickformat=',.0f')
        st.plotly_chart(fig_ranking_seg, use_container_width=True)
    
    # =========================================================================
    # 🤝 SEÇÃO 4: DISTRIBUIÇÃO ENTRE SÓCIOS
    # =========================================================================
    if show_charts:
        st.markdown("""
        <div class="section-header" style="background: linear-gradient(135deg, #2e86ab 0%, #4ea8de 100%);">
            <h2>🤝 DISTRIBUIÇÃO DE RESULTADOS - SÓCIOS</h2>
        </div>
        """, unsafe_allow_html=True)
        
        meses_dist = list(dados_mensais_atual.keys())
        resultado_dist = [dados_mensais_atual[m]['resultado_op'] for m in meses_dist]
        partner = [int(r * 0.65) for r in resultado_dist]
        maldivas = [int(r * 0.35) for r in resultado_dist]
        
        fig_dist = go.Figure()
        
        fig_dist.add_trace(go.Bar(
            name='Partner (65%)',
            x=meses_dist,
            y=partner,
            marker_color='#0a1628',
            marker_line=dict(width=3, color='white'),
            text=[f"R$ {v/1000:.1f}K" for v in partner],
            textposition='outside',
            textfont=dict(size=16, family='Inter', weight='bold'),
            width=0.35
        ))
        
        fig_dist.add_trace(go.Bar(
            name='Maldivas (35%)',
            x=meses_dist,
            y=maldivas,
            marker_color='#4ea8de',
            marker_line=dict(width=3, color='white'),
            text=[f"R$ {v/1000:.1f}K" for v in maldivas],
            textposition='outside',
            textfont=dict(size=16, family='Inter', weight='bold'),
            width=0.35
        ))
        
        fig_dist.add_trace(go.Scatter(
            name='Resultado Total',
            x=meses_dist,
            y=resultado_dist,
            mode='lines+markers+text',
            line=dict(color='#00d4aa', width=4, dash='dot'),
            marker=dict(
                size=16, 
                color=['#00d4aa' if r >= 0 else '#ff6b6b' for r in resultado_dist], 
                line=dict(width=3, color='white')
            ),
            text=[f"R$ {v/1000:.1f}K" for v in resultado_dist],
            textposition='top center',
            textfont=dict(size=14, family='Inter', color='#0a1628', weight='bold'),
        ))
        
        fig_dist.add_hline(y=0, line_dash="solid", line_color="#ff6b6b", line_width=3)
        
        min_val = min(min(partner), min(maldivas), min(resultado_dist))
        max_val = max(max(partner), max(maldivas), max(resultado_dist))
        y_range = [min_val * 1.4 if min_val < 0 else -1000, max_val * 1.4]
        
        fig_dist.update_layout(
            title=dict(
                text='📊 Distribuição do Resultado - Partner 65% / Maldivas 35%',
                font=dict(size=22, family='Inter', color='#0a1628', weight='bold'),
                x=0.5,
                xanchor='center'
            ),
            height=550,
            paper_bgcolor='white',
            plot_bgcolor='rgba(0,0,0,0)',
            barmode='group',
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=-0.22,
                xanchor='center',
                x=0.5,
                font=dict(size=15, family='Inter', weight='bold')
            ),
            font=dict(family='Inter', size=14),
            margin=dict(l=70, r=70, t=120, b=120),
            yaxis=dict(
                title='Valor (R$)',
                gridcolor='#e8e8e8',
                range=y_range,
                tickformat=',.0f',
                tickfont=dict(size=13)
            ),
            xaxis=dict(
                title='',
                tickfont=dict(size=16, family='Inter', weight='bold')
            )
        )
        
        st.plotly_chart(fig_dist, use_container_width=True)
        
        total_resultado = sum(resultado_dist)
        partner_total = int(total_resultado * 0.65)
        maldivas_total = int(total_resultado * 0.35)
        
        # =========================================================================
        # ✅ TOTAIS YTD - FORMATAÇÃO CORRIGIDA E BONITA
        # =========================================================================
        if total_resultado >= 0:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #00d4aa 0%, #00b894 100%);
                padding: 25px 35px;
                border-radius: 16px;
                margin: 20px 0;
                box-shadow: 0 10px 30px rgba(0, 212, 170, 0.3);
            ">
                <div style="display: flex; align-items: center; justify-content: center; flex-wrap: wrap; gap: 15px;">
                    <span style="font-size: 2rem;">✅</span>
                    <div style="color: white; font-size: 1.1rem; font-weight: 600; text-align: center;">
                        <strong style="font-size: 1.3rem;">TOTAIS YTD</strong><br/>
                        <span style="font-size: 1.5rem; font-weight: 900;">Resultado: {formatar_moeda(total_resultado)}</span>
                    </div>
                </div>
                <div style="
                    display: flex; 
                    justify-content: center; 
                    gap: 40px; 
                    margin-top: 20px; 
                    flex-wrap: wrap;
                ">
                    <div style="
                        background: rgba(255,255,255,0.2); 
                        padding: 15px 25px; 
                        border-radius: 12px;
                        text-align: center;
                    ">
                        <div style="color: white; font-size: 0.9rem; opacity: 0.9;">Partner (65%)</div>
                        <div style="color: white; font-size: 1.4rem; font-weight: 900;">{formatar_moeda(partner_total)}</div>
                    </div>
                    <div style="
                        background: rgba(255,255,255,0.2); 
                        padding: 15px 25px; 
                        border-radius: 12px;
                        text-align: center;
                    ">
                        <div style="color: white; font-size: 0.9rem; opacity: 0.9;">Maldivas (35%)</div>
                        <div style="color: white; font-size: 1.4rem; font-weight: 900;">{formatar_moeda(maldivas_total)}</div>
                    </div>
                    <div style="
                        background: rgba(255,255,255,0.3); 
                        padding: 15px 25px; 
                        border-radius: 12px;
                        text-align: center;
                    ">
                        <div style="color: white; font-size: 0.9rem; opacity: 0.9;">Status</div>
                        <div style="color: white; font-size: 1.4rem; font-weight: 900;">📈 LUCRO</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
                padding: 25px 35px;
                border-radius: 16px;
                margin: 20px 0;
                box-shadow: 0 10px 30px rgba(255, 107, 107, 0.3);
            ">
                <div style="display: flex; align-items: center; justify-content: center; flex-wrap: wrap; gap: 15px;">
                    <span style="font-size: 2rem;">⚠️</span>
                    <div style="color: white; font-size: 1.1rem; font-weight: 600; text-align: center;">
                        <strong style="font-size: 1.3rem;">TOTAIS YTD</strong><br/>
                        <span style="font-size: 1.5rem; font-weight: 900;">Resultado: {formatar_moeda(total_resultado)}</span>
                    </div>
                </div>
                <div style="
                    display: flex; 
                    justify-content: center; 
                    gap: 40px; 
                    margin-top: 20px; 
                    flex-wrap: wrap;
                ">
                    <div style="
                        background: rgba(255,255,255,0.2); 
                        padding: 15px 25px; 
                        border-radius: 12px;
                        text-align: center;
                    ">
                        <div style="color: white; font-size: 0.9rem; opacity: 0.9;">Partner (65%)</div>
                        <div style="color: white; font-size: 1.4rem; font-weight: 900;">{formatar_moeda(partner_total)}</div>
                    </div>
                    <div style="
                        background: rgba(255,255,255,0.2); 
                        padding: 15px 25px; 
                        border-radius: 12px;
                        text-align: center;
                    ">
                        <div style="color: white; font-size: 0.9rem; opacity: 0.9;">Maldivas (35%)</div>
                        <div style="color: white; font-size: 1.4rem; font-weight: 900;">{formatar_moeda(maldivas_total)}</div>
                    </div>
                    <div style="
                        background: rgba(255,255,255,0.3); 
                        padding: 15px 25px; 
                        border-radius: 12px;
                        text-align: center;
                    ">
                        <div style="color: white; font-size: 0.9rem; opacity: 0.9;">Status</div>
                        <div style="color: white; font-size: 1.4rem; font-weight: 900;">📉 PREJUÍZO</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # =========================================================================
    # 📦 SEÇÃO 5: ANÁLISE POR PRODUTO
    # =========================================================================
    if show_charts and df_prod is not None and len(df_prod) > 0:
        st.markdown("""
        <div class="section-header" style="background: linear-gradient(135deg, #feca57 0%, #ff9f43 100%);">
            <h2 style="color: #0a1628;">📦 ANÁLISE POR TIPO DE PRODUTO</h2>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_prod = px.sunburst(
                df_prod, 
                path=['Produto'], 
                values='Total', 
                color='Total', 
                color_continuous_scale='YlOrRd', 
                title='☀️ Distribuição por Produto (Sunburst)'
            )
            fig_prod.update_layout(
                height=600, 
                paper_bgcolor='white', 
                font=dict(family='Inter', size=13),
                title=dict(
                    font=dict(size=20, family='Inter', color='#0a1628', weight='bold'), 
                    x=0.5, 
                    xanchor='center'
                ), 
                margin=dict(l=40, r=40, t=100, b=40)
            )
            fig_prod.update_traces(
                textinfo='label+percent entry', 
                textfont=dict(size=14, family='Inter'),
                hovertemplate='<b>%{label}</b><br>Comissão: R$ %{value:,.2f}<br>Participação: %{percentEntry:.1%}<extra></extra>'
            )
            st.plotly_chart(fig_prod, use_container_width=True)
        
        with col2:
            fig_prod_bar = go.Figure()
            fig_prod_bar.add_trace(go.Bar(
                y=df_prod['Produto'], 
                x=df_prod['Total'], 
                orientation='h',
                marker=dict(
                    color=df_prod['Total'], 
                    colorscale='YlOrRd', 
                    showscale=True,
                    colorbar=dict(
                        title=dict(text='Comissão', font=dict(size=12)), 
                        thickness=15, 
                        len=0.7
                    ), 
                    line=dict(width=2, color='white'),
                    cornerradius=5
                ),
                text=[f"R$ {v/1000:.1f}K ({p:.1f}%)" for v, p in zip(df_prod['Total'], df_prod['% do Total'])],
                textposition='outside', 
                textfont=dict(size=13, family='Inter', color='#0a1628'),
                hovertemplate='<b>%{y}</b><br>Comissão: R$ %{x:,.2f}<extra></extra>', 
                width=0.7
            ))
            fig_prod_bar.update_layout(
                title=dict(
                    text='📊 Comissão por Tipo de Produto', 
                    font=dict(size=20, family='Inter', color='#0a1628', weight='bold'), 
                    x=0.5, 
                    xanchor='center'
                ),
                height=550, 
                paper_bgcolor='white', 
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis_title=dict(text='Comissão Total (R$)', font=dict(size=14, family='Inter')),
                yaxis=dict(categoryorder='total ascending', tickfont=dict(size=12, family='Inter')),
                font=dict(family='Inter', size=13), 
                margin=dict(l=180, r=150, t=100, b=70)
            )
            fig_prod_bar.update_xaxes(gridcolor='#e8e8e8', tickformat=',.0f')
            st.plotly_chart(fig_prod_bar, use_container_width=True)
    
    # =========================================================================
    # 👥 SEÇÃO 6: RANKING DE ORIGINADORES
    # =========================================================================
    if show_charts and df_orig is not None and len(df_orig) > 0:
        st.markdown("""
        <div class="section-header" style="background: linear-gradient(135deg, #2e86ab 0%, #00d4aa 100%);">
            <h2>👥 RANKING - TOP ORIGINADORES</h2>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            fig_orig = go.Figure()
            top_5 = df_orig.head(5)
            outros_total = df_orig.iloc[5:]['Total'].sum() if len(df_orig) > 5 else 0
            outros_perc = df_orig.iloc[5:]['% do Total'].sum() if len(df_orig) > 5 else 0
            
            if outros_total > 0:
                outros = pd.DataFrame({
                    'Originador': ['Outros'], 
                    'Total': [outros_total], 
                    '% do Total': [outros_perc]
                })
                df_orig_chart = pd.concat([top_5, outros])
            else:
                df_orig_chart = top_5
            
            fig_orig.add_trace(go.Pie(
                labels=df_orig_chart['Originador'], 
                values=df_orig_chart['Total'], 
                hole=0.55,
                marker=dict(colors=CORES['gradiente'], line=dict(width=4, color='white')),
                textinfo='label+percent', 
                textposition='outside', 
                textfont=dict(size=14, family='Inter'),
                hovertemplate='<b>%{label}</b><br>Comissão: R$ %{value:,.2f}<br>Participação: %{percent}<extra></extra>'
            ))
            
            fig_orig.update_layout(
                title=dict(
                    text='🏅 Distribuição de Comissão por Originador', 
                    font=dict(size=20, family='Inter', color='#0a1628', weight='bold'), 
                    x=0.5, 
                    xanchor='center'
                ),
                height=600, 
                paper_bgcolor='white',
                annotations=[dict(
                    text=f'Total<br><b>{formatar_moeda(df_orig["Total"].sum())}</b>', 
                    x=0.5, 
                    y=0.5, 
                    font_size=16, 
                    font_family='Inter', 
                    showarrow=False
                )],
                showlegend=True, 
                legend=dict(
                    orientation='h', 
                    yanchor='bottom', 
                    y=-0.18, 
                    xanchor='center', 
                    x=0.5, 
                    font=dict(size=12)
                ),
                margin=dict(l=80, r=80, t=100, b=120)
            )
            st.plotly_chart(fig_orig, use_container_width=True)
        
        with col2:
            st.markdown("### 🏆 Top 3 Originadores")
            medalhas = ['🥇', '🥈', '🥉']
            cores_medalha = ['#ffd700', '#c0c0c0', '#cd7f32']
            classes_medalha = ['ouro', 'prata', 'bronze']
            
            for i, (idx, row) in enumerate(df_orig.head(3).iterrows()):
                st.markdown(f"""
                <div class="ranking-card {classes_medalha[i]}" style="border-color: {cores_medalha[i]};">
                    <div style="display: flex; align-items: center;">
                        <span style="font-size: 3.5rem; margin-right: 25px; filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.2));">{medalhas[i]}</span>
                        <div>
                            <div style="font-size: 1.3rem; font-weight: 800; color: #0a1628; margin-bottom: 8px;">{row['Originador']}</div>
                            <div style="font-size: 1.8rem; color: #00d4aa; font-weight: 900;">{formatar_moeda(row['Total'])}</div>
                            <div style="font-size: 1rem; color: #6c757d; margin-top: 8px;">
                                📊 {int(row['Operações'])} operações | 💰 Ticket: {formatar_moeda(row['Ticket Médio'])}
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # =========================================================================
    # 🏅 SEÇÃO 7: RANKING MAIORES CLIENTES
    # =========================================================================
    if show_charts and df_cli is not None and len(df_cli) > 0:
        st.markdown("""
        <div class="section-header" style="background: linear-gradient(135deg, #00d4aa 0%, #2e86ab 100%);">
            <h2>🏅 RANKING - MAIORES CLIENTES POR RECEITA</h2>
        </div>
        """, unsafe_allow_html=True)
        
        fig_ranking_cli = go.Figure()
        
        fig_ranking_cli.add_trace(go.Bar(
            y=df_cli['Cliente'].head(15), 
            x=df_cli['Total'].head(15), 
            orientation='h',
            marker=dict(
                color=df_cli['Total'].head(15), 
                colorscale='Tealgrn', 
                showscale=True,
                colorbar=dict(
                    title=dict(text='Receita (R$)', font=dict(size=12)), 
                    thickness=18, 
                    len=0.7
                ), 
                line=dict(width=2, color='white'),
                cornerradius=6
            ),
            text=[f"R$ {v/1000:.1f}K ({p:.1f}%)" for v, p in zip(df_cli['Total'].head(15), df_cli['% do Total'].head(15))],
            textposition='outside', 
            textfont=dict(size=12, family='Inter', color='#0a1628'),
            hovertemplate='<b>%{y}</b><br>Receita: R$ %{x:,.2f}<extra></extra>', 
            width=0.7
        ))
        
        fig_ranking_cli.update_layout(
            title=dict(
                text='🏢 Top 15 Clientes por Volume de Receita', 
                font=dict(size=22, family='Inter', color='#0a1628', weight='bold'), 
                x=0.5, 
                xanchor='center'
            ),
            height=700, 
            paper_bgcolor='white', 
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis_title=dict(text='Receita Total (R$)', font=dict(size=15, family='Inter')),
            yaxis=dict(categoryorder='total ascending', tickfont=dict(size=11, family='Inter')),
            font=dict(family='Inter', size=13), 
            margin=dict(l=300, r=180, t=100, b=70)
        )
        fig_ranking_cli.update_xaxes(gridcolor='#e8e8e8', tickformat=',.0f')
        st.plotly_chart(fig_ranking_cli, use_container_width=True)
    
    # =========================================================================
    # 💸 SEÇÃO 8: RANKING DE DESPESAS
    # =========================================================================
    if show_charts and df_cat is not None and len(df_cat) > 0:
        st.markdown("""
        <div class="section-header" style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);">
            <h2>💸 RANKING - MAIORES DESPESAS</h2>
        </div>
        """, unsafe_allow_html=True)
        
        fig_desp_bar = go.Figure()
        
        fig_desp_bar.add_trace(go.Bar(
            x=df_cat['Categoria'].head(10), 
            y=df_cat['Total'].head(10),
            marker=dict(
                color=df_cat['Total'].head(10), 
                colorscale='Reds', 
                showscale=False, 
                line=dict(width=2, color='white'),
                cornerradius=8
            ),
            text=[f"R$ {v/1000:.1f}K" for v in df_cat['Total'].head(10)],
            textposition='outside', 
            textfont=dict(size=14, family='Inter', color='#0a1628'),
            hovertemplate='<b>%{x}</b><br>Valor: R$ %{y:,.2f}<extra></extra>', 
            width=0.7
        ))
        
        fig_desp_bar.update_layout(
            title=dict(
                text='📊 Top 10 Categorias de Despesas', 
                font=dict(size=22, family='Inter', color='#0a1628', weight='bold'), 
                x=0.5, 
                xanchor='center'
            ),
            height=600, 
            paper_bgcolor='white', 
            plot_bgcolor='rgba(0,0,0,0)', 
            xaxis_tickangle=-35,
            xaxis=dict(tickfont=dict(size=11, family='Inter')),
            yaxis_title=dict(text='Valor (R$)', font=dict(size=15, family='Inter')),
            yaxis=dict(range=[0, df_cat['Total'].head(10).max() * 1.3]),
            font=dict(family='Inter', size=13), 
            margin=dict(l=80, r=60, t=100, b=200)
        )
        fig_desp_bar.update_yaxes(gridcolor='#e8e8e8', tickformat=',.0f')
        st.plotly_chart(fig_desp_bar, use_container_width=True)
    
    # =========================================================================
    # 📋 SEÇÃO 9: RESUMO EXECUTIVO
    # =========================================================================
    if show_tables:
        st.markdown("""
        <div class="section-header" style="background: linear-gradient(135deg, #0a1628 0%, #1a3a5c 100%);">
            <h2>📋 RESUMO EXECUTIVO - DRE</h2>
        </div>
        """, unsafe_allow_html=True)
        
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
                '📉 CUSTOS TOTAIS',
                '',
                '(=) MARGEM DE CONTRIBUIÇÃO',
                '',
                '💸 DESPESAS TOTAIS',
                '    → Despesas Operacionais',
                '    → Folha + Terceiros',
                '',
                '🎯 RESULTADO OPERACIONAL',
            ],
            'Valor': [
                formatar_moeda(totais['receita_bruta']),
                'R$ 177.797,00',
                'R$ 275,00',
                '',
                '(R$ 31.044,00)',
                '(R$ 14.842,00)',
                'R$ 803,00',
                '(R$ 50.646,00)',
                '',
                formatar_moeda(totais['custos_totais']),
                '',
                formatar_moeda(totais['margem_contrib']),
                '',
                formatar_moeda(totais['despesas']),
                '(R$ 29.104,00)',
                '(R$ 16.946,00)',
                '',
                formatar_moeda(totais['resultado_op']),
            ]
        }
        
        df_resumo_display = pd.DataFrame(resumo_data)
        st.dataframe(df_resumo_display, use_container_width=True, hide_index=True, height=650)
    
    # =========================================================================
    # 📥 SEÇÃO 10: EXPORTAR PDF
    # =========================================================================
    st.markdown("---")
    st.markdown("""
    <div class="section-header" style="background: linear-gradient(135deg, #00d4aa 0%, #00b894 100%);">
        <h2>📥 EXPORTAR DASHBOARD PARA PDF</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("📄 GERAR PDF PROFISSIONAL PREMIUM", type="primary", use_container_width=True):
            with st.spinner("🎬 Gerando PDF..."):
                try:
                    pdf_generator = PDFDashboardGenerator()
                    pdf_bytes = pdf_generator.generate_pdf(
                        df_receitas_clean=df_receitas_clean,
                        df_despesas_clean=df_despesas_clean,
                        df_seg=df_seg,
                        df_prod=df_prod,
                        df_orig=df_orig,
                        df_cli=df_cli,
                        df_cat=df_cat
                    )
                    
                    st.success("✅ PDF gerado com sucesso!")
                    
                    st.download_button(
                        label="⬇️ BAIXAR PDF",
                        data=pdf_bytes,
                        file_name=f"Assertif_Dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    
                except Exception as e:
                    st.error(f"❌ Erro ao gerar PDF: {str(e)}")
                    st.info("💡 Verifique se todas as bibliotecas estão instaladas corretamente.")
    
    # =========================================================================
    # 🎬 FOOTER - AZUL MALDIVAS
    # =========================================================================
    st.markdown("---")
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #0a1628 0%, #1a3a5c 50%, #2e86ab 100%);
        padding: 50px;
        border-radius: 28px;
        text-align: center;
        margin-top: 50px;
        color: white;
        box-shadow: 0 25px 70px rgba(10, 22, 40, 0.5);
    ">
        <span style="font-size: 4rem; display: block; margin-bottom: 20px;">📊</span>
        <h2 style="margin-bottom: 15px; font-size: 2rem; font-weight: 900;">ASSERTIF CORRETORA</h2>
        <h3 style="margin-bottom: 20px; font-weight: 600; opacity: 0.95;">Dashboard Financeiro</h3>
        <p style="opacity: 0.9; font-size: 1.1rem; line-height: 1.8;">
            📊 Versão 6.0 | 🗓️ Período: Janeiro a Abril 2026 | 📈 Status: LUCRO<br/>
            Desenvolvido com Streamlit + Plotly + ReportLab | Design Premium
        </p>
        <div style="
            margin-top: 30px;
            padding: 15px 30px;
            background: rgba(255,255,255,0.1);
            border-radius: 50px;
            display: inline-block;
            backdrop-filter: blur(10px);
        ">
            <span style="font-size: 0.95rem;">✨ Maldivas Holding ✨</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# 🚀 EXECUÇÃO DA APLICAÇÃO
# =============================================================================

if __name__ == "__main__":
    main()
