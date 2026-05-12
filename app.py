# =============================================================================
# 🚀 ASSERTIF CORRETORA - DASHBOARD FINANCEIRO PREMIUM
# =============================================================================
# Dashboard interativo com rankings, filtros e visualizações profissionais
# Versão: 7.0 PREMIUM - PDF COMPLETO E PERFEITO
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
# 🎨 CONFIGURAÇÕES DE ESTILO PREMIUM - PALETA AZUL MALDIVAS
# =============================================================================

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

PALETA_SEQUENCIAL = px.colors.sequential.Viridis
PALETA_QUALITATIVA = px.colors.qualitative.Set2
PALETA_DIVERGENTE = px.colors.diverging.RdYlGn

# =============================================================================
# 📊 DADOS MENSAIS DA DRE - ATUALIZADOS CONFORME PLANILHA
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
        'custos_totais': 26781,
        'margem_contrib': 22732,
        'despesas': 15065,
        'resultado_op': 7667
    },
    'Março': {
        'receita_bruta': 71946,
        'custos_totais': 39510,
        'margem_contrib': 32436,
        'despesas': 15746,
        'resultado_op': 16690
    },
    'Abril': {
        'receita_bruta': 14350,
        'custos_totais': 7547,
        'margem_contrib': 6803,
        'despesas': 0,
        'resultado_op': 0
    }
}

# =============================================================================
# 📊 FUNÇÕES AUXILIARES
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


def converter_valor_brasileiro(valor):
    """Converte valor no formato brasileiro para float"""
    try:
        if pd.isna(valor) or valor == '' or valor == ' ':
            return 0
        if isinstance(valor, (int, float)):
            if pd.isna(valor):
                return 0
            return float(valor)
        val_str = str(valor).strip()
        is_negative = False
        if val_str.startswith('(') and val_str.endswith(')'):
            is_negative = True
            val_str = val_str[1:-1]
        if val_str.startswith('-'):
            is_negative = True
            val_str = val_str[1:]
        val_str = val_str.replace('R$', '').replace(' ', '').strip()
        # Formato brasileiro: 1.234,56
        if '.' in val_str and ',' in val_str:
            val_str = val_str.replace('.', '').replace(',', '.')
        elif ',' in val_str:
            val_str = val_str.replace(',', '.')
        if val_str == '' or val_str == '-':
            return 0
        resultado = float(val_str)
        return -resultado if is_negative else resultado
    except:
        return 0


def extrair_dados_dre(df_dre):
    """Extrai dados da DRE"""
    dados_extraidos = {}
    
    meses_colunas = {
        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
        5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
        9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
    }
    
    linhas_encontradas = {
        'receita_bruta_total': None, 'impostos_diretos': None,
        'custo_op_da': None, 'co_corretagem': None, 'rebate_aai': None,
        'margem_contrib_direta': None, 'despesas': None,
        'folha_terceiros': None, 'margem_contrib_maas': None, 'resultado_op': None
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
                elif 'MARGEM DE CONTRIBUIÇÃO' in texto_celula or '(=) MARGEM DE CONTRIBUIÇÃO' in texto_celula:
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
                    return converter_valor_brasileiro(val)
                return 0
            except:
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
        return None


def criar_cartao_kpi_html(titulo, valor, subtitulo="", cor=CORES['primaria'], icone="📊", tamanho="normal"):
    """Cria HTML para cartão de KPI"""
    if tamanho == "grande":
        padding, icone_size, titulo_size, valor_size, min_height = "35px 25px", "3rem", "1.1rem", "2.2rem", "200px"
    else:
        padding, icone_size, titulo_size, valor_size, min_height = "30px 20px", "2.8rem", "0.95rem", "1.9rem", "180px"
    
    html = f"""
    <div style="
        background: linear-gradient(145deg, {cor} 0%, {cor}dd 50%, {cor}bb 100%);
        padding: {padding}; border-radius: 24px; color: white; text-align: center;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3), 0 8px 25px {cor}40, inset 0 1px 0 rgba(255,255,255,0.2);
        margin: 10px 5px; min-height: {min_height}; border: 1px solid rgba(255,255,255,0.15);
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        position: relative; overflow: hidden;
    ">
        <div style="position: absolute; top: -30%; right: -30%; width: 150px; height: 150px;
            background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 70%); border-radius: 50%;"></div>
        <div style="font-size: {icone_size}; margin-bottom: 15px; text-shadow: 3px 3px 6px rgba(0,0,0,0.4);
            filter: drop-shadow(0 4px 8px rgba(0,0,0,0.3)); position: relative; z-index: 1;">{icone}</div>
        <div style="font-size: {titulo_size}; font-weight: 700; opacity: 1; margin-top: 5px;
            text-transform: uppercase; letter-spacing: 2px; text-shadow: 2px 2px 4px rgba(0,0,0,0.4);
            position: relative; z-index: 1;">{titulo}</div>
        <div style="font-size: {valor_size}; font-weight: 900; margin: 18px 0;
            text-shadow: 3px 3px 6px rgba(0,0,0,0.4); letter-spacing: 1px; position: relative; z-index: 1;">{valor}</div>
    </div>
    """
    return html


# =============================================================================
# 📄 CLASSE PDF - VERSÃO COMPLETA E PERFEITA
# =============================================================================

class PDFDashboardCompleto:
    """Gera PDF completo e perfeito do dashboard"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_styles()
        
    def _setup_styles(self):
        """Configura estilos do PDF"""
        self.styles.add(ParagraphStyle(
            name='CapaTitulo', fontSize=48, textColor=colors.white, alignment=TA_CENTER,
            fontName='Helvetica-Bold', spaceAfter=10, leading=55
        ))
        self.styles.add(ParagraphStyle(
            name='CapaSubtitulo', fontSize=20, textColor=colors.white, alignment=TA_CENTER,
            fontName='Helvetica', spaceAfter=20, leading=26
        ))
        self.styles.add(ParagraphStyle(
            name='SecaoTitulo', fontSize=16, textColor=colors.white, alignment=TA_LEFT,
            fontName='Helvetica-Bold', spaceBefore=0, spaceAfter=0
        ))
        self.styles.add(ParagraphStyle(
            name='TextoNormal', fontSize=10, textColor=HexColor('#333333'), alignment=TA_LEFT,
            fontName='Helvetica', spaceAfter=8, leading=14
        ))
        self.styles.add(ParagraphStyle(
            name='KPITitulo', fontSize=9, textColor=colors.white, alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        self.styles.add(ParagraphStyle(
            name='KPIValor', fontSize=14, textColor=colors.white, alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
    
    def _criar_cabecalho_rodape(self, canvas_obj, doc):
        """Adiciona cabeçalho e rodapé em todas as páginas"""
        canvas_obj.saveState()
        
        # Cabeçalho
        canvas_obj.setFillColor(HexColor('#0a1628'))
        canvas_obj.rect(0, A4[1] - 50, A4[0], 50, fill=True, stroke=False)
        canvas_obj.setFillColor(colors.white)
        canvas_obj.setFont('Helvetica-Bold', 10)
        canvas_obj.drawString(30, A4[1] - 32, "ASSERTIF CORRETORA - Dashboard Financeiro")
        canvas_obj.drawRightString(A4[0] - 30, A4[1] - 32, "YTD 2026")
        
        # Rodapé
        canvas_obj.setFillColor(HexColor('#0a1628'))
        canvas_obj.rect(0, 0, A4[0], 35, fill=True, stroke=False)
        canvas_obj.setFillColor(colors.white)
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.drawString(30, 14, f"Gerado em: {datetime.now().strftime('%d/%m/%Y as %H:%M')}")
        canvas_obj.drawCentredString(A4[0]/2, 14, "Confidencial - Uso Interno")
        canvas_obj.drawRightString(A4[0] - 30, 14, f"Pagina {doc.page}")
        
        canvas_obj.restoreState()
    
    def _criar_capa(self, totais):
        """Cria página de capa"""
        elements = []
        elements.append(Spacer(1, 80))
        
        # Calcular margem
        margem_pct = (totais['resultado_op'] / totais['receita_bruta'] * 100) if totais['receita_bruta'] > 0 else 0
        status = "LUCRO" if totais['resultado_op'] >= 0 else "PREJUIZO"
        
        capa_data = [
            [Paragraph("<br/><br/>", self.styles['CapaTitulo'])],
            [Paragraph("ASSERTIF CORRETORA", self.styles['CapaTitulo'])],
            [Paragraph("DE SEGUROS", self.styles['CapaTitulo'])],
            [Spacer(1, 30)],
            [Paragraph("_" * 40, ParagraphStyle(name='Linha', alignment=TA_CENTER, textColor=colors.white))],
            [Spacer(1, 30)],
            [Paragraph("Dashboard Financeiro", self.styles['CapaSubtitulo'])],
            [Paragraph("Relatorio Executivo Completo", self.styles['CapaSubtitulo'])],
            [Paragraph("YTD 2026", self.styles['CapaSubtitulo'])],
            [Spacer(1, 50)],
            [Paragraph("Periodo: Janeiro a Abril de 2026", ParagraphStyle(
                name='Info1', fontSize=14, textColor=colors.white, alignment=TA_CENTER, fontName='Helvetica'))],
            [Spacer(1, 10)],
            [Paragraph(f"Status: {status} | Margem: {margem_pct:.0f}%", ParagraphStyle(
                name='Info2', fontSize=14, textColor=HexColor('#00d4aa'), alignment=TA_CENTER, fontName='Helvetica-Bold'))],
            [Spacer(1, 50)],
            [Paragraph(f"Documento gerado em: {datetime.now().strftime('%d/%m/%Y as %H:%M')}", ParagraphStyle(
                name='Data', fontSize=11, textColor=colors.white, alignment=TA_CENTER, fontName='Helvetica'))],
            [Paragraph("<br/><br/>", self.styles['CapaTitulo'])],
        ]
        
        capa_table = Table([[row[0]] for row in capa_data], colWidths=[17*cm])
        capa_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), HexColor('#0a1628')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 20),
            ('RIGHTPADDING', (0, 0), (-1, -1), 20),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        
        elements.append(capa_table)
        elements.append(Spacer(1, 20))
        
        # Resumo na capa
        partner = int(totais['resultado_op'] * 0.65)
        maldivas = int(totais['resultado_op'] * 0.35)
        
        resumo_capa = [
            ['Faturamento YTD', formatar_moeda(totais['receita_bruta']), 'Margem Contribuicao', formatar_moeda(totais['margem_contrib'])],
            ['Despesas Totais', formatar_moeda(totais['despesas']), 'Resultado Operacional', formatar_moeda(totais['resultado_op'])],
            ['Partner (65%)', formatar_moeda(partner), 'Maldivas (35%)', formatar_moeda(maldivas)],
        ]
        
        resumo_table = Table(resumo_capa, colWidths=[4.5*cm, 4*cm, 4.5*cm, 4*cm])
        resumo_table.setStyle(TableStyle([
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
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#e0e0e0')),
            ('BOX', (0, 0), (-1, -1), 2, HexColor('#0a1628')),
        ]))
        elements.append(resumo_table)
        
        elements.append(PageBreak())
        return elements
    
    def _criar_sumario(self):
        """Cria sumário"""
        elements = []
        elements.append(Spacer(1, 60))
        
        titulo_sumario = Table([[Paragraph("<b>SUMARIO</b>", ParagraphStyle(
            name='SumTit', fontSize=18, textColor=colors.white, alignment=TA_CENTER, fontName='Helvetica-Bold'
        ))]], colWidths=[17*cm])
        titulo_sumario.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), HexColor('#0a1628')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ]))
        elements.append(titulo_sumario)
        elements.append(Spacer(1, 30))
        
        itens = [
            ('1.', 'Indicadores Principais (KPIs)', '3'),
            ('2.', 'Evolucao Mensal Detalhada', '4'),
            ('3.', 'Ranking de Seguradoras', '5'),
            ('4.', 'Distribuicao de Resultados entre Socios', '6'),
            ('5.', 'Ranking de Originadores', '7'),
            ('6.', 'Ranking de Clientes', '8'),
            ('7.', 'Analise por Produto', '9'),
            ('8.', 'Ranking de Despesas', '10'),
            ('9.', 'DRE Completo - Demonstrativo de Resultados', '11'),
            ('10.', 'Resumo Executivo Final', '12'),
        ]
        
        for num, titulo, pag in itens:
            item_data = [[
                Paragraph(f"<b>{num}</b>", ParagraphStyle(name='SumNum', fontSize=12, textColor=HexColor('#1a3a5c'))),
                Paragraph(titulo, ParagraphStyle(name='SumItem', fontSize=12, textColor=HexColor('#333333'))),
                Paragraph(f"<b>{pag}</b>", ParagraphStyle(name='SumPag', fontSize=12, textColor=HexColor('#666666'), alignment=TA_RIGHT)),
            ]]
            item_table = Table(item_data, colWidths=[1.5*cm, 12.5*cm, 3*cm])
            item_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('LINEBELOW', (0, 0), (-1, -1), 0.5, HexColor('#e0e0e0')),
            ]))
            elements.append(item_table)
        
        elements.append(PageBreak())
        return elements
    
    def _criar_secao_titulo(self, titulo, cor=HexColor('#0a1628')):
        """Cria título de seção"""
        secao = Table([[Paragraph(f"<b>{titulo}</b>", self.styles['SecaoTitulo'])]], colWidths=[17*cm])
        secao.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), cor),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 20),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        return secao
    
    def _criar_kpis(self, totais):
        """Cria seção de KPIs"""
        elements = []
        elements.append(Spacer(1, 60))
        elements.append(self._criar_secao_titulo("1. INDICADORES PRINCIPAIS (KPIs)"))
        elements.append(Spacer(1, 25))
        
        kpis = [
            ('FATURAMENTO', formatar_moeda(totais['receita_bruta']), HexColor('#0a1628')),
            ('CUSTOS', formatar_moeda(totais['custos_totais']), HexColor('#ff6b6b')),
            ('MARGEM', formatar_moeda(totais['margem_contrib']), HexColor('#2e86ab')),
            ('DESPESAS', formatar_moeda(totais['despesas']), HexColor('#feca57')),
            ('RESULTADO', formatar_moeda(totais['resultado_op']), HexColor('#00d4aa')),
        ]
        
        kpi_cells = []
        for titulo, valor, cor in kpis:
            cell_content = [
                [Paragraph(f"<b>{titulo}</b>", self.styles['KPITitulo'])],
                [Spacer(1, 8)],
                [Paragraph(f"<b>{valor}</b>", self.styles['KPIValor'])],
            ]
            cell_table = Table(cell_content, colWidths=[3.2*cm])
            cell_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), cor),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 15),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
            ]))
            kpi_cells.append(cell_table)
        
        kpi_row = Table([kpi_cells], colWidths=[3.4*cm] * 5)
        kpi_row.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(kpi_row)
        elements.append(Spacer(1, 30))
        
        # Legenda dos KPIs
        legenda_titulo = Table([[Paragraph("<b>Legenda dos Indicadores</b>", ParagraphStyle(
            name='LegTit', fontSize=12, textColor=HexColor('#0a1628'), fontName='Helvetica-Bold'
        ))]], colWidths=[17*cm])
        legenda_titulo.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), HexColor('#f0f8ff')),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('BOX', (0, 0), (-1, -1), 1, HexColor('#2e86ab')),
        ]))
        elements.append(legenda_titulo)
        elements.append(Spacer(1, 10))
        
        legendas = [
            ('Faturamento Bruto:', 'Soma da Receita Bruta de Producao Direta e Portal MAAS'),
            ('Custos Totais:', 'Impostos Diretos + Custo Operacional (D.A.) + Rebate AAI - Co-corretagem'),
            ('Margem de Contribuicao:', 'Faturamento Bruto menos Custos Totais'),
            ('Despesas Totais:', 'Despesas Operacionais + Folha + Terceiros'),
            ('Resultado Operacional:', 'Margem de Contribuicao menos Despesas (Base para distribuicao 65/35)'),
        ]
        
        for titulo, desc in legendas:
            leg_data = [[
                Paragraph(f"<b>{titulo}</b>", ParagraphStyle(name='LegItem', fontSize=9, textColor=HexColor('#0a1628'))),
                Paragraph(desc, ParagraphStyle(name='LegDesc', fontSize=9, textColor=HexColor('#555555'))),
            ]]
            leg_table = Table(leg_data, colWidths=[4*cm, 13*cm])
            leg_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(leg_table)
        
        elements.append(PageBreak())
        return elements
    
    def _criar_evolucao_mensal(self, dados_mensais):
        """Cria seção de evolução mensal"""
        elements = []
        elements.append(Spacer(1, 60))
        elements.append(self._criar_secao_titulo("2. EVOLUCAO MENSAL DETALHADA", HexColor('#1a3a5c')))
        elements.append(Spacer(1, 25))
        
        headers = ['Mes', 'Receita Bruta', 'Custos', 'Margem Contrib.', 'Despesas', 'Resultado', 'Margem %']
        data = [headers]
        
        meses_lista = list(dados_mensais.keys())
        for i, mes in enumerate(meses_lista):
            d = dados_mensais[mes]
            margem_pct = (d['resultado_op'] / d['receita_bruta'] * 100) if d['receita_bruta'] > 0 else 0
            
            row = [
                mes,
                formatar_moeda(d['receita_bruta']),
                formatar_moeda(d['custos_totais']),
                formatar_moeda(d['margem_contrib']),
                formatar_moeda(d['despesas']),
                formatar_moeda(d['resultado_op']),
                f"{margem_pct:.1f}%"
            ]
            data.append(row)
        
        total_receita = sum(d['receita_bruta'] for d in dados_mensais.values())
        total_custos = sum(d['custos_totais'] for d in dados_mensais.values())
        total_margem = sum(d['margem_contrib'] for d in dados_mensais.values())
        total_desp = sum(d['despesas'] for d in dados_mensais.values())
        total_result = sum(d['resultado_op'] for d in dados_mensais.values())
        margem_total_pct = (total_result / total_receita * 100) if total_receita > 0 else 0
        
        data.append([
            'TOTAL YTD',
            formatar_moeda(total_receita),
            formatar_moeda(total_custos),
            formatar_moeda(total_margem),
            formatar_moeda(total_desp),
            formatar_moeda(total_result),
            f"{margem_total_pct:.1f}%"
        ])
        
        col_widths = [2.5*cm, 2.5*cm, 2.3*cm, 2.5*cm, 2.3*cm, 2.5*cm, 2*cm]
        table = Table(data, colWidths=col_widths)
        
        style_commands = [
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#0a1628')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
            ('BOX', (0, 0), (-1, -1), 1.5, HexColor('#0a1628')),
            ('BACKGROUND', (0, -1), (-1, -1), HexColor('#e8f4f8')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ]
        
        for i in range(1, len(data) - 1):
            if i % 2 == 0:
                style_commands.append(('BACKGROUND', (0, i), (-1, i), HexColor('#f8f9fa')))
        
        table.setStyle(TableStyle(style_commands))
        elements.append(table)
        elements.append(Spacer(1, 30))
        
        # Análise de variação
        elements.append(Paragraph("<b>Analise de Variacao Mensal da Receita:</b>", ParagraphStyle(
            name='VarTit', fontSize=11, textColor=HexColor('#0a1628'), fontName='Helvetica-Bold'
        )))
        elements.append(Spacer(1, 10))
        
        for i in range(1, len(meses_lista)):
            mes_atual = meses_lista[i]
            mes_anterior = meses_lista[i-1]
            rec_atual = dados_mensais[mes_atual]['receita_bruta']
            rec_anterior = dados_mensais[mes_anterior]['receita_bruta']
            
            if rec_anterior > 0:
                var = ((rec_atual - rec_anterior) / rec_anterior) * 100
                sinal = "+" if var >= 0 else ""
                cor = HexColor('#00d4aa') if var >= 0 else HexColor('#ff6b6b')
                
                var_text = Paragraph(
                    f"{mes_anterior} para {mes_atual}: <b>{sinal}{var:.1f}%</b> (de {formatar_moeda(rec_anterior)} para {formatar_moeda(rec_atual)})",
                    ParagraphStyle(name=f'Var{i}', fontSize=10, textColor=cor)
                )
                elements.append(var_text)
                elements.append(Spacer(1, 5))
        
        elements.append(PageBreak())
        return elements
    
    def _criar_ranking_seguradoras(self, df_seg):
        """Cria ranking de seguradoras"""
        elements = []
        elements.append(Spacer(1, 60))
        elements.append(self._criar_secao_titulo("3. RANKING DE SEGURADORAS", HexColor('#2e86ab')))
        elements.append(Spacer(1, 25))
        
        if df_seg is not None and len(df_seg) > 0:
            headers = ['Pos.', 'Seguradora', 'Total Comissao', 'Qtd. Ops', '% do Total']
            data = [headers]
            
            for i, (_, row) in enumerate(df_seg.head(15).iterrows()):
                data.append([
                    f"{i+1}",
                    str(row['Seguradora'])[:30],
                    formatar_moeda(row['Total']),
                    str(int(row['Qtd'])),
                    f"{row['% do Total']:.1f}%"
                ])
            
            col_widths = [1.2*cm, 7*cm, 3.5*cm, 2*cm, 2.5*cm]
            table = Table(data, colWidths=col_widths)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2e86ab')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
                ('BOX', (0, 0), (-1, -1), 1.5, HexColor('#2e86ab')),
            ]))
            elements.append(table)
        else:
            elements.append(Paragraph("Dados de seguradoras nao disponiveis. Carregue o arquivo Excel com a aba 'ASSERTIF DIRETO'.", self.styles['TextoNormal']))
        
        elements.append(PageBreak())
        return elements
    
    def _criar_distribuicao_socios(self, dados_mensais, totais):
        """Cria seção de distribuição entre sócios"""
        elements = []
        elements.append(Spacer(1, 60))
        elements.append(self._criar_secao_titulo("4. DISTRIBUICAO DE RESULTADOS - SOCIOS", HexColor('#4ea8de')))
        elements.append(Spacer(1, 25))
        
        headers = ['Mes', 'Resultado', 'Partner (65%)', 'Maldivas (35%)']
        data = [headers]
        
        total_resultado = 0
        for mes, d in dados_mensais.items():
            resultado = d['resultado_op']
            total_resultado += resultado
            partner = int(resultado * 0.65)
            maldivas = int(resultado * 0.35)
            data.append([mes, formatar_moeda(resultado), formatar_moeda(partner), formatar_moeda(maldivas)])
        
        partner_total = int(total_resultado * 0.65)
        maldivas_total = int(total_resultado * 0.35)
        data.append(['TOTAL YTD', formatar_moeda(total_resultado), formatar_moeda(partner_total), formatar_moeda(maldivas_total)])
        
        col_widths = [4*cm, 4.5*cm, 4.5*cm, 4*cm]
        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#4ea8de')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
            ('BOX', (0, 0), (-1, -1), 1.5, HexColor('#4ea8de')),
            ('BACKGROUND', (0, -1), (-1, -1), HexColor('#e8f4f8')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 30))
        
        status = "LUCRO" if total_resultado >= 0 else "PREJUIZO"
        cor_status = HexColor('#00d4aa') if total_resultado >= 0 else HexColor('#ff6b6b')
        
        resumo_data = [
            [Paragraph(f"<b>RESUMO DA DISTRIBUICAO YTD 2026</b>", ParagraphStyle(
                name='ResSum', fontSize=14, textColor=colors.white, alignment=TA_CENTER, fontName='Helvetica-Bold'
            ))],
            [Spacer(1, 15)],
            [Paragraph(f"Resultado Total: <b>{formatar_moeda(total_resultado)}</b>", ParagraphStyle(
                name='ResVal', fontSize=12, textColor=colors.white, alignment=TA_CENTER
            ))],
            [Spacer(1, 10)],
            [Paragraph(f"Partner (65%): <b>{formatar_moeda(partner_total)}</b>  |  Maldivas (35%): <b>{formatar_moeda(maldivas_total)}</b>", ParagraphStyle(
                name='ResDist', fontSize=11, textColor=colors.white, alignment=TA_CENTER
            ))],
            [Spacer(1, 10)],
            [Paragraph(f"Status: <b>{status}</b>", ParagraphStyle(
                name='ResStat', fontSize=12, textColor=cor_status, alignment=TA_CENTER, fontName='Helvetica-Bold'
            ))],
            [Spacer(1, 10)],
        ]
        
        resumo_table = Table([[row[0]] for row in resumo_data], colWidths=[17*cm])
        resumo_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), HexColor('#0a1628')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(resumo_table)
        
        elements.append(PageBreak())
        return elements
    
    def _criar_ranking_originadores(self, df_orig):
        """Cria ranking de originadores"""
        elements = []
        elements.append(Spacer(1, 60))
        elements.append(self._criar_secao_titulo("5. RANKING DE ORIGINADORES", HexColor('#00d4aa')))
        elements.append(Spacer(1, 25))
        
        if df_orig is not None and len(df_orig) > 0:
            headers = ['Pos.', 'Originador', 'Total Comissao', 'Operacoes', 'Ticket Medio', '% Total']
            data = [headers]
            
            for i, (_, row) in enumerate(df_orig.head(10).iterrows()):
                data.append([
                    f"{i+1}",
                    str(row['Originador'])[:25],
                    formatar_moeda(row['Total']),
                    str(int(row['Operações'])),
                    formatar_moeda(row['Ticket Médio']),
                    f"{row['% do Total']:.1f}%"
                ])
            
            col_widths = [1.2*cm, 5*cm, 3*cm, 2*cm, 3*cm, 2*cm]
            table = Table(data, colWidths=col_widths)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#00d4aa')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
                ('BOX', (0, 0), (-1, -1), 1.5, HexColor('#00d4aa')),
                ('BACKGROUND', (0, 1), (-1, 1), HexColor('#fffde7')),
                ('BACKGROUND', (0, 2), (-1, 2), HexColor('#f5f5f5')),
                ('BACKGROUND', (0, 3), (-1, 3), HexColor('#fff3e0')),
            ]))
            elements.append(table)
        else:
            elements.append(Paragraph("Dados de originadores nao disponiveis. Carregue o arquivo Excel.", self.styles['TextoNormal']))
        
        elements.append(PageBreak())
        return elements
    
    def _criar_ranking_clientes(self, df_cli):
        """Cria ranking de clientes"""
        elements = []
        elements.append(Spacer(1, 60))
        elements.append(self._criar_secao_titulo("6. RANKING DE CLIENTES", HexColor('#1a3a5c')))
        elements.append(Spacer(1, 25))
        
        if df_cli is not None and len(df_cli) > 0:
            headers = ['Pos.', 'Cliente', 'Total Receita', 'Qtd', '% Total']
            data = [headers]
            
            for i, (_, row) in enumerate(df_cli.head(15).iterrows()):
                data.append([
                    f"{i+1}",
                    str(row['Cliente'])[:35],
                    formatar_moeda(row['Total']),
                    str(int(row['Qtd'])),
                    f"{row['% do Total']:.1f}%"
                ])
            
            col_widths = [1.2*cm, 8*cm, 3.5*cm, 1.5*cm, 2*cm]
            table = Table(data, colWidths=col_widths)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1a3a5c')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
                ('BOX', (0, 0), (-1, -1), 1.5, HexColor('#1a3a5c')),
            ]))
            elements.append(table)
        else:
            elements.append(Paragraph("Dados de clientes nao disponiveis.", self.styles['TextoNormal']))
        
        elements.append(PageBreak())
        return elements
    
    def _criar_analise_produtos(self, df_prod):
        """Cria análise por produto"""
        elements = []
        elements.append(Spacer(1, 60))
        elements.append(self._criar_secao_titulo("7. ANALISE POR TIPO DE PRODUTO", HexColor('#feca57')))
        elements.append(Spacer(1, 25))
        
        if df_prod is not None and len(df_prod) > 0:
            headers = ['Pos.', 'Produto', 'Total Comissao', 'Qtd', '% Total']
            data = [headers]
            
            for i, (_, row) in enumerate(df_prod.iterrows()):
                data.append([
                    f"{i+1}",
                    str(row['Produto'])[:30],
                    formatar_moeda(row['Total']),
                    str(int(row['Qtd'])),
                    f"{row['% do Total']:.1f}%"
                ])
            
            col_widths = [1.2*cm, 7*cm, 4*cm, 2*cm, 2.5*cm]
            table = Table(data, colWidths=col_widths)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#feca57')),
                ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#333333')),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
                ('BOX', (0, 0), (-1, -1), 1.5, HexColor('#feca57')),
            ]))
            elements.append(table)
        else:
            elements.append(Paragraph("Dados de produtos nao disponiveis.", self.styles['TextoNormal']))
        
        elements.append(PageBreak())
        return elements
    
    def _criar_ranking_despesas(self, df_cat):
        """Cria ranking de despesas"""
        elements = []
        elements.append(Spacer(1, 60))
        elements.append(self._criar_secao_titulo("8. RANKING DE DESPESAS", HexColor('#ff6b6b')))
        elements.append(Spacer(1, 25))
        
        if df_cat is not None and len(df_cat) > 0:
            headers = ['Pos.', 'Categoria', 'Total', 'Qtd', '% Total']
            data = [headers]
            
            for i, (_, row) in enumerate(df_cat.head(10).iterrows()):
                data.append([
                    f"{i+1}",
                    str(row['Categoria'])[:35],
                    formatar_moeda(row['Total']),
                    str(int(row['Qtd'])),
                    f"{row['% do Total']:.1f}%"
                ])
            
            col_widths = [1.2*cm, 8*cm, 3.5*cm, 1.5*cm, 2*cm]
            table = Table(data, colWidths=col_widths)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#ff6b6b')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
                ('BOX', (0, 0), (-1, -1), 1.5, HexColor('#ff6b6b')),
            ]))
            elements.append(table)
        else:
            elements.append(Paragraph("Dados de despesas nao disponiveis.", self.styles['TextoNormal']))
        
        elements.append(PageBreak())
        return elements
    
    def _criar_dre_completo(self, totais, dados_mensais):
        """Cria DRE completo"""
        elements = []
        elements.append(Spacer(1, 60))
        elements.append(self._criar_secao_titulo("9. DRE COMPLETO - DEMONSTRATIVO DE RESULTADOS", HexColor('#0a1628')))
        elements.append(Spacer(1, 25))
        
        # Calcular totais
        total_receita = sum(d['receita_bruta'] for d in dados_mensais.values())
        total_custos = sum(d['custos_totais'] for d in dados_mensais.values())
        total_margem = sum(d['margem_contrib'] for d in dados_mensais.values())
        total_despesas = sum(d['despesas'] for d in dados_mensais.values())
        total_resultado = sum(d['resultado_op'] for d in dados_mensais.values())
        
        dre_data = [
            ['DEMONSTRATIVO DE RESULTADOS DO EXERCICIO', 'VALOR YTD'],
            ['', ''],
            ['RECEITA BRUTA TOTAL (Prod. Direta + MAAS)', formatar_moeda(total_receita)],
            ['    Producao Direta', 'R$ 177.797,00'],
            ['    Portal MAAS', 'R$ 275,00'],
            ['', ''],
            ['(-) DEDUCOES DA RECEITA', ''],
            ['    Impostos Diretos', '(R$ 30.990,00)'],
            ['    Custo Operacional (D.A.)', '(R$ 14.820,00)'],
            ['    (+) Co-corretagem', 'R$ 803,00'],
            ['    Rebate AAI', '(R$ 50.646,00)'],
            ['', ''],
            ['(=) CUSTOS TOTAIS', formatar_moeda(total_custos)],
            ['', ''],
            ['(=) MARGEM DE CONTRIBUICAO', formatar_moeda(total_margem)],
            ['', ''],
            ['(-) DESPESAS OPERACIONAIS', ''],
            ['    Despesas', '(R$ 29.104,00)'],
            ['    Folha + Terceiros', '(R$ 16.946,00)'],
            ['', ''],
            ['(=) DESPESAS TOTAIS', formatar_moeda(total_despesas)],
            ['', ''],
            ['(=) RESULTADO OPERACIONAL', formatar_moeda(total_resultado)],
        ]
        
        col_widths = [11*cm, 6*cm]
        table = Table(dre_data, colWidths=col_widths)
        
        style_commands = [
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#0a1628')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('BOX', (0, 0), (-1, -1), 1.5, HexColor('#0a1628')),
        ]
        
        linhas_destaque = [2, 12, 14, 20, 22]
        for linha in linhas_destaque:
            if linha < len(dre_data):
                style_commands.append(('BACKGROUND', (0, linha), (-1, linha), HexColor('#e8f4f8')))
                style_commands.append(('FONTNAME', (0, linha), (-1, linha), 'Helvetica-Bold'))
        
        table.setStyle(TableStyle(style_commands))
        elements.append(table)
        
        elements.append(PageBreak())
        return elements
    
    def _criar_resumo_final(self, totais, dados_mensais):
        """Cria resumo executivo final"""
        elements = []
        elements.append(Spacer(1, 60))
        elements.append(self._criar_secao_titulo("10. RESUMO EXECUTIVO FINAL", HexColor('#0a1628')))
        elements.append(Spacer(1, 25))
        
        total_resultado = sum(d['resultado_op'] for d in dados_mensais.values())
        total_receita = sum(d['receita_bruta'] for d in dados_mensais.values())
        margem = (total_resultado / total_receita * 100) if total_receita > 0 else 0
        partner = int(total_resultado * 0.65)
        maldivas = int(total_resultado * 0.35)
        status = "LUCRO" if total_resultado >= 0 else "PREJUIZO"
        
        resumo_items = [
            ('Periodo Analisado:', 'Janeiro a Abril de 2026'),
            ('Faturamento Total:', formatar_moeda(total_receita)),
            ('Resultado Operacional:', formatar_moeda(total_resultado)),
            ('Margem de Lucro:', f"{margem:.1f}%"),
            ('Distribuicao Partner (65%):', formatar_moeda(partner)),
            ('Distribuicao Maldivas (35%):', formatar_moeda(maldivas)),
            ('Status do Periodo:', status),
        ]
        
        for titulo, valor in resumo_items:
            cor_valor = HexColor('#00d4aa') if 'LUCRO' in valor or valor.startswith('R$') else HexColor('#333333')
            item_data = [[
                Paragraph(f"<b>{titulo}</b>", ParagraphStyle(name='ResFinal1', fontSize=11, textColor=HexColor('#0a1628'))),
                Paragraph(f"<b>{valor}</b>", ParagraphStyle(name='ResFinal2', fontSize=11, textColor=cor_valor, alignment=TA_RIGHT)),
            ]]
            item_table = Table(item_data, colWidths=[10*cm, 7*cm])
            item_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('LINEBELOW', (0, 0), (-1, -1), 1, HexColor('#e0e0e0')),
            ]))
            elements.append(item_table)
        
        elements.append(Spacer(1, 40))
        
        footer_data = [
            [Paragraph("<b>ASSERTIF CORRETORA DE SEGUROS</b>", ParagraphStyle(
                name='FootFinal1', fontSize=14, textColor=colors.white, alignment=TA_CENTER, fontName='Helvetica-Bold'
            ))],
            [Spacer(1, 10)],
            [Paragraph("Dashboard Financeiro - Relatorio Executivo Completo", ParagraphStyle(
                name='FootFinal2', fontSize=11, textColor=colors.white, alignment=TA_CENTER
            ))],
            [Paragraph(f"Documento gerado em {datetime.now().strftime('%d/%m/%Y as %H:%M')}", ParagraphStyle(
                name='FootFinal3', fontSize=10, textColor=colors.white, alignment=TA_CENTER
            ))],
            [Spacer(1, 15)],
            [Paragraph("Maldivas Holding", ParagraphStyle(
                name='FootFinal4', fontSize=10, textColor=HexColor('#7dd3fc'), alignment=TA_CENTER
            ))],
        ]
        
        footer_table = Table([[row[0]] for row in footer_data], colWidths=[17*cm])
        footer_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), HexColor('#0a1628')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(footer_table)
        
        return elements
    
    def gerar_pdf(self, totais, dados_mensais, df_seg=None, df_orig=None, df_cli=None, df_prod=None, df_cat=None):
        """Gera o PDF completo"""
        buffer = io.BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1.5*cm,
            leftMargin=1.5*cm,
            topMargin=2*cm,
            bottomMargin=1.5*cm
        )
        
        elements = []
        
        elements.extend(self._criar_capa(totais))
        elements.extend(self._criar_sumario())
        elements.extend(self._criar_kpis(totais))
        elements.extend(self._criar_evolucao_mensal(dados_mensais))
        elements.extend(self._criar_ranking_seguradoras(df_seg))
        elements.extend(self._criar_distribuicao_socios(dados_mensais, totais))
        elements.extend(self._criar_ranking_originadores(df_orig))
        elements.extend(self._criar_ranking_clientes(df_cli))
        elements.extend(self._criar_analise_produtos(df_prod))
        elements.extend(self._criar_ranking_despesas(df_cat))
        elements.extend(self._criar_dre_completo(totais, dados_mensais))
        elements.extend(self._criar_resumo_final(totais, dados_mensais))
        
        doc.build(elements, onFirstPage=self._criar_cabecalho_rodape, onLaterPages=self._criar_cabecalho_rodape)
        
        buffer.seek(0)
        return buffer.getvalue()


# =============================================================================
# 🎯 APLICAÇÃO STREAMLIT - PROCESSAMENTO DE DADOS CORRIGIDO
# =============================================================================

def main():
    st.set_page_config(
        page_title="Assertif Corretora - Dashboard Financeiro",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
        * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
        .main .block-container { padding: 2rem 3rem; max-width: 1400px; }
        .main-header {
            background: linear-gradient(135deg, #0a1628 0%, #1a3a5c 25%, #2e86ab 50%, #1a3a5c 75%, #0a1628 100%);
            background-size: 400% 400%; animation: gradientShift 8s ease infinite;
            padding: 60px 50px; border-radius: 32px; text-align: center; margin-bottom: 50px;
            box-shadow: 0 30px 80px rgba(10, 22, 40, 0.5); border: 2px solid rgba(255,255,255,0.2);
            position: relative; overflow: hidden;
        }
        @keyframes gradientShift { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
        .main-header h1 { color: white; font-size: 3.8rem; font-weight: 900; text-shadow: 4px 4px 12px rgba(0,0,0,0.4); margin-bottom: 15px; position: relative; z-index: 1; }
        .main-header h2 { color: white; font-size: 1.6rem; font-weight: 500; opacity: 0.95; position: relative; z-index: 1; }
        .main-header .badge { display: inline-block; background: rgba(255,255,255,0.2); padding: 10px 25px; border-radius: 50px; margin-top: 20px; font-size: 1rem; font-weight: 600; color: white; }
        .section-header { padding: 28px 40px; border-radius: 20px; margin: 40px 0 25px 0; box-shadow: 0 15px 45px rgba(0,0,0,0.15); }
        .section-header h2 { color: white; font-size: 1.9rem; font-weight: 800; margin: 0; }
        .legenda-box { background: linear-gradient(135deg, #ffffff 0%, #f0f8ff 100%); border: 3px solid #2e86ab; border-left: 10px solid #2e86ab; border-radius: 20px; padding: 35px 40px; margin: 35px 0; }
        .legenda-box h3 { color: #0a1628; margin-bottom: 25px; font-size: 1.5rem; font-weight: 800; }
        .legenda-item { margin: 12px 0; padding: 15px 20px; border-radius: 14px; border-left: 5px solid; font-size: 1.1rem; line-height: 1.6; }
        .ranking-card { background: white; border-radius: 20px; padding: 25px; margin: 15px 0; box-shadow: 0 10px 30px rgba(0,0,0,0.1); border: 3px solid; }
        .stButton > button { background: linear-gradient(135deg, #0a1628 0%, #1a3a5c 100%); color: white; border: none; padding: 18px 50px; font-size: 1.2rem; font-weight: 800; border-radius: 16px; }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🏆 ASSERTIF CORRETORA</h1>
        <h2>Dashboard Financeiro</h2>
        <div class="badge">📊 YTD Janeiro - Abril 2026 • Versão 7.0</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
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
        uploaded_file = st.file_uploader("Arraste sua planilha Excel aqui", type=['xlsx', 'xls'])
        st.markdown("---")
        st.markdown("### ⚙️ Configurações")
        show_tables = st.checkbox("📋 Mostrar tabelas", value=True)
        show_charts = st.checkbox("📈 Mostrar gráficos", value=True)
    
    # Filtro de período
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0a1628 0%, #1a3a5c 100%); padding: 20px 35px; border-radius: 20px; margin-bottom: 35px;">
        <h3 style="color: white; margin: 0; font-size: 1.4rem; font-weight: 700;">🗓️ SELECIONE O PERÍODO DE ANÁLISE</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col_filtro1, col_filtro2 = st.columns([3, 1])
    with col_filtro1:
        meses_selecionados = st.multiselect("Selecione o(s) mês(es):", ['All', 'Janeiro', 'Fevereiro', 'Março', 'Abril'], default=['All'])
    with col_filtro2:
        if 'All' in meses_selecionados or len(meses_selecionados) == 0:
            st.success("📊 **YTD Completo**")
        else:
            st.info(f"📊 **{', '.join(meses_selecionados)}**")
    
    # Inicializar variáveis
    df_receitas_clean = None
    df_despesas_clean = None
    df_seg = None
    df_prod = None
    df_orig = None
    df_cli = None
    df_cat = None
    dados_mensais_atual = DADOS_MENSAIS.copy()
    
    # Processamento do arquivo
    if uploaded_file is not None:
        try:
            dados = pd.read_excel(uploaded_file, sheet_name=None)
            st.sidebar.success(f"✅ Arquivo carregado com sucesso!")
            st.sidebar.info(f"📄 Abas encontradas: {', '.join(dados.keys())}")
            
            # Processar DRE 2026
            df_dre = dados.get('DRE 2026', pd.DataFrame())
            if len(df_dre) > 0:
                dados_extraidos = extrair_dados_dre(df_dre)
                if dados_extraidos:
                    dados_mensais_atual = dados_extraidos
                    st.sidebar.success("✅ DRE processado!")
            
            # Processar ASSERTIF DIRETO - CORRIGIDO
            df_receitas = dados.get('ASSERTIF DIRETO', pd.DataFrame())
            if len(df_receitas) > 0:
                st.sidebar.success(f"✅ ASSERTIF DIRETO: {len(df_receitas)} linhas")
                
                # Identificar colunas pelo nome (mais robusto)
                colunas = df_receitas.columns.tolist()
                
                # Encontrar índices das colunas importantes
                col_seguradora = None
                col_produto = None
                col_originador = None
                col_cliente = None
                col_comissao = None
                
                for i, col in enumerate(colunas):
                    col_upper = str(col).upper().strip()
                    if 'SEGURADORA' in col_upper:
                        col_seguradora = col
                    elif 'PRODUTO' in col_upper:
                        col_produto = col
                    elif 'ORIGINADOR' in col_upper:
                        col_originador = col
                    elif 'CLIENTE' in col_upper:
                        col_cliente = col
                    elif 'COMISSÃO BRUTA' in col_upper or 'COMISSAO BRUTA' in col_upper:
                        if col_comissao is None:  # Pegar a primeira ocorrência
                            col_comissao = col
                
                # Se não encontrou pelo nome, usar índices padrão
                if col_seguradora is None:
                    col_seguradora = colunas[4] if len(colunas) > 4 else None
                if col_produto is None:
                    col_produto = colunas[10] if len(colunas) > 10 else None
                if col_originador is None:
                    col_originador = colunas[7] if len(colunas) > 7 else None
                if col_cliente is None:
                    col_cliente = colunas[3] if len(colunas) > 3 else None
                if col_comissao is None:
                    col_comissao = colunas[12] if len(colunas) > 12 else None
                
                if col_comissao is not None:
                    # Limpar e converter valores de comissão
                    df_receitas_clean = df_receitas.copy()
                    df_receitas_clean['COMISSAO_CALC'] = df_receitas_clean[col_comissao].apply(converter_valor_brasileiro)
                    df_receitas_clean = df_receitas_clean[df_receitas_clean['COMISSAO_CALC'] > 0]
                    
                    st.sidebar.info(f"💰 {len(df_receitas_clean)} operações com comissão > 0")
                    
                    # Rankings - Seguradoras
                    if col_seguradora is not None:
                        df_seg = df_receitas_clean.groupby(col_seguradora)['COMISSAO_CALC'].agg(['sum', 'count', 'mean']).reset_index()
                        df_seg.columns = ['Seguradora', 'Total', 'Qtd', 'Média']
                        df_seg = df_seg[df_seg['Total'] > 0].sort_values('Total', ascending=False)
                        df_seg['% do Total'] = (df_seg['Total'] / df_seg['Total'].sum() * 100).round(1)
                    
                    # Rankings - Produtos
                    if col_produto is not None:
                        df_prod = df_receitas_clean.groupby(col_produto)['COMISSAO_CALC'].agg(['sum', 'count', 'mean']).reset_index()
                        df_prod.columns = ['Produto', 'Total', 'Qtd', 'Média']
                        df_prod = df_prod[df_prod['Total'] > 0].sort_values('Total', ascending=False)
                        df_prod['% do Total'] = (df_prod['Total'] / df_prod['Total'].sum() * 100).round(1)
                    
                    # Rankings - Originadores
                    if col_originador is not None:
                        df_orig = df_receitas_clean.groupby(col_originador)['COMISSAO_CALC'].agg(['sum', 'count', 'mean']).reset_index()
                        df_orig.columns = ['Originador', 'Total', 'Operações', 'Ticket Médio']
                        df_orig = df_orig[df_orig['Total'] > 0].sort_values('Total', ascending=False)
                        df_orig['% do Total'] = (df_orig['Total'] / df_orig['Total'].sum() * 100).round(1)
                    
                    # Rankings - Clientes
                    if col_cliente is not None:
                        df_cli = df_receitas_clean.groupby(col_cliente)['COMISSAO_CALC'].agg(['sum', 'count', 'mean']).reset_index()
                        df_cli.columns = ['Cliente', 'Total', 'Qtd', 'Média']
                        df_cli = df_cli[df_cli['Total'] > 0].sort_values('Total', ascending=False)
                        df_cli['% do Total'] = (df_cli['Total'] / df_cli['Total'].sum() * 100).round(1)
            
            # Processar DESPESAS - CORRIGIDO
            df_despesas = dados.get('DESPESAS', pd.DataFrame())
            if len(df_despesas) > 0:
                st.sidebar.success(f"✅ DESPESAS: {len(df_despesas)} linhas")
                
                colunas_desp = df_despesas.columns.tolist()
                
                # Encontrar colunas de valor e categoria
                col_valor_desp = None
                col_categoria = None
                
                for i, col in enumerate(colunas_desp):
                    col_upper = str(col).upper().strip()
                    if col_valor_desp is None and i == 4:  # Coluna E (índice 4)
                        col_valor_desp = col
                    if col_categoria is None and i == 5:  # Coluna F (índice 5)
                        col_categoria = col
                
                if col_valor_desp is not None and col_categoria is not None:
                    df_despesas_clean = df_despesas.dropna(subset=[col_valor_desp])
                    df_despesas_clean = df_despesas_clean.copy()
                    df_despesas_clean['VALOR_CALC'] = df_despesas_clean[col_valor_desp].apply(converter_valor_brasileiro)
                    df_despesas_clean = df_despesas_clean[df_despesas_clean['VALOR_CALC'] > 0]
                    
                    df_cat = df_despesas_clean.groupby(col_categoria)['VALOR_CALC'].agg(['sum', 'count']).reset_index()
                    df_cat.columns = ['Categoria', 'Total', 'Qtd']
                    df_cat = df_cat[df_cat['Total'] > 0].sort_values('Total', ascending=False)
                    df_cat['% do Total'] = (df_cat['Total'] / df_cat['Total'].sum() * 100).round(1)
                    
                    st.sidebar.info(f"💸 {len(df_cat)} categorias de despesas")
        
        except Exception as e:
            st.sidebar.error(f"❌ Erro ao processar arquivo: {str(e)}")
    
    # Calcular totais com os dados disponíveis
    totais, meses_ativos = calcular_dados_filtrados(meses_selecionados, dados_mensais_atual)
    
    # KPIs
    st.markdown("""<div class="section-header" style="background: linear-gradient(135deg, #0a1628 0%, #1a3a5c 100%);"><h2>💰 INDICADORES PRINCIPAIS (KPIs)</h2></div>""", unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(criar_cartao_kpi_html("FATURAMENTO", formatar_moeda(totais['receita_bruta']), "", "#0a1628", "💰"), unsafe_allow_html=True)
    with col2:
        st.markdown(criar_cartao_kpi_html("CUSTOS TOTAIS", formatar_moeda(totais['custos_totais']), "", "#ff6b6b", "📉"), unsafe_allow_html=True)
    with col3:
        st.markdown(criar_cartao_kpi_html("MARGEM CONTRIB.", formatar_moeda(totais['margem_contrib']), "", "#2e86ab", "📊"), unsafe_allow_html=True)
    with col4:
        st.markdown(criar_cartao_kpi_html("DESPESAS TOTAIS", formatar_moeda(totais['despesas']), "", "#feca57", "💸"), unsafe_allow_html=True)
    with col5:
        cor_resultado = "#00d4aa" if totais['resultado_op'] >= 0 else "#ff6b6b"
        st.markdown(criar_cartao_kpi_html("RESULTADO OPER.", formatar_moeda(totais['resultado_op']), "", cor_resultado, "🎯"), unsafe_allow_html=True)
    
    # Legenda
    st.markdown("""
    <div class="legenda-box">
        <h3>📌 Legenda dos Indicadores</h3>
        <div style="color: #0a1628; font-size: 1.1rem; line-height: 2.2;">
            <div class="legenda-item" style="background: rgba(10, 22, 40, 0.1); border-color: #0a1628;"><strong style="color: #0a1628;">💰 Faturamento Bruto:</strong> Soma da Receita Bruta de Produção Direta e Portal MAAS</div>
            <div class="legenda-item" style="background: rgba(255, 107, 107, 0.1); border-color: #ff6b6b;"><strong style="color: #ff6b6b;">📉 Custos Totais:</strong> Impostos Diretos + Custo Operacional (D.A.) + Rebate AAI - Co-corretagem</div>
            <div class="legenda-item" style="background: rgba(46, 134, 171, 0.1); border-color: #2e86ab;"><strong style="color: #2e86ab;">📊 Margem de Contribuição:</strong> Faturamento Bruto menos Custos Totais</div>
            <div class="legenda-item" style="background: rgba(254, 202, 87, 0.1); border-color: #feca57;"><strong style="color: #e0a800;">💸 Despesas Totais:</strong> Despesas Operacionais + Folha + Terceiros</div>
            <div class="legenda-item" style="background: rgba(0, 212, 170, 0.1); border-color: #00d4aa;"><strong style="color: #00d4aa;">🎯 Resultado Operacional:</strong> Margem de Contribuição - Despesas • Base para distribuição 65/35</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Gráficos de evolução
    if show_charts:
        st.markdown("""<div class="section-header" style="background: linear-gradient(135deg, #1a3a5c 0%, #2e86ab 100%);"><h2>📈 EVOLUÇÃO MENSAL - RECEITA vs RESULTADO</h2></div>""", unsafe_allow_html=True)
        
        meses = list(dados_mensais_atual.keys())
        receita_bruta = [dados_mensais_atual[m]['receita_bruta'] for m in meses]
        resultado_op_mensal = [dados_mensais_atual[m]['resultado_op'] for m in meses]
        
        crescimento = [0]
        for i in range(1, len(receita_bruta)):
            if receita_bruta[i-1] > 0:
                crescimento.append(round(((receita_bruta[i] - receita_bruta[i-1]) / receita_bruta[i-1]) * 100, 1))
            else:
                crescimento.append(0)
        
        azul_claro = '#7dd3fc'
        fig_evolucao = make_subplots(rows=1, cols=3, subplot_titles=('<b>Receita Bruta</b>', '<b>Crescimento Mensal (%)</b>', '<b>Resultado Operacional</b>'), horizontal_spacing=0.08)
        
        fig_evolucao.add_trace(go.Bar(x=meses, y=receita_bruta, marker=dict(color=azul_claro, line=dict(width=3, color='white')), text=[f"R$ {v/1000:.1f}K" for v in receita_bruta], textposition='outside', textfont=dict(size=14, color='#0a1628')), row=1, col=1)
        fig_evolucao.add_trace(go.Scatter(x=meses, y=crescimento, mode='lines+markers+text', line=dict(color=azul_claro, width=4), marker=dict(size=18, color=azul_claro, line=dict(width=3, color='white')), text=[f"{v:+.1f}%" for v in crescimento], textposition='top center', textfont=dict(size=13, color='#0a1628')), row=1, col=2)
        fig_evolucao.add_hline(y=0, line_dash="dash", line_color="#ff6b6b", line_width=2, row=1, col=2)
        fig_evolucao.add_trace(go.Bar(x=meses, y=resultado_op_mensal, marker=dict(color=azul_claro, line=dict(width=3, color='white')), text=[f"R$ {v/1000:.1f}K" for v in resultado_op_mensal], textposition='outside', textfont=dict(size=14, color='#0a1628')), row=1, col=3)
        fig_evolucao.add_hline(y=0, line_dash="solid", line_color="#ff6b6b", line_width=2, row=1, col=3)
        
        fig_evolucao.update_layout(height=500, showlegend=False, paper_bgcolor='white', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=50, r=50, t=80, b=50))
        fig_evolucao.update_xaxes(gridcolor='#e8e8e8')
        fig_evolucao.update_yaxes(gridcolor='#e8e8e8')
        st.plotly_chart(fig_evolucao, use_container_width=True)
    
    # Distribuição Sócios
    if show_charts:
        st.markdown("""<div class="section-header" style="background: linear-gradient(135deg, #2e86ab 0%, #4ea8de 100%);"><h2>🤝 DISTRIBUIÇÃO DE RESULTADOS - SÓCIOS</h2></div>""", unsafe_allow_html=True)
        
        resultado_dist = [dados_mensais_atual[m]['resultado_op'] for m in meses]
        partner = [int(r * 0.65) for r in resultado_dist]
        maldivas = [int(r * 0.35) for r in resultado_dist]
        
        fig_dist = go.Figure()
        fig_dist.add_trace(go.Bar(name='Partner (65%)', x=meses, y=partner, marker_color='#0a1628', text=[f"R$ {v/1000:.1f}K" for v in partner], textposition='outside'))
        fig_dist.add_trace(go.Bar(name='Maldivas (35%)', x=meses, y=maldivas, marker_color='#4ea8de', text=[f"R$ {v/1000:.1f}K" for v in maldivas], textposition='outside'))
        fig_dist.add_trace(go.Scatter(name='Resultado Total', x=meses, y=resultado_dist, mode='lines+markers', line=dict(color='#00d4aa', width=3, dash='dot'), marker=dict(size=12)))
        fig_dist.add_hline(y=0, line_dash="solid", line_color="#ff6b6b", line_width=2)
        fig_dist.update_layout(height=500, barmode='group', paper_bgcolor='white', plot_bgcolor='rgba(0,0,0,0)', legend=dict(orientation='h', y=-0.15, x=0.5, xanchor='center'))
        st.plotly_chart(fig_dist, use_container_width=True)
        
        total_resultado = sum(resultado_dist)
        partner_total = int(total_resultado * 0.65)
        maldivas_total = int(total_resultado * 0.35)
        
        cor_box = "#00d4aa" if total_resultado >= 0 else "#ff6b6b"
        status_txt = "LUCRO" if total_resultado >= 0 else "PREJUÍZO"
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {cor_box} 0%, {cor_box}dd 100%); padding: 25px; border-radius: 16px; margin: 20px 0;">
            <div style="display: flex; justify-content: center; align-items: center; flex-wrap: wrap; gap: 30px; color: white;">
                <div style="text-align: center;"><div style="font-size: 0.9rem; opacity: 0.9;">Resultado Total</div><div style="font-size: 1.5rem; font-weight: 900;">{formatar_moeda(total_resultado)}</div></div>
                <div style="text-align: center;"><div style="font-size: 0.9rem; opacity: 0.9;">Partner (65%)</div><div style="font-size: 1.3rem; font-weight: 700;">{formatar_moeda(partner_total)}</div></div>
                <div style="text-align: center;"><div style="font-size: 0.9rem; opacity: 0.9;">Maldivas (35%)</div><div style="font-size: 1.3rem; font-weight: 700;">{formatar_moeda(maldivas_total)}</div></div>
                <div style="text-align: center;"><div style="font-size: 0.9rem; opacity: 0.9;">Status</div><div style="font-size: 1.3rem; font-weight: 900;">{status_txt}</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # RANKINGS - SEGURADORAS
    if show_tables and df_seg is not None and len(df_seg) > 0:
        st.markdown("""<div class="section-header" style="background: linear-gradient(135deg, #2e86ab 0%, #4ea8de 100%);"><h2>🏢 RANKING DE SEGURADORAS</h2></div>""", unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.dataframe(df_seg.head(15), use_container_width=True, hide_index=True)
        with col2:
            fig_seg = px.pie(df_seg.head(8), values='Total', names='Seguradora', hole=0.4, color_discrete_sequence=CORES['chart_colors'])
            fig_seg.update_layout(height=400, showlegend=True, legend=dict(orientation='h', y=-0.1))
            st.plotly_chart(fig_seg, use_container_width=True)
    
    # RANKINGS - ORIGINADORES
    if show_tables and df_orig is not None and len(df_orig) > 0:
        st.markdown("""<div class="section-header" style="background: linear-gradient(135deg, #00d4aa 0%, #00b894 100%);"><h2>👤 RANKING DE ORIGINADORES</h2></div>""", unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.dataframe(df_orig.head(10), use_container_width=True, hide_index=True)
        with col2:
            fig_orig = px.bar(df_orig.head(5), x='Total', y='Originador', orientation='h', color='Total', color_continuous_scale='Teal')
            fig_orig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_orig, use_container_width=True)
    
    # RANKINGS - CLIENTES
    if show_tables and df_cli is not None and len(df_cli) > 0:
        st.markdown("""<div class="section-header" style="background: linear-gradient(135deg, #1a3a5c 0%, #2e86ab 100%);"><h2>👥 RANKING DE CLIENTES</h2></div>""", unsafe_allow_html=True)
        st.dataframe(df_cli.head(15), use_container_width=True, hide_index=True)
    
    # RANKINGS - PRODUTOS
    if show_tables and df_prod is not None and len(df_prod) > 0:
        st.markdown("""<div class="section-header" style="background: linear-gradient(135deg, #feca57 0%, #f39c12 100%);"><h2>📦 ANÁLISE POR PRODUTO</h2></div>""", unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.dataframe(df_prod, use_container_width=True, hide_index=True)
        with col2:
            fig_prod = px.pie(df_prod, values='Total', names='Produto', hole=0.3, color_discrete_sequence=CORES['chart_colors'])
            fig_prod.update_layout(height=400)
            st.plotly_chart(fig_prod, use_container_width=True)
    
    # RANKINGS - DESPESAS
    if show_tables and df_cat is not None and len(df_cat) > 0:
        st.markdown("""<div class="section-header" style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a5a 100%);"><h2>💸 RANKING DE DESPESAS</h2></div>""", unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.dataframe(df_cat.head(10), use_container_width=True, hide_index=True)
        with col2:
            fig_desp = px.bar(df_cat.head(8), x='Total', y='Categoria', orientation='h', color='Total', color_continuous_scale='Reds')
            fig_desp.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_desp, use_container_width=True)
    
    # Exportar PDF
    st.markdown("---")
    st.markdown("""<div class="section-header" style="background: linear-gradient(135deg, #00d4aa 0%, #00b894 100%);"><h2>📥 EXPORTAR DASHBOARD COMPLETO PARA PDF</h2></div>""", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📄 GERAR PDF COMPLETO E PERFEITO", type="primary", use_container_width=True):
            with st.spinner("Gerando PDF completo..."):
                try:
                    pdf_gen = PDFDashboardCompleto()
                    pdf_bytes = pdf_gen.gerar_pdf(totais, dados_mensais_atual, df_seg, df_orig, df_cli, df_prod, df_cat)
                    st.success("✅ PDF gerado com sucesso!")
                    st.download_button("⬇️ BAIXAR PDF COMPLETO", data=pdf_bytes, file_name=f"Assertif_Dashboard_Completo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf", mime="application/pdf", use_container_width=True)
                except Exception as e:
                    st.error(f"❌ Erro: {str(e)}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0a1628 0%, #1a3a5c 50%, #2e86ab 100%); padding: 50px; border-radius: 28px; text-align: center; margin-top: 50px; color: white;">
        <span style="font-size: 4rem; display: block; margin-bottom: 20px;">📊</span>
        <h2 style="margin-bottom: 15px; font-size: 2rem; font-weight: 900;">ASSERTIF CORRETORA</h2>
        <h3 style="margin-bottom: 20px; font-weight: 600; opacity: 0.95;">Dashboard Financeiro</h3>
        <p style="opacity: 0.9; font-size: 1.1rem;">Versão 7.0 | YTD 2026 | Status: LUCRO</p>
        <div style="margin-top: 30px; padding: 15px 30px; background: rgba(255,255,255,0.1); border-radius: 50px; display: inline-block;">
            <span style="font-size: 0.95rem;">✨ Maldivas Holding ✨</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
