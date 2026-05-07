# =============================================================================
# 🚀 ASSERTIF CORRETORA - DASHBOARD FINANCEIRO PREMIUM
# =============================================================================
# Dashboard interativo com rankings, filtros e visualizações profissionais
# Versão: 2.1 PREMIUM CORRIGIDO - STREAMLIT + REPORTLAB
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
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.linecharts import HorizontalLineChart
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

PALETA_SEQUENCIAL = px.colors.sequential.Viridis
PALETA_QUALITATIVA = px.colors.qualitative.Set2
PALETA_DIVERGENTE = px.colors.diverging.RdYlGn

# =============================================================================
# 📊 FUNÇÕES AUXILIARES PREMIUM
# =============================================================================

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
# 📄 CLASSE PARA GERAÇÃO DE PDF COM REPORTLAB - VERSÃO CORRIGIDA
# =============================================================================

class PDFDashboardGenerator:
    """Classe para gerar PDF profissional do dashboard - VERSÃO CORRIGIDA"""
    
    def __init__(self, filename="Assertif_Dashboard_Premium.pdf"):
        self.filename = filename
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configura estilos customizados para o PDF"""
        
        # Estilo do título principal
        self.styles.add(ParagraphStyle(
            name='MainTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            textColor=colors.white,
            alignment=TA_CENTER,
            spaceAfter=12,
            fontName='Helvetica-Bold',
            leading=34
        ))
        
        # Estilo do subtítulo
        self.styles.add(ParagraphStyle(
            name='SubTitle',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.white,
            alignment=TA_CENTER,
            spaceAfter=15,
            fontName='Helvetica',
            leading=16
        ))
        
        # Estilo de seção
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=HexColor('#1E3A5F'),
            alignment=TA_LEFT,
            spaceAfter=10,
            spaceBefore=18,
            fontName='Helvetica-Bold'
        ))
        
        # Estilo de texto normal
        self.styles.add(ParagraphStyle(
            name='NormalText',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=HexColor('#1E3A5F'),
            alignment=TA_LEFT,
            spaceAfter=5,
            fontName='Helvetica'
        ))
        
        # Estilo para KPI
        self.styles.add(ParagraphStyle(
            name='KPIStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.white,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=14
        ))
    
    def _create_header_table(self):
        """Cria o cabeçalho do dashboard com visual premium"""
        # Criar conteúdo do header com formatação correta
        header_content = [
            [Paragraph("<font size='24'><b>ASSERTIF CORRETORA</b></font>", 
                      ParagraphStyle(name='H1', fontSize=24, textColor=colors.white, 
                                    alignment=TA_CENTER, fontName='Helvetica-Bold'))],
            [Paragraph("<font size='14'>Dashboard Financeiro Premium | YTD 2026</font>", 
                      ParagraphStyle(name='H2', fontSize=14, textColor=colors.white, 
                                    alignment=TA_CENTER, fontName='Helvetica'))],
            [Paragraph(f"<font size='10'>Gerado em: {datetime.now().strftime('%d/%m/%Y as %H:%M')}</font>", 
                      ParagraphStyle(name='H3', fontSize=10, textColor=colors.white, 
                                    alignment=TA_CENTER, fontName='Helvetica'))]
        ]
        
        header_table = Table(header_content, colWidths=[18*cm])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), HexColor('#667eea')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, 0), 30),
            ('BOTTOMPADDING', (0, -1), (-1, -1), 30),
            ('LEFTPADDING', (0, 0), (-1, -1), 20),
            ('RIGHTPADDING', (0, 0), (-1, -1), 20),
            ('ROUNDEDCORNERS', [10, 10, 10, 10]),
        ]))
        
        return header_table
    
    def _create_kpi_cards(self, kpis):
        """Cria cartões de KPI com visual aprimorado - CORRIGIDO"""
        kpi_cells = []
        
        cores_kpi = [
            HexColor('#667eea'),  # Faturamento
            HexColor('#dc3545'),  # Despesas
            HexColor('#17a2b8'),  # Margem
            HexColor('#764ba2'),  # EBITDA
        ]
        
        for i, kpi in enumerate(kpis):
            cor = cores_kpi[i] if i < len(cores_kpi) else HexColor('#667eea')
            
            # Criar célula de KPI com formatação adequada
            kpi_content = f"""<para align="center" spaceBefore="5" spaceAfter="5">
                <font size="20">{kpi.get('icone', '')}</font><br/><br/>
                <font size="8" color="white"><b>{kpi['titulo']}</b></font><br/>
                <font size="16" color="white"><b>{kpi['valor']}</b></font><br/>
                <font size="7" color="white">{kpi.get('subtitulo', '')}</font>
            </para>"""
            
            kpi_cells.append(Paragraph(kpi_content, self.styles['Normal']))
        
        # Criar tabela de KPIs
        kpi_table = Table([kpi_cells], colWidths=[4.5*cm] * len(kpis))
        
        style_commands = [
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]
        
        # Aplicar cores de fundo para cada KPI
        for i, cor in enumerate(cores_kpi[:len(kpis)]):
            style_commands.append(('BACKGROUND', (i, 0), (i, 0), cor))
        
        kpi_table.setStyle(TableStyle(style_commands))
        
        return kpi_table
    
    def _create_section_header(self, titulo, cor=None):
        """Cria cabeçalho de seção com visual premium"""
        if cor is None:
            cor = HexColor('#667eea')
        
        section_content = [[Paragraph(f"<font color='white' size='12'><b>{titulo}</b></font>", 
                                      self.styles['Normal'])]]
        
        section_table = Table(section_content, colWidths=[18*cm])
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
    
    def _create_data_table(self, headers, data, col_widths=None):
        """Cria tabela de dados formatada - CORRIGIDO"""
        # Converter headers para Paragraphs
        header_row = [Paragraph(f"<font color='white' size='9'><b>{h}</b></font>", 
                               self.styles['Normal']) for h in headers]
        
        # Converter dados para Paragraphs
        data_rows = []
        for row in data:
            data_row = [Paragraph(f"<font size='9'>{str(cell)}</font>", 
                                 self.styles['Normal']) for cell in row]
            data_rows.append(data_row)
        
        table_data = [header_row] + data_rows
        
        if col_widths is None:
            col_widths = [18*cm / len(headers)] * len(headers)
        
        table = Table(table_data, colWidths=col_widths)
        
        style_commands = [
            # Cabeçalho
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            # Corpo
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#e8e8e8')),
            ('BOX', (0, 0), (-1, -1), 1, HexColor('#667eea')),
        ]
        
        # Alternar cores das linhas
        for i in range(1, len(table_data)):
            if i % 2 == 0:
                style_commands.append(('BACKGROUND', (0, i), (-1, i), HexColor('#f8f9fa')))
            else:
                style_commands.append(('BACKGROUND', (0, i), (-1, i), colors.white))
        
        table.setStyle(TableStyle(style_commands))
        
        return table
    
    def _create_ranking_card(self, posicao, nome, valor, detalhes=""):
        """Cria card de ranking com visual premium - CORRIGIDO"""
        medalhas = ['1o', '2o', '3o']
        cores_medalha = [HexColor('#FFD700'), HexColor('#C0C0C0'), HexColor('#CD7F32')]
        
        medalha = medalhas[posicao - 1] if posicao <= 3 else f"#{posicao}"
        cor = cores_medalha[posicao - 1] if posicao <= 3 else HexColor('#6c757d')
        
        # Criar conteúdo do card
        medalha_content = Paragraph(f"<font size='18' color='#{cor.hexval()[2:]}'><b>{medalha}</b></font>", 
                                   self.styles['Normal'])
        
        info_content = Paragraph(
            f"""<font size='11' color='#1E3A5F'><b>{nome}</b></font><br/>
            <font size='14' color='#28a745'><b>{valor}</b></font><br/>
            <font size='8' color='#6c757d'>{detalhes}</font>""",
            self.styles['Normal']
        )
        
        card_data = [[medalha_content, info_content]]
        
        card_table = Table(card_data, colWidths=[2*cm, 16*cm])
        card_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('BOX', (0, 0), (-1, -1), 2, cor),
        ]))
        
        return card_table
    
    def _create_resumo_executivo_table(self):
        """Cria tabela do resumo executivo - CORRIGIDO E LIMPO"""
        
        # Dados do resumo executivo
        data = [
            ['INDICADOR', 'VALOR'],
            ['RECEITA BRUTA TOTAL (P. MAAS + DIRETO)', 'R$ 178.072,00'],
            ['', ''],
            ['PRODUCAO DIRETA', ''],
            ['    Receita Bruta', 'R$ 177.797,00'],
            ['    Impostos Diretos', '(R$ 30.990,00)'],
            ['    Custo Operacional (D.A)', '(R$ 14.820,00)'],
            ['    Co-Corretagem', 'R$ 803,00'],
            ['    Rebate AAI', '(R$ 50.646,00)'],
            ['(=) Margem de Contribuicao', 'R$ 82.144,00'],
            ['    Despesas', '(R$ 29.104,00)'],
            ['    Folha + Terceiros', '(R$ 16.946,00)'],
            ['EBITDA Societario', 'R$ 36.094,00'],
            ['', ''],
            ['PORTAL MAAS', ''],
            ['    Receita Bruta', 'R$ 275,00'],
            ['    Impostos Diretos', '(R$ 54,00)'],
            ['    Custo Operacional (D.A)', '(R$ 22,00)'],
            ['(=) Margem de Contribuicao', 'R$ 199,00'],
            ['EBITDA Societario', 'R$ 199,00'],
            ['', ''],
            ['RESULTADO OPERACIONAL TOTAL', 'R$ 29.490,00'],
            ['', ''],
            ['DISTRIBUICAO DO RESULTADO', ''],
            ['    Resultado Operacional - Distribuicao', 'R$ 26.949,00'],
            ['    Socio Partner (65%)', 'R$ 19.169,00'],
            ['    Socio Maldivas (35%)', 'R$ 7.780,00'],
        ]
        
        # Converter para Paragraphs
        table_data = []
        for i, row in enumerate(data):
            if i == 0:  # Header
                table_data.append([
                    Paragraph(f"<font color='white' size='10'><b>{row[0]}</b></font>", self.styles['Normal']),
                    Paragraph(f"<font color='white' size='10'><b>{row[1]}</b></font>", self.styles['Normal'])
                ])
            else:
                # Determinar cor do valor
                valor = row[1]
                if valor.startswith('('):
                    cor_valor = '#dc3545'  # Vermelho para negativos
                elif valor.startswith('R$'):
                    cor_valor = '#28a745'  # Verde para positivos
                else:
                    cor_valor = '#1E3A5F'
                
                table_data.append([
                    Paragraph(f"<font size='9' color='#1E3A5F'>{row[0]}</font>", self.styles['Normal']),
                    Paragraph(f"<font size='9' color='{cor_valor}'><b>{valor}</b></font>", self.styles['Normal'])
                ])
        
        table = Table(table_data, colWidths=[12*cm, 6*cm])
        
        style_commands = [
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#e8e8e8')),
            ('BOX', (0, 0), (-1, -1), 1.5, HexColor('#667eea')),
        ]
        
        # Linhas de destaque
        linhas_destaque = {
            1: HexColor('#e8f5e9'),   # Receita bruta total
            9: HexColor('#c8e6c9'),   # Margem de contribuição
            12: HexColor('#bbdefb'),  # EBITDA
            18: HexColor('#c8e6c9'),  # Margem contribuição Portal
            19: HexColor('#bbdefb'),  # EBITDA Portal
            21: HexColor('#a5d6a7'),  # Resultado operacional total
            24: HexColor('#e3f2fd'),  # Resultado distribuição
            25: HexColor('#e8f5e9'),  # Partner
            26: HexColor('#e8f5e9'),  # Maldivas
        }
        
        for linha, cor in linhas_destaque.items():
            if linha < len(data):
                style_commands.append(('BACKGROUND', (0, linha), (-1, linha), cor))
        
        table.setStyle(TableStyle(style_commands))
        
        return table
    
    def _create_footer(self):
        """Cria rodapé do documento com visual premium"""
        footer_content = Paragraph(
            f"""<para align="center">
            <font color='white' size='10'><b>ASSERTIF CORRETORA - Dashboard Financeiro Premium</b></font><br/>
            <font color='white' size='9'>Versao 2.1 | Periodo: Janeiro a Abril 2026 | Status: LUCRO</font><br/>
            <font color='white' size='8'>Documento gerado automaticamente em {datetime.now().strftime('%d/%m/%Y as %H:%M')}</font>
            </para>""",
            self.styles['Normal']
        )
        
        footer_table = Table([[footer_content]], colWidths=[18*cm])
        footer_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), HexColor('#1E3A5F')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 25),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 25),
            ('LEFTPADDING', (0, 0), (-1, -1), 20),
            ('RIGHTPADDING', (0, 0), (-1, -1), 20),
        ]))
        
        return footer_table
    
    def generate_pdf(self, df_receitas_clean=None, df_despesas_clean=None, 
                     df_seg=None, df_prod=None, df_orig=None, df_cli=None, df_cat=None):
        """Gera o PDF completo do dashboard - VERSAO CORRIGIDA"""
        
        buffer = io.BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1*cm,
            leftMargin=1*cm,
            topMargin=1*cm,
            bottomMargin=1*cm
        )
        
        elements = []
        
        # =====================================================================
        # PAGINA 1: HEADER + KPIs + EVOLUCAO MENSAL
        # =====================================================================
        
        # HEADER
        elements.append(self._create_header_table())
        elements.append(Spacer(1, 20))
        
        # KPIs PRINCIPAIS
        elements.append(self._create_section_header("INDICADORES PRINCIPAIS (KPIs) YTD"))
        elements.append(Spacer(1, 10))
        
        kpis = [
            {'titulo': 'FATURAMENTO YTD', 'valor': 'R$ 178.072', 'subtitulo': 'Jan - Abr 2026', 'icone': ''},
            {'titulo': 'DESPESAS', 'valor': 'R$ 29.104', 'subtitulo': 'Total de Despesas', 'icone': ''},
            {'titulo': 'MARGEM DE LUCRO', 'valor': '17%', 'subtitulo': 'Status: LUCRO', 'icone': ''},
            {'titulo': 'LUCRO LIQUIDO', 'valor': 'R$ 29.490', 'subtitulo': 'Resultado Operacional', 'icone': ''},
        ]
        elements.append(self._create_kpi_cards(kpis))
        elements.append(Spacer(1, 20))
        
        # EVOLUCAO MENSAL
        elements.append(self._create_section_header("EVOLUCAO MENSAL - RECEITA vs RESULTADO", HexColor('#28a745')))
        elements.append(Spacer(1, 10))
        
        evolucao_headers = ['Mes', 'Receita Bruta', 'Crescimento', 'Resultado Operacional']
        evolucao_data = [
            ['Janeiro', 'R$ 42.263,00', '-', 'R$ 5.133,00'],
            ['Fevereiro', 'R$ 49.513,00', '+17,2%', 'R$ 7.667,00'],
            ['Marco', 'R$ 71.946,00', '+45,3%', 'R$ 16.690,00'],
            ['Abril', 'R$ 14.350,00', '-80,1%', '-'],
            ['TOTAL YTD', 'R$ 178.072,00', '-', 'R$ 29.490,00'],
        ]
        elements.append(self._create_data_table(evolucao_headers, evolucao_data, [4.5*cm, 4.5*cm, 4.5*cm, 4.5*cm]))
        elements.append(Spacer(1, 20))
        
        # DISTRIBUICAO ENTRE SOCIOS
        elements.append(self._create_section_header("DISTRIBUICAO DE RESULTADOS - SOCIOS", HexColor('#6f42c1')))
        elements.append(Spacer(1, 10))
        
        dist_headers = ['Mes', 'Partner (65%)', 'Maldivas (35%)', 'Total']
        dist_data = [
            ['Janeiro', 'R$ 3.336,00', 'R$ 986,00', 'R$ 4.322,00'],
            ['Fevereiro', 'R$ 4.984,00', 'R$ 1.818,00', 'R$ 6.802,00'],
            ['Marco', 'R$ 10.849,00', 'R$ 4.976,00', 'R$ 15.825,00'],
            ['Abril', '-', '-', '-'],
            ['TOTAL YTD', 'R$ 19.169,00', 'R$ 7.780,00', 'R$ 26.949,00'],
        ]
        elements.append(self._create_data_table(dist_headers, dist_data, [4.5*cm, 4.5*cm, 4.5*cm, 4.5*cm]))
        elements.append(Spacer(1, 20))
        
        # VALOR A RECEBER - MALDIVAS (TRIMESTRAL)
        elements.append(self._create_section_header("RESULTADO TRIMESTRAL - VALOR A RECEBER (MALDIVAS)", HexColor('#17a2b8')))
        elements.append(Spacer(1, 10))
        
        trim_headers = ['1o Trimestre', '2o Trimestre', '3o Trimestre', '4o Trimestre']
        trim_data = [
            ['R$ 20.439,00', 'R$ 1.159,00', 'R$ 0,00', 'R$ 0,00'],
        ]
        elements.append(self._create_data_table(trim_headers, trim_data, [4.5*cm, 4.5*cm, 4.5*cm, 4.5*cm]))
        
        elements.append(PageBreak())
        
        # =====================================================================
        # PAGINA 2: RANKINGS
        # =====================================================================
        
        # TOP ORIGINADORES
        elements.append(self._create_section_header("RANKING - TOP ORIGINADORES", HexColor('#17a2b8')))
        elements.append(Spacer(1, 10))
        
        if df_orig is not None and len(df_orig) > 0:
            for i, (_, row) in enumerate(df_orig.head(3).iterrows()):
                elements.append(self._create_ranking_card(
                    i + 1,
                    str(row['Originador']),
                    formatar_moeda(row['Total']),
                    f"{int(row['Operacoes'])} operacoes | Ticket medio: {formatar_moeda(row['Ticket Medio'])}"
                ))
                elements.append(Spacer(1, 8))
        else:
            originadores_default = [
                ('JOSE GUILHERME SABINO', 'R$ 107.842,67', '58 operacoes | Ticket medio: R$ 1.859,70'),
                ('JOAO GABRIEL RIBEIRO', 'R$ 29.119,17', 'Segundo maior volume'),
                ('FLAVIO ZANINI', 'R$ 24.756,96', 'Terceiro maior volume'),
            ]
            for i, (nome, valor, detalhe) in enumerate(originadores_default):
                elements.append(self._create_ranking_card(i + 1, nome, valor, detalhe))
                elements.append(Spacer(1, 8))
        
        elements.append(Spacer(1, 15))
        
        # TOP SEGURADORAS
        elements.append(self._create_section_header("RANKING - MAIORES COMISSOES POR SEGURADORA", HexColor('#764ba2')))
        elements.append(Spacer(1, 10))
        
        if df_seg is not None and len(df_seg) > 0:
            seg_headers = ['#', 'Seguradora', 'Comissao Total', '% do Total']
            seg_data = []
            for i, (_, row) in enumerate(df_seg.head(10).iterrows()):
                seg_data.append([
                    f"{i+1}",
                    str(row['Seguradora'])[:30],
                    formatar_moeda(row['Total']),
                    f"{row['% do Total']:.1f}%"
                ])
            elements.append(self._create_data_table(seg_headers, seg_data, [1.5*cm, 8.5*cm, 5*cm, 3*cm]))
        else:
            seg_headers = ['#', 'Seguradora', 'Comissao Total', '% do Total']
            seg_data = [
                ['1', 'SULAMERICA', 'R$ 45.230,00', '25,4%'],
                ['2', 'BRADESCO', 'R$ 38.450,00', '21,6%'],
                ['3', 'AXA', 'R$ 28.750,00', '16,2%'],
                ['4', 'CHUBB', 'R$ 22.180,00', '12,5%'],
                ['5', 'TOKIO', 'R$ 18.920,00', '10,6%'],
            ]
            elements.append(self._create_data_table(seg_headers, seg_data, [1.5*cm, 8.5*cm, 5*cm, 3*cm]))
        
        elements.append(PageBreak())
        
        # =====================================================================
        # PAGINA 3: CLIENTES E PRODUTOS
        # =====================================================================
        
        # TOP CLIENTES
        elements.append(self._create_section_header("RANKING - MAIORES CLIENTES POR RECEITA", HexColor('#20c997')))
        elements.append(Spacer(1, 10))
        
        if df_cli is not None and len(df_cli) > 0:
            cli_headers = ['#', 'Cliente', 'Receita Total', '% do Total']
            cli_data = []
            for i, (_, row) in enumerate(df_cli.head(10).iterrows()):
                nome_cliente = str(row['Cliente'])[:35] + ('...' if len(str(row['Cliente'])) > 35 else '')
                cli_data.append([
                    f"{i+1}",
                    nome_cliente,
                    formatar_moeda(row['Total']),
                    f"{row['% do Total']:.1f}%"
                ])
            elements.append(self._create_data_table(cli_headers, cli_data, [1.5*cm, 8.5*cm, 5*cm, 3*cm]))
        else:
            cli_headers = ['#', 'Cliente', 'Receita Total', '% do Total']
            cli_data = [
                ['1', 'VALE COMPANY COMERCIO E SERVICOS', 'R$ 25.008,96', '14,1%'],
                ['2', 'RESOLV VIGILANCIA LTDA', 'R$ 18.450,00', '10,4%'],
                ['3', 'CFJ PARTICIPACOES S.A.', 'R$ 12.320,00', '6,9%'],
            ]
            elements.append(self._create_data_table(cli_headers, cli_data, [1.5*cm, 8.5*cm, 5*cm, 3*cm]))
        
        elements.append(Spacer(1, 20))
        
        # ANALISE POR PRODUTO
        elements.append(self._create_section_header("ANALISE POR TIPO DE PRODUTO", HexColor('#fd7e14')))
        elements.append(Spacer(1, 10))
        
        if df_prod is not None and len(df_prod) > 0:
            prod_headers = ['Produto', 'Comissao Total', '% do Total', 'Qtd Operacoes']
            prod_data = []
            for _, row in df_prod.head(10).iterrows():
                prod_data.append([
                    str(row['Produto'])[:25],
                    formatar_moeda(row['Total']),
                    f"{row['% do Total']:.1f}%",
                    str(int(row['Qtd']))
                ])
            elements.append(self._create_data_table(prod_headers, prod_data, [6*cm, 5*cm, 4*cm, 3*cm]))
        else:
            prod_headers = ['Produto', 'Comissao Total', '% do Total', 'Qtd Operacoes']
            prod_data = [
                ['SAUDE', 'R$ 85.420,00', '48,0%', '45'],
                ['EMPRESARIAL', 'R$ 42.350,00', '23,8%', '22'],
                ['D&O', 'R$ 18.920,00', '10,6%', '8'],
                ['AUTOMOVEL', 'R$ 15.230,00', '8,6%', '12'],
                ['RC', 'R$ 10.152,00', '5,7%', '5'],
            ]
            elements.append(self._create_data_table(prod_headers, prod_data, [6*cm, 5*cm, 4*cm, 3*cm]))
        
        elements.append(Spacer(1, 20))
        
        # DESPESAS
        elements.append(self._create_section_header("RANKING - MAIORES DESPESAS", HexColor('#dc3545')))
        elements.append(Spacer(1, 10))
        
        if df_cat is not None and len(df_cat) > 0:
            desp_headers = ['Categoria', 'Valor Total', '% do Total']
            desp_data = []
            for _, row in df_cat.head(10).iterrows():
                desp_data.append([
                    str(row['Categoria'])[:40],
                    formatar_moeda(row['Total']),
                    f"{row['% do Total']:.1f}%"
                ])
            elements.append(self._create_data_table(desp_headers, desp_data, [10*cm, 5*cm, 3*cm]))
        else:
            desp_headers = ['Categoria', 'Valor Total', '% do Total']
            desp_data = [
                ['Despesas Gerais - Servicos Prestados por PJ', 'R$ 12.580,27', '43,2%'],
                ['Diretoria / Pro-Labore', 'R$ 10.818,21', '37,2%'],
                ['Darf Previdenciaria', 'R$ 4.252,52', '14,6%'],
                ['Despesas Financeiras / Despesas Bancarias', 'R$ 477,00', '1,6%'],
                ['Despesas de Viagens / Locmocao', 'R$ 333,87', '1,1%'],
            ]
            elements.append(self._create_data_table(desp_headers, desp_data, [10*cm, 5*cm, 3*cm]))
        
        elements.append(PageBreak())
        
        # =====================================================================
        # PAGINA 4: RESUMO EXECUTIVO + FOOTER
        # =====================================================================
        
        # RESUMO EXECUTIVO
        elements.append(self._create_section_header("RESUMO EXECUTIVO - DRE YTD 2026", HexColor('#1E3A5F')))
        elements.append(Spacer(1, 10))
        elements.append(self._create_resumo_executivo_table())
        elements.append(Spacer(1, 30))
        
        # FOOTER
        elements.append(self._create_footer())
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        
        return buffer.getvalue()


# =============================================================================
# 🎯 APLICAÇÃO STREAMLIT PRINCIPAL
# =============================================================================

def main():
    # Configuração da página
    st.set_page_config(
        page_title="Assertif Corretora - Dashboard Premium",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS customizado
    st.markdown("""
    <style>
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            padding: 40px 30px;
            border-radius: 25px;
            text-align: center;
            margin-bottom: 35px;
            box-shadow: 0 20px 50px rgba(102, 126, 234, 0.4);
        }
        .main-header h1 {
            color: white;
            font-size: 3rem;
            font-weight: 800;
            text-shadow: 3px 3px 6px rgba(0,0,0,0.3);
        }
        .main-header h2 {
            color: white;
            font-size: 1.4rem;
            font-weight: 500;
        }
        .section-header {
            padding: 20px 30px;
            border-radius: 15px;
            margin: 25px 0;
        }
        .section-header h2 {
            color: white;
            font-size: 1.6rem;
            font-weight: 700;
        }
        .stMetric {
            background: linear-gradient(135deg, #667eea 0%, #667eeacc 100%);
            padding: 20px;
            border-radius: 15px;
            color: white;
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
    
    # Sidebar para upload
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
    
    # Variáveis para armazenar dados processados
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
        df_inputs = dados.get('INPUTS', pd.DataFrame())
        df_resumo = dados.get('RESUMO DRE', pd.DataFrame())
        df_portal = dados.get('EXTRATO PORTAL MAAS', pd.DataFrame())
        
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
            df_seg.columns = ['Seguradora', 'Total', 'Qtd', 'Media']
            df_seg = df_seg[df_seg['Total'] > 0].sort_values('Total', ascending=False)
            df_seg['% do Total'] = (df_seg['Total'] / df_seg['Total'].sum() * 100).round(1)
            
            # Agrupar por produto
            df_prod = df_receitas_clean.groupby(col_produto)[col_comissao].agg(['sum', 'count', 'mean']).reset_index()
            df_prod.columns = ['Produto', 'Total', 'Qtd', 'Media']
            df_prod = df_prod[df_prod['Total'] > 0].sort_values('Total', ascending=False)
            df_prod['% do Total'] = (df_prod['Total'] / df_prod['Total'].sum() * 100).round(1)
            
            # Agrupar por originador
            df_orig = df_receitas_clean.groupby(col_originador)[col_comissao].agg(['sum', 'count', 'mean']).reset_index()
            df_orig.columns = ['Originador', 'Total', 'Operacoes', 'Ticket Medio']
            df_orig = df_orig[df_orig['Total'] > 0].sort_values('Total', ascending=False)
            df_orig['% do Total'] = (df_orig['Total'] / df_orig['Total'].sum() * 100).round(1)
            
            # Agrupar por cliente
            df_cli = df_receitas_clean.groupby(col_cliente)[col_comissao].agg(['sum', 'count', 'mean']).reset_index()
            df_cli.columns = ['Cliente', 'Total', 'Qtd', 'Media']
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
    
    # KPIs PRINCIPAIS
    st.markdown("""
    <div class="section-header" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
        <h2>💰 INDICADORES PRINCIPAIS (KPIs) YTD</h2>
    </div>
    """, unsafe_allow_html=True)
    
    faturamento_ytd = 178072
    despesas_total = 29104
    margem = 17
    lucro = 29490
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(criar_cartao_kpi_html("FATURAMENTO YTD", formatar_moeda(faturamento_ytd), "Jan - Abr 2026", "#667eea", "💰"), unsafe_allow_html=True)
    
    with col2:
        st.markdown(criar_cartao_kpi_html("DESPESAS", formatar_moeda(despesas_total), "Total de Despesas", "#dc3545", "💸"), unsafe_allow_html=True)
    
    with col3:
        st.markdown(criar_cartao_kpi_html("MARGEM DE LUCRO", "17%", "Status: LUCRO", "#17a2b8", "📊"), unsafe_allow_html=True)
    
    with col4:
        st.markdown(criar_cartao_kpi_html("LUCRO LÍQUIDO", formatar_moeda(lucro), "Resultado Operacional", "#764ba2", "🎯"), unsafe_allow_html=True)
    
    # BOTÃO DE EXPORTAR PDF
    st.markdown("---")
    st.markdown("""
    <div class="section-header" style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%);">
        <h2>📥 EXPORTAR DASHBOARD PARA PDF</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📄 GERAR PDF PROFISSIONAL", type="primary", use_container_width=True):
            with st.spinner("Gerando PDF profissional..."):
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
                        label="⬇️ BAIXAR PDF PROFISSIONAL",
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
            📊 Versão 2.1 | 🗓️ Período: Janeiro a Abril 2026 | 📈 Status: LUCRO<br>
            Desenvolvido com Streamlit + Plotly + ReportLab
        </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
