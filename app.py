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
# MAPEAMENTO PRECISO DAS LINHAS DA ABA 'DRE 2026':
# - Linha 4 (índice 2): RECEITA BRUTA TOTAL (P. MAAS + DIRETO)
# - Linha 8 (índice 6): IMPOSTOS DIRETOS
# - Linha 9 (índice 7): CUSTO OPERACIONAL (D.A)
# - Linha 10 (índice 8): CO-CORRETAGEM
# - Linha 11 (índice 9): REBATE AAI
# - Linha 12 (índice 10): MARGEM DE CONTRIBUIÇÃO (Prod. Direta)
# - Linha 13 (índice 11): DESPESAS
# - Linha 14 (índice 12): FOLHA+TERCEIROS
# - Linha 22 (índice 20): MARGEM DE CONTRIBUIÇÃO (Portal MAAS)
# - Linha 27 (índice 25): RESULTADO OPERACIONAL (Total)
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
        'despesas': 15064,
        'resultado_op': 7667
    },
    'Março': {
        'receita_bruta': 71946,
        'custos_totais': 39509,
        'margem_contrib': 32437,
        'despesas': 15746,
        'resultado_op': 16690
    },
    'Abril': {
        'receita_bruta': 17075,
        'custos_totais': 8758,
        'margem_contrib': 8317,
        'despesas': 17016,
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
    mapeamento EXATO dos índices das linhas.
    
    MAPEAMENTO PRECISO DAS LINHAS (índice baseado em 0 a partir da linha B2):
    =========================================================================
    - Índice 2:  RECEITA BRUTA TOTAL (P. MAAS + DIRETO) → Linha 4 Excel
    - Índice 6:  IMPOSTOS DIRETOS                       → Linha 8 Excel
    - Índice 7:  CUSTO OPERACIONAL (D.A)                → Linha 9 Excel
    - Índice 8:  CO-CORRETAGEM                          → Linha 10 Excel
    - Índice 9:  REBATE AAI                             → Linha 11 Excel
    - Índice 10: MARGEM DE CONTRIBUIÇÃO (Prod. Direta)  → Linha 12 Excel
    - Índice 11: DESPESAS                               → Linha 13 Excel
    - Índice 12: FOLHA+TERCEIROS                        → Linha 14 Excel
    - Índice 20: MARGEM DE CONTRIBUIÇÃO (Portal MAAS)   → Linha 22 Excel
    - Índice 25: RESULTADO OPERACIONAL (Total)          → Linha 27 Excel
    =========================================================================
    """
    dados_extraidos = {}
    
    # Mapear colunas para meses (coluna 1=Jan, 2=Fev, 3=Mar, 4=Abr, etc.)
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
    
    # =========================================================================
    # 🎯 ÍNDICES EXATOS DAS LINHAS NA DRE (baseado no array da planilha)
    # =========================================================================
    LINHA_RECEITA_BRUTA_TOTAL = 2      # RECEITA BRUTA TOTAL (P. MAAS + DIRETO)
    LINHA_IMPOSTOS_DIRETOS = 6         # IMPOSTOS DIRETOS
    LINHA_CUSTO_OP_DA = 7              # CUSTO OPERACIONAL (D.A)
    LINHA_CO_CORRETAGEM = 8            # CO-CORRETAGEM
    LINHA_REBATE_AAI = 9               # REBATE AAI
    LINHA_MARGEM_CONTRIB_DIRETA = 10   # MARGEM DE CONTRIBUIÇÃO (Prod. Direta)
    LINHA_DESPESAS = 11                # DESPESAS
    LINHA_FOLHA_TERCEIROS = 12         # FOLHA+TERCEIROS
    LINHA_MARGEM_CONTRIB_MAAS = 20     # MARGEM DE CONTRIBUIÇÃO (Portal MAAS)
    LINHA_RESULTADO_OP = 25            # RESULTADO OPERACIONAL (Linha 27)
    
    try:
        # Converter DataFrame para array se necessário
        if hasattr(df_dre, 'values'):
            dados = df_dre.values
        else:
            dados = df_dre
        
        # Verificar se temos dados suficientes
        if len(dados) < 26:
            print(f"⚠️ Aviso: DataFrame tem apenas {len(dados)} linhas, esperado >= 26")
            return None
        
        def get_valor(linha_idx, col_idx):
            """
            🔢 Extrai valor numérico de uma célula específica com tratamento robusto
            """
            try:
                if linha_idx < len(dados) and col_idx < len(dados[linha_idx]):
                    val = dados[linha_idx][col_idx]
                    
                    # Tratar valores nulos ou vazios
                    if val is None or val == '' or val == ' ' or (isinstance(val, str) and val.strip() == ''):
                        return 0
                    
                    # Se já é número, retornar diretamente
                    if isinstance(val, (int, float)):
                        if pd.isna(val):
                            return 0
                        return float(val)
                    
                    # Tentar converter string para número
                    val_str = str(val).replace(',', '.').replace(' ', '').replace('R$', '').strip()
                    if val_str == '' or val_str == '-' or val_str.lower() == 'nan':
                        return 0
                    
                    return float(val_str)
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
            receita_bruta = get_valor(LINHA_RECEITA_BRUTA_TOTAL, col_idx)
            
            # Só adiciona o mês se tiver receita > 0
            if receita_bruta > 0:
                # Extrair valores das linhas específicas
                impostos = abs(get_valor(LINHA_IMPOSTOS_DIRETOS, col_idx))
                custo_da = abs(get_valor(LINHA_CUSTO_OP_DA, col_idx))
                co_corretagem = get_valor(LINHA_CO_CORRETAGEM, col_idx)  # Positivo (reduz custos)
                rebate = abs(get_valor(LINHA_REBATE_AAI, col_idx))
                
                # Margem de contribuição combinada (Prod. Direta + Portal MAAS)
                margem_direta = get_valor(LINHA_MARGEM_CONTRIB_DIRETA, col_idx)
                margem_maas = get_valor(LINHA_MARGEM_CONTRIB_MAAS, col_idx)
                margem_contrib = margem_direta + margem_maas
                
                # Despesas (valores absolutos, pois são negativos na planilha)
                despesas_op = abs(get_valor(LINHA_DESPESAS, col_idx))
                folha_terceiros = abs(get_valor(LINHA_FOLHA_TERCEIROS, col_idx))
                despesas_total = despesas_op + folha_terceiros
                
                # RESULTADO OPERACIONAL (Linha 27) - ESTE É O VALOR CHAVE!
                # Pode ser negativo (prejuízo)
                resultado_op = get_valor(LINHA_RESULTADO_OP, col_idx)
                
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
        # 📊 LOG DE VALIDAÇÃO (para debug)
        # =========================================================================
        if dados_extraidos:
            print(f"\n{'='*60}")
            print(f"✅ DADOS EXTRAÍDOS COM SUCESSO DA DRE 2026")
            print(f"{'='*60}")
            print(f"📅 Meses encontrados: {len(dados_extraidos)}")
            print(f"{'─'*60}")
            for mes, valores in dados_extraidos.items():
                status = "🟢 LUCRO" if valores['resultado_op'] >= 0 else "🔴 PREJUÍZO"
                print(f"  {mes:12} | Receita: R$ {valores['receita_bruta']:>12,.2f} | "
                      f"Resultado: R$ {valores['resultado_op']:>12,.2f} | {status}")
            print(f"{'='*60}\n")
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
