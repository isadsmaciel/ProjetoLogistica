"""
Sistema de Otimização Logística - Fulô do Açaí
Etapa 1: Implementação Determinística Clássica

Autor: Isadora da Silva Maciel - 190108991
Universidade de Brasília - UnB
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Importação dos módulos do projeto
from modulos.parametrizacao import ParametrosLogistica
from modulos.previsao_demanda import PrevisaoDemanda
from modulos.otimizacao_espacial import OtimizacaoEspacial
from modulos.analise_cenarios import AnaliseCenarios
from utils.visualizacao import Visualizacao
from utils.geracao_dados import GeradorDados


def main():
    """
    Função principal que orquestra a execução de todos os módulos
    """
    print("="*70)
    print("SISTEMA DE OTIMIZAÇÃO LOGÍSTICA - FULÔ DO AÇAÍ")
    print("="*70)
    print()
    
    # ========================================================================
    # MÓDULO 1: PARAMETRIZAÇÃO E ENTRADA DE DADOS
    # ========================================================================
    print("📊 MÓDULO 1: Carregando parâmetros do sistema...")
    print("-"*70)
    
    params = ParametrosLogistica()
    params.exibir_resumo()
    
    # Gerar dados simulados de demanda
    print("\n🔄 Gerando dados históricos de demanda...")
    gerador = GeradorDados(params)
    df_historico = gerador.gerar_historico_demanda(dias=90)
    
    print(f"✅ {len(df_historico)} dias de histórico gerados")
    print(f"   Demanda média: {df_historico['demanda_kg'].mean():.2f} kg/dia")
    print(f"   Demanda máxima: {df_historico['demanda_kg'].max():.2f} kg/dia")
    print(f"   Demanda mínima: {df_historico['demanda_kg'].min():.2f} kg/dia")
    
    # ========================================================================
    # MÓDULO 2: PREVISÃO DE DEMANDA
    # ========================================================================
    print("\n" + "="*70)
    print("📈 MÓDULO 2: Previsão de Demanda")
    print("-"*70)
    
    previsao = PrevisaoDemanda(df_historico)
    
    # Método 1: Holt-Winters (Suavização Exponencial Tripla)
    print("\n🔮 Método 1: Holt-Winters (Suavização Exponencial Tripla)")
    previsao_hw, metricas_hw = previsao.holt_winters(dias_previsao=30)
    print(f"   MAPE: {metricas_hw['mape']:.2f}%")
    print(f"   RMSE: {metricas_hw['rmse']:.2f} kg")
    
    # Método 2: Regressão Linear Múltipla
    print("\n📊 Método 2: Regressão Linear Múltipla (com variáveis climáticas)")
    previsao_rlm, metricas_rlm = previsao.regressao_linear_multipla(dias_previsao=30)
    print(f"   MAPE: {metricas_rlm['mape']:.2f}%")
    print(f"   RMSE: {metricas_rlm['rmse']:.2f} kg")
    print(f"   R²: {metricas_rlm['r2']:.4f}")
    
    # Comparação de métodos
    print("\n🏆 Melhor método:", metricas_hw['nome'] if metricas_hw['mape'] < metricas_rlm['mape'] else metricas_rlm['nome'])
    
    # Usar a melhor previsão
    melhor_previsao = previsao_hw if metricas_hw['mape'] < metricas_rlm['mape'] else previsao_rlm
    demanda_projetada = melhor_previsao['previsao'].mean()
    
    # ========================================================================
    # MÓDULO 3: OTIMIZAÇÃO ESPACIAL
    # ========================================================================
    print("\n" + "="*70)
    print("📍 MÓDULO 3: Otimização Espacial")
    print("-"*70)
    
    otimizacao = OtimizacaoEspacial(params, demanda_projetada)
    
    # 3.1 Centro de Gravidade
    print("\n🎯 Calculando Centro de Gravidade...")
    localizacao_otima = otimizacao.calcular_centro_gravidade()
    print(f"   Localização ótima do galpão:")
    print(f"   Latitude: {localizacao_otima['latitude']:.6f}")
    print(f"   Longitude: {localizacao_otima['longitude']:.6f}")
    print(f"   Distância total ponderada: {localizacao_otima['distancia_total']:.2f} km")
    
    # 3.2 Lote Econômico de Compra (EOQ)
    print("\n📦 Calculando Lote Econômico de Compra (EOQ)...")
    eoq_resultado = otimizacao.calcular_eoq()
    print(f"   Lote ótimo: {eoq_resultado['lote_otimo']:.2f} kg")
    print(f"   Número de pedidos/ano: {eoq_resultado['num_pedidos']:.0f}")
    print(f"   Custo total anual: R$ {eoq_resultado['custo_total_anual']:.2f}")
    
    # ========================================================================
    # MÓDULO 4: ANÁLISE COMPARATIVA DE CENÁRIOS
    # ========================================================================
    print("\n" + "="*70)
    print("💰 MÓDULO 4: Análise Comparativa de Cenários")
    print("-"*70)
    
    analise = AnaliseCenarios(params, demanda_projetada, localizacao_otima, eoq_resultado)
    
    # Cenário A: Operação Atual (sem galpão)
    print("\n📌 Cenário A: Operação Atual (Fábrica → Lojas direto)")
    cenario_a = analise.calcular_cenario_atual()
    print(f"   Custo de Transporte: R$ {cenario_a['custo_transporte']:.2f}/ano")
    print(f"   Custo de Estoque: R$ {cenario_a['custo_estoque']:.2f}/ano")
    print(f"   Custo de Instalação: R$ {cenario_a['custo_instalacao']:.2f}/ano")
    print(f"   ➡️  CUSTO TOTAL: R$ {cenario_a['custo_total']:.2f}/ano")
    
    # Cenário B: Com Galpão Central
    print("\n📌 Cenário B: Com Galpão Central (Fábrica → Galpão → Lojas)")
    cenario_b = analise.calcular_cenario_proposto()
    print(f"   Custo de Transporte: R$ {cenario_b['custo_transporte']:.2f}/ano")
    print(f"   Custo de Estoque: R$ {cenario_b['custo_estoque']:.2f}/ano")
    print(f"   Custo de Instalação: R$ {cenario_b['custo_instalacao']:.2f}/ano")
    print(f"   ➡️  CUSTO TOTAL: R$ {cenario_b['custo_total']:.2f}/ano")
    
    # Análise de Viabilidade
    print("\n" + "="*70)
    print("🎯 RESULTADO DA ANÁLISE")
    print("="*70)
    
    economia = cenario_a['custo_total'] - cenario_b['custo_total']
    percentual = (economia / cenario_a['custo_total']) * 100
    
    if economia > 0:
        print(f"✅ VIÁVEL: A implementação do Galpão Central é RECOMENDADA!")
        print(f"   Economia anual: R$ {economia:.2f}")
        print(f"   Redução de custos: {percentual:.2f}%")
    else:
        print(f"❌ INVIÁVEL: Manter operação atual é mais econômico")
        print(f"   Custo adicional: R$ {abs(economia):.2f}")
        print(f"   Aumento de custos: {abs(percentual):.2f}%")
    
    # ========================================================================
    # VISUALIZAÇÕES
    # ========================================================================
    print("\n" + "="*70)
    print("📊 Gerando visualizações...")
    print("-"*70)
    
    viz = Visualizacao()
    
    # Gráfico 1: Histórico e Previsão de Demanda
    viz.plot_previsao_demanda(df_historico, previsao_hw, previsao_rlm)
    
    # Gráfico 2: Comparação de Custos
    viz.plot_comparacao_cenarios(cenario_a, cenario_b)
    
    # Mapa 3: Localização Ótima do Galpão
    viz.plot_mapa_localizacao(params, localizacao_otima)
    
    print("✅ Visualizações salvas na pasta 'resultados/'")
    
    # ========================================================================
    # RELATÓRIO FINAL
    # ========================================================================
    print("\n" + "="*70)
    print("📄 Gerando relatório final...")
    
    analise.gerar_relatorio_completo(
        previsao_hw, previsao_rlm, metricas_hw, metricas_rlm,
        localizacao_otima, eoq_resultado,
        cenario_a, cenario_b
    )
    
    print("✅ Relatório salvo em 'resultados/relatorio_final.txt'")
    print("\n" + "="*70)
    print("🎉 Execução concluída com sucesso!")
    print("="*70)


if __name__ == "__main__":
    main()
