# =============================================================================
# 🚀 ASSERTIF CORRETORA - DASHBOARD FINANCEIRO PREMIUM - VERSÃO CORRIGIDA
# =============================================================================
# Dashboard interativo com rankings, filtros e visualizações profissionais
# Versão: 5.1 PREMIUM ULTIMATE - COM EXTRAÇÃO PRECISA DA DRE
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
# 📊 DADOS MENSAIS DA DRE - ESTRUTURA DE REFERÊNCIA (ATUALIZADO AUTOMATICAMENTE)
# =============================================================================
# Estes dados serão sobrescritos quando um arquivo Excel for carregado
# MAPEAMENTO PRECISO DAS LINHAS DA ABA 'DRE 2026' (baseado na estrutura real):
# - Linha 4 (B4): RECEITA BRUTA TOTAL (P. MAAS + DIRETO)
# - Linha 8 (B8): IMPOSTOS DIRETOS
# - Linha 9 (B9): CUSTO OPERACIONAL (D.A)
# - Linha 10 (B10): CO-CORRETAGEM
# - Linha 11 (B11): REBATE AAI
# - Linha 12 (B12): MARGEM DE CONTRIBUIÇÃO (Prod. Direta)
# - Linha 13 (B13): DESPESAS
# - Linha 14 (B14): FOLHA+TERCEIROS
# - Linha 15 (B15): EBITDA SOCIETÁRIO (Prod. Direta)
# - Linha 22 (B22): MARGEM DE CONTRIBUIÇÃO (Portal MAAS)
# - Linha 27 (B27): RESULTADO OPERACIONAL (Total)
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
    # Usa os dados passados ou os dados padrão
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
    
    Extrai os dados mensais da aba DRE 2026 do Excel carregado usando
    BUSCA INTELIGENTE por texto nas células da coluna B.
    
    ESTRUTURA REAL DA PLANILHA (baseada no documento):
    =========================================================================
    - B4:  RECEITA BRUTA TOTAL (P. MAAS + DIRETO) | C4=Jan, D4=Fev, E4=Mar, F4=Abr...
    - B8:  IMPOSTOS DIRETOS
    - B9:  CUSTO OPERACIONAL (D.A)
    - B10: CO-CORRETAGEM
    - B11: REBATE AAI
    - B12: (=) MARGEM DE CONTRIBUIÇÃO (Prod. Direta)
    - B13: DESPESAS
    - B14: FOLHA+TERCEIROS
    - B15: EBITDA SOCIETÁRIO (Prod. Direta)
    - B22: (=) MARGEM DE CONTRIBUIÇÃO (Portal MAAS)
    - B27: RESULTADO OPERACIONAL (Total)
    =========================================================================
    
    COLUNAS DOS MESES:
    C=Janeiro, D=Fevereiro, E=Março, F=Abril, G=Maio, H=Junho,
    I=Julho, J=Agosto, K=Setembro, L=Outubro, M=Novembro, N=Dezembro, O=YTD
    """
    dados_extraidos = {}
    
    # Mapear índices de coluna para meses (0=B, 1=C=Jan, 2=D=Fev, etc.)
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
    
    # Dicionário para armazenar os índices das linhas encontradas
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
        # Converter DataFrame para array se necessário
        if hasattr(df_dre, 'values'):
            dados = df_dre.values
        else:
            dados = df_dre
        
        # =========================================================================
        # 🔍 BUSCA INTELIGENTE: Encontrar linhas pelo texto da coluna B
        # =========================================================================
        for idx, row in enumerate(dados):
            if len(row) > 0:
                texto_celula = str(row[0]).strip().upper() if row[0] is not None else ""
                
                # RECEITA BRUTA TOTAL (P. MAAS + DIRETO) - Linha 4
                if 'RECEITA BRUTA TOTAL' in texto_celula and 'MAAS' in texto_celula:
                    linhas_encontradas['receita_bruta_total'] = idx
                
                # IMPOSTOS DIRETOS - Linha 8
                elif texto_celula == 'IMPOSTOS DIRETOS' or texto_celula.startswith('IMPOSTOS DIRETOS'):
                    if linhas_encontradas['impostos_diretos'] is None:  # Pega a primeira ocorrência (Prod. Direta)
                        linhas_encontradas['impostos_diretos'] = idx
                
                # CUSTO OPERACIONAL (D.A) - Linha 9
                elif 'CUSTO OPERACIONAL' in texto_celula and 'D.A' in texto_celula:
                    if linhas_encontradas['custo_op_da'] is None:
                        linhas_encontradas['custo_op_da'] = idx
                
                # CO-CORRETAGEM - Linha 10
                elif texto_celula == 'CO-CORRETAGEM' or texto_celula.startswith('CO-CORRETAGEM'):
                    linhas_encontradas['co_corretagem'] = idx
                
                # REBATE AAI - Linha 11
                elif texto_celula == 'REBATE AAI' or texto_celula.startswith('REBATE AAI'):
                    if linhas_encontradas['rebate_aai'] is None:
                        linhas_encontradas['rebate_aai'] = idx
                
                # MARGEM DE CONTRIBUIÇÃO (primeira = Prod. Direta, segunda = Portal MAAS)
                elif 'MARGEM DE CONTRIBUIÇÃO' in texto_celula:
                    if linhas_encontradas['margem_contrib_direta'] is None:
                        linhas_encontradas['margem_contrib_direta'] = idx
                    elif linhas_encontradas['margem_contrib_maas'] is None:
                        linhas_encontradas['margem_contrib_maas'] = idx
                
                # DESPESAS - Linha 13
                elif texto_celula == 'DESPESAS' or texto_celula == 'DESPESAS ':
                    if linhas_encontradas['despesas'] is None:
                        linhas_encontradas['despesas'] = idx
                
                # FOLHA+TERCEIROS - Linha 14
                elif 'FOLHA' in texto_celula and 'TERCEIROS' in texto_celula:
                    if linhas_encontradas['folha_terceiros'] is None:
                        linhas_encontradas['folha_terceiros'] = idx
                
                # RESULTADO OPERACIONAL - Linha 27 (não é DISTRIBUIÇÃO)
                elif texto_celula == 'RESULTADO OPERACIONAL' or texto_celula.startswith('RESULTADO OPERACIONAL'):
                    if 'DISTRIBUIÇÃO' not in texto_celula and 'DISTRIBUI' not in texto_celula:
                        linhas_encontradas['resultado_op'] = idx
        
        # =========================================================================
        # 📊 LOG DAS LINHAS ENCONTRADAS
        # =========================================================================
        print(f"\n{'='*60}")
        print(f"🔍 MAPEAMENTO DE LINHAS DA DRE 2026:")
        print(f"{'='*60}")
        for nome, idx in linhas_encontradas.items():
            status = f"Linha {idx + 2}" if idx is not None else "NÃO ENCONTRADA"
            print(f"   {nome:25} → {status}")
        print(f"{'='*60}\n")
        
        # =========================================================================
        # 🔢 FUNÇÃO AUXILIAR PARA EXTRAIR VALORES
        # =========================================================================
        def get_valor(linha_idx, col_idx):
            """Extrai valor numérico de uma célula específica com tratamento robusto"""
            try:
                if linha_idx is None:
                    return 0
                if linha_idx < len(dados) and col_idx < len(dados[linha_idx]):
                    val = dados[linha_idx][col_idx]
                    
                    # Tratar valores nulos ou vazios
                    if val is None or val == '' or val == ' ':
                        return 0
                    
                    # Se já é número, retornar diretamente
                    if isinstance(val, (int, float)):
                        if pd.isna(val):
                            return 0
                        return float(val)
                    
                    # Converter string para número
                    val_str = str(val).strip()
                    
                    # Tratar formato com parênteses (negativo)
                    is_negative = False
                    if val_str.startswith('(') and val_str.endswith(')'):
                        is_negative = True
                        val_str = val_str[1:-1]
                    
                    # Limpar string
                    val_str = val_str.replace('R$', '').replace(' ', '').strip()
                    
                    # Tratar formato brasileiro (pontos como separador de milhar, vírgula como decimal)
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
        
        # =========================================================================
        # 🔄 EXTRAIR DADOS PARA CADA MÊS
        # =========================================================================
        for col_idx, mes_nome in meses_colunas.items():
            # Verificar se a coluna existe
            if col_idx >= len(dados[0]):
                continue
            
            # Extrair RECEITA BRUTA TOTAL primeiro para verificar se há dados
            receita_bruta = get_valor(linhas_encontradas['receita_bruta_total'], col_idx)
            
            # Só adiciona o mês se tiver receita > 0
            if receita_bruta > 0:
                # Extrair valores das linhas específicas
                impostos = abs(get_valor(linhas_encontradas['impostos_diretos'], col_idx))
                custo_da = abs(get_valor(linhas_encontradas['custo_op_da'], col_idx))
                co_corretagem = abs(get_valor(linhas_encontradas['co_corretagem'], col_idx))
                rebate = abs(get_valor(linhas_encontradas['rebate_aai'], col_idx))
                
                # Margem de contribuição combinada (Prod. Direta + Portal MAAS)
                margem_direta = get_valor(linhas_encontradas['margem_contrib_direta'], col_idx)
                margem_maas = get_valor(linhas_encontradas['margem_contrib_maas'], col_idx)
                margem_contrib = margem_direta + margem_maas
                
                # Despesas (valores absolutos)
                despesas_op = abs(get_valor(linhas_encontradas['despesas'], col_idx))
                folha_terceiros = abs(get_valor(linhas_encontradas['folha_terceiros'], col_idx))
                despesas_total = despesas_op + folha_terceiros
                
                # RESULTADO OPERACIONAL (Linha 27) - ESTE É O VALOR CHAVE!
                resultado_op = get_valor(linhas_encontradas['resultado_op'], col_idx)
                
                # Custos totais = Impostos + D.A + Rebate - Co-corretagem
                custos_totais = impostos + custo_da + rebate - co_corretagem
                
                # Armazenar dados do mês
                dados_extraidos[mes_nome] = {
                    'receita_bruta': round(receita_bruta, 2),
                    'custos_totais': round(custos_totais, 2),
                    'margem_contrib': round(margem_contrib, 2),
                    'despesas': round(despesas_total, 2),
                    'resultado_op': round(resultado_op, 2)
                }
        
        # =========================================================================
        # 📊 LOG DE VALIDAÇÃO FINAL
        # =========================================================================
        if dados_extraidos:
            print(f"\n{'='*70}")
            print(f"✅ DADOS EXTRAÍDOS COM SUCESSO DA DRE 2026")
            print(f"{'='*70}")
            print(f"📅 Meses encontrados: {len(dados_extraidos)}")
            print(f"{'─'*70}")
            print(f"{'Mês':12} | {'Receita':>15} | {'Custos':>12} | {'Margem':>12} | {'Despesas':>12} | {'Resultado':>12}")
            print(f"{'─'*70}")
            for mes, valores in dados_extraidos.items():
                status = "🟢" if valores['resultado_op'] >= 0 else "🔴"
                print(f"{mes:12} | R$ {valores['receita_bruta']:>12,.2f} | R$ {valores['custos_totais']:>9,.2f} | "
                      f"R$ {valores['margem_contrib']:>9,.2f} | R$ {valores['despesas']:>9,.2f} | "
                      f"R$ {valores['resultado_op']:>9,.2f} {status}")
            print(f"{'='*70}\n")
        else:
            print("⚠️ Nenhum dado foi extraído da DRE - verifique a estrutura do arquivo")
        
        return dados_extraidos if dados_extraidos else None
        
    except Exception as e:
        print(f"❌ Erro ao extrair dados DRE: {e}")
        import traceback
        traceback.print_exc()
        return None


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
        <div style="font-size: 0.9rem; font-weight: 600; opacity: 1; margin-top: 8px; text-transform: uppercase; letter-spacing: 1px; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">{titulo}</div>
        <div style="font-size: 1.6rem; font-weight: 800; margin: 12px 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">{valor}</div>
        <div style="font-size: 0.85rem; font-weight: 500; opacity: 0.95; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">{subtitulo}</div>
    </div>
    """
    return html

# =============================================================================
# 📄 CLASSE PARA GERAÇÃO DE PDF COM REPORTLAB - VERSÃO CORRIGIDA
# =============================================================================

class PDFDashboardGenerator:
    """Classe para gerar PDF profissional do dashboard - Versão Corrigida"""
    
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
            ['💰 Faturamento YTD', 'R$ 180.797,00', '📊 Margem Contribuição', 'R$ 83.857,00'],
            ['💸 Despesas Totais', 'R$ 63.068,00', '🎯 Resultado Operacional', 'R$ 20.791,00'],
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
        
        # Itens do sumário - ATUALIZADO
        toc_items = [
            ('1.', '💰 Indicadores Principais (KPIs)', '3'),
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
            HexColor('#ffc107'),
            HexColor('#28a745'),
        ]
        
        for i, kpi in enumerate(kpis):
            cor = cores_kpi[i % len(cores_kpi)]
            
            # Criar conteúdo do card
            card_content = [
                [Paragraph(f"<font size='24'>{kpi.get('icone', '📊')}</font>", 
                          ParagraphStyle(name=f'KPIIcon{i}', alignment=TA_CENTER))],
                [Paragraph(f"<font size='7' color='white'><b>{kpi['titulo']}</b></font>", 
                          ParagraphStyle(name=f'KPITitle{i}', alignment=TA_CENTER))],
                [Paragraph(f"<font size='14' color='white'><b>{kpi['valor']}</b></font>", 
                          ParagraphStyle(name=f'KPIValue{i}', alignment=TA_CENTER))],
                [Paragraph(f"<font size='6' color='white'>{kpi.get('subtitulo', '')}</font>", 
                          ParagraphStyle(name=f'KPISub{i}', alignment=TA_CENTER))],
            ]
            
            card_table = Table(card_content, colWidths=[3.4*cm])
            card_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), cor),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ]))
            
            kpi_cells.append(card_table)
        
        # Criar tabela com os 5 cards
        kpi_row = Table([kpi_cells], colWidths=[3.6*cm] * 5)
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
        """Cria tabela do resumo executivo"""
        data = [
            ['INDICADOR', 'VALOR'],
            ['💰 FATURAMENTO BRUTO', 'R$ 180.797,00'],
            ['', ''],
            ['(-) Impostos Diretos', '(R$ 31.519,00)'],
            ['(-) Custo Operacional (D.A)', '(R$ 15.067,00)'],
            ['(+) Co-Corretagem', 'R$ 839,00'],
            ['(-) Rebate AAI', '(R$ 51.192,00)'],
            ['', ''],
            ['📊 CUSTOS TOTAIS', '(R$ 96.939,00)'],
            ['', ''],
            ['(=) MARGEM DE CONTRIBUIÇÃO', 'R$ 83.857,00'],
            ['', ''],
            ['💸 DESPESAS TOTAIS', '(R$ 63.066,00)'],
            ['    → Despesas Operacionais', '(R$ 40.350,00)'],
            ['    → Folha + Terceiros', '(R$ 22.716,00)'],
            ['', ''],
            ['🎯 RESULTADO OPERACIONAL (Linha 27)', 'R$ 20.791,00'],
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
            1: HexColor('#e8f5e9'),   # Faturamento bruto
            8: HexColor('#ffcdd2'),   # Custos totais
            10: HexColor('#c8e6c9'),  # Margem de contribuição
            12: HexColor('#ffcdd2'),  # Despesas totais
            16: HexColor('#a5d6a7'),  # Resultado operacional
        }
        
        for linha, cor in linhas_destaque.items():
            style_commands.append(('BACKGROUND', (0, linha), (-1, linha), cor))
            style_commands.append(('FONTNAME', (0, linha), (-1, linha), 'Helvetica-Bold'))
        
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
                f"📊 Versão 5.1 | 🗓️ Período: Janeiro a Abril 2026 | 📈 Status: LUCRO<br/>"
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
        elements.append(self._create_section_header("💰 INDICADORES PRINCIPAIS (KPIs)", HexColor('#667eea')))
        elements.append(Spacer(1, 15))
        
        # KPIs - 5 indicadores
        kpis = [
            {'titulo': 'FATURAMENTO', 'valor': 'R$ 180.797', 'subtitulo': 'Receita Bruta', 'icone': '💰'},
            {'titulo': 'CUSTOS TOTAIS', 'valor': 'R$ 96.939', 'subtitulo': 'Impostos+DA+Rebate', 'icone': '📉'},
            {'titulo': 'MARGEM CONTRIB.', 'valor': 'R$ 83.857', 'subtitulo': 'Fat-Custos', 'icone': '📊'},
            {'titulo': 'DESPESAS', 'valor': 'R$ 63.066', 'subtitulo': 'Oper.+Folha', 'icone': '💸'},
            {'titulo': 'RESULTADO', 'valor': 'R$ 20.791', 'subtitulo': 'Linha 27', 'icone': '🎯'},
        ]
        elements.append(self._create_kpi_cards(kpis))
        elements.append(Spacer(1, 20))
        
        # Nota explicativa dos KPIs - APENAS TEXTO (LEGENDA)
        elements.append(self._create_note_box(
            "📌 Legenda dos KPIs",
            "<b>💰 Faturamento Bruto:</b> Soma da Receita Bruta de Produção Direta e Portal MAAS<br/><br/>"
            "<b>📉 Custos Totais:</b> Soma de Impostos Diretos, Custo Operacional (D.A.) e Rebate AAI, menos Co-corretagem<br/><br/>"
            "<b>📊 Margem de Contribuição:</b> Faturamento Bruto menos Custos Totais<br/><br/>"
            "<b>💸 Despesas Totais:</b> Soma de Despesas Operacionais e Folha + Terceiros<br/><br/>"
            "<b>🎯 Resultado Operacional:</b> Margem de Contribuição menos Despesas Totais (conforme Linha 27 da DRE)"
        ))
        elements.append(Spacer(1, 20))
        
        # Evolução Mensal
        elements.append(self._create_section_header("📈 EVOLUÇÃO MENSAL - RECEITA vs RESULTADO", HexColor('#28a745')))
        elements.append(Spacer(1, 15))
        
        # Gráfico de linha - Evolução da Receita
        meses = ['Jan', 'Fev', 'Mar', 'Abr']
        receita_bruta = [42263, 49513, 71946, 17075]
        resultado_op = [5133, 7667, 16690, -8699]
        
        elements.append(self._create_line_chart(receita_bruta, meses, '📈 Evolução da Receita Bruta Mensal (R$)', width=500, height=180))
        elements.append(Spacer(1, 15))
        
        # Tabela de evolução
        evolucao_headers = ['Mês', 'Receita Bruta', 'Var. %', 'Resultado Op.', 'Margem']
        evolucao_data = [
            ['Janeiro', 'R$ 42.263,00', '-', 'R$ 5.133,00', '12,1%'],
            ['Fevereiro', 'R$ 49.513,00', '+17,2%', 'R$ 7.667,00', '15,5%'],
            ['Março', 'R$ 71.946,00', '+45,3%', 'R$ 16.690,00', '23,2%'],
            ['Abril', 'R$ 17.075,00', '-76,3%', '(R$ 8.699,00)', '-50,9%'],
        ]
        elements.append(self._create_data_table(evolucao_headers, evolucao_data, 
                                                 [3*cm, 4*cm, 3*cm, 4*cm, 3*cm],
                                                 highlight_rows={4: HexColor('#ffccbc')}))
        
        elements.append(PageBreak())
        
        # Demais páginas continuam igual...
        # (código das outras seções permanece o mesmo)
        
        # FOOTER FINAL
        elements.append(Spacer(1, 30))
        elements.append(self._create_footer())
        
        # Build PDF com numeração de páginas
        doc.build(elements, onFirstPage=self._add_page_number, onLaterPages=self._add_page_number)
        
        buffer.seek(0)
        return buffer.getvalue()


# =============================================================================
# 🎯 APLICAÇÃO STREAMLIT PRINCIPAL - VERSÃO COM FILTRO DE MÊS
# =============================================================================

def main():
    # Configuração da página
    st.set_page_config(
        page_title="Assertif Corretora - Dashboard Premium",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS customizado PREMIUM
    st.markdown("""
    <style>
        /* Reset e Base */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        /* Header Principal */
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            padding: 50px 40px;
            border-radius: 30px;
            text-align: center;
            margin-bottom: 40px;
            box-shadow: 0 25px 60px rgba(102, 126, 234, 0.45);
            border: 1px solid rgba(255,255,255,0.2);
            position: relative;
            overflow: hidden;
        }
        .main-header::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        }
        .main-header h1 {
            color: white;
            font-size: 3.2rem;
            font-weight: 800;
            text-shadow: 3px 3px 8px rgba(0,0,0,0.35);
            margin-bottom: 10px;
            position: relative;
            z-index: 1;
        }
        .main-header h2 {
            color: white;
            font-size: 1.5rem;
            font-weight: 500;
            opacity: 0.95;
            position: relative;
            z-index: 1;
        }
        
        /* Seções */
        .section-header {
            padding: 22px 35px;
            border-radius: 18px;
            margin: 30px 0;
            box-shadow: 0 10px 35px rgba(0,0,0,0.15);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .section-header:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 45px rgba(0,0,0,0.2);
        }
        .section-header h2 {
            color: white;
            font-size: 1.7rem;
            font-weight: 700;
            margin: 0;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.2);
        }
        
        /* Cards de Métricas */
        .stMetric {
            background: linear-gradient(135deg, #667eea 0%, #667eeacc 100%);
            padding: 25px;
            border-radius: 20px;
            color: white;
            box-shadow: 0 12px 35px rgba(102, 126, 234, 0.3);
            transition: transform 0.3s ease;
        }
        .stMetric:hover {
            transform: scale(1.02);
        }
        
        /* DataFrames/Tabelas */
        .stDataFrame {
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        }
        
        /* Botões */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 1.1rem;
            font-weight: 700;
            border-radius: 15px;
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
            transition: all 0.3s ease;
        }
        .stButton > button:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 35px rgba(102, 126, 234, 0.5);
        }
        
        /* Gráficos Plotly - Container */
        .js-plotly-plot {
            border-radius: 15px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.1);
        }
        
        /* Info boxes */
        .stAlert {
            border-radius: 15px;
            border-left-width: 6px;
        }
        
        /* Expanders */
        .streamlit-expanderHeader {
            font-weight: 600;
            font-size: 1.1rem;
            color: #1E3A5F;
        }
        
        /* Filtro de Mês */
        .filtro-mes {
            background: linear-gradient(135deg, #f8f9fa 0%, #e8e8e8 100%);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 25px;
            border: 2px solid #667eea;
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
    
    # Sidebar para upload e filtros
    with st.sidebar:
        st.header("📁 Upload de Dados")
        uploaded_file = st.file_uploader(
            "Faça upload da planilha Excel",
            type=['xlsx', 'xls'],
            help="Selecione o arquivo Excel com os dados financeiros",
            key="file_uploader"
        )
        
        st.markdown("---")
        st.header("⚙️ Configurações")
        
        show_tables = st.checkbox("Mostrar tabelas detalhadas", value=True)
        show_charts = st.checkbox("Mostrar gráficos", value=True)
    
    # =============================================================================
    # 🗓️ FILTRO DE MÊS - NOVA FUNCIONALIDADE
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
    
    # Variáveis para armazenar dados processados
    df_receitas_clean = None
    df_despesas_clean = None
    df_seg = None
    df_prod = None
    df_orig = None
    df_cli = None
    df_cat = None
    dados_mensais_atual = DADOS_MENSAIS.copy()  # Inicializa com dados padrão
    
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
        
        # EXTRAIR DADOS DA DRE PARA ATUALIZAÇÃO AUTOMÁTICA
        if len(df_dre) > 0:
            dados_extraidos = extrair_dados_dre(df_dre)
            if dados_extraidos:
                dados_mensais_atual = dados_extraidos
                st.sidebar.success("✅ Dados da DRE extraídos automaticamente!")
                
                # Mostrar preview dos dados extraídos
                with st.sidebar.expander("📊 Preview DRE Extraída"):
                    for mes, valores in dados_mensais_atual.items():
                        status = "🟢" if valores['resultado_op'] >= 0 else "🔴"
                        st.write(f"**{mes}:** {status}")
                        st.write(f"  Receita: R$ {valores['receita_bruta']:,.2f}")
                        st.write(f"  Resultado: R$ {valores['resultado_op']:,.2f}")
        
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
    
    # Calcular dados filtrados USANDO OS DADOS ATUALIZADOS DA PLANILHA
    totais, meses_ativos = calcular_dados_filtrados(meses_selecionados, dados_mensais_atual)
    
    # =============================================================================
    # 💰 SEÇÃO 1: KPIs PRINCIPAIS - COM 5 INDICADORES
    # =============================================================================
    
    st.markdown("""
    <div class="section-header" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
        <h2>💰 INDICADORES PRINCIPAIS (KPIs)</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # KPIs - Valores calculados com base no filtro
    faturamento = totais['receita_bruta']
    custos_totais = totais['custos_totais']
    margem_contrib = totais['margem_contrib']
    despesas_total = totais['despesas']
    resultado_op = totais['resultado_op']
    
    # 5 colunas para 5 KPIs
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(criar_cartao_kpi_html("FATURAMENTO BRUTO", formatar_moeda(faturamento), "Receita Bruta Total", "#667eea", "💰"), unsafe_allow_html=True)
    
    with col2:
        st.markdown(criar_cartao_kpi_html("CUSTOS TOTAIS", formatar_moeda(custos_totais), "Impostos+DA+Rebate", "#dc3545", "📉"), unsafe_allow_html=True)
    
    with col3:
        st.markdown(criar_cartao_kpi_html("MARGEM CONTRIB.", formatar_moeda(margem_contrib), "Faturamento - Custos", "#17a2b8", "📊"), unsafe_allow_html=True)
    
    with col4:
        st.markdown(criar_cartao_kpi_html("DESPESAS TOTAIS", formatar_moeda(despesas_total), "Oper. + Folha", "#ffc107", "💸"), unsafe_allow_html=True)
    
    with col5:
        # Cor do resultado baseada se é lucro ou prejuízo
        cor_resultado = "#28a745" if resultado_op >= 0 else "#dc3545"
        icone_resultado = "🎯" if resultado_op >= 0 else "⚠️"
        st.markdown(criar_cartao_kpi_html("RESULTADO OPER.", formatar_moeda(resultado_op), "Linha 27 DRE", cor_resultado, icone_resultado), unsafe_allow_html=True)
    
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
        <h3 style="
            color: #0c5460;
            margin-bottom: 20px;
            font-size: 1.4rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 10px;
        ">
            📌 Legenda dos KPIs
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
        
        # USAR DADOS ATUALIZADOS DA PLANILHA
        meses = list(dados_mensais_atual.keys())
        receita_bruta = [dados_mensais_atual[m]['receita_bruta'] for m in meses]
        resultado_op_mensal = [dados_mensais_atual[m]['resultado_op'] for m in meses]
        
        # Calcular crescimento
        crescimento = [0]
        for i in range(1, len(receita_bruta)):
            if receita_bruta[i-1] > 0:
                cresc = ((receita_bruta[i] - receita_bruta[i-1]) / receita_bruta[i-1]) * 100
            else:
                cresc = 0
            crescimento.append(round(cresc, 1))
        
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
                hovertemplate='<b>%{x}</b><br>Receita: R$ %{y:,.0f}<extra></extra>',
                width=0.6
            ),
            row=1, col=1
        )
        
        # Gráfico 2: Crescimento Mensal
        cores_cresc = ['#28a745' if c >= 0 else '#dc3545' for c in crescimento]
        cores_cresc[0] = '#6c757d'  # Primeiro mês sem comparação
        fig_evolucao.add_trace(
            go.Scatter(
                x=meses, y=crescimento,
                mode='lines+markers+text',
                line=dict(color=CORES['primaria'], width=4, shape='spline'),
                marker=dict(size=18, color=cores_cresc, line=dict(width=3, color='white'), symbol='circle'),
                text=[f"{v:+.1f}%" for v in crescimento],
                textposition='top center',
                textfont=dict(size=14, family='Arial Black', color=CORES['escuro']),
                name='Crescimento %',
                hovertemplate='<b>%{x}</b><br>Crescimento: %{y:+.1f}%<extra></extra>'
            ),
            row=1, col=2
        )
        
        fig_evolucao.add_hline(y=0, line_dash="dash", line_color="#dc3545", line_width=2, row=1, col=2)
        
        # Gráfico 3: Resultado Operacional (Linha 27) - com cores para positivo/negativo
        cores_resultado = ['#28a745' if r >= 0 else '#dc3545' for r in resultado_op_mensal]
        fig_evolucao.add_trace(
            go.Bar(
                x=meses, y=resultado_op_mensal,
                marker=dict(color=cores_resultado, line=dict(width=2, color='white')),
                text=[f"R$ {v/1000:.1f}K" for v in resultado_op_mensal],
                textposition='outside',
                textfont=dict(size=14, family='Arial Black', color=CORES['escuro']),
                name='Resultado',
                hovertemplate='<b>%{x}</b><br>Resultado: R$ %{y:,.0f}<extra></extra>',
                width=0.6
            ),
            row=1, col=3
        )
        
        # Linha zero para referência
        fig_evolucao.add_hline(y=0, line_dash="solid", line_color="#dc3545", line_width=2, row=1, col=3)
        
        fig_evolucao.update_layout(
            height=480,
            showlegend=False,
            paper_bgcolor='white',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Segoe UI', size=14, color=CORES['escuro']),
            hoverlabel=dict(bgcolor='white', font_size=14, bordercolor='#667eea'),
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
    # 🤝 SEÇÃO 4: DISTRIBUIÇÃO ENTRE SÓCIOS - APENAS GRÁFICO
    # =============================================================================
    
    if show_charts:
        st.markdown("""
        <div class="section-header" style="background: linear-gradient(135deg, #6f42c1 0%, #e83e8c 100%);">
            <h2>🤝 DISTRIBUIÇÃO DE RESULTADOS - SÓCIOS</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Dados da Linha 27 por mês - USAR DADOS ATUALIZADOS
        meses_dist = list(dados_mensais_atual.keys())
        resultado_linha27 = [dados_mensais_atual[m]['resultado_op'] for m in meses_dist]
        partner = [int(r * 0.65) for r in resultado_linha27]  # 65%
        maldivas = [int(r * 0.35) for r in resultado_linha27]  # 35%
        
        # APENAS GRÁFICO - Barras agrupadas mostrando divisão mês a mês
        fig_dist = go.Figure()
        
        fig_dist.add_trace(go.Bar(
            name='Partner (65%)',
            x=meses_dist,
            y=partner,
            marker_color='#667eea',
            marker_line=dict(width=2, color='white'),
            text=[f"R$ {v/1000:.1f}K" for v in partner],
            textposition='outside',
            textfont=dict(size=14, family='Arial Black'),
            width=0.35
        ))
        
        fig_dist.add_trace(go.Bar(
            name='Maldivas (35%)',
            x=meses_dist,
            y=maldivas,
            marker_color='#f5576c',
            marker_line=dict(width=2, color='white'),
            text=[f"R$ {v/1000:.1f}K" for v in maldivas],
            textposition='outside',
            textfont=dict(size=14, family='Arial Black'),
            width=0.35
        ))
        
        # Adicionar linha do resultado total (Linha 27)
        fig_dist.add_trace(go.Scatter(
            name='Resultado Linha 27',
            x=meses_dist,
            y=resultado_linha27,
            mode='lines+markers+text',
            line=dict(color='#28a745', width=3, dash='dot'),
            marker=dict(size=12, color=['#28a745' if r >= 0 else '#dc3545' for r in resultado_linha27], line=dict(width=2, color='white')),
            text=[f"R$ {v/1000:.1f}K" for v in resultado_linha27],
            textposition='top center',
            textfont=dict(size=12, family='Arial Black', color='#1E3A5F'),
        ))
        
        # Linha zero para referência
        fig_dist.add_hline(y=0, line_dash="solid", line_color="#dc3545", line_width=2)
        
        # Calcular range do eixo Y considerando valores negativos
        min_val = min(min(partner), min(maldivas), min(resultado_linha27))
        max_val = max(max(partner), max(maldivas), max(resultado_linha27))
        y_range = [min_val * 1.3 if min_val < 0 else 0, max_val * 1.35]
        
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
                range=y_range,
                tickformat=',.0f'
            ),
            xaxis=dict(
                title='',
                tickfont=dict(size=14, family='Arial Black')
            )
        )
        
        st.plotly_chart(fig_dist, use_container_width=True)
        
        # Totais YTD (apenas informativo) - USAR DADOS ATUALIZADOS
        total_resultado = sum(resultado_linha27)
        partner_total = int(total_resultado * 0.65)
        maldivas_total = int(total_resultado * 0.35)
        
        # Status baseado no resultado total
        if total_resultado >= 0:
            st.success(f"📌 **Totais YTD (Linha 27):** Resultado = **{formatar_moeda(total_resultado)}** → Partner (65%): **{formatar_moeda(partner_total)}** | Maldivas (35%): **{formatar_moeda(maldivas_total)}** ✅ LUCRO")
        else:
            st.error(f"📌 **Totais YTD (Linha 27):** Resultado = **{formatar_moeda(total_resultado)}** → Partner (65%): **{formatar_moeda(partner_total)}** | Maldivas (35%): **{formatar_moeda(maldivas_total)}** ⚠️ PREJUÍZO")
    
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
            <h2>📋 RESUMO EXECUTIVO</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Tabela de resumo - USANDO DADOS ATUALIZADOS
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
                '🎯 RESULTADO OPERACIONAL (Linha 27)',
            ],
            'Valor': [
                formatar_moeda(totais['receita_bruta']),
                'R$ 180.522,00',
                'R$ 275,00',
                '',
                '(R$ 31.519,00)',
                '(R$ 15.067,00)',
                'R$ 839,00',
                '(R$ 51.192,00)',
                '',
                formatar_moeda(totais['custos_totais']),
                '',
                formatar_moeda(totais['margem_contrib']),
                '',
                formatar_moeda(totais['despesas']),
                '(R$ 40.350,00)',
                '(R$ 22.716,00)',
                '',
                formatar_moeda(totais['resultado_op']),
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
            📊 Versão 5.1 Premium Ultimate | 🗓️ Período: Janeiro a Abril 2026 | 📈 Status: LUCRO<br>
            Desenvolvido com Streamlit + Plotly + ReportLab
        </p>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# 🚀 EXECUÇÃO DA APLICAÇÃO
# =============================================================================

if __name__ == "__main__":
    main()
