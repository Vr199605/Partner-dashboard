# =============================================================================
# 🚀 ASSERTIF CORRETORA - DASHBOARD FINANCEIRO PREMIUM
# =============================================================================
# Dashboard interativo com rankings, filtros e visualizações profissionais
# Versão: 3.0 PREMIUM ULTIMATE - STREAMLIT + REPORTLAB + GRÁFICOS PDF
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
# 🎨 CONFIGURAÇÕES DE ESTILO PREMIUM
# =============================================================================

# Paleta de cores profissional
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

# Paletas para gráficos
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
# 📄 CLASSE PARA GERAÇÃO DE PDF COM REPORTLAB - VERSÃO PREMIUM ULTIMATE
# =============================================================================

class PDFDashboardGenerator:
    """Classe para gerar PDF profissional do dashboard - Versão Premium Ultimate"""
    
    def __init__(self, filename="Assertif_Dashboard_Premium.pdf"):
        self.filename = filename
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        self.page_number = 0
        self.total_pages = 0
        
    def _setup_custom_styles(self):
        """Configura estilos customizados para o PDF"""
        # Estilo do título principal (Capa)
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
        
        # Estilo do subtítulo da capa
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
        
        # Estilo do título principal
        self.styles.add(ParagraphStyle(
            name='MainTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            textColor=colors.white,
            alignment=TA_CENTER,
            spaceAfter=10,
            fontName='Helvetica-Bold'
        ))
        
        # Estilo do subtítulo
        self.styles.add(ParagraphStyle(
            name='SubTitle',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.white,
            alignment=TA_CENTER,
            spaceAfter=20,
            fontName='Helvetica'
        ))
        
        # Estilo de seção
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
        
        # Estilo de texto normal
        self.styles.add(ParagraphStyle(
            name='NormalText',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=HexColor('#1E3A5F'),
            alignment=TA_LEFT,
            spaceAfter=6,
            fontName='Helvetica'
        ))
        
        # Estilo para sumário
        self.styles.add(ParagraphStyle(
            name='TOCEntry',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=HexColor('#1E3A5F'),
            alignment=TA_LEFT,
            spaceAfter=8,
            fontName='Helvetica',
            leftIndent=20
        ))
        
        # Estilo para notas explicativas
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
        
        # Estilo de valor positivo
        self.styles.add(ParagraphStyle(
            name='PositiveValue',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=HexColor('#28a745'),
            alignment=TA_RIGHT,
            fontName='Helvetica-Bold'
        ))
        
        # Estilo de valor negativo
        self.styles.add(ParagraphStyle(
            name='NegativeValue',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=HexColor('#dc3545'),
            alignment=TA_RIGHT,
            fontName='Helvetica-Bold'
        ))
    
    def _create_cover_page(self):
        """Cria página de capa profissional"""
        elements = []
        
        # Espaçador superior
        elements.append(Spacer(1, 2*cm))
        
        # Logo/Ícone grande centralizado
        logo_data = [[Paragraph(
            "<font size='80'>📊</font>",
            ParagraphStyle(name='LogoStyle', alignment=TA_CENTER, fontSize=80)
        )]]
        logo_table = Table(logo_data, colWidths=[18*cm])
        logo_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        # Container principal da capa com gradiente simulado
        cover_content = [
            [logo_table],
            [Spacer(1, 1*cm)],
            [Paragraph("ASSERTIF CORRETORA", self.styles['CoverTitle'])],
            [Paragraph("DE SEGUROS", self.styles['CoverTitle'])],
            [Spacer(1, 0.5*cm)],
            [Paragraph("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", 
                      ParagraphStyle(name='LineCover', alignment=TA_CENTER, textColor=colors.white, fontSize=14))],
            [Spacer(1, 0.5*cm)],
            [Paragraph("Dashboard Financeiro Premium", self.styles['CoverSubtitle'])],
            [Paragraph("Relatório Executivo | YTD 2026", self.styles['CoverSubtitle'])],
            [Spacer(1, 2*cm)],
            [Paragraph(f"📅 Período: Janeiro a Abril de 2026", 
                      ParagraphStyle(name='CoverInfo', alignment=TA_CENTER, textColor=colors.white, fontSize=14, fontName='Helvetica'))],
            [Paragraph(f"📈 Status: LUCRO | Margem: 17%", 
                      ParagraphStyle(name='CoverInfo2', alignment=TA_CENTER, textColor=HexColor('#28a745'), fontSize=14, fontName='Helvetica-Bold'))],
            [Spacer(1, 2*cm)],
            [Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}", 
                      ParagraphStyle(name='CoverDate', alignment=TA_CENTER, textColor=colors.white, fontSize=11, fontName='Helvetica'))],
        ]
        
        cover_table = Table([[item[0]] for item in cover_content], colWidths=[18*cm])
        cover_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), HexColor('#667eea')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 30),
            ('RIGHTPADDING', (0, 0), (-1, -1), 30),
        ]))
        
        elements.append(cover_table)
        
        # Box de informações adicionais
        elements.append(Spacer(1, 1*cm))
        
        info_data = [
            ['💰 Faturamento YTD', 'R$ 178.072,00', '📊 Margem Contribuição', 'R$ 82.144,00'],
            ['📈 Resultado Operacional', 'R$ 29.490,00', '🎯 EBITDA', 'R$ 36.094,00'],
        ]
        
        info_table = Table(info_data, colWidths=[5*cm, 4*cm, 5*cm, 4*cm])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), HexColor('#f8f9fa')),
            ('TEXTCOLOR', (0, 0), (0, -1), HexColor('#1E3A5F')),
            ('TEXTCOLOR', (2, 0), (2, -1), HexColor('#1E3A5F')),
            ('TEXTCOLOR', (1, 0), (1, -1), HexColor('#28a745')),
            ('TEXTCOLOR', (3, 0), (3, -1), HexColor('#28a745')),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
            ('FONTNAME', (3, 0), (3, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#e8e8e8')),
            ('BOX', (0, 0), (-1, -1), 2, HexColor('#667eea')),
        ]))
        
        elements.append(info_table)
        elements.append(PageBreak())
        
        return elements
    
    def _create_table_of_contents(self):
        """Cria sumário/índice do documento"""
        elements = []
        
        # Título do sumário
        toc_header = [[Paragraph("<font color='white'><b>📑 SUMÁRIO</b></font>", 
                                 ParagraphStyle(name='TOCHeader', alignment=TA_CENTER, fontSize=20, fontName='Helvetica-Bold'))]]
        toc_header_table = Table(toc_header, colWidths=[18*cm])
        toc_header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), HexColor('#1E3A5F')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 20),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
        ]))
        
        elements.append(toc_header_table)
        elements.append(Spacer(1, 1*cm))
        
        # Itens do sumário
        toc_items = [
            ('1.', '💰 Indicadores Principais (KPIs) YTD', '3'),
            ('2.', '📈 Evolução Mensal - Receita vs Resultado', '3'),
            ('3.', '🏆 Ranking - Maiores Comissões por Seguradora', '4'),
            ('4.', '🤝 Distribuição de Resultados - Sócios', '4'),
            ('5.', '👥 Ranking - Top Originadores', '5'),
            ('6.', '🏅 Ranking - Maiores Clientes', '5'),
            ('7.', '📦 Análise por Tipo de Produto', '6'),
            ('8.', '💸 Ranking - Maiores Despesas', '6'),
            ('9.', '📋 Resumo Executivo - DRE Completo', '7'),
            ('10.', '📊 Análise Gráfica Consolidada', '8'),
            ('11.', '📝 Notas e Observações', '9'),
        ]
        
        toc_data = []
        for num, titulo, pagina in toc_items:
            toc_data.append([
                Paragraph(f"<b>{num}</b>", ParagraphStyle(name='TOCNum', fontSize=12, textColor=HexColor('#667eea'), fontName='Helvetica-Bold')),
                Paragraph(titulo, ParagraphStyle(name='TOCTitle', fontSize=12, textColor=HexColor('#1E3A5F'), fontName='Helvetica')),
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
            ('LINEBELOW', (0, -1), (-1, -1), 2, HexColor('#667eea')),
        ]))
        
        elements.append(toc_table)
        elements.append(Spacer(1, 2*cm))
        
        # Box de informações
        info_box = [[Paragraph(
            "<b>ℹ️ Sobre este Relatório</b><br/><br/>"
            "Este dashboard apresenta uma visão consolidada do desempenho financeiro da Assertif Corretora "
            "no período de Janeiro a Abril de 2026. Os dados incluem análise de receitas por seguradora, "
            "produto, originador e cliente, além da distribuição de resultados entre os sócios e "
            "evolução mensal dos principais indicadores.",
            ParagraphStyle(name='InfoBox', fontSize=10, textColor=HexColor('#1E3A5F'), 
                          alignment=TA_JUSTIFY, fontName='Helvetica', leading=14)
        )]]
        
        info_box_table = Table(info_box, colWidths=[17*cm])
        info_box_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), HexColor('#e8f4f8')),
            ('BOX', (0, 0), (-1, -1), 2, HexColor('#17a2b8')),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ]))
        
        elements.append(info_box_table)
        elements.append(PageBreak())
        
        return elements
    
    def _create_header_table(self):
        """Cria o cabeçalho do dashboard"""
        header_data = [
            [Paragraph("📊 ASSERTIF CORRETORA", self.styles['MainTitle'])],
            [Paragraph("Dashboard Financeiro Premium | YTD 2026", self.styles['SubTitle'])],
            [Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}", self.styles['SubTitle'])]
        ]
        
        header_table = Table(header_data, colWidths=[18*cm])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), HexColor('#667eea')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, 0), 30),
            ('BOTTOMPADDING', (0, -1), (-1, -1), 30),
            ('LEFTPADDING', (0, 0), (-1, -1), 20),
            ('RIGHTPADDING', (0, 0), (-1, -1), 20),
        ]))
        
        return header_table
    
    def _create_kpi_cards(self, kpis):
        """Cria cards de KPIs com visual premium"""
        kpi_cells = []
        
        cores_kpi = [
            HexColor('#667eea'),
            HexColor('#dc3545'),
            HexColor('#17a2b8'),
            HexColor('#764ba2'),
        ]
        
        for i, kpi in enumerate(kpis):
            cor = cores_kpi[i % len(cores_kpi)]
            
            # Criar conteúdo do card
            card_content = [
                [Paragraph(f"<font size='28'>{kpi.get('icone', '📊')}</font>", 
                          ParagraphStyle(name=f'KPIIcon{i}', alignment=TA_CENTER))],
                [Paragraph(f"<font size='8' color='white'><b>{kpi['titulo']}</b></font>", 
                          ParagraphStyle(name=f'KPITitle{i}', alignment=TA_CENTER))],
                [Paragraph(f"<font size='16' color='white'><b>{kpi['valor']}</b></font>", 
                          ParagraphStyle(name=f'KPIValue{i}', alignment=TA_CENTER))],
                [Paragraph(f"<font size='7' color='white'>{kpi.get('subtitulo', '')}</font>", 
                          ParagraphStyle(name=f'KPISub{i}', alignment=TA_CENTER))],
            ]
            
            card_table = Table(card_content, colWidths=[4.2*cm])
            card_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), cor),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ]))
            
            kpi_cells.append(card_table)
        
        # Criar tabela com os 4 cards
        kpi_row = Table([kpi_cells], colWidths=[4.5*cm] * 4)
        kpi_row.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        return kpi_row
    
    def _create_section_header(self, titulo, cor=HexColor('#667eea'), icone="📊"):
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
    
    def _create_bar_chart(self, data, labels, title, width=400, height=200, colors_list=None):
        """Cria gráfico de barras verticais"""
        drawing = Drawing(width, height)
        
        # Fundo
        drawing.add(Rect(0, 0, width, height, fillColor=HexColor('#f8f9fa'), strokeColor=None))
        
        bc = VerticalBarChart()
        bc.x = 50
        bc.y = 40
        bc.height = height - 80
        bc.width = width - 100
        bc.data = [data]
        bc.categoryAxis.categoryNames = labels
        bc.categoryAxis.labels.fontName = 'Helvetica'
        bc.categoryAxis.labels.fontSize = 8
        bc.categoryAxis.labels.angle = 45
        bc.categoryAxis.labels.boxAnchor = 'ne'
        bc.valueAxis.valueMin = 0
        bc.valueAxis.valueMax = max(data) * 1.2 if data else 100
        bc.valueAxis.labels.fontName = 'Helvetica'
        bc.valueAxis.labels.fontSize = 8
        bc.bars[0].fillColor = HexColor('#667eea')
        
        if colors_list:
            for i, cor in enumerate(colors_list):
                if i < len(data):
                    bc.bars[0].fillColor = HexColor(cor) if isinstance(cor, str) else cor
        
        drawing.add(bc)
        
        # Título
        drawing.add(String(width/2, height - 15, title, 
                          fontName='Helvetica-Bold', fontSize=10, textAnchor='middle',
                          fillColor=HexColor('#1E3A5F')))
        
        return drawing
    
    def _create_horizontal_bar_chart(self, data, labels, title, width=500, height=250):
        """Cria gráfico de barras horizontais"""
        drawing = Drawing(width, height)
        
        # Fundo
        drawing.add(Rect(0, 0, width, height, fillColor=HexColor('#f8f9fa'), strokeColor=None))
        
        bc = HorizontalBarChart()
        bc.x = 120
        bc.y = 30
        bc.height = height - 60
        bc.width = width - 180
        bc.data = [data]
        bc.categoryAxis.categoryNames = labels
        bc.categoryAxis.labels.fontName = 'Helvetica'
        bc.categoryAxis.labels.fontSize = 8
        bc.valueAxis.valueMin = 0
        bc.valueAxis.valueMax = max(data) * 1.2 if data else 100
        bc.valueAxis.labels.fontName = 'Helvetica'
        bc.valueAxis.labels.fontSize = 8
        bc.bars[0].fillColor = HexColor('#667eea')
        
        # Cores gradientes
        cores = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe', '#28a745', '#ffc107']
        for i in range(len(data)):
            bc.bars[0].fillColor = HexColor(cores[i % len(cores)])
        
        drawing.add(bc)
        
        # Título
        drawing.add(String(width/2, height - 15, title, 
                          fontName='Helvetica-Bold', fontSize=11, textAnchor='middle',
                          fillColor=HexColor('#1E3A5F')))
        
        return drawing
    
    def _create_pie_chart(self, data, labels, title, width=300, height=250):
        """Cria gráfico de pizza/donut"""
        drawing = Drawing(width, height)
        
        # Fundo
        drawing.add(Rect(0, 0, width, height, fillColor=HexColor('#f8f9fa'), strokeColor=None))
        
        pie = Pie()
        pie.x = width/2 - 60
        pie.y = 40
        pie.width = 120
        pie.height = 120
        pie.data = data
        pie.labels = labels
        pie.slices.strokeWidth = 2
        pie.slices.strokeColor = colors.white
        
        # Cores
        cores = [HexColor('#667eea'), HexColor('#f5576c'), HexColor('#28a745'), 
                HexColor('#ffc107'), HexColor('#17a2b8'), HexColor('#764ba2')]
        for i in range(len(data)):
            pie.slices[i].fillColor = cores[i % len(cores)]
        
        pie.slices.fontName = 'Helvetica'
        pie.slices.fontSize = 8
        
        drawing.add(pie)
        
        # Título
        drawing.add(String(width/2, height - 15, title, 
                          fontName='Helvetica-Bold', fontSize=11, textAnchor='middle',
                          fillColor=HexColor('#1E3A5F')))
        
        # Legenda
        legend = Legend()
        legend.x = width - 80
        legend.y = height/2
        legend.dx = 8
        legend.dy = 8
        legend.fontName = 'Helvetica'
        legend.fontSize = 7
        legend.boxAnchor = 'w'
        legend.columnMaximum = 10
        legend.strokeWidth = 0.5
        legend.strokeColor = HexColor('#e8e8e8')
        legend.deltax = 75
        legend.deltay = 10
        legend.autoXPadding = 5
        legend.yGap = 0
        legend.dxTextSpace = 5
        legend.alignment = 'right'
        legend.dividerLines = 1|2|4
        legend.dividerOffsY = 4.5
        legend.subCols.rpad = 30
        
        legend.colorNamePairs = [(cores[i % len(cores)], labels[i][:15]) for i in range(len(data))]
        drawing.add(legend)
        
        return drawing
    
    def _create_line_chart(self, data, labels, title, width=450, height=200):
        """Cria gráfico de linha"""
        drawing = Drawing(width, height)
        
        # Fundo
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
        lc.lines[0].strokeColor = HexColor('#667eea')
        lc.lines[0].strokeWidth = 3
        lc.lines[0].symbol = makeMarker('Circle')
        lc.lines[0].symbol.fillColor = HexColor('#667eea')
        lc.lines[0].symbol.strokeColor = colors.white
        lc.lines[0].symbol.strokeWidth = 2
        lc.lines[0].symbol.size = 8
        
        drawing.add(lc)
        
        # Título
        drawing.add(String(width/2, height - 15, title, 
                          fontName='Helvetica-Bold', fontSize=11, textAnchor='middle',
                          fillColor=HexColor('#1E3A5F')))
        
        return drawing
    
    def _create_data_table(self, headers, data, col_widths=None, highlight_rows=None):
        """Cria tabela de dados formatada premium"""
        # Preparar dados da tabela
        table_data = [headers] + data
        
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
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            # Corpo
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#e8e8e8')),
            ('BOX', (0, 0), (-1, -1), 1.5, HexColor('#667eea')),
        ]
        
        # Alternar cores das linhas (zebra)
        for i in range(1, len(table_data)):
            if i % 2 == 0:
                style_commands.append(('BACKGROUND', (0, i), (-1, i), HexColor('#f8f9fa')))
            else:
                style_commands.append(('BACKGROUND', (0, i), (-1, i), colors.white))
        
        # Destacar linhas específicas
        if highlight_rows:
            for row_idx, cor in highlight_rows.items():
                if row_idx < len(table_data):
                    style_commands.append(('BACKGROUND', (0, row_idx), (-1, row_idx), cor))
                    style_commands.append(('FONTNAME', (0, row_idx), (-1, row_idx), 'Helvetica-Bold'))
        
        table.setStyle(TableStyle(style_commands))
        
        return table
    
    def _create_ranking_card(self, posicao, nome, valor, detalhes=""):
        """Cria card de ranking premium"""
        medalhas = ['🥇', '🥈', '🥉']
        cores_medalha = [HexColor('#FFD700'), HexColor('#C0C0C0'), HexColor('#CD7F32')]
        
        medalha = medalhas[posicao - 1] if posicao <= 3 else f"#{posicao}"
        cor = cores_medalha[posicao - 1] if posicao <= 3 else HexColor('#6c757d')
        
        card_data = [[
            Paragraph(f"<font size='24'>{medalha}</font>", 
                     ParagraphStyle(name=f'Medal{posicao}', alignment=TA_CENTER)),
            Paragraph(f"<b>{nome}</b><br/><font size='16' color='#28a745'><b>{valor}</b></font><br/><font size='8' color='#6c757d'>{detalhes}</font>", 
                     ParagraphStyle(name=f'RankInfo{posicao}', fontSize=10, leading=14))
        ]]
        
        card_table = Table(card_data, colWidths=[2.5*cm, 15.5*cm])
        card_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('BOX', (0, 0), (-1, -1), 3, cor),
            ('BACKGROUND', (0, 0), (0, 0), HexColor('#f8f9fa')),
        ]))
        
        return card_table
    
    def _create_resumo_executivo_table(self):
        """Cria tabela do resumo executivo com dados atualizados - SEM as linhas removidas"""
        data = [
            ['INDICADOR', 'VALOR'],
            ['💰 RECEITA BRUTA TOTAL (P. MAAS + DIRETO)', 'R$ 178.072,00'],
            ['📦 PRODUÇÃO DIRETA', ''],
            ['    Receita Bruta', 'R$ 177.797,00'],
            ['    Impostos Diretos', '(R$ 30.990,00)'],
            ['    Custo Operacional (D.A)', '(R$ 14.820,00)'],
            ['    Co-Corretagem', 'R$ 803,00'],
            ['    Rebate AAI', '(R$ 50.646,00)'],
            ['(=) Margem de Contribuição', 'R$ 82.144,00'],
            ['    Despesas', '(R$ 29.104,00)'],
            ['    Folha + Terceiros', '(R$ 16.946,00)'],
            ['EBITDA Societário', 'R$ 36.094,00'],
            ['🌐 PORTAL MAAS', ''],
            ['    Receita Bruta', 'R$ 275,00'],
            ['    Impostos Diretos', '(R$ 54,00)'],
            ['    Custo Operacional (D.A)', '(R$ 22,00)'],
            ['(=) Margem de Contribuição', 'R$ 199,00'],
            ['EBITDA Societário', 'R$ 199,00'],
            ['🎯 RESULTADO OPERACIONAL TOTAL', 'R$ 29.490,00'],
            ['📊 DISTRIBUIÇÃO DO RESULTADO', ''],
            ['    Resultado Operacional - Distribuição', 'R$ 26.949,00'],
            ['    → Sócio Partner (65%)', 'R$ 19.169,00'],
            ['    → Sócio Maldivas (35%)', 'R$ 7.780,00'],
        ]
        
        table = Table(data, colWidths=[12*cm, 6*cm])
        
        style_commands = [
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#e8e8e8')),
            ('BOX', (0, 0), (-1, -1), 2, HexColor('#667eea')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]
        
        # Destacar linhas específicas
        linhas_destaque = {
            1: HexColor('#e8f5e9'),   # Receita bruta total
            8: HexColor('#c8e6c9'),   # Margem de contribuição
            11: HexColor('#bbdefb'),  # EBITDA
            16: HexColor('#c8e6c9'),  # Margem contribuição Portal
            17: HexColor('#bbdefb'),  # EBITDA Portal
            18: HexColor('#a5d6a7'),  # Resultado operacional total
        }
        
        for linha, cor in linhas_destaque.items():
            style_commands.append(('BACKGROUND', (0, linha), (-1, linha), cor))
            style_commands.append(('FONTNAME', (0, linha), (-1, linha), 'Helvetica-Bold'))
        
        # Colorir valores negativos
        linhas_negativas = [4, 5, 7, 9, 10, 14, 15]
        for linha in linhas_negativas:
            style_commands.append(('TEXTCOLOR', (1, linha), (1, linha), HexColor('#dc3545')))
        
        # Colorir valores positivos
        linhas_positivas = [1, 3, 6, 8, 11, 13, 16, 17, 18, 21, 22]
        for linha in linhas_positivas:
            style_commands.append(('TEXTCOLOR', (1, linha), (1, linha), HexColor('#28a745')))
        
        table.setStyle(TableStyle(style_commands))
        
        return table
    
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
    
    def _create_footer(self):
        """Cria rodapé do documento"""
        footer_data = [[
            Paragraph(
                "<font color='white'><b>✅ ASSERTIF CORRETORA - Dashboard Financeiro Premium</b><br/>"
                f"📊 Versão 3.0 | 🗓️ Período: Janeiro a Abril 2026 | 📈 Status: LUCRO<br/>"
                f"Documento gerado automaticamente em {datetime.now().strftime('%d/%m/%Y às %H:%M')}</font>",
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
            ('BACKGROUND', (0, 0), (-1, -1), HexColor('#1E3A5F')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 20),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
            ('LEFTPADDING', (0, 0), (-1, -1), 20),
            ('RIGHTPADDING', (0, 0), (-1, -1), 20),
        ]))
        
        return footer_table
    
    def _add_page_number(self, canvas, doc):
        """Adiciona número de página e cabeçalho/rodapé em cada página"""
        canvas.saveState()
        
        # Cabeçalho
        canvas.setFillColor(HexColor('#667eea'))
        canvas.rect(1*cm, A4[1] - 1.5*cm, A4[0] - 2*cm, 0.8*cm, fill=True, stroke=False)
        
        canvas.setFillColor(colors.white)
        canvas.setFont('Helvetica-Bold', 9)
        canvas.drawString(1.5*cm, A4[1] - 1.1*cm, "📊 ASSERTIF CORRETORA - Dashboard Financeiro Premium")
        canvas.drawRightString(A4[0] - 1.5*cm, A4[1] - 1.1*cm, f"YTD 2026")
        
        # Rodapé com número de página
        canvas.setFillColor(HexColor('#1E3A5F'))
        canvas.rect(1*cm, 0.5*cm, A4[0] - 2*cm, 0.6*cm, fill=True, stroke=False)
        
        canvas.setFillColor(colors.white)
        canvas.setFont('Helvetica', 8)
        canvas.drawString(1.5*cm, 0.7*cm, f"Gerado em: {datetime.now().strftime('%d/%m/%Y')}")
        canvas.drawCentredString(A4[0]/2, 0.7*cm, "Confidencial - Uso Interno")
        canvas.drawRightString(A4[0] - 1.5*cm, 0.7*cm, f"Página {doc.page}")
        
        canvas.restoreState()
    
    def generate_pdf(self, df_receitas_clean=None, df_despesas_clean=None, df_seg=None, 
                     df_prod=None, df_orig=None, df_cli=None, df_cat=None):
        """Gera o PDF completo do dashboard - Versão Premium Ultimate"""
        
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
        
        # =====================================================================
        # PÁGINA 1: CAPA
        # =====================================================================
        elements.extend(self._create_cover_page())
        
        # =====================================================================
        # PÁGINA 2: SUMÁRIO
        # =====================================================================
        elements.extend(self._create_table_of_contents())
        
        # =====================================================================
        # PÁGINA 3: KPIs E EVOLUÇÃO MENSAL
        # =====================================================================
        elements.append(self._create_section_header("💰 INDICADORES PRINCIPAIS (KPIs) YTD", HexColor('#667eea')))
        elements.append(Spacer(1, 15))
        
        # KPIs ALTERADOS: Lucro Líquido -> Despesas
        kpis = [
            {'titulo': 'FATURAMENTO YTD', 'valor': 'R$ 178.072', 'subtitulo': 'Jan - Abr 2026', 'icone': '💰'},
            {'titulo': 'DESPESAS', 'valor': 'R$ 46.050', 'subtitulo': 'Desp + Folha', 'icone': '💸'},
            {'titulo': 'MARGEM DE LUCRO', 'valor': '17%', 'subtitulo': 'Status: LUCRO', 'icone': '📊'},
            {'titulo': 'EBITDA', 'valor': 'R$ 36.094', 'subtitulo': 'Resultado Operacional', 'icone': '🎯'},
        ]
        elements.append(self._create_kpi_cards(kpis))
        elements.append(Spacer(1, 20))
        
        # Nota explicativa dos KPIs
        elements.append(self._create_note_box(
            "📌 Nota sobre os KPIs",
            "Os indicadores acima representam o acumulado do ano (YTD - Year To Date) de Janeiro a Abril de 2026. "
            "O Faturamento inclui receitas da Produção Direta e Portal MAAS. As Despesas incluem Despesas Operacionais "
            "(R$ 29.104) e Folha + Terceiros (R$ 16.946). A Margem de Lucro de 17% indica resultado positivo."
        ))
        elements.append(Spacer(1, 20))
        
        # Evolução Mensal
        elements.append(self._create_section_header("📈 EVOLUÇÃO MENSAL - RECEITA vs RESULTADO", HexColor('#28a745')))
        elements.append(Spacer(1, 15))
        
        # Gráfico de linha - Evolução da Receita
        meses = ['Jan', 'Fev', 'Mar', 'Abr']
        receita_bruta = [42263, 49513, 71946, 14350]
        resultado_op = [5133, 7667, 16690, 0]
        
        elements.append(self._create_line_chart(receita_bruta, meses, '📈 Evolução da Receita Bruta Mensal (R$)', width=500, height=180))
        elements.append(Spacer(1, 15))
        
        # Tabela de evolução
        evolucao_headers = ['Mês', 'Receita Bruta', 'Var. %', 'Resultado Op.', 'Margem']
        evolucao_data = [
            ['Janeiro', 'R$ 42.263', '-', 'R$ 5.133', '12,1%'],
            ['Fevereiro', 'R$ 49.513', '+17,2%', 'R$ 7.667', '15,5%'],
            ['Março', 'R$ 71.946', '+45,3%', 'R$ 16.690', '23,2%'],
            ['Abril', 'R$ 14.350', '-80,1%', 'R$ 0', '0%'],
        ]
        elements.append(self._create_data_table(evolucao_headers, evolucao_data, 
                                                 [3*cm, 4*cm, 3*cm, 4*cm, 3*cm],
                                                 highlight_rows={4: HexColor('#ffccbc')}))
        elements.append(Spacer(1, 10))
        
        elements.append(self._create_note_box(
            "⚠️ Observação Abril/2026",
            "O mês de Abril apresenta dados parciais, o que explica a queda significativa nos indicadores. "
            "A tendência de crescimento observada de Janeiro a Março (média de +31%) indica performance positiva.",
            HexColor('#ffc107')
        ))
        
        elements.append(PageBreak())
        
        # =====================================================================
        # PÁGINA 4: RANKINGS - SEGURADORAS E DISTRIBUIÇÃO SÓCIOS
        # =====================================================================
        elements.append(self._create_section_header("🏆 RANKING - MAIORES COMISSÕES POR SEGURADORA", HexColor('#764ba2')))
        elements.append(Spacer(1, 15))
        
        if df_seg is not None and len(df_seg) > 0:
            # Top 3 Seguradoras em cards
            for i, (_, row) in enumerate(df_seg.head(3).iterrows()):
                elements.append(self._create_ranking_card(
                    i + 1,
                    str(row['Seguradora'])[:40],
                    formatar_moeda(row['Total']),
                    f"{row['Qtd']:.0f} operações | {row['% do Total']:.1f}% do total"
                ))
                elements.append(Spacer(1, 8))
            
            elements.append(Spacer(1, 10))
            
            # Tabela completa
            seg_headers = ['#', 'Seguradora', 'Comissão Total', '% Total', 'Qtd']
            seg_data = []
            for i, (_, row) in enumerate(df_seg.head(10).iterrows()):
                seg_data.append([
                    f"{i+1}",
                    str(row['Seguradora'])[:30],
                    formatar_moeda(row['Total']),
                    f"{row['% do Total']:.1f}%",
                    f"{int(row['Qtd'])}"
                ])
            elements.append(self._create_data_table(seg_headers, seg_data, [1.5*cm, 8*cm, 4*cm, 2.5*cm, 2*cm]))
        
        elements.append(Spacer(1, 20))
        
        # Distribuição entre Sócios
        elements.append(self._create_section_header("🤝 DISTRIBUIÇÃO DE RESULTADOS - SÓCIOS", HexColor('#6f42c1')))
        elements.append(Spacer(1, 15))
        
        # Gráfico de pizza
        partner_total = 19169
        maldivas_total = 7780
        elements.append(self._create_pie_chart(
            [partner_total, maldivas_total], 
            ['Partner (65%)', 'Maldivas (35%)'],
            '🍩 Distribuição YTD entre Sócios',
            width=350, height=200
        ))
        elements.append(Spacer(1, 15))
        
        dist_headers = ['Mês', 'Partner (65%)', 'Maldivas (35%)', 'Total']
        dist_data = [
            ['Janeiro', 'R$ 3.336', 'R$ 986', 'R$ 4.322'],
            ['Fevereiro', 'R$ 4.984', 'R$ 1.818', 'R$ 6.802'],
            ['Março', 'R$ 10.849', 'R$ 4.976', 'R$ 15.825'],
            ['Abril', 'R$ 0', 'R$ 0', 'R$ 0'],
            ['TOTAL YTD', 'R$ 19.169', 'R$ 7.780', 'R$ 26.949'],
        ]
        elements.append(self._create_data_table(dist_headers, dist_data, 
                                                 [4*cm, 4.5*cm, 4.5*cm, 5*cm],
                                                 highlight_rows={5: HexColor('#e8f5e9')}))
        
        elements.append(PageBreak())
        
        # =====================================================================
        # PÁGINA 5: RANKINGS - ORIGINADORES E CLIENTES
        # =====================================================================
        elements.append(self._create_section_header("👥 RANKING - TOP ORIGINADORES", HexColor('#17a2b8')))
        elements.append(Spacer(1, 15))
        
        if df_orig is not None and len(df_orig) > 0:
            # Top 3 em cards
            for i, (_, row) in enumerate(df_orig.head(3).iterrows()):
                elements.append(self._create_ranking_card(
                    i + 1,
                    str(row['Originador']),
                    formatar_moeda(row['Total']),
                    f"{int(row['Operações'])} operações | Ticket médio: {formatar_moeda(row['Ticket Médio'])}"
                ))
                elements.append(Spacer(1, 8))
            
            elements.append(Spacer(1, 10))
            
            # Tabela
            orig_headers = ['#', 'Originador', 'Total', '% Total', 'Operações']
            orig_data = []
            for i, (_, row) in enumerate(df_orig.head(8).iterrows()):
                orig_data.append([
                    f"{i+1}",
                    str(row['Originador'])[:25],
                    formatar_moeda(row['Total']),
                    f"{row['% do Total']:.1f}%",
                    f"{int(row['Operações'])}"
                ])
            elements.append(self._create_data_table(orig_headers, orig_data, [1.5*cm, 7*cm, 4*cm, 2.5*cm, 3*cm]))
        else:
            # Dados default
            orig_default = [
                ('JOSE GUILHERME SABINO', 'R$ 107.842,67', '58 operações'),
                ('JOAO GABRIEL RIBEIRO', 'R$ 29.119,17', '25 operações'),
                ('FLAVIO ZANINI', 'R$ 24.756,96', '12 operações'),
            ]
            for i, (nome, valor, det) in enumerate(orig_default):
                elements.append(self._create_ranking_card(i + 1, nome, valor, det))
                elements.append(Spacer(1, 8))
        
        elements.append(Spacer(1, 20))
        
        # Top Clientes
        elements.append(self._create_section_header("🏅 RANKING - MAIORES CLIENTES POR RECEITA", HexColor('#20c997')))
        elements.append(Spacer(1, 15))
        
        if df_cli is not None and len(df_cli) > 0:
            cli_headers = ['#', 'Cliente', 'Receita Total', '% Total']
            cli_data = []
            for i, (_, row) in enumerate(df_cli.head(10).iterrows()):
                nome = str(row['Cliente'])[:35] + ('...' if len(str(row['Cliente'])) > 35 else '')
                cli_data.append([
                    f"{i+1}",
                    nome,
                    formatar_moeda(row['Total']),
                    f"{row['% do Total']:.1f}%"
                ])
            elements.append(self._create_data_table(cli_headers, cli_data, [1.5*cm, 9*cm, 4.5*cm, 3*cm]))
        
        elements.append(PageBreak())
        
        # =====================================================================
        # PÁGINA 6: PRODUTOS E DESPESAS
        # =====================================================================
        elements.append(self._create_section_header("📦 ANÁLISE POR TIPO DE PRODUTO", HexColor('#fd7e14')))
        elements.append(Spacer(1, 15))
        
        if df_prod is not None and len(df_prod) > 0:
            # Gráfico de barras
            prod_data = df_prod.head(6)['Total'].tolist()
            prod_labels = [str(p)[:15] for p in df_prod.head(6)['Produto'].tolist()]
            elements.append(self._create_bar_chart(prod_data, prod_labels, 
                                                   '📊 Comissão por Tipo de Produto (Top 6)',
                                                   width=500, height=180))
            elements.append(Spacer(1, 15))
            
            # Tabela
            prod_headers = ['Produto', 'Comissão Total', '% Total', 'Qtd Operações']
            prod_data_table = []
            for _, row in df_prod.head(8).iterrows():
                prod_data_table.append([
                    str(row['Produto'])[:25],
                    formatar_moeda(row['Total']),
                    f"{row['% do Total']:.1f}%",
                    f"{int(row['Qtd'])}"
                ])
            elements.append(self._create_data_table(prod_headers, prod_data_table, [6*cm, 5*cm, 3*cm, 4*cm]))
        
        elements.append(Spacer(1, 20))
        
        # Despesas
        elements.append(self._create_section_header("💸 RANKING - MAIORES DESPESAS", HexColor('#dc3545')))
        elements.append(Spacer(1, 15))
        
        if df_cat is not None and len(df_cat) > 0:
            # Tabela de despesas
            desp_headers = ['Categoria', 'Valor Total', '% Total', 'Qtd']
            desp_data = []
            for _, row in df_cat.head(10).iterrows():
                desp_data.append([
                    str(row['Categoria'])[:35],
                    formatar_moeda(row['Total']),
                    f"{row['% do Total']:.1f}%",
                    f"{int(row['Qtd'])}"
                ])
            elements.append(self._create_data_table(desp_headers, desp_data, [8*cm, 4*cm, 3*cm, 3*cm]))
        
        elements.append(Spacer(1, 15))
        
        elements.append(self._create_note_box(
            "💡 Análise de Despesas",
            "As principais categorias de despesas são Pró-Labore (Diretoria) e Serviços Prestados por PJ. "
            "Recomenda-se monitoramento contínuo para identificar oportunidades de otimização de custos.",
            HexColor('#dc3545')
        ))
        
        elements.append(PageBreak())
        
        # =====================================================================
        # PÁGINA 7: RESUMO EXECUTIVO - DRE
        # =====================================================================
        elements.append(self._create_section_header("📋 RESUMO EXECUTIVO - DRE YTD 2026", HexColor('#1E3A5F')))
        elements.append(Spacer(1, 15))
        
        elements.append(self._create_resumo_executivo_table())
        elements.append(Spacer(1, 20))
        
        # Box de análise
        elements.append(self._create_note_box(
            "📊 Análise do Resultado",
            "• A empresa apresenta resultado positivo com margem de 17% sobre o faturamento bruto.\n"
            "• O Rebate AAI representa 28,5% da receita bruta, sendo o maior custo variável.\n"
            "• A Margem de Contribuição de R$ 82.144 indica boa eficiência operacional.\n"
            "• A distribuição segue o share de 65%/35% entre Partner e Maldivas.",
            HexColor('#667eea')
        ))
        
        elements.append(PageBreak())
        
        # =====================================================================
        # PÁGINA 8: ANÁLISE GRÁFICA CONSOLIDADA
        # =====================================================================
        elements.append(self._create_section_header("📊 ANÁLISE GRÁFICA CONSOLIDADA", HexColor('#17a2b8')))
        elements.append(Spacer(1, 15))
        
        # Composição do Resultado
        elements.append(Paragraph("<b>🎯 Composição do Resultado Operacional</b>", 
                                  ParagraphStyle(name='ChartTitle', fontSize=12, textColor=HexColor('#1E3A5F'))))
        elements.append(Spacer(1, 10))
        
        composicao_data = [82144, 29104, 16946, 29490]  # Margem, Despesas, Folha, Resultado
        composicao_labels = ['Margem Contrib.', 'Despesas', 'Folha', 'Resultado']
        elements.append(self._create_bar_chart(composicao_data, composicao_labels, 
                                               'Estrutura de Custos e Resultado (R$)',
                                               width=450, height=180))
        elements.append(Spacer(1, 20))
        
        # Tabela comparativa
        comp_headers = ['Indicador', 'Jan', 'Fev', 'Mar', 'Abr', 'YTD']
        comp_data = [
            ['Receita Bruta', '42.263', '49.513', '71.946', '14.350', '178.072'],
            ['Margem Contrib.', '20.373', '22.732', '32.237', '6.803', '82.144'],
            ['EBITDA', '5.133', '7.667', '16.491', '0', '36.094'],
            ['Partner', '3.336', '4.984', '10.849', '0', '19.169'],
            ['Maldivas', '986', '1.818', '4.976', '0', '7.780'],
        ]
        elements.append(self._create_data_table(comp_headers, comp_data, 
                                                 [4*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 4*cm],
                                                 highlight_rows={5: HexColor('#e8f5e9')}))
        
        elements.append(PageBreak())
        
        # =====================================================================
        # PÁGINA 9: NOTAS E OBSERVAÇÕES
        # =====================================================================
        elements.append(self._create_section_header("📝 NOTAS E OBSERVAÇÕES", HexColor('#6c757d')))
        elements.append(Spacer(1, 15))
        
        # Premissas
        elements.append(self._create_note_box(
            "📌 Premissas e Parâmetros Utilizados",
            "• <b>Alíquotas de Impostos:</b> ISS 5,00% | PIS 0,65% | COFINS 3,00% | IRPJ 4,80% | CSLL 6,08%\n"
            "• <b>D.A. (Despesas Administrativas):</b> 10% sobre a receita bruta\n"
            "• <b>Rebate/Repasse AAI:</b> 40% da comissão\n"
            "• <b>Share Sócio Partner:</b> 65% do resultado\n"
            "• <b>Share Sócio Maldivas:</b> 35% do resultado\n"
            "• <b>Pró Labore:</b> 15% deduzido do resultado (50% para cada parte)",
            HexColor('#667eea')
        ))
        elements.append(Spacer(1, 15))
        
        # Metodologia
        elements.append(self._create_note_box(
            "📊 Metodologia de Cálculo",
            "1. A <b>Receita Bruta</b> considera todas as comissões recebidas no período.\n"
            "2. Os <b>Impostos Diretos</b> são calculados com base nas alíquotas vigentes.\n"
            "3. O <b>Custo Operacional (D.A.)</b> é apurado como 10% da receita bruta.\n"
            "4. O <b>Rebate AAI</b> corresponde a 40% das comissões, repassado aos agentes.\n"
            "5. A <b>Margem de Contribuição</b> = Receita - Impostos - Custos - Rebate + Co-corretagem.\n"
            "6. O <b>EBITDA</b> = Margem de Contribuição - Despesas - Folha/Terceiros.\n"
            "7. A <b>Distribuição</b> segue o share de 65%/35% entre Partner e Maldivas.",
            HexColor('#28a745')
        ))
        elements.append(Spacer(1, 15))
        
        # Glossário
        elements.append(self._create_note_box(
            "📖 Glossário",
            "• <b>YTD (Year To Date):</b> Acumulado do ano até a data atual.\n"
            "• <b>EBITDA:</b> Lucro antes de juros, impostos, depreciação e amortização.\n"
            "• <b>Margem de Contribuição:</b> Receita menos custos variáveis diretos.\n"
            "• <b>D.A.:</b> Despesas Administrativas da operação.\n"
            "• <b>Rebate AAI:</b> Comissão repassada aos Agentes Autônomos de Investimento.\n"
            "• <b>Portal MAAS:</b> Plataforma digital de distribuição de seguros.",
            HexColor('#17a2b8')
        ))
        elements.append(Spacer(1, 15))
        
        # Disclaimer
        elements.append(self._create_note_box(
            "⚠️ Disclaimer",
            "Este relatório é de uso exclusivo interno da Assertif Corretora de Seguros LTDA. "
            "Os dados apresentados são baseados nas informações contábeis e operacionais do período "
            "e podem estar sujeitos a ajustes. Para decisões estratégicas, recomenda-se consultar "
            "a equipe financeira e contábil da empresa.",
            HexColor('#dc3545')
        ))
        
        elements.append(Spacer(1, 30))
        
        # FOOTER FINAL
        elements.append(self._create_footer())
        
        # Build PDF com numeração de páginas
        doc.build(elements, onFirstPage=self._add_page_number, onLaterPages=self._add_page_number)
        
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
            
            # Processamentos adicionais
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
            
            # Agrupar por categoria
            df_cat = df_despesas_clean.groupby(col_categoria)[col_valor_desp].agg(['sum', 'count']).reset_index()
            df_cat.columns = ['Categoria', 'Total', 'Qtd']
            df_cat = df_cat[df_cat['Total'] > 0].sort_values('Total', ascending=False)
            df_cat['% do Total'] = (df_cat['Total'] / df_cat['Total'].sum() * 100).round(1)
    
    # =============================================================================
    # 💰 SEÇÃO 1: KPIs PRINCIPAIS YTD - ALTERADO: Lucro Líquido -> Despesas
    # =============================================================================
    
    st.markdown("""
    <div class="section-header" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
        <h2>💰 INDICADORES PRINCIPAIS (KPIs) YTD</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # KPIs - Valores atualizados conforme planilha
    faturamento_ytd = 178072
    despesas_total = 46050  # 29.104 + 16.946
    margem = 17
    ebitda = 36094
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(criar_cartao_kpi_html("FATURAMENTO YTD", formatar_moeda(faturamento_ytd), "Jan - Abr 2026", "#667eea", "💰"), unsafe_allow_html=True)
    
    with col2:
        st.markdown(criar_cartao_kpi_html("DESPESAS", formatar_moeda(despesas_total), "Desp + Folha", "#dc3545", "💸"), unsafe_allow_html=True)
    
    with col3:
        st.markdown(criar_cartao_kpi_html("MARGEM DE LUCRO", "17%", "Status: LUCRO", "#17a2b8", "📊"), unsafe_allow_html=True)
    
    with col4:
        st.markdown(criar_cartao_kpi_html("EBITDA", formatar_moeda(ebitda), "Resultado Operacional", "#764ba2", "🎯"), unsafe_allow_html=True)
    
    # =============================================================================
    # 📈 SEÇÃO 2: EVOLUÇÃO MENSAL
    # =============================================================================
    
    if show_charts:
        st.markdown("""
        <div class="section-header" style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%);">
            <h2>📈 EVOLUÇÃO MENSAL - RECEITA vs RESULTADO</h2>
        </div>
        """, unsafe_allow_html=True)
        
        meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril']
        receita_bruta = [42263, 49513, 71946, 14350]
        resultado_op = [5133, 7667, 16690, 0]
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
                textfont=dict(size=13, color=CORES['escuro'], family='Arial Black'),
                name='Receita Bruta',
                hovertemplate='<b>%{x}</b><br>Receita: R$ %{y:,.0f}<extra></extra>',
                width=0.6
            ),
            row=1, col=1
        )
        
        # Gráfico 2: Crescimento Mensal
        cores_cresc = ['#6c757d', '#28a745', '#28a745', '#dc3545']
        fig_evolucao.add_trace(
            go.Scatter(
                x=meses, y=crescimento,
                mode='lines+markers+text',
                line=dict(color=CORES['primaria'], width=4, shape='spline'),
                marker=dict(size=20, color=cores_cresc, line=dict(width=3, color='white'), symbol='circle'),
                text=[f"{v:+.1f}%" for v in crescimento],
                textposition='top center',
                textfont=dict(size=13, family='Arial Black', color=CORES['escuro']),
                name='Crescimento %',
                hovertemplate='<b>%{x}</b><br>Crescimento: %{y:+.1f}%<extra></extra>'
            ),
            row=1, col=2
        )
        
        fig_evolucao.add_hline(y=0, line_dash="dash", line_color="#dc3545", line_width=2, row=1, col=2)
        
        # Gráfico 3: Resultado Operacional
        fig_evolucao.add_trace(
            go.Scatter(
                x=meses, y=resultado_op,
                mode='lines+markers+text',
                fill='tozeroy',
                fillcolor='rgba(102, 126, 234, 0.25)',
                line=dict(color=CORES['primaria'], width=4, shape='spline'),
                marker=dict(size=16, color=CORES['primaria'], line=dict(width=3, color='white'), symbol='circle'),
                text=[f"R$ {v/1000:.1f}K" for v in resultado_op],
                textposition='top center',
                textfont=dict(size=13, family='Arial Black', color=CORES['escuro']),
                name='Resultado',
                hovertemplate='<b>%{x}</b><br>Resultado: R$ %{y:,.0f}<extra></extra>'
            ),
            row=1, col=3
        )
        
        fig_evolucao.update_layout(
            height=500,
            showlegend=False,
            paper_bgcolor='white',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Segoe UI', size=12, color=CORES['escuro']),
            hoverlabel=dict(bgcolor='white', font_size=13, bordercolor='#667eea'),
            margin=dict(l=60, r=60, t=80, b=60)
        )
        
        fig_evolucao.update_xaxes(gridcolor='#e8e8e8', tickfont=dict(size=11, family='Arial', color=CORES['escuro']), tickangle=0)
        fig_evolucao.update_yaxes(gridcolor='#e8e8e8', tickfont=dict(size=11, family='Arial'))
        
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
            hovertemplate='<b>%{y}</b><br>Comissão: R$ %{x:,.2f}<extra></extra>',
            width=0.7
        ))
        
        fig_ranking_seg.update_layout(
            title=dict(text='🏢 Top 15 Seguradoras por Volume de Comissão', font=dict(size=18, family='Arial Black', color='#1E3A5F'), x=0.5, xanchor='center'),
            height=650,
            paper_bgcolor='white',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis_title=dict(text='Comissão Total (R$)', font=dict(size=13, family='Arial Black')),
            yaxis=dict(categoryorder='total ascending', tickfont=dict(size=11, family='Arial')),
            font=dict(family='Segoe UI', size=12),
            margin=dict(l=180, r=150, t=80, b=60)
        )
        
        fig_ranking_seg.update_xaxes(gridcolor='#e8e8e8', tickformat=',.0f')
        st.plotly_chart(fig_ranking_seg, use_container_width=True)
    
    # =============================================================================
    # 🤝 SEÇÃO 4: DISTRIBUIÇÃO ENTRE SÓCIOS
    # =============================================================================
    
    if show_charts:
        st.markdown("""
        <div class="section-header" style="background: linear-gradient(135deg, #6f42c1 0%, #e83e8c 100%);">
            <h2>🤝 DISTRIBUIÇÃO DE RESULTADOS - SÓCIOS</h2>
        </div>
        """, unsafe_allow_html=True)
        
        meses_dist = ['Janeiro', 'Fevereiro', 'Março', 'Abril']
        partner = [3336, 4984, 10849, 0]
        maldivas = [986, 1818, 4976, 0]
        
        fig_dist = make_subplots(
            rows=1, cols=2,
            subplot_titles=('<b>📊 Distribuição Mensal por Sócio</b>', '<b>🍩 Share Total YTD</b>'),
            specs=[[{"type": "bar"}, {"type": "pie"}]],
            column_widths=[0.6, 0.4],
            horizontal_spacing=0.1
        )
        
        fig_dist.add_trace(
            go.Bar(name='Partner (65%)', x=meses_dist, y=partner, marker_color='#667eea', marker_line=dict(width=2, color='white'),
                   text=[f"R$ {v/1000:.1f}K" for v in partner], textposition='outside', textfont=dict(size=11, family='Arial Black'), width=0.35),
            row=1, col=1
        )
        fig_dist.add_trace(
            go.Bar(name='Maldivas (35%)', x=meses_dist, y=maldivas, marker_color='#f5576c', marker_line=dict(width=2, color='white'),
                   text=[f"R$ {v/1000:.1f}K" for v in maldivas], textposition='outside', textfont=dict(size=11, family='Arial Black'), width=0.35),
            row=1, col=1
        )
        
        fig_dist.add_trace(
            go.Pie(labels=['Partner', 'Maldivas'], values=[19169, 7780], hole=0.55,
                   marker=dict(colors=['#667eea', '#f5576c'], line=dict(width=3, color='white')),
                   textinfo='label+percent', textfont=dict(size=14, family='Arial Black'),
                   hovertemplate='<b>%{label}</b><br>Valor: R$ %{value:,.0f}<br>%{percent}<extra></extra>'),
            row=1, col=2
        )
        
        fig_dist.update_layout(
            height=480, paper_bgcolor='white', plot_bgcolor='rgba(0,0,0,0)', barmode='group',
            legend=dict(orientation='h', yanchor='bottom', y=-0.18, xanchor='center', x=0.3, font=dict(size=12, family='Arial Black')),
            font=dict(family='Segoe UI', size=12), margin=dict(l=60, r=60, t=80, b=80)
        )
        fig_dist.update_yaxes(gridcolor='#e8e8e8', range=[0, max(max(partner), max(maldivas)) * 1.3], tickformat=',.0f', row=1, col=1)
        
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
                                   title=dict(font=dict(size=18, family='Arial Black', color='#1E3A5F'), x=0.5, xanchor='center'), margin=dict(l=40, r=40, t=80, b=40))
            fig_prod.update_traces(textinfo='label+percent entry', textfont=dict(size=12, family='Arial Black'),
                                   hovertemplate='<b>%{label}</b><br>Comissão: R$ %{value:,.2f}<br>Participação: %{percentEntry:.1%}<extra></extra>')
            st.plotly_chart(fig_prod, use_container_width=True)
        
        with col2:
            fig_prod_bar = go.Figure()
            fig_prod_bar.add_trace(go.Bar(
                y=df_prod['Produto'], x=df_prod['Total'], orientation='h',
                marker=dict(color=df_prod['Total'], colorscale='YlOrRd', showscale=True,
                           colorbar=dict(title=dict(text='Comissão', font=dict(size=12)), thickness=15, len=0.7), line=dict(width=1, color='white')),
                text=[f"R$ {v/1000:.1f}K ({p:.1f}%)" for v, p in zip(df_prod['Total'], df_prod['% do Total'])],
                textposition='outside', textfont=dict(size=11, family='Arial Black', color='#1E3A5F'),
                hovertemplate='<b>%{y}</b><br>Comissão: R$ %{x:,.2f}<extra></extra>', width=0.7
            ))
            fig_prod_bar.update_layout(
                title=dict(text='📊 Comissão por Tipo de Produto', font=dict(size=18, family='Arial Black', color='#1E3A5F'), x=0.5, xanchor='center'),
                height=500, paper_bgcolor='white', plot_bgcolor='rgba(0,0,0,0)',
                xaxis_title=dict(text='Comissão Total (R$)', font=dict(size=13, family='Arial Black')),
                yaxis=dict(categoryorder='total ascending', tickfont=dict(size=11, family='Arial')),
                font=dict(family='Segoe UI', size=12), margin=dict(l=180, r=150, t=80, b=60)
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
            outros = pd.DataFrame({'Originador': ['Outros'], 'Total': [df_orig.iloc[5:]['Total'].sum()], '% do Total': [df_orig.iloc[5:]['% do Total'].sum()]})
            df_orig_chart = pd.concat([top_5, outros])
            
            fig_orig.add_trace(go.Pie(
                labels=df_orig_chart['Originador'], values=df_orig_chart['Total'], hole=0.55,
                marker=dict(colors=CORES['gradiente'], line=dict(width=3, color='white')),
                textinfo='label+percent', textposition='outside', textfont=dict(size=12, family='Arial Black'),
                hovertemplate='<b>%{label}</b><br>Comissão: R$ %{value:,.2f}<br>Participação: %{percent}<extra></extra>'
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
            hovertemplate='<b>%{y}</b><br>Receita: R$ %{x:,.2f}<extra></extra>', width=0.7
        ))
        
        fig_ranking_cli.update_layout(
            title=dict(text='🏢 Top 15 Clientes por Volume de Receita', font=dict(size=18, family='Arial Black', color='#1E3A5F'), x=0.5, xanchor='center'),
            height=650, paper_bgcolor='white', plot_bgcolor='rgba(0,0,0,0)',
            xaxis_title=dict(text='Receita Total (R$)', font=dict(size=13, family='Arial Black')),
            yaxis=dict(categoryorder='total ascending', tickfont=dict(size=10, family='Arial')),
            font=dict(family='Segoe UI', size=12), margin=dict(l=280, r=150, t=80, b=60)
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
            hovertemplate='<b>%{x}</b><br>Valor: R$ %{y:,.2f}<extra></extra>', width=0.7
        ))
        
        fig_desp_bar.update_layout(
            title=dict(text='📊 Top 10 Categorias de Despesas', font=dict(size=18, family='Arial Black', color='#1E3A5F'), x=0.5, xanchor='center'),
            height=550, paper_bgcolor='white', plot_bgcolor='rgba(0,0,0,0)', xaxis_tickangle=-35,
            xaxis=dict(tickfont=dict(size=10, family='Arial')),
            yaxis_title=dict(text='Valor (R$)', font=dict(size=13, family='Arial Black')),
            yaxis=dict(range=[0, df_cat['Total'].head(10).max() * 1.25]),
            font=dict(family='Segoe UI', size=12), margin=dict(l=80, r=60, t=80, b=180)
        )
        fig_desp_bar.update_yaxes(gridcolor='#e8e8e8', tickformat=',.0f')
        st.plotly_chart(fig_desp_bar, use_container_width=True)
    
    # =============================================================================
    # 📋 SEÇÃO 9: RESUMO EXECUTIVO
    # =============================================================================
    
    if show_tables:
        st.markdown("""
        <div class="section-header" style="background: linear-gradient(135deg, #1E3A5F 0%, #2d5a87 100%);">
            <h2>📋 RESUMO EXECUTIVO - YTD 2026</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Tabela de resumo atualizada - SEM as linhas removidas
        resumo_data = {
            'Indicador': [
                '💰 RECEITA BRUTA TOTAL', 'Receita Bruta (Produção Direta)', 'Impostos Diretos',
                'Custo Operacional (D.A)', 'Co-Corretagem', 'Rebate AAI', '(=) Margem de Contribuição',
                'Despesas', 'Folha + Terceiros', 'EBITDA Societário', '🎯 RESULTADO OPERACIONAL TOTAL',
                '📊 RESULTADO OPERACIONAL - DISTRIBUIÇÃO',
                '→ Sócio Partner (65%)', '→ Sócio Maldivas (35%)'
            ],
            'Valor': [
                'R$ 178.072,00', 'R$ 177.797,00', '(R$ 30.990,00)',
                '(R$ 14.820,00)', 'R$ 803,00', '(R$ 50.646,00)', 'R$ 82.144,00',
                '(R$ 29.104,00)', '(R$ 16.946,00)', 'R$ 36.094,00', 'R$ 29.490,00',
                'R$ 26.949,00',
                'R$ 19.169,00', 'R$ 7.780,00'
            ]
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
            with st.spinner("Gerando PDF profissional com todas as melhorias..."):
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
                    st.info("💡 Verifique se todas as bibliotecas estão instaladas corretamente.")
    
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
            📊 Versão 3.0 Premium Ultimate | 🗓️ Período: Janeiro a Abril 2026 | 📈 Status: LUCRO<br>
            Desenvolvido com Streamlit + Plotly + ReportLab
        </p>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# 🚀 EXECUÇÃO DA APLICAÇÃO
# =============================================================================

if __name__ == "__main__":
    main()
