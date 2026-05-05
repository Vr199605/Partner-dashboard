import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
from datetime import datetime

# ReportLab
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.colors import HexColor


# =========================
# UTIL
# =========================
def formatar_moeda(valor):
    try:
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return str(valor)


def criar_cartao_kpi_html(titulo, valor, subtitulo="", cor="#667eea", icone="📊"):
    return f"""
    <div style="
        background: {cor};
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
    ">
        <div style="font-size: 25px;">{icone}</div>
        <div>{titulo}</div>
        <div style="font-size: 22px; font-weight: bold;">{valor}</div>
        <div>{subtitulo}</div>
    </div>
    """
    class PDFDashboardGenerator:

    def __init__(self):
        self.styles = getSampleStyleSheet()

    def _create_resumo(self):
        data = [
            ['INDICADOR', 'VALOR'],
            ['💰 RECEITA BRUTA TOTAL', 'R$ 180.797,00'],
            ['Despesas', '(R$ 29.104,00)'],
            ['🎯 RESULTADO OPERACIONAL TOTAL', 'R$ 37.807,00'],
            [' RESULTADO OPERACIONAL - DISTRIBUIÇÃO', 'R$ 35.266,00'],
            [' Sócio Partner', 'R$ 24.575,00'],
            [' Sócio Maldivas', 'R$ 10.691,00'],
        ]

        table = Table(data, colWidths=[14*cm, 10*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), HexColor('#667eea')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),

            # MELHORIA VISUAL
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, HexColor('#f4f6fb')]),
        ]))

        return table

    def generate(self):
        buffer = io.BytesIO()

        # ✅ PDF HORIZONTAL
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4)
        )

        elements = []

        elements.append(Paragraph("ASSERTIF CORRETORA - DASHBOARD", self.styles['Title']))
        elements.append(Spacer(1, 20))
        elements.append(self._create_resumo())

        doc.build(elements)
        buffer.seek(0)

        return buffer.getvalue()
def main():
    st.set_page_config(layout="wide")

    st.markdown("""
    <h1 style='text-align: center;'>📊 ASSERTIF CORRETORA</h1>
    """, unsafe_allow_html=True)

    # KPIs
    faturamento_ytd = 180797
    despesas = 29104
    margem = 21
    ebitda = 37807

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(criar_cartao_kpi_html(
            "FATURAMENTO YTD",
            formatar_moeda(faturamento_ytd),
            "Jan - Abr 2026",
            "#667eea",
            "💰"
        ), unsafe_allow_html=True)

    with col2:
        # ✅ ALTERADO PARA DESPESAS
        st.markdown(criar_cartao_kpi_html(
            "DESPESAS",
            formatar_moeda(despesas),
            "Custos totais",
            "#dc3545",
            "💸"
        ), unsafe_allow_html=True)

    with col3:
        st.markdown(criar_cartao_kpi_html(
            "MARGEM",
            f"{margem}%",
            "Status",
            "#17a2b8",
            "📊"
        ), unsafe_allow_html=True)

    with col4:
        st.markdown(criar_cartao_kpi_html(
            "EBITDA",
            formatar_moeda(ebitda),
            "Resultado",
            "#764ba2",
            "🎯"
        ), unsafe_allow_html=True)

    st.markdown("---")

    if st.button("📄 GERAR PDF"):
        pdf = PDFDashboardGenerator().generate()

        st.download_button(
            label="⬇️ Baixar PDF",
            data=pdf,
            file_name=f"dashboard_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf"
        )


if __name__ == "__main__":
    main()
