"""
GERAÇÃO DE DADOS SIMULADOS

Gera histórico de demanda com características realistas:
- Sazonalidade semanal (picos de fim de semana)
- Correlação com temperatura
- Impacto de chuva
- Variabilidade aleatória
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta


class GeradorDados:
    """
    Classe para gerar dados históricos simulados
    """
    
    def __init__(self, params):
        """
        Inicializa com parâmetros do sistema
        
        Args:
            params (ParametrosLogistica): Parâmetros do sistema
        """
        self.params = params
        np.random.seed(42)  # Para reprodutibilidade
    
    
    def gerar_historico_demanda(self, dias=90):
        """
        Gera histórico de demanda com padrões realistas
        
        Args:
            dias (int): Número de dias de histórico
            
        Returns:
            pd.DataFrame: DataFrame com histórico
        """
        
        # Data inicial
        data_inicial = datetime.now() - timedelta(days=dias)
        
        # Arrays para armazenar dados
        datas = []
        demandas = []
        temperaturas = []
        chuvas = []
        dias_semana = []
        fins_de_semana = []
        
        for i in range(dias):
            data = data_inicial + timedelta(days=i)
            dia_semana = data.weekday()  # 0=Segunda, 6=Domingo
            
            # ================================================================
            # 1. TEMPERATURA
            # ================================================================
            
            # Simular temperatura com sazonalidade
            # Período de seca (Maio-Set): mais quente
            # Período de chuva (Nov-Mar): mais frio
            mes = data.month
            
            if mes in [5, 6, 7, 8, 9]:  # Seca
                temp_base = self.params.clima['temp_seca_media']
            else:  # Chuva
                temp_base = self.params.clima['temp_chuva_media']
            
            # Adicionar variação diária
            temperatura = np.random.normal(temp_base, 3)
            
            # ================================================================
            # 2. CHUVA
            # ================================================================
            
            # Probabilidade de chuva depende da estação
            if mes in [5, 6, 7, 8, 9]:  # Seca
                prob_chuva = self.params.clima['prob_chuva_estacao_seca']
            else:  # Chuva
                prob_chuva = self.params.clima['prob_chuva_estacao_chuvosa']
            
            chuva = np.random.binomial(1, prob_chuva)
            
            # ================================================================
            # 3. DEMANDA BASE
            # ================================================================
            
            # Demanda base depende do dia da semana
            if dia_semana >= 5:  # Fim de semana (Sáb/Dom)
                demanda_base = (self.params.loja_taguatinga['demanda_fds_dia'] + 
                               self.params.loja_ceilandia['demanda_fds_dia'])
                fim_de_semana = 1
            else:  # Dia útil
                demanda_base = (self.params.loja_taguatinga['demanda_media_dia'] + 
                               self.params.loja_ceilandia['demanda_media_dia'])
                fim_de_semana = 0
            
            # ================================================================
            # 4. AJUSTES CLIMÁTICOS
            # ================================================================
            
            # Ajuste por temperatura (dias quentes aumentam demanda)
            if temperatura > 28:
                fator_temp = self.params.clima['fator_calor']
            else:
                fator_temp = 1.0
            
            # Ajuste por chuva (reduz demanda)
            if chuva == 1:
                fator_chuva = self.params.clima['fator_chuva']
            else:
                fator_chuva = 1.0
            
            # ================================================================
            # 5. DEMANDA FINAL
            # ================================================================
            
            # Aplicar fatores
            demanda = demanda_base * fator_temp * fator_chuva
            
            # Adicionar ruído aleatório (±10%)
            ruido = np.random.normal(1.0, 0.10)
            demanda = demanda * ruido
            
            # Garantir que demanda seja positiva
            demanda = max(demanda, 50)
            
            # ================================================================
            # ARMAZENAR
            # ================================================================
            
            datas.append(data)
            demandas.append(demanda)
            temperaturas.append(temperatura)
            chuvas.append(chuva)
            dias_semana.append(dia_semana)
            fins_de_semana.append(fim_de_semana)
        
        # Criar DataFrame
        df = pd.DataFrame({
            'data': datas,
            'demanda_kg': demandas,
            'temperatura': temperaturas,
            'chuva': chuvas,
            'dia_semana': dias_semana,
            'fim_de_semana': fins_de_semana
        })
        
        return df
    
    
    def gerar_dados_custos(self):
        """
        Gera tabela de custos para análise
        
        Returns:
            pd.DataFrame: Tabela de custos
        """
        
        custos = {
            'Categoria': [
                'Transporte (por km)',
                'Armazenagem (por kg/ano)',
                'Aluguel Galpão (por ano)',
                'Energia Galpão (por mês)',
                'Manutenção Galpão (por mês)'
            ],
            'Valor (R$)': [
                self.params.transporte['custo_total_km'],
                self.params.armazenagem['custo_manutencao_kg_ano'],
                self.params.galpao['aluguel_total_ano'],
                self.params.galpao['custo_energia_mes'],
                self.params.galpao['custo_manutencao_mes']
            ]
        }
        
        df = pd.DataFrame(custos)
        
        return df
