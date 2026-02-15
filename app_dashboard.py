
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium

# Importar módulos do projeto
from modulos.parametrizacao import ParametrosLogistica
from modulos.otimizacao_espacial import OtimizacaoEspacial
from modulos.analise_cenarios import AnaliseCenarios
from modulos.simulacao_estocastica import SimulacaoMonteCarlo


# Configuração da Página
st.set_page_config(
    page_title="Fulô do Açaí - Decisão Logística",
    page_icon="🫐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo Customizado (CSS) - Dark Mode & Premium UI
st.markdown("""
<style>
    /* Global Styles */
    .main {
        background-color: #0e1117;
    }
    h1, h2, h3 {
        color: #f0f2f6 !important;
    }
    p, label, .stMarkdown {
        color: #c4c4c4 !important;
    }
    
    /* Card KPI Customizado - Design Glassmorphism */
    div.kpi-card {
        background-color: #1f2937;
        border: 1px solid #374151;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s;
    }
    div.kpi-card:hover {
        transform: translateY(-2px);
        border-color: #6366f1;
    }
    div.kpi-title {
        color: #9ca3af;
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }
    div.kpi-value {
        color: #f3f4f6;
        font-size: 1.875rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }
    div.kpi-delta-pos {
        color: #34d399; /* Green */
        font-size: 0.875rem;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    div.kpi-delta-neg {
        color: #f87171; /* Red */
        font-size: 0.875rem;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    
    /* Ajustes no Sidebar */
    [data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #374151;
    }
    
    /* Botões */
    div.stButton > button {
        background: linear-gradient(45deg, #4f46e5, #6366f1);
        color: white;
        border: none;
        box-shadow: 0 4px 14px 0 rgba(99, 102, 241, 0.39);
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button:hover {
        background: linear-gradient(45deg, #4338ca, #4f46e5);
        transform: scale(1.02);
    }
</style>
""", unsafe_allow_html=True)

# Título Principal
st.title("🫐 Painel Estratégico de Logística - Fulô do Açaí")
st.markdown("### Etapa 2: Análise de Risco e Viabilidade Sob Incerteza")
st.markdown("---")

# Inicializar Estado da Sessão
if 'simulacoes' not in st.session_state:
    st.session_state['simulacoes'] = []
if 'lojas_extras' not in st.session_state:
    st.session_state['lojas_extras'] = []
if 'fabricas_extras' not in st.session_state:
    st.session_state['fabricas_extras'] = []
if 'coords_selecionadas' not in st.session_state:
    st.session_state['coords_selecionadas'] = None

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2921/2921226.png", width=100)
    
    # --- Gestão de Lojas ---
    st.header("🏪 Lista de Lojas Extras")
    
    if st.session_state['lojas_extras']:
        # Mostrar tabela de lojas extras
        df_extras = pd.DataFrame(st.session_state['lojas_extras'])
        st.dataframe(df_extras[['nome', 'demanda_media_dia']], use_container_width=True, hide_index=True)
        
        if st.button("🗑️ Limpar Lojas Extras"):
            st.session_state['lojas_extras'] = []
            st.session_state['coords_selecionadas'] = None
            st.rerun()
    else:
        st.info("Nenhuma loja adicional cadastrada.")
        
    st.divider()
    st.header("🏭 Lista de Fábricas Extras")
    if st.session_state['fabricas_extras']:
        df_fab = pd.DataFrame(st.session_state['fabricas_extras'])
        st.dataframe(df_fab[['nome']], use_container_width=True, hide_index=True)
        
        if st.button("🗑️ Limpar Fábricas Extras"):
            st.session_state['fabricas_extras'] = []
            st.session_state['coords_selecionadas'] = None
            st.rerun()
    else:
        st.info("Nenhuma fábrica adicional cadastrada.")
    
    st.markdown("---")
    
    # --- Configuração da Simulação ---
    st.header("⚙️ Configuração da Simulação")
    
    # Nome do Cenário para Comparação
    st.markdown("### 🏷️ Identificação")
    nome_cenario = st.text_input("Nome do Cenário", f"Simulação {len(st.session_state['simulacoes']) + 1}")
    
    st.subheader("📊 Incerteza (Variáveis Estocásticas)")
    desvio_padrao_pct = st.slider("Variabilidade da Demanda (CV%)", 5, 50, 20, 5, help="Coeficiente de Variação (Sigma/Média)") / 100.0
    lead_time_medio = st.slider("Lead Time Médio (dias)", 1, 7, 1)
    lead_time_var = st.slider("Incerteza do Lead Time (dias)", 0, 3, 0, help="Desvio padrão do tempo de entrega")
    
    st.subheader("🎯 Nível de Serviço")
    nivel_servico_alvo = st.slider("Meta de Nível de Serviço (%)", 85, 99, 95) / 100.0
    
    st.markdown("---")
    
    # Botão de Execução
    if st.button("🚀 Executar e Registrar", type="primary", use_container_width=True):
        with st.spinner('Simulando e registrando cenário...'):
            # Inicialização dos parâmetros COM lojas e fábricas extras
            params = ParametrosLogistica(
                lojas_adicionais=st.session_state['lojas_extras'],
                fabricas_adicionais=st.session_state['fabricas_extras']
            )
            params.operacional['lead_time_reposicao_dias'] = lead_time_medio

            # Simulação
            simulador = SimulacaoMonteCarlo(params, desvio_padrao_pct, lead_time_medio, lead_time_var)
            resultados_a = simulador.rodar_cenario(com_galpao=False, iteracoes=100)
            resultados_b = simulador.rodar_cenario(com_galpao=True, iteracoes=100)
            
            # Salvar no Histórico
            novo_registro = {
                'id': len(st.session_state['simulacoes']),
                'nome': nome_cenario,
                'params': {
                    'var_demanda': desvio_padrao_pct,
                    'lead_time': lead_time_medio,
                    'var_lead_time': lead_time_var,
                    'num_lojas': 2 + len(st.session_state['lojas_extras'])
                },
                'resultados_a': resultados_a,
                'resultados_b': resultados_b
            }
            st.session_state['simulacoes'].append(novo_registro)
            st.success(f"Cenário '{nome_cenario}' registrado com sucesso!")

# Inicialização dos parâmetros (uso geral)
params = ParametrosLogistica(
    lojas_adicionais=st.session_state['lojas_extras'],
    fabricas_adicionais=st.session_state['fabricas_extras']
)
params.operacional['lead_time_reposicao_dias'] = lead_time_medio

# Layout Principal em Abas
tab1, tab2, tab3, tab4 = st.tabs(["📊 Comparativo de Cenários", "🔎 Detalhes da Última Simulação", "📍 Mapa da Rede (Interativo)", "📋 Conceitos"])

with tab1:
    st.subheader("📚 Comparativo de Simulações Registradas")
    
    if len(st.session_state['simulacoes']) > 0:
        # Preparar Dataframe para Exibição
        dados_comp = []
        for sim in st.session_state['simulacoes']:
            # Dados do Cenário B (Com Galpão) que é o nosso foco de "Proposta"
            dados_comp.append({
                'Nome do Cenário': sim['nome'],
                'Lojas': sim['params']['num_lojas'],
                'Lead Time': sim['params']['lead_time'],
                'Var. Demanda (%)': f"{sim['params']['var_demanda']*100:.0f}%",
                'Custo Médio (R$)': sim['resultados_b']['custo_medio'],
                'Risco Ruptura (%)': sim['resultados_b']['prob_ruptura'],
                'Economia vs Atual': sim['resultados_a']['custo_medio'] - sim['resultados_b']['custo_medio']
            })
        
        df_comp = pd.DataFrame(dados_comp)
        
        # Formatando para exibição
        st.dataframe(
            df_comp.style.format({
                'Custo Médio (R$)': 'R$ {:,.2f}',
                'Risco Ruptura (%)': '{:.1f}%',
                'Economia vs Atual': 'R$ {:,.2f}'
            }).background_gradient(subset=['Economia vs Atual'], cmap='RdYlGn'),
            use_container_width=True
        )
        
        # Gráficos Comparativos
        col_c1, col_c2 = st.columns(2)
        
        with col_c1:
            fig_custo = px.bar(df_comp, x='Nome do Cenário', y='Custo Médio (R$)', 
                             text='Custo Médio (R$)', # Adiciona valor nas barras
                             color='Economia vs Atual', 
                             title="<b>Comparativo de Custos Totais</b>",
                             template="plotly_dark",
                             color_continuous_scale="RdYlGn") # Escala semantica
            
            fig_custo.update_traces(texttemplate='R$ %{text:.2s}', textposition='outside')
            fig_custo.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(17, 24, 39, 0.5)',
                xaxis_title="",
                font=dict(family="Inter, sans-serif", color='#9ca3af'),
                uniformtext_minsize=8, uniformtext_mode='hide'
            )
            fig_custo.update_yaxes(showgrid=True, gridcolor='#374151', tickprefix="R$ ")
            
            st.plotly_chart(fig_custo, use_container_width=True)
            
        with col_c2:
            fig_risco = px.scatter(df_comp, x='Risco Ruptura (%)', y='Custo Médio (R$)', 
                                 size='Lojas', color='Nome do Cenário',
                                 hover_data=['Lead Time', 'Var. Demanda (%)'], # Mais dados no hover
                                 title="<b>Trade-off: Risco vs Custo</b>",
                                 template="plotly_dark")
            
            fig_risco.update_traces(marker=dict(line=dict(width=2, color='DarkSlateGrey')))
            fig_risco.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(17, 24, 39, 0.5)',
                xaxis_title="Risco de Ruptura (%)",
                yaxis_title="Custo Médio (R$)",
                font=dict(family="Inter, sans-serif", color='#9ca3af')
            )
            fig_risco.update_xaxes(showgrid=True, gridcolor='#374151', ticksuffix="%")
            fig_risco.update_yaxes(showgrid=True, gridcolor='#374151', tickprefix="R$ ")

            st.plotly_chart(fig_risco, use_container_width=True)
            
        if st.button("🗑️ Limpar Histórico"):
            st.session_state['simulacoes'] = []
            st.rerun()
            
    else:
        st.info("👈 Configure os parâmetros na barra lateral e clique em 'Executar e Registrar' para adicionar cenários à comparação.")

with tab2:
    if len(st.session_state['simulacoes']) > 0:
        # Pega a última simulação
        last_sim = st.session_state['simulacoes'][-1]
        resultados_a = last_sim['resultados_a']
        resultados_b = last_sim['resultados_b']
        
        # Cálculo de Delta (Economia)
        economia = resultados_a['custo_medio'] - resultados_b['custo_medio']
        delta_pct = (economia / resultados_a['custo_medio']) * 100 if resultados_a['custo_medio'] > 0 else 0
        
        # KPIs Principais Customizados (HTML)
        st.markdown(f"### 🏆 Resultados: {last_sim['nome']}")
        
        # Helper para criar cards
        def kpi_card(title, value, delta_val=None, delta_text=None, is_good=True):
            delta_html = ""
            if delta_text:
                color_class = "kpi-delta-pos" if is_good else "kpi-delta-neg"
                icon = "↓" if is_good else "↑"
                delta_html = f'<div class="{color_class}">{icon} {delta_text}</div>'
            
            return f"""
            <div class="kpi-card">
                <div class="kpi-title">{title}</div>
                <div class="kpi-value">{value}</div>
                {delta_html}
            </div>
            """

        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(kpi_card("Custo Médio (Cenário A)", f"R$ {resultados_a['custo_medio']:,.2f}"), unsafe_allow_html=True)
        
        with col2:
            is_eco_good = economia > 0
            st.markdown(kpi_card("Custo Médio (Cenário B)", 
                               f"R$ {resultados_b['custo_medio']:,.2f}", 
                               delta_text=f"{delta_pct:.1f}% vs Cenário A",
                               is_good=is_eco_good), unsafe_allow_html=True)
        
        with col3:
            diff_ruptura = resultados_b['prob_ruptura'] - resultados_a['prob_ruptura']
            is_ruptura_good = diff_ruptura <= 0
            st.markdown(kpi_card("Risco de Ruptura (B)", 
                               f"{resultados_b['prob_ruptura']:.1f}%", 
                               delta_text=f"{diff_ruptura:+.1f} p.p.",
                               is_good=is_ruptura_good), unsafe_allow_html=True)

        # Dividir em colunas para os gráficos
        col_chart1, col_chart2 = st.columns(2)
        
        # --- NOVO: Análise Detalhada (Por que é melhor?) ---
        st.markdown("### 🧠 Análise Inteligente do Cenário")
        
        # Calcular diferenciais para narrativa
        delta_transporte = resultados_a.get('custo_transporte_medio', 0) - resultados_b.get('custo_transporte_medio', 0)
        delta_estoque = resultados_a.get('custo_estoque_medio', 0) - resultados_b.get('custo_estoque_medio', 0)
        custo_fixo_novo = resultados_b.get('custo_fixo', 0)
        
        # Preparar dados para Radar Chart (Normalizado: Maior é Melhor)
        # Se valor for 0, evitar divisão por zero
        def get_score(base, novo, inversamente_proporcional=True):
            if base == 0: return 1
            if novo == 0: return 2 # Dobro de bom
            ratio = base / novo if inversamente_proporcional else novo / base
            return min(ratio, 2.5) # Limitar a 2.5x
            
        metrics = ['Eficiência Transporte', 'Eficiência Estoque', 'Nível de Serviço', 'Estabilidade (Risco)']
        
        # Cenário A (Base = 1.0)
        valores_a = [1.0, 1.0, 1.0, 1.0]
        
        # Cenário B (Comparativo)
        score_transp = get_score(resultados_a.get('custo_transporte_medio', 1), resultados_b.get('custo_transporte_medio', 1))
        score_estoque = get_score(resultados_a.get('custo_estoque_medio', 1), resultados_b.get('custo_estoque_medio', 1))
        
        servico_a = 100 - resultados_a.get('prob_ruptura', 0)
        servico_b = 100 - resultados_b.get('prob_ruptura', 0)
        score_servico = servico_b / servico_a if servico_a > 0 else 1
        
        score_risco = get_score(resultados_a.get('desvio_padrao_custo', 1), resultados_b.get('desvio_padrao_custo', 1))
        
        valores_b = [score_transp, score_estoque, score_servico, score_risco]
        
        col_radar, col_texto = st.columns([0.4, 0.6])
        
        with col_radar:
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=valores_a, theta=metrics, fill='toself', name='Cenário A (Atual)',
                line_color='#ef5350'
            ))
            fig_radar.add_trace(go.Scatterpolar(
                r=valores_b, theta=metrics, fill='toself', name='Cenário B (Proposto)',
                line_color='#00e676'
            ))
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, max(2.0, max(valores_b))])),
                showlegend=True,
                title="<b>Performance Relativa (Maior Área = Melhor)</b>",
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Inter, sans-serif", color='#9ca3af')
            )
            st.plotly_chart(fig_radar, use_container_width=True)
            
        with col_texto:
            st.info(f"""
            **📋 Diagnóstico:**
            
            O **Cenário B** apresenta uma economia total de **R$ {economia:,.2f}** ({delta_pct:.1f}%).
            
            **Principais Fatores:**
            1.  🚚 **Transporte:** A centralização gerou uma economia de **R$ {delta_transporte:,.2f}**.
            2.  📦 **Estoque:** O "Risk Pooling" reduziu o custo de manutenção de estoque em **R$ {delta_estoque:,.2f}**.
            3.  🏗️ **Trade-off:** Essa economia absorve o custo fixo do novo galpão (R$ {custo_fixo_novo:,.2f}) e ainda gera lucro.
            
            **Conclusão:** A estratégia de centralização é **{'VIÁVEL' if economia > 0 else 'INVÁVEL'}** financeiramente e **{'REDUZ' if diff_ruptura < 0 else 'AUMENTA'}** o risco de ruptura.
            """)

        # Gráficos Interativos (Plotly)
        st.markdown("---")
        
        with col_chart1:
            st.subheader("📉 Distribuição de Risco (Histograma)")
            df_hist = pd.DataFrame({
                'Custo Total': resultados_a['distribuicao_custos'] + resultados_b['distribuicao_custos'],
                'Cenário': ['Cenário A (Atual)']*len(resultados_a['distribuicao_custos']) + ['Cenário B (Proposto)']*len(resultados_b['distribuicao_custos'])
            })
            
            # Histograma melhorado com Box Plot marginal
            fig_hist = px.histogram(df_hist, x="Custo Total", color="Cenário", barmode="overlay",
                                  marginal="box", # Adiciona boxplot no topo para ver quartis
                                  color_discrete_map={'Cenário A (Atual)': '#ef5350', 'Cenário B (Proposto)': '#00e676'},
                                  opacity=0.6, 
                                  nbins=50, # Mais bins para melhor definição
                                  title="<b>Distribuição de Probabilidade dos Custos</b>")
            
            fig_hist.update_layout(
                xaxis_title="Custo Total Anual (R$)", 
                yaxis_title="Frequência",
                legend=dict(orientation="h", y=1.1, x=0, title=None), # Legenda no topo
                hovermode="x unified",
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(17, 24, 39, 0.5)', # Fundo levemente destacado
                bargap=0.05,
                font=dict(family="Inter, sans-serif", color='#9ca3af')
            )
            # Formatando Eixo X para Moeda
            fig_hist.update_xaxes(tickprefix="R$ ", showgrid=True, gridcolor='#374151')
            fig_hist.update_yaxes(showgrid=True, gridcolor='#374151')
            
            st.plotly_chart(fig_hist, use_container_width=True)
            
        with col_chart2:
            st.subheader("📦 Comportamento do Estoque (Simulação)")
            dias = list(range(1, 366))
            hist_estoque = resultados_b.get('historico_estoque_exemplo', [0]*365)
            if len(hist_estoque) < 365:
                hist_estoque = hist_estoque + [0]*(365-len(hist_estoque))
            
            df_estoque = pd.DataFrame({
                'Dia': dias,
                'Estoque (kg)': hist_estoque[:365]
            })
            
            # Gráfico de Área para dar volume visual
            fig_line = px.area(df_estoque, x="Dia", y="Estoque (kg)", 
                             title="<b>Nível de Estoque no Galpão (1 Ano Exemplo)</b>")
            
            # Linha de Capacidade
            fig_line.add_hline(y=params.galpao['capacidade_estoque_kg'], 
                             line_dash="dot", line_color="#ef5350", line_width=2,
                             annotation_text="Capacidade Máxima", annotation_position="top right")
            
            # Linha de Segurança (apenas visual)
            estoque_seguranca_visual = 1000 # Valor aproximado visual
            fig_line.add_hrect(y0=0, y1=estoque_seguranca_visual, 
                             fillcolor="red", opacity=0.1, line_width=0,
                             annotation_text="Zona de Risco", annotation_position="bottom right")

            fig_line.update_traces(line_color='#6366f1', fillcolor='rgba(99, 102, 241, 0.2)')
            
            fig_line.update_layout(
                xaxis_title="Dia do Ano", 
                yaxis_title="Estoque (kg)", 
                hovermode="x unified",
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(17, 24, 39, 0.5)',
                font=dict(family="Inter, sans-serif", color='#9ca3af')
            )
            fig_line.update_xaxes(showgrid=True, gridcolor='#374151')
            fig_line.update_yaxes(showgrid=True, gridcolor='#374151')
            
            st.plotly_chart(fig_line, use_container_width=True)

    else:
        st.info("👆 Execute uma simulação para ver os detalhes aqui.")

with tab3:
    st.subheader("🗺️ Rede Logística Interativa")
    st.markdown("💡 **Clique no mapa** para selecionar um local e adicionar uma nova Loja ou Fábrica.")
    
    col_mapa, col_form = st.columns([0.7, 0.3])
    
    # Calcular Centro de Gravidade único (padrão)
    demanda_total = sum([p['demanda_anual_kg'] for p in params.get_pontos_demanda()]) / 365
    otimizador = OtimizacaoEspacial(params, demanda_total)
    
    # Determinar se Múltiplos CDs são necessários (Heurística: > 2 lojas ou alta demanda)
    num_lojas = len(params.get_pontos_demanda())
    sugerir_multiplos_cds = num_lojas > 2
    
    # Criar Mapa Folium
    # Centralizar mapa na média dos pontos
    todas_coords = [(p['latitude'], p['longitude']) for p in params.get_pontos_demanda()] + \
                   [(f['latitude'], f['longitude']) for f in params.get_pontos_fabrica()]
    
    if todas_coords:
        centro_lat = np.mean([c[0] for c in todas_coords])
        centro_lon = np.mean([c[1] for c in todas_coords])
    else:
        centro_lat, centro_lon = -15.7942, -47.8822
        
    m = folium.Map(location=[centro_lat, centro_lon], zoom_start=11, tiles="CartoDB dark_matter")
    
    # --- Marcadores de Fábricas ---
    for fab in params.get_pontos_fabrica():
        folium.Marker(
            [fab['latitude'], fab['longitude']], 
            popup=fab['nome'],
            tooltip=f"{fab['nome']} (Indústria)",
            icon=folium.Icon(color='red', icon='industry', prefix='fa')
        ).add_to(m)
    
    # --- Marcadores de Lojas ---
    for loja in params.get_pontos_demanda():
        nome_loja = loja.get('nome', 'Loja')
        folium.CircleMarker(
            [loja['latitude'], loja['longitude']],
            radius=8,
            popup=f"{nome_loja} (Demanda: {loja['demanda_anual_kg']:.0f} kg/ano)",
            tooltip=nome_loja,
            color='#3b82f6',
            fill=True,
            fill_color='#3b82f6'
        ).add_to(m)
        
    # --- Lógica de Centros de Distribuição ---
    if sugerir_multiplos_cds:
        # Modo Automático: Múltiplos CDs (sem checar checkbox)
        n_clusters = 2 # Começar com 2
        if num_lojas >= 6: n_clusters = 3 # Heurística simples
        
        centros_multiplos = otimizador.calcular_multiples_cg(n_clusters)
        
        st.info(f"⚡ **Algoritmo de Otimização:** Devido ao crescimento da rede ({num_lojas} lojas), o sistema sugere automaticamente a divisão em **{n_clusters} Centros de Distribuição Regionais** para maior eficiência.")
        
        for i, c in enumerate(centros_multiplos):
            folium.Marker(
                [c['latitude'], c['longitude']],
                popup=f"CD Regional {i+1} (Sugerido)",
                tooltip=f"CD Regional {i+1}",
                icon=folium.Icon(color='orange', icon='building', prefix='fa')
            ).add_to(m)
            
            # (Opcional) Desenhar linhas de conexão aqui se desejado
            
    else:
        # Modo Padrão: 1 Galpão Central (Centro de Gravidade Único)
        cg_unico = otimizador.calcular_centro_gravidade()
        folium.Marker(
            [cg_unico['latitude'], cg_unico['longitude']],
            popup="Galpão Sugerido",
            tooltip="Galpão Otimizado",
            icon=folium.Icon(color='green', icon='star', prefix='fa')
        ).add_to(m)

    with col_mapa:
        # Exibir Mapa e capturar clique
        output = st_folium(m, width=900, height=600, returned_objects=["last_clicked"])

    # Lógica de Captura de Clique
    if output["last_clicked"]:
        st.session_state['coords_selecionadas'] = output["last_clicked"]
    
    with col_form:
        st.markdown("### ➕ Adicionar Ponto")
        
        if st.session_state['coords_selecionadas']:
            lat_clicada = st.session_state['coords_selecionadas']['lat']
            lon_clicada = st.session_state['coords_selecionadas']['lng']
            
            st.info(f"📍 Local Selecionado:\nLat: {lat_clicada:.4f}\nLon: {lon_clicada:.4f}")
            
            tipo_ponto = st.radio("O que você deseja adicionar?", ["🏪 Loja", "🏭 Fábrica"])
            
            with st.form("form_add_ponto_mapa"):
                if tipo_ponto == "🏪 Loja":
                    nome_nova = st.text_input("Nome da Loja", f"Nova Loja {len(st.session_state['lojas_extras']) + 1}")
                    demanda_nova = st.number_input("Demanda (kg/dia)", value=200, min_value=10)
                else:
                    nome_nova = st.text_input("Nome da Fábrica", f"Nova Fábrica {len(st.session_state['fabricas_extras']) + 1}")
                    demanda_nova = 0 # Não usa demanda, mas mantemos o form simples
                    
                submit = st.form_submit_button("✅ Confirmar Adição")
                
                if submit:
                    if tipo_ponto == "🏪 Loja":
                        st.session_state['lojas_extras'].append({
                            'nome': nome_nova,
                            'latitude': lat_clicada,
                            'longitude': lon_clicada,
                            'demanda_media_dia': demanda_nova
                        })
                        msg = "Loja adicionada!"
                    else:
                        st.session_state['fabricas_extras'].append({
                            'nome': nome_nova,
                            'latitude': lat_clicada,
                            'longitude': lon_clicada,
                            'capacidade_producao_dia': 1000
                        })
                        msg = "Fábrica adicionada!"
                        
                    st.session_state['coords_selecionadas'] = None # Limpar seleção
                    st.success(f"{msg} Atualizando mapa...")
                    st.rerun()
            
            if st.button("Cancelar Seleção"):
                st.session_state['coords_selecionadas'] = None
                st.rerun()
                
        else:
            st.info("👆 Clique em um ponto no mapa para adicionar.")
        
        st.divider()
        col_stat1, col_stat2 = st.columns(2)
        col_stat1.metric("Lojas Extras", len(st.session_state['lojas_extras']))
        col_stat2.metric("Fábricas Extras", len(st.session_state['fabricas_extras']))

    # --- Análise de Impacto da Expansão ---
    st.markdown("---")
    st.subheader("📊 Análise de Impacto da Expansão")
    
    col_impact1, col_impact2 = st.columns(2)
    
    # 1. Gráfico de Demanda por Loja (Ranking)
    dados_lojas = params.get_pontos_demanda()
    df_demanda = pd.DataFrame(dados_lojas)
    
    with col_impact1:
        if not df_demanda.empty:
            df_demanda = df_demanda.sort_values('demanda_anual_kg', ascending=True)
            fig_demand = px.bar(df_demanda, x='demanda_anual_kg', y='nome', 
                              orientation='h',
                              title="<b>Demanda Anual por Loja (Ranking)</b>",
                              text='demanda_anual_kg',
                              color='demanda_anual_kg',
                              color_continuous_scale='Blues')
            
            fig_demand.update_traces(texttemplate='%{text:.2s} kg', textposition='outside')
            fig_demand.update_layout(
                yaxis_title="", xaxis_title="Demanda Anual (kg)",
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(17, 24, 39, 0.5)',
                font=dict(family="Inter, sans-serif", color='#9ca3af'),
                uniformtext_minsize=8, uniformtext_mode='hide'
            )
            st.plotly_chart(fig_demand, use_container_width=True)
            
    # 2. Gráfico de Eficiência Logística (Distância Média)
    with col_impact2:
        if not df_demanda.empty:
            # Calcular distâncias
            fab = params.fabrica
            # Se tiver múltiplos CDs, usar o mais próximo. Se não, usar o único.
            cds_disponiveis = centros_multiplos if sugerir_multiplos_cds else [cg_unico]
            
            dados_grafico_dist = []

            for loja in dados_lojas:
                # Distância Direta (Fábrica -> Loja)
                d_direta = params.calcular_distancia_euclidiana(fab['latitude'], fab['longitude'], loja['latitude'], loja['longitude'])
                
                # Encontrar CD mais próximo da loja e calcular rota via esse CD
                min_dist_rota_cd = float('inf')
                
                for cd in cds_disponiveis:
                    # Rota: Fábrica -> CD -> Loja
                    d_fab_cd = params.calcular_distancia_euclidiana(fab['latitude'], fab['longitude'], cd['latitude'], cd['longitude'])
                    d_cd_loja = params.calcular_distancia_euclidiana(cd['latitude'], cd['longitude'], loja['latitude'], loja['longitude'])
                    dist_total = d_fab_cd + d_cd_loja
                    
                    if dist_total < min_dist_rota_cd:
                        min_dist_rota_cd = dist_total
                
                dados_grafico_dist.append({'Loja': loja['nome'], 'Distância (km)': d_direta, 'Modelo': 'Direto (Fábrica)'})
                dados_grafico_dist.append({'Loja': loja['nome'], 'Distância (km)': min_dist_rota_cd, 'Modelo': 'Otimizado (via CD)'})
            
            df_dist = pd.DataFrame(dados_grafico_dist)
            
            fig_dist = px.bar(df_dist, x='Loja', y='Distância (km)', color='Modelo',
                            barmode='group',
                            title="<b>Comparativo de Distância Percorrida (km)</b>",
                            color_discrete_map={'Direto (Fábrica)': '#ef5350', 'Otimizado (via CD)': '#00e676'})
            
            fig_dist.update_layout(
                yaxis_title="Distância Total (km)", xaxis_title="",
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(17, 24, 39, 0.5)',
                legend=dict(orientation="h", y=1.1, x=0, title=None),
                font=dict(family="Inter, sans-serif", color='#9ca3af')
            )
            st.plotly_chart(fig_dist, use_container_width=True)


with tab4:
    st.markdown("### 📚 Conceitos Aplicados")
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("#### 📌 Cenário A (Atual)")
        st.write("- **Fluxo:** Fábrica → Lojas (Direto)")
        st.write("- **Transporte:** Sprinter (Capacidade Reduzida)")
        st.write("- **Estoque:** Descentralizado")
    
    with col_b:
        st.markdown("#### 📌 Cenário B (Otimizado)")
        st.write("- **Risk Pooling:** Centralização reduz variabilidade do estoque em ~30%")
        st.write("- **Centro de Gravidade:** Localização que minimiza 'Distância × Peso'")
        st.write("- **EOQ:** Lote econômico equilibra custos de pedido e armazenagem")
