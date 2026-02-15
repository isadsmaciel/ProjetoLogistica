"""
MÓDULO 3: OTIMIZAÇÃO ESPACIAL

Implementa:
1. Método do Centro de Gravidade - Localização ótima do galpão
2. Lote Econômico de Compra (EOQ) - Dimensionamento de lotes
3. Clusterização (K-Means) - Sugestão de múltiplos centros
"""

import numpy as np
from sklearn.cluster import KMeans

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
        Método do Centro de Gravidade Ponderado (1 Galpão)
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
        
    def calcular_multiples_cg(self, n_clusters=2):
        """
        Sugere múltiplos centros de distribuição usando K-Means Clustering Ponderado
        
        Args:
            n_clusters (int): Número de CDs a sugerir
            
        Returns:
            list: Lista de dicionários, cada um contendo lat/lon de um CD sugerido
        """
        pontos = self.params.get_pontos_demanda()
        
        if len(pontos) < n_clusters:
            return [] # Não há pontos suficientes para clusterizar

        # Preparar dados para o KMeans (Lat, Lon)
        # O KMeans do sklearn não suporta pesos diretos, então usamos
        # a aproximação de repetir pontos ou apenas a geometria simples
        # Dado que as lojas são poucas, a geometria simples é um bom começo,
        # mas idealmente usaríamos um K-Means ponderado.
        # Vamos usar geometria simples (distância) para os clusters,
        # e depois calcular o CG de cada cluster.
        
        X = np.array([[p['latitude'], p['longitude']] for p in pontos])
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        kmeans.fit(X)
        labels = kmeans.labels_
        
        # Para cada cluster, calcular o Centro de Gravidade Ponderado Real
        centros_finais = []
        
        for i in range(n_clusters):
            # Filtrar pontos deste cluster
            indices = np.where(labels == i)[0]
            cluster_pontos = [pontos[idx] for idx in indices]
            
            # Arrays
            lats = np.array([p['latitude'] for p in cluster_pontos])
            lons = np.array([p['longitude'] for p in cluster_pontos])
            vols = np.array([p['demanda_anual_kg'] for p in cluster_pontos])
            
            # CG Ponderado do cluster
            if np.sum(vols) > 0:
                lat_c = np.sum(vols * lats) / np.sum(vols)
                lon_c = np.sum(vols * lons) / np.sum(vols)
            else:
                lat_c = np.mean(lats)
                lon_c = np.mean(lons)
                
            centros_finais.append({
                'id': i+1,
                'latitude': lat_c,
                'longitude': lon_c,
                'lojas_atendidas': [p['nome'] for p in cluster_pontos]
            })
            
        return centros_finais
    
    
    def calcular_eoq(self):
        """
        Lote Econômico de Compra (Economic Order Quantity)
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
        num_pedidos = D / Q_otimo if Q_otimo > 0 else 0
        
        # Custos anuais
        custo_pedidos_ano = num_pedidos * S
        custo_manutencao_ano = (Q_otimo / 2) * H  # Estoque médio = Q/2
        custo_total_ano = custo_pedidos_ano + custo_manutencao_ano
        
        resultado = {
            'lote_otimo': Q_otimo,
            'num_pedidos': num_pedidos,
            'frequencia_dias': 365 / num_pedidos if num_pedidos > 0 else 0,
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
