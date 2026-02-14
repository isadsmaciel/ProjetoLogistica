
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

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

# Inicializar Estado da Sessão para Histórico
if 'simulacoes' not in st.session_state:
    st.session_state['simulacoes'] = []

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2921/2921226.png", width=100)
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
            # Inicialização dos parâmetros
            params = ParametrosLogistica()
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
                    'var_lead_time': lead_time_var
                },
                'resultados_a': resultados_a,
                'resultados_b': resultados_b
            }
            st.session_state['simulacoes'].append(novo_registro)
            st.success(f"Cenário '{nome_cenario}' registrado com sucesso!")

# Inicialização dos parâmetros (uso geral)
params = ParametrosLogistica()
params.operacional['lead_time_reposicao_dias'] = lead_time_medio

# Layout Principal em Abas
tab1, tab2, tab3, tab4 = st.tabs(["📊 Comparativo de Cenários", "🔎 Detalhes da Última Simulação", "📍 Mapa da Rede", "📋 Conceitos"])

with tab1:
    st.subheader("📚 Comparativo de Simulações Registradas")
    
    if len(st.session_state['simulacoes']) > 0:
        # Preparar Dataframe para Exibição
        dados_comp = []
        for sim in st.session_state['simulacoes']:
            # Dados do Cenário B (Com Galpão) que é o nosso foco de "Proposta"
            dados_comp.append({
                'Nome do Cenário': sim['nome'],
                'Lead Time (dias)': sim['params']['lead_time'],
                'Var. Demanda (%)': f"{sim['params']['var_demanda']*100:.0f}%",
                'Custo Médio (R$)': sim['resultados_b']['custo_medio'],
                'Risco Ruptura (%)': sim['resultados_b']['prob_ruptura'],
                'CO2 (Ton)': sim['resultados_b']['co2_medio'],
                'Economia vs Atual': sim['resultados_a']['custo_medio'] - sim['resultados_b']['custo_medio']
            })
        
        df_comp = pd.DataFrame(dados_comp)
        
        # Formatando para exibição
        st.dataframe(
            df_comp.style.format({
                'Custo Médio (R$)': 'R$ {:,.2f}',
                'Risco Ruptura (%)': '{:.1f}%',
                'CO2 (Ton)': '{:.2f}',
                'Economia vs Atual': 'R$ {:,.2f}'
            }).background_gradient(subset=['Economia vs Atual'], cmap='RdYlGn'),
            use_container_width=True
        )
        
        # Gráficos Comparativos
        col_c1, col_c2 = st.columns(2)
        
        with col_c1:
            fig_custo = px.bar(df_comp, x='Nome do Cenário', y='Custo Médio (R$)', 
                             color='Economia vs Atual', title="Comparativo de Custos",
                             template="plotly_dark")
            fig_custo.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_custo, use_container_width=True)
            
        with col_c2:
            fig_risco = px.scatter(df_comp, x='Risco Ruptura (%)', y='Custo Médio (R$)', 
                                 size='Lead Time (dias)', color='Nome do Cenário',
                                 title="Trade-off: Risco vs Custo",
                                 template="plotly_dark")
            fig_risco.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
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
        delta_pct = (economia / resultados_a['custo_medio']) * 100
        
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

        col1, col2, col3, col4 = st.columns(4)
        
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
        
        with col4:
            diff_co2 = resultados_b['co2_medio'] - resultados_a['co2_medio']
            is_co2_good = diff_co2 <= 0
            st.markdown(kpi_card("Emissões CO2", 
                               f"{resultados_b['co2_medio']:.1f} ton", 
                               delta_text=f"{diff_co2:+.1f} ton",
                               is_good=is_co2_good), unsafe_allow_html=True)

        # Gráficos Interativos (Plotly)
        st.markdown("---")
        
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.subheader("📉 Distribuição de Risco (Histograma)")
            df_hist = pd.DataFrame({
                'Custo Total': resultados_a['distribuicao_custos'] + resultados_b['distribuicao_custos'],
                'Cenário': ['Cenário A']*len(resultados_a['distribuicao_custos']) + ['Cenário B']*len(resultados_b['distribuicao_custos'])
            })
            
            fig_hist = px.histogram(df_hist, x="Custo Total", color="Cenário", barmode="overlay",
                                  color_discrete_map={'Cenário A': '#ef5350', 'Cenário B': '#6366f1'},
                                  opacity=0.75, nbins=30,
                                  title="Comparação de Distribuição de Custos (Risco)")
            fig_hist.update_layout(
                xaxis_title="Custo Total Anual (R$)", 
                yaxis_title="Frequência (Anos Simulados)",
                legend_title_text="", 
                hovermode="x unified",
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#9ca3af')
            )
            st.plotly_chart(fig_hist, use_container_width=True)
            
        with col_chart2:
            st.subheader("📦 Comportamento do Estoque (Exemplo)")
            dias = list(range(1, 366))
            df_estoque = pd.DataFrame({
                'Dia': dias,
                'Estoque (kg)': resultados_b['historico_estoque_exemplo']
            })
            
            fig_line = px.line(df_estoque, x="Dia", y="Estoque (kg)", title="Nível de Estoque no Galpão (1 Ano Exemplo)")
            fig_line.add_hline(y=params.galpao['capacidade_estoque_kg'], line_dash="dash", line_color="#ef5350", annotation_text="Capacidade Máxima")
            fig_line.update_traces(line_color='#6366f1')
            fig_line.update_layout(
                xaxis_title="Dia do Ano", 
                yaxis_title="Estoque (kg)", 
                hovermode="x unified",
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#9ca3af')
            )
            st.plotly_chart(fig_line, use_container_width=True)

    else:
        st.info("👆 Execute uma simulação para ver os detalhes aqui.")

with tab3:
    st.subheader("🗺️ Rede Logística Proposta")
    
    # Dados para o mapa
    data_mapa = pd.DataFrame({
        'lat': [params.fabrica['latitude'], params.loja_taguatinga['latitude'], params.loja_ceilandia['latitude'], -15.8278],
        'lon': [params.fabrica['longitude'], params.loja_taguatinga['longitude'], params.loja_ceilandia['longitude'], -48.0814],
        'Nome': ['Fábrica (Brazlândia)', 'Loja Taguatinga', 'Loja Ceilândia', '🎯 Galpão Sugerido'],
        'Tipo': ['Fábrica', 'Loja', 'Loja', 'Galpão'],
        'Cor': ['#ff0000', '#0000ff', '#0000ff', '#00ff00'],
        'Tamanho': [200, 100, 100, 150]
    })
    
    st.map(data_mapa, size='Tamanho', color='Cor', zoom=10)
    
    st.markdown("""
    **Legenda:**
    - 🔴 **Fábrica** (Origem)
    - 🔵 **Lojas** (Destinos de Venda)
    - 🟢 **Galpão** (Localização Otimizada pelo Centro de Gravidade)
    """)

with tab4:
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("### 📌 Cenário A (Atual)")
        st.write("- **Fluxo:** Fábrica → Lojas (Direto)")
        st.write("- **Transporte:** Sprinter (Capacidade Reduzida)")
        st.write("- **Estoque:** Descentralizado (Alto risco de ruptura individual)")
        st.write("- **Custo Fixo:** R$ 0,00")
        
    with col_b:
        st.markdown("### 📌 Cenário B (Galpão)")
        st.write("- **Fluxo:** Fábrica → Galpão → Lojas")
        st.write("- **Transporte:** Consolidado até Galpão + Distribuição Capilar")
        st.write("- **Estoque:** Centralizado (*Risk Pooling*)")
        st.write(f"- **Custo Fixo:** R$ {params.galpao['custo_fixo_total_ano']:,.2f}")
