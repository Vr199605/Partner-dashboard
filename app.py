 > 5 else 0
            
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
                    font=dict(size=20, family='Inter', color='#1a1a2e', weight='bold'), 
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
                            <div style="font-size: 1.3rem; font-weight: 800; color: #1a1a2e; margin-bottom: 8px;">{row['Originador']}</div>
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
        <div class="section-header" style="background: linear-gradient(135deg, #00d4aa 0%, #54a0ff 100%);">
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
            textfont=dict(size=12, family='Inter', color='#1a1a2e'),
            hovertemplate='<b>%{y}</b><br>Receita: R$ %{x:,.2f}<extra></extra>', 
            width=0.7
        ))
        
        fig_ranking_cli.update_layout(
            title=dict(
                text='🏢 Top 15 Clientes por Volume de Receita', 
                font=dict(size=22, family='Inter', color='#1a1a2e', weight='bold'), 
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
            textfont=dict(size=14, family='Inter', color='#1a1a2e'),
            hovertemplate='<b>%{x}</b><br>Valor: R$ %{y:,.2f}<extra></extra>', 
            width=0.7
        ))
        
        fig_desp_bar.update_layout(
            title=dict(
                text='📊 Top 10 Categorias de Despesas', 
                font=dict(size=22, family='Inter', color='#1a1a2e', weight='bold'), 
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
        <div class="section-header" style="background: linear-gradient(135deg, #1a1a2e 0%, #2d3a87 100%);">
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
                '🎯 RESULTADO OPERACIONAL (Linha 27)',
            ],
            'Valor': [
                formatar_moeda(totais['receita_bruta']),
                'R$ 180.522,00',
                'R$ 275,00',
                '',
                '(R$ 31.465,00)',
                '(R$ 15.045,00)',
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
            with st.spinner("🎬 Gerando PDF Oscar Edition..."):
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
                    
                    st.success("✅ PDF Oscar Edition gerado com sucesso!")
                    
                    st.download_button(
                        label="⬇️ BAIXAR PDF OSCAR EDITION",
                        data=pdf_bytes,
                        file_name=f"Assertif_Dashboard_Oscar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    
                except Exception as e:
                    st.error(f"❌ Erro ao gerar PDF: {str(e)}")
                    st.info("💡 Verifique se todas as bibliotecas estão instaladas corretamente.")
    
    # =========================================================================
    # 🎬 FOOTER OSCAR EDITION
    # =========================================================================
    st.markdown("---")
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1a1a2e 0%, #2d3a87 50%, #667eea 100%);
        padding: 50px;
        border-radius: 28px;
        text-align: center;
        margin-top: 50px;
        color: white;
        box-shadow: 0 25px 70px rgba(26, 26, 46, 0.5);
    ">
        <span style="font-size: 4rem; display: block; margin-bottom: 20px;">🏆</span>
        <h2 style="margin-bottom: 15px; font-size: 2rem; font-weight: 900;">ASSERTIF CORRETORA</h2>
        <h3 style="margin-bottom: 20px; font-weight: 600; opacity: 0.95;">Dashboard Financeiro Premium - Oscar Edition</h3>
        <p style="opacity: 0.9; font-size: 1.1rem; line-height: 1.8;">
            📊 Versão 6.0 Oscar Edition | 🗓️ Período: Janeiro a Abril 2026 | 📈 Status: LUCRO<br/>
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
            <span style="font-size: 0.95rem;">✨ Uma apresentação digna de Oscar ✨</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# 🚀 EXECUÇÃO DA APLICAÇÃO
# =============================================================================

if __name__ == "__main__":
    main()
