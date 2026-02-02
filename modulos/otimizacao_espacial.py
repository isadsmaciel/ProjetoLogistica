"""
MÓDULO 3: OTIMIZAÇÃO ESPACIAL

Implementa:
1. Método do Centro de Gravidade - Localização ótima do galpão
2. Lote Econômico de Compra (EOQ) - Dimensionamento de lotes
"""

import numpy as np


class OtimizacaoEspacial:
    """
    Classe para otimização da localização e dimensionamento
    """
    
    def __init__(self, params, demanda_projetada):
        """
        Inicializa com parâmetros do sistema
        
        Args:
            params (ParametrosLogistica): Objeto com parâmetros
            demanda_projetada (float): Demanda média diária projetada (kg/dia)
        """
        self.params = params
        self.demanda_projetada = demanda_projetada
        
        # Demanda anual total
        self.demanda_anual = demanda_projetada * params.operacional['dias_trabalho_ano']
    
    
    def calcular_centro_gravidade(self):
        """
        Método do Centro de Gravidade Ponderado
        
        Determina as coordenadas (X*, Y*) que minimizam o momento de transporte:
        
        X* = Σ(Vi * Xi) / Σ(Vi)
        Y* = Σ(Vi * Yi) / Σ(Vi)
        
        Onde:
        - Vi = Volume (demanda anual) do ponto i
        - Xi, Yi = Coordenadas do ponto i
        
        Returns:
            dict: Coordenadas ótimas e métricas
        """
        
        # Obter pontos de demanda (lojas)
        pontos = self.params.get_pontos_demanda()
        
        # Arrays para cálculo
        latitudes = np.array([p['latitude'] for p in pontos])
        longitudes = np.array([p['longitude'] for p in pontos])
        volumes = np.array([p['demanda_anual_kg'] for p in pontos])
        
        # Calcular centro de gravidade
        lat_otima = np.sum(volumes * latitudes) / np.sum(volumes)
        lon_otima = np.sum(volumes * longitudes) / np.sum(volumes)
        
        # Calcular distância total ponderada
        distancia_total = 0
        distancias_individuais = []
        
        for ponto in pontos:
            dist = self.params.calcular_distancia_euclidiana(
                lat_otima, lon_otima,
                ponto['latitude'], ponto['longitude']
            )
            distancia_total += dist * ponto['demanda_anual_kg']
            distancias_individuais.append({
                'destino': ponto['nome'],
                'distancia_km': dist
            })
        
        # Calcular também distância da fábrica ao galpão
        dist_fabrica_galpao = self.params.calcular_distancia_euclidiana(
            self.params.fabrica['latitude'],
            self.params.fabrica['longitude'],
            lat_otima,
            lon_otima
        )
        
        resultado = {
            'latitude': lat_otima,
            'longitude': lon_otima,
            'distancia_total': distancia_total / np.sum(volumes),  # Média ponderada
            'distancia_fabrica_galpao': dist_fabrica_galpao,
            'distancias_galpao_lojas': distancias_individuais
        }
        
        return resultado
    
    
    def calcular_eoq(self):
        """
        Lote Econômico de Compra (Economic Order Quantity)
        
        Determina o lote Q* que minimiza o custo total:
        
        Q* = √(2 * D * S / H)
        
        Onde:
        - D = Demanda anual (kg/ano)
        - S = Custo por pedido/viagem (R$)
        - H = Custo de manutenção de estoque (R$/kg/ano)
        
        Returns:
            dict: Lote ótimo e custos associados
        """
        
        # Parâmetros
        D = self.demanda_anual  # kg/ano
        
        # Custo por viagem (S)
        # Distância média Fábrica → Galpão (estimada em 20 km)
        distancia_media = 20  # km (será refinado após calcular centro de gravidade)
        custo_viagem = distancia_media * 2 * self.params.transporte['custo_total_km']  # Ida e volta
        S = custo_viagem
        
        # Custo de manutenção (H)
        H = self.params.armazenagem['custo_manutencao_kg_ano']
        
        # Calcular EOQ
        Q_otimo = np.sqrt((2 * D * S) / H)
        
        # Número de pedidos por ano
        num_pedidos = D / Q_otimo
        
        # Custos anuais
        custo_pedidos_ano = num_pedidos * S
        custo_manutencao_ano = (Q_otimo / 2) * H  # Estoque médio = Q/2
        custo_total_ano = custo_pedidos_ano + custo_manutencao_ano
        
        resultado = {
            'lote_otimo': Q_otimo,
            'num_pedidos': num_pedidos,
            'frequencia_dias': 365 / num_pedidos,
            'custo_pedidos_ano': custo_pedidos_ano,
            'custo_manutencao_ano': custo_manutencao_ano,
            'custo_total_anual': custo_total_ano,
            'estoque_medio': Q_otimo / 2,
            'parametros': {
                'demanda_anual': D,
                'custo_por_viagem': S,
                'custo_manutencao_unitario': H
            }
        }
        
        return resultado
    
    
    def calcular_estoque_seguranca(self):
        """
        Calcula estoque de segurança para cobrir variabilidade
        
        ES = Z * σ * √LT
        
        Onde:
        - Z = Fator de serviço (ex: 1.65 para 95% de nível de serviço)
        - σ = Desvio padrão da demanda diária
        - LT = Lead time (dias)
        
        Returns:
            dict: Estoque de segurança e ponto de pedido
        """
        
        # Estimativa de variabilidade (20% da demanda média)
        desvio_padrao_dia = self.demanda_projetada * 0.20
        
        # Nível de serviço 95% → Z = 1.65
        Z = 1.65
        
        # Lead time
        LT = self.params.operacional['lead_time_reposicao_dias']
        
        # Estoque de segurança
        ES = Z * desvio_padrao_dia * np.sqrt(LT)
        
        # Ponto de pedido (reorder point)
        demanda_durante_LT = self.demanda_projetada * LT
        ponto_pedido = demanda_durante_LT + ES
        
        resultado = {
            'estoque_seguranca': ES,
            'ponto_pedido': ponto_pedido,
            'demanda_durante_lead_time': demanda_durante_LT,
            'nivel_servico': 0.95,
            'parametros': {
                'desvio_padrao_dia': desvio_padrao_dia,
                'lead_time_dias': LT,
                'fator_z': Z
            }
        }
        
        return resultado
