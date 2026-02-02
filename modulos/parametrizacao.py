"""
MÓDULO 1: PARAMETRIZAÇÃO E ENTRADA DE DADOS

Este módulo centraliza todos os parâmetros do sistema logístico:
- Coordenadas geográficas dos pontos (Fábrica, Lojas)
- Custos operacionais (transporte, armazenagem, instalação)
- Capacidades e restrições físicas
"""

import numpy as np


class ParametrosLogistica:
    """
    Classe que armazena todos os parâmetros do sistema logístico
    """
    
    def __init__(self):
        """
        Inicializa os parâmetros com valores baseados no documento
        """
        
        # ====================================================================
        # COORDENADAS GEOGRÁFICAS (Latitude, Longitude)
        # ====================================================================
        
        # Fábrica em Brazlândia-DF
        self.fabrica = {
            'nome': 'Fábrica Brazlândia',
            'latitude': -15.6667,
            'longitude': -48.2039,
            'capacidade_producao_dia': 1000  # kg/dia
        }
        
        # Restaurante 1 - Taguatinga
        self.loja_taguatinga = {
            'nome': 'Restaurante Taguatinga',
            'latitude': -15.8389,
            'longitude': -48.0556,
            'demanda_media_dia': 250,  # kg/dia (dias úteis)
            'demanda_fds_dia': 500,    # kg/dia (fim de semana)
            'capacidade_estoque': 1500  # kg
        }
        
        # Restaurante 2 - Ceilândia
        self.loja_ceilandia = {
            'nome': 'Restaurante Ceilândia',
            'latitude': -15.8167,
            'longitude': -48.1072,
            'demanda_media_dia': 250,  # kg/dia (dias úteis)
            'demanda_fds_dia': 500,    # kg/dia (fim de semana)
            'capacidade_estoque': 1500  # kg
        }
        
        # ====================================================================
        # CUSTOS DE TRANSPORTE
        # ====================================================================
        
        # Veículo: Sprinter 2020
        self.transporte = {
            'veiculo': 'Mercedes Sprinter 2020',
            'capacidade_volume_m3': 12,  # m³
            'capacidade_peso_kg': 1400,  # kg
            
            # RESTRIÇÃO CRÍTICA: Não empilhamento de baldes
            'capacidade_real_kg': 800,  # kg (limitado por volume, não peso)
            
            # Custos por km
            'custo_combustivel_km': 0.80,  # R$/km (diesel)
            'custo_manutencao_km': 0.20,   # R$/km
            'custo_depreciacao_km': 0.15,  # R$/km
            'custo_motorista_km': 0.25,    # R$/km (proporcional)
            
            # Custo total por km
            'custo_total_km': 1.40  # R$/km
        }
        
        # ====================================================================
        # CUSTOS DE ARMAZENAGEM
        # ====================================================================
        
        self.armazenagem = {
            # Custo de manter 1 kg em estoque por 1 ano
            'custo_manutencao_kg_ano': 2.50,  # R$/kg/ano
            
            # Componentes do custo de armazenagem:
            'custo_energia_frio_kwh': 0.65,     # R$/kWh
            'consumo_camara_fria_kwh_dia': 50,  # kWh/dia
            'custo_oportunidade_capital': 0.10,  # 10% ao ano
        }
        
        # ====================================================================
        # CUSTOS DE INSTALAÇÃO (GALPÃO CENTRAL)
        # ====================================================================
        
        self.galpao = {
            'area_m2': 200,  # m²
            'aluguel_m2_mes': 25,  # R$/m²/mês
            'aluguel_total_mes': 5000,  # R$/mês
            'aluguel_total_ano': 60000,  # R$/ano
            
            # Custos adicionais
            'custo_energia_mes': 1500,  # R$/mês (câmara fria)
            'custo_manutencao_mes': 500,  # R$/mês
            'custo_seguranca_mes': 800,  # R$/mês
            
            # Custo fixo total anual
            'custo_fixo_total_ano': 84000,  # R$/ano (60k + 24k extras)
            
            # Capacidade
            'capacidade_estoque_kg': 5000  # kg
        }
        
        # ====================================================================
        # PARÂMETROS CLIMÁTICOS (DISTRITO FEDERAL)
        # ====================================================================
        
        self.clima = {
            # Temperatura média por estação
            'temp_seca_media': 28,  # °C (Maio-Setembro)
            'temp_chuva_media': 22,  # °C (Novembro-Março)
            
            # Impacto na demanda
            'fator_calor': 1.25,  # +25% demanda em dias quentes (>28°C)
            'fator_chuva': 0.70,  # -30% demanda em dias chuvosos
            
            # Probabilidades
            'prob_chuva_estacao_seca': 0.05,  # 5%
            'prob_chuva_estacao_chuvosa': 0.60,  # 60%
        }
        
        # ====================================================================
        # PARÂMETROS OPERACIONAIS
        # ====================================================================
        
        self.operacional = {
            'dias_trabalho_ano': 365,
            'dias_semana': 7,
            'fator_correcao_distancia': 1.3,  # Distância rodoviária / euclidiana
            
            # Estoque de segurança
            'dias_cobertura_seguranca': 3,  # dias
            
            # Lead time
            'lead_time_reposicao_dias': 1,  # dia
        }
    
    
    def get_pontos_demanda(self):
        """
        Retorna lista de pontos de demanda (lojas) com coordenadas e volumes
        
        Returns:
            list: Lista de dicionários com dados das lojas
        """
        return [
            {
                'nome': self.loja_taguatinga['nome'],
                'latitude': self.loja_taguatinga['latitude'],
                'longitude': self.loja_taguatinga['longitude'],
                'demanda_anual_kg': (self.loja_taguatinga['demanda_media_dia'] * 260 + 
                                     self.loja_taguatinga['demanda_fds_dia'] * 105)  # ~91.250 kg/ano
            },
            {
                'nome': self.loja_ceilandia['nome'],
                'latitude': self.loja_ceilandia['latitude'],
                'longitude': self.loja_ceilandia['longitude'],
                'demanda_anual_kg': (self.loja_ceilandia['demanda_media_dia'] * 260 + 
                                     self.loja_ceilandia['demanda_fds_dia'] * 105)  # ~91.250 kg/ano
            }
        ]
    
    
    def calcular_distancia_euclidiana(self, lat1, lon1, lat2, lon2):
        """
        Calcula distância euclidiana aproximada entre dois pontos
        
        Args:
            lat1, lon1: Coordenadas do ponto 1
            lat2, lon2: Coordenadas do ponto 2
            
        Returns:
            float: Distância em km
        """
        # Conversão aproximada: 1 grau ≈ 111 km
        delta_lat = (lat2 - lat1) * 111
        delta_lon = (lon2 - lon1) * 111 * np.cos(np.radians((lat1 + lat2) / 2))
        
        distancia_euclidiana = np.sqrt(delta_lat**2 + delta_lon**2)
        
        # Aplicar fator de correção para distância rodoviária
        distancia_rodoviaria = distancia_euclidiana * self.operacional['fator_correcao_distancia']
        
        return distancia_rodoviaria
    
    
    def exibir_resumo(self):
        """
        Exibe resumo dos parâmetros principais
        """
        print("📍 LOCALIZAÇÃO DOS PONTOS:")
        print(f"   Fábrica: {self.fabrica['nome']}")
        print(f"   - Lat: {self.fabrica['latitude']:.4f}, Lon: {self.fabrica['longitude']:.4f}")
        print(f"   - Capacidade: {self.fabrica['capacidade_producao_dia']} kg/dia")
        
        print(f"\n   Loja 1: {self.loja_taguatinga['nome']}")
        print(f"   - Lat: {self.loja_taguatinga['latitude']:.4f}, Lon: {self.loja_taguatinga['longitude']:.4f}")
        print(f"   - Demanda: {self.loja_taguatinga['demanda_media_dia']} kg/dia (útil), {self.loja_taguatinga['demanda_fds_dia']} kg/dia (FDS)")
        
        print(f"\n   Loja 2: {self.loja_ceilandia['nome']}")
        print(f"   - Lat: {self.loja_ceilandia['latitude']:.4f}, Lon: {self.loja_ceilandia['longitude']:.4f}")
        print(f"   - Demanda: {self.loja_ceilandia['demanda_media_dia']} kg/dia (útil), {self.loja_ceilandia['demanda_fds_dia']} kg/dia (FDS)")
        
        print(f"\n💰 CUSTOS PRINCIPAIS:")
        print(f"   Transporte: R$ {self.transporte['custo_total_km']:.2f}/km")
        print(f"   Armazenagem: R$ {self.armazenagem['custo_manutencao_kg_ano']:.2f}/kg/ano")
        print(f"   Galpão (fixo): R$ {self.galpao['custo_fixo_total_ano']:,.2f}/ano")
        
        # Calcular distâncias atuais
        dist_fab_tag = self.calcular_distancia_euclidiana(
            self.fabrica['latitude'], self.fabrica['longitude'],
            self.loja_taguatinga['latitude'], self.loja_taguatinga['longitude']
        )
        
        dist_fab_cei = self.calcular_distancia_euclidiana(
            self.fabrica['latitude'], self.fabrica['longitude'],
            self.loja_ceilandia['latitude'], self.loja_ceilandia['longitude']
        )
        
        print(f"\n📏 DISTÂNCIAS ATUAIS:")
        print(f"   Fábrica → Taguatinga: {dist_fab_tag:.2f} km")
        print(f"   Fábrica → Ceilândia: {dist_fab_cei:.2f} km")
