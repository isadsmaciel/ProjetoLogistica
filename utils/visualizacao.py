"""
VISUALIZAÇÃO DE RESULTADOS

Gera gráficos e mapas para análise dos resultados
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import os


class Visualizacao:
    """
    Classe para geração de visualizações
    """
    
    def __init__(self):
        """
        Inicializa configurações de visualização
        """
        # Criar pasta de resultados
        os.makedirs('resultados', exist_ok=True)
        
        # Configurar estilo
        plt.style.use('seaborn-v0_8-darkgrid')
        plt.rcParams['figure.figsize'] = (12, 6)
        plt.rcParams['font.size'] = 10
    
    
    def plot_previsao_demanda(self, df_historico, previsao_hw, previsao_rlm):
        """
        Plota histórico e previsões de demanda
        
        Args:
            df_historico (pd.DataFrame): Dados históricos
            previsao_hw (pd.DataFrame): Previsão Holt-Winters
            previsao_rlm (pd.DataFrame): Previsão Regressão Linear
        """
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        
        # ====================================================================
        # GRÁFICO 1: Histórico de Demanda
        # ====================================================================
        
        ax1.plot(df_historico['data'], df_historico['demanda_kg'], 
                 'o-', color='#2E86AB', linewidth=1.5, markersize=3, 
                 label='Demanda Real', alpha=0.7)
        
        # Destacar fins de semana
        fds = df_historico[df_historico['fim_de_semana'] == 1]
        ax1.scatter(fds['data'], fds['demanda_kg'], 
                   color='#A23B72', s=50, alpha=0.6, 
                   label='Fim de Semana', zorder=5)
        
        ax1.set_xlabel('Data', fontsize=12)
        ax1.set_ylabel('Demanda (kg)', fontsize=12)
        ax1.set_title('Histórico de Demanda - Fulô do Açaí', fontsize=14, fontweight='bold')
        ax1.legend(loc='upper left')
        ax1.grid(True, alpha=0.3)
        
        # Formatar eixo x
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
        ax1.xaxis.set_major_locator(mdates.DayLocator(interval=7))
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
        
        # ====================================================================
        # GRÁFICO 2: Comparação de Previsões
        # ====================================================================
        
        # Últimos 30 dias do histórico
        historico_recente = df_historico.tail(30)
        
        ax2.plot(historico_recente['data'], historico_recente['demanda_kg'], 
                 'o-', color='#2E86AB', linewidth=2, markersize=4, 
                 label='Histórico Recente', alpha=0.7)
        
        # Previsão Holt-Winters
        ax2.plot(previsao_hw['data'], previsao_hw['previsao'], 
                 's-', color='#F18F01', linewidth=2, markersize=4, 
                 label='Holt-Winters', alpha=0.8)
        
        ax2.fill_between(previsao_hw['data'], 
                         previsao_hw['ic_inferior'], 
                         previsao_hw['ic_superior'], 
                         color='#F18F01', alpha=0.2)
        
        # Previsão Regressão Linear
        ax2.plot(previsao_rlm['data'], previsao_rlm['previsao'], 
                 '^-', color='#06A77D', linewidth=2, markersize=4, 
                 label='Regressão Linear Múltipla', alpha=0.8)
        
        ax2.fill_between(previsao_rlm['data'], 
                         previsao_rlm['ic_inferior'], 
                         previsao_rlm['ic_superior'], 
                         color='#06A77D', alpha=0.2)
        
        ax2.set_xlabel('Data', fontsize=12)
        ax2.set_ylabel('Demanda (kg)', fontsize=12)
        ax2.set_title('Comparação de Métodos de Previsão', fontsize=14, fontweight='bold')
        ax2.legend(loc='upper left')
        ax2.grid(True, alpha=0.3)
        
        # Formatar eixo x
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
        ax2.xaxis.set_major_locator(mdates.DayLocator(interval=5))
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        plt.savefig('resultados/previsao_demanda.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("   ✅ Gráfico salvo: resultados/previsao_demanda.png")
    
    
    def plot_comparacao_cenarios(self, cenario_a, cenario_b):
        """
        Plota comparação de custos entre cenários
        
        Args:
            cenario_a (dict): Custos do cenário atual
            cenario_b (dict): Custos do cenário proposto
        """
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # ====================================================================
        # GRÁFICO 1: Comparação de Custos Totais
        # ====================================================================
        
        cenarios = ['Cenário A\n(Atual)', 'Cenário B\n(Com Galpão)']
        custos_totais = [cenario_a['custo_total'], cenario_b['custo_total']]
        
        cores = ['#E63946', '#06A77D']
        
        bars = ax1.bar(cenarios, custos_totais, color=cores, alpha=0.7, edgecolor='black')
        
        # Adicionar valores nas barras
        for bar, custo in zip(bars, custos_totais):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'R$ {custo:,.0f}',
                    ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        ax1.set_ylabel('Custo Total Anual (R$)', fontsize=12)
        ax1.set_title('Comparação de Custo Total', fontsize=14, fontweight='bold')
        ax1.grid(axis='y', alpha=0.3)
        
        # Adicionar economia
        economia = cenario_a['custo_total'] - cenario_b['custo_total']
        if economia > 0:
            ax1.text(0.5, max(custos_totais) * 0.9, 
                    f'Economia: R$ {economia:,.0f}\n({economia/cenario_a["custo_total"]*100:.1f}%)',
                    ha='center', fontsize=11, 
                    bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
        
        # ====================================================================
        # GRÁFICO 2: Decomposição de Custos
        # ====================================================================
        
        categorias = ['Transporte', 'Estoque', 'Instalação']
        
        custos_a = [
            cenario_a['custo_transporte'],
            cenario_a['custo_estoque'],
            cenario_a['custo_instalacao']
        ]
        
        custos_b = [
            cenario_b['custo_transporte'],
            cenario_b['custo_estoque'],
            cenario_b['custo_instalacao']
        ]
        
        x = np.arange(len(categorias))
        width = 0.35
        
        bars1 = ax2.bar(x - width/2, custos_a, width, label='Cenário A', 
                       color='#E63946', alpha=0.7, edgecolor='black')
        bars2 = ax2.bar(x + width/2, custos_b, width, label='Cenário B', 
                       color='#06A77D', alpha=0.7, edgecolor='black')
        
        ax2.set_ylabel('Custo Anual (R$)', fontsize=12)
        ax2.set_title('Decomposição de Custos por Categoria', fontsize=14, fontweight='bold')
        ax2.set_xticks(x)
        ax2.set_xticklabels(categorias)
        ax2.legend()
        ax2.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('resultados/comparacao_cenarios.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("   ✅ Gráfico salvo: resultados/comparacao_cenarios.png")
    
    
    def plot_mapa_localizacao(self, params, localizacao):
        """
        Plota mapa com localização dos pontos e do galpão otimizado
        
        Args:
            params (ParametrosLogistica): Parâmetros do sistema
            localizacao (dict): Localização ótima do galpão
        """
        
        try:
            import folium
            from folium import plugins
            
            # Criar mapa centrado no DF
            mapa = folium.Map(
                location=[-15.7801, -47.9292],  # Centro de Brasília
                zoom_start=11,
                tiles='OpenStreetMap'
            )
            
            # Adicionar marcador da Fábrica
            folium.Marker(
                location=[params.fabrica['latitude'], params.fabrica['longitude']],
                popup=f"<b>{params.fabrica['nome']}</b><br>Capacidade: {params.fabrica['capacidade_producao_dia']} kg/dia",
                tooltip='Fábrica',
                icon=folium.Icon(color='blue', icon='industry', prefix='fa')
            ).add_to(mapa)
            
            # Adicionar marcadores das Lojas
            folium.Marker(
                location=[params.loja_taguatinga['latitude'], params.loja_taguatinga['longitude']],
                popup=f"<b>{params.loja_taguatinga['nome']}</b><br>Demanda: {params.loja_taguatinga['demanda_media_dia']} kg/dia",
                tooltip='Loja Taguatinga',
                icon=folium.Icon(color='green', icon='store', prefix='fa')
            ).add_to(mapa)
            
            folium.Marker(
                location=[params.loja_ceilandia['latitude'], params.loja_ceilandia['longitude']],
                popup=f"<b>{params.loja_ceilandia['nome']}</b><br>Demanda: {params.loja_ceilandia['demanda_media_dia']} kg/dia",
                tooltip='Loja Ceilândia',
                icon=folium.Icon(color='green', icon='store', prefix='fa')
            ).add_to(mapa)
            
            # Adicionar marcador do Galpão Otimizado
            folium.Marker(
                location=[localizacao['latitude'], localizacao['longitude']],
                popup=f"<b>Galpão Central (Otimizado)</b><br>Centro de Gravidade",
                tooltip='Galpão Otimizado',
                icon=folium.Icon(color='red', icon='warehouse', prefix='fa')
            ).add_to(mapa)
            
            # Adicionar linhas de conexão
            # Fábrica → Galpão
            folium.PolyLine(
                locations=[
                    [params.fabrica['latitude'], params.fabrica['longitude']],
                    [localizacao['latitude'], localizacao['longitude']]
                ],
                color='blue',
                weight=3,
                opacity=0.7,
                popup=f"Fábrica → Galpão<br>{localizacao['distancia_fabrica_galpao']:.2f} km"
            ).add_to(mapa)
            
            # Galpão → Lojas
            for dist_info in localizacao['distancias_galpao_lojas']:
                if 'Taguatinga' in dist_info['destino']:
                    lat_dest = params.loja_taguatinga['latitude']
                    lon_dest = params.loja_taguatinga['longitude']
                else:
                    lat_dest = params.loja_ceilandia['latitude']
                    lon_dest = params.loja_ceilandia['longitude']
                
                folium.PolyLine(
                    locations=[
                        [localizacao['latitude'], localizacao['longitude']],
                        [lat_dest, lon_dest]
                    ],
                    color='green',
                    weight=3,
                    opacity=0.7,
                    popup=f"Galpão → {dist_info['destino']}<br>{dist_info['distancia_km']:.2f} km"
                ).add_to(mapa)
            
            # Salvar mapa
            mapa.save('resultados/mapa_localizacao.html')
            print("   ✅ Mapa salvo: resultados/mapa_localizacao.html")
            
        except ImportError:
            print("   ⚠️  Biblioteca 'folium' não instalada. Mapa não gerado.")
            print("      Para instalar: pip install folium")
