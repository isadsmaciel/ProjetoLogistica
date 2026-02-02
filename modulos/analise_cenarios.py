"""
MÓDULO 4: ANÁLISE COMPARATIVA DE CENÁRIOS

Compara o Custo Logístico Total (CLT) entre:
- Cenário A: Operação atual (Fábrica → Lojas direto)
- Cenário B: Com Galpão Central (Fábrica → Galpão → Lojas)
"""

import numpy as np


class AnaliseCenarios:
    """
    Classe para análise comparativa de cenários
    """
    
    def __init__(self, params, demanda_projetada, localizacao_galpao, eoq_resultado):
        """
        Inicializa com parâmetros e resultados de otimização
        
        Args:
            params (ParametrosLogistica): Parâmetros do sistema
            demanda_projetada (float): Demanda média diária (kg/dia)
            localizacao_galpao (dict): Resultado do centro de gravidade
            eoq_resultado (dict): Resultado do EOQ
        """
        self.params = params
        self.demanda_projetada = demanda_projetada
        self.demanda_anual = demanda_projetada * params.operacional['dias_trabalho_ano']
        self.localizacao_galpao = localizacao_galpao
        self.eoq = eoq_resultado
    
    
    def calcular_cenario_atual(self):
        """
        Cenário A: Operação Atual (sem galpão)
        
        Características:
        - Entregas diretas Fábrica → Lojas
        - Viagens frequentes (quase diárias)
        - Sem custo de instalação
        - Estoque mínimo nas lojas
        
        Returns:
            dict: Custos detalhados do cenário
        """
        
        # ====================================================================
        # 1. CUSTO DE TRANSPORTE
        # ====================================================================
        
        # Distâncias
        dist_fab_tag = self.params.calcular_distancia_euclidiana(
            self.params.fabrica['latitude'],
            self.params.fabrica['longitude'],
            self.params.loja_taguatinga['latitude'],
            self.params.loja_taguatinga['longitude']
        )
        
        dist_fab_cei = self.params.calcular_distancia_euclidiana(
            self.params.fabrica['latitude'],
            self.params.fabrica['longitude'],
            self.params.loja_ceilandia['latitude'],
            self.params.loja_ceilandia['longitude']
        )
        
        # Demanda anual de cada loja
        demanda_tag_ano = (self.params.loja_taguatinga['demanda_media_dia'] * 260 + 
                           self.params.loja_taguatinga['demanda_fds_dia'] * 105)
        
        demanda_cei_ano = (self.params.loja_ceilandia['demanda_media_dia'] * 260 + 
                           self.params.loja_ceilandia['demanda_fds_dia'] * 105)
        
        # Capacidade do veículo (limitada por volume)
        capacidade_veiculo = self.params.transporte['capacidade_real_kg']
        
        # Número de viagens necessárias por ano
        viagens_tag = np.ceil(demanda_tag_ano / capacidade_veiculo)
        viagens_cei = np.ceil(demanda_cei_ano / capacidade_veiculo)
        
        # Custo de transporte (ida e volta)
        custo_transporte_tag = viagens_tag * dist_fab_tag * 2 * self.params.transporte['custo_total_km']
        custo_transporte_cei = viagens_cei * dist_fab_cei * 2 * self.params.transporte['custo_total_km']
        
        custo_transporte_total = custo_transporte_tag + custo_transporte_cei
        
        # ====================================================================
        # 2. CUSTO DE ESTOQUE
        # ====================================================================
        
        # Estoque médio nas lojas (mínimo, pois entregas frequentes)
        # Assumir 2 dias de cobertura em cada loja
        estoque_medio_tag = self.params.loja_taguatinga['demanda_media_dia'] * 2
        estoque_medio_cei = self.params.loja_ceilandia['demanda_media_dia'] * 2
        
        estoque_medio_total = estoque_medio_tag + estoque_medio_cei
        
        custo_estoque = estoque_medio_total * self.params.armazenagem['custo_manutencao_kg_ano']
        
        # ====================================================================
        # 3. CUSTO DE INSTALAÇÃO
        # ====================================================================
        
        # Sem galpão central
        custo_instalacao = 0
        
        # ====================================================================
        # CUSTO TOTAL
        # ====================================================================
        
        custo_total = custo_transporte_total + custo_estoque + custo_instalacao
        
        resultado = {
            'cenario': 'A - Operação Atual',
            'custo_transporte': custo_transporte_total,
            'custo_estoque': custo_estoque,
            'custo_instalacao': custo_instalacao,
            'custo_total': custo_total,
            'detalhes': {
                'viagens_taguatinga': viagens_tag,
                'viagens_ceilandia': viagens_cei,
                'viagens_total_ano': viagens_tag + viagens_cei,
                'distancia_taguatinga': dist_fab_tag,
                'distancia_ceilandia': dist_fab_cei,
                'estoque_medio_kg': estoque_medio_total
            }
        }
        
        return resultado
    
    
    def calcular_cenario_proposto(self):
        """
        Cenário B: Com Galpão Central
        
        Características:
        - Entregas consolidadas Fábrica → Galpão
        - Distribuição curta Galpão → Lojas
        - Custo fixo de instalação
        - Estoque centralizado (Risk Pooling)
        
        Returns:
            dict: Custos detalhados do cenário
        """
        
        # ====================================================================
        # 1. CUSTO DE TRANSPORTE
        # ====================================================================
        
        # 1.1 Transporte Fábrica → Galpão
        dist_fab_galpao = self.localizacao_galpao['distancia_fabrica_galpao']
        
        # Número de viagens (baseado no EOQ)
        viagens_fab_galpao = self.eoq['num_pedidos']
        
        custo_fab_galpao = viagens_fab_galpao * dist_fab_galpao * 2 * self.params.transporte['custo_total_km']
        
        # 1.2 Transporte Galpão → Lojas
        # Viagens mais frequentes, mas distâncias menores
        
        # Distâncias do galpão às lojas
        distancias_galpao_lojas = self.localizacao_galpao['distancias_galpao_lojas']
        
        dist_galpao_tag = distancias_galpao_lojas[0]['distancia_km']
        dist_galpao_cei = distancias_galpao_lojas[1]['distancia_km']
        
        # Demanda anual de cada loja
        demanda_tag_ano = (self.params.loja_taguatinga['demanda_media_dia'] * 260 + 
                           self.params.loja_taguatinga['demanda_fds_dia'] * 105)
        
        demanda_cei_ano = (self.params.loja_ceilandia['demanda_media_dia'] * 260 + 
                           self.params.loja_ceilandia['demanda_fds_dia'] * 105)
        
        # Capacidade do veículo
        capacidade_veiculo = self.params.transporte['capacidade_real_kg']
        
        # Número de viagens
        viagens_galpao_tag = np.ceil(demanda_tag_ano / capacidade_veiculo)
        viagens_galpao_cei = np.ceil(demanda_cei_ano / capacidade_veiculo)
        
        # Custos
        custo_galpao_tag = viagens_galpao_tag * dist_galpao_tag * 2 * self.params.transporte['custo_total_km']
        custo_galpao_cei = viagens_galpao_cei * dist_galpao_cei * 2 * self.params.transporte['custo_total_km']
        
        custo_galpao_lojas = custo_galpao_tag + custo_galpao_cei
        
        # Custo total de transporte
        custo_transporte_total = custo_fab_galpao + custo_galpao_lojas
        
        # ====================================================================
        # 2. CUSTO DE ESTOQUE
        # ====================================================================
        
        # Estoque no galpão (baseado no EOQ)
        estoque_medio_galpao = self.eoq['estoque_medio']
        
        # Estoque nas lojas (reduzido, pois reposição é mais rápida)
        estoque_medio_tag = self.params.loja_taguatinga['demanda_media_dia'] * 1.5
        estoque_medio_cei = self.params.loja_ceilandia['demanda_media_dia'] * 1.5
        
        estoque_medio_total = estoque_medio_galpao + estoque_medio_tag + estoque_medio_cei
        
        custo_estoque = estoque_medio_total * self.params.armazenagem['custo_manutencao_kg_ano']
        
        # ====================================================================
        # 3. CUSTO DE INSTALAÇÃO
        # ====================================================================
        
        custo_instalacao = self.params.galpao['custo_fixo_total_ano']
        
        # ====================================================================
        # CUSTO TOTAL
        # ====================================================================
        
        custo_total = custo_transporte_total + custo_estoque + custo_instalacao
        
        resultado = {
            'cenario': 'B - Com Galpão Central',
            'custo_transporte': custo_transporte_total,
            'custo_estoque': custo_estoque,
            'custo_instalacao': custo_instalacao,
            'custo_total': custo_total,
            'detalhes': {
                'viagens_fabrica_galpao': viagens_fab_galpao,
                'viagens_galpao_taguatinga': viagens_galpao_tag,
                'viagens_galpao_ceilandia': viagens_galpao_cei,
                'viagens_total_ano': viagens_fab_galpao + viagens_galpao_tag + viagens_galpao_cei,
                'distancia_fabrica_galpao': dist_fab_galpao,
                'distancia_galpao_taguatinga': dist_galpao_tag,
                'distancia_galpao_ceilandia': dist_galpao_cei,
                'estoque_medio_kg': estoque_medio_total,
                'custo_transporte_fab_galpao': custo_fab_galpao,
                'custo_transporte_galpao_lojas': custo_galpao_lojas
            }
        }
        
        return resultado
    
    
    def gerar_relatorio_completo(self, previsao_hw, previsao_rlm, metricas_hw, metricas_rlm,
                                 localizacao, eoq, cenario_a, cenario_b):
        """
        Gera relatório completo em arquivo de texto
        """
        import os
        
        # Criar pasta de resultados
        os.makedirs('resultados', exist_ok=True)
        
        with open('resultados/relatorio_final.txt', 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("RELATÓRIO DE OTIMIZAÇÃO LOGÍSTICA - FULÔ DO AÇAÍ\n")
            f.write("="*80 + "\n\n")
            
            f.write("Projeto: Etapa 1 - Implementação Determinística Clássica\n")
            f.write("Aluno: Isadora da Silva Maciel - 190108991\n")
            f.write("Universidade de Brasília - UnB\n\n")
            
            # Módulo 2: Previsão
            f.write("-"*80 + "\n")
            f.write("MÓDULO 2: PREVISÃO DE DEMANDA\n")
            f.write("-"*80 + "\n\n")
            
            f.write(f"Método 1: {metricas_hw['nome']}\n")
            f.write(f"  MAPE: {metricas_hw['mape']:.2f}%\n")
            f.write(f"  RMSE: {metricas_hw['rmse']:.2f} kg\n\n")
            
            f.write(f"Método 2: {metricas_rlm['nome']}\n")
            f.write(f"  MAPE: {metricas_rlm['mape']:.2f}%\n")
            f.write(f"  RMSE: {metricas_rlm['rmse']:.2f} kg\n")
            f.write(f"  R²: {metricas_rlm['r2']:.4f}\n\n")
            
            # Módulo 3: Otimização
            f.write("-"*80 + "\n")
            f.write("MÓDULO 3: OTIMIZAÇÃO ESPACIAL\n")
            f.write("-"*80 + "\n\n")
            
            f.write("Localização Ótima do Galpão:\n")
            f.write(f"  Latitude: {localizacao['latitude']:.6f}\n")
            f.write(f"  Longitude: {localizacao['longitude']:.6f}\n")
            f.write(f"  Distância Fábrica → Galpão: {localizacao['distancia_fabrica_galpao']:.2f} km\n\n")
            
            f.write("Lote Econômico de Compra (EOQ):\n")
            f.write(f"  Lote Ótimo: {eoq['lote_otimo']:.2f} kg\n")
            f.write(f"  Número de Pedidos/Ano: {eoq['num_pedidos']:.0f}\n")
            f.write(f"  Frequência: A cada {eoq['frequencia_dias']:.1f} dias\n\n")
            
            # Módulo 4: Cenários
            f.write("-"*80 + "\n")
            f.write("MÓDULO 4: ANÁLISE COMPARATIVA DE CENÁRIOS\n")
            f.write("-"*80 + "\n\n")
            
            f.write("CENÁRIO A - Operação Atual:\n")
            f.write(f"  Custo de Transporte: R$ {cenario_a['custo_transporte']:,.2f}/ano\n")
            f.write(f"  Custo de Estoque: R$ {cenario_a['custo_estoque']:,.2f}/ano\n")
            f.write(f"  Custo de Instalação: R$ {cenario_a['custo_instalacao']:,.2f}/ano\n")
            f.write(f"  CUSTO TOTAL: R$ {cenario_a['custo_total']:,.2f}/ano\n\n")
            
            f.write("CENÁRIO B - Com Galpão Central:\n")
            f.write(f"  Custo de Transporte: R$ {cenario_b['custo_transporte']:,.2f}/ano\n")
            f.write(f"  Custo de Estoque: R$ {cenario_b['custo_estoque']:,.2f}/ano\n")
            f.write(f"  Custo de Instalação: R$ {cenario_b['custo_instalacao']:,.2f}/ano\n")
            f.write(f"  CUSTO TOTAL: R$ {cenario_b['custo_total']:,.2f}/ano\n\n")
            
            # Conclusão
            economia = cenario_a['custo_total'] - cenario_b['custo_total']
            percentual = (economia / cenario_a['custo_total']) * 100
            
            f.write("="*80 + "\n")
            f.write("CONCLUSÃO\n")
            f.write("="*80 + "\n\n")
            
            if economia > 0:
                f.write("✅ RECOMENDAÇÃO: Implementar o Galpão Central\n\n")
                f.write(f"Economia Anual: R$ {economia:,.2f}\n")
                f.write(f"Redução de Custos: {percentual:.2f}%\n")
            else:
                f.write("❌ RECOMENDAÇÃO: Manter operação atual\n\n")
                f.write(f"Custo Adicional: R$ {abs(economia):,.2f}\n")
                f.write(f"Aumento de Custos: {abs(percentual):.2f}%\n")
