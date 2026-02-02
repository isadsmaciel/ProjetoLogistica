"""
MÓDULO 2: PREVISÃO DE DEMANDA

Implementa dois métodos de previsão:
1. Holt-Winters (Suavização Exponencial Tripla) - Captura sazonalidade
2. Regressão Linear Múltipla - Incorpora variáveis climáticas
"""

import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')


class PrevisaoDemanda:
    """
    Classe para previsão de demanda usando múltiplos métodos
    """
    
    def __init__(self, df_historico):
        """
        Inicializa com dados históricos
        
        Args:
            df_historico (pd.DataFrame): DataFrame com colunas:
                - data
                - demanda_kg
                - temperatura
                - chuva (0 ou 1)
                - dia_semana
                - fim_de_semana (0 ou 1)
        """
        self.df = df_historico.copy()
        self.df['data'] = pd.to_datetime(self.df['data'])
        self.df = self.df.sort_values('data').reset_index(drop=True)
        
        # Separar treino e teste (últimos 14 dias para teste)
        self.tamanho_teste = 14
        self.df_treino = self.df.iloc[:-self.tamanho_teste]
        self.df_teste = self.df.iloc[-self.tamanho_teste:]
    
    
    def holt_winters(self, dias_previsao=30):
        """
        Método 1: Suavização Exponencial Tripla (Holt-Winters)
        
        Captura três componentes:
        - Nível (média)
        - Tendência (crescimento)
        - Sazonalidade (padrão semanal)
        
        Args:
            dias_previsao (int): Número de dias para prever
            
        Returns:
            tuple: (DataFrame com previsões, dicionário com métricas)
        """
        print("   Treinando modelo Holt-Winters...")
        
        # Configurar modelo
        # seasonal_periods=7 captura padrão semanal (picos de fim de semana)
        modelo = ExponentialSmoothing(
            self.df_treino['demanda_kg'],
            seasonal_periods=7,
            trend='add',        # Tendência aditiva
            seasonal='add',     # Sazonalidade aditiva
            damped_trend=True   # Tendência amortecida (mais realista)
        )
        
        # Treinar
        modelo_fit = modelo.fit(optimized=True)
        
        # Prever no conjunto de teste (para calcular métricas)
        previsao_teste = modelo_fit.forecast(steps=self.tamanho_teste)
        
        # Calcular métricas de erro
        y_real = self.df_teste['demanda_kg'].values
        y_pred = previsao_teste.values
        
        mape = mean_absolute_percentage_error(y_real, y_pred) * 100
        rmse = np.sqrt(mean_squared_error(y_real, y_pred))
        mae = np.mean(np.abs(y_real - y_pred))
        
        # Prever para o futuro
        previsao_futura = modelo_fit.forecast(steps=dias_previsao)
        
        # Criar DataFrame de resultado
        datas_futuras = pd.date_range(
            start=self.df['data'].max() + pd.Timedelta(days=1),
            periods=dias_previsao,
            freq='D'
        )
        
        df_previsao = pd.DataFrame({
            'data': datas_futuras,
            'previsao': previsao_futura.values,
            'metodo': 'Holt-Winters'
        })
        
        # Adicionar intervalo de confiança (aproximado)
        df_previsao['ic_inferior'] = df_previsao['previsao'] * 0.85
        df_previsao['ic_superior'] = df_previsao['previsao'] * 1.15
        
        metricas = {
            'nome': 'Holt-Winters',
            'mape': mape,
            'rmse': rmse,
            'mae': mae,
            'modelo': modelo_fit
        }
        
        return df_previsao, metricas
    
    
    def regressao_linear_multipla(self, dias_previsao=30):
        """
        Método 2: Regressão Linear Múltipla com variáveis exógenas
        
        Modelo: Demanda = β0 + β1*temperatura + β2*chuva + β3*fim_de_semana + ε
        
        Args:
            dias_previsao (int): Número de dias para prever
            
        Returns:
            tuple: (DataFrame com previsões, dicionário com métricas)
        """
        print("   Treinando modelo de Regressão Linear Múltipla...")
        
        # Preparar features (variáveis independentes)
        features = ['temperatura', 'chuva', 'fim_de_semana']
        
        X_treino = self.df_treino[features].values
        y_treino = self.df_treino['demanda_kg'].values
        
        X_teste = self.df_teste[features].values
        y_teste = self.df_teste['demanda_kg'].values
        
        # Treinar modelo
        modelo = LinearRegression()
        modelo.fit(X_treino, y_treino)
        
        # Prever no conjunto de teste
        y_pred_teste = modelo.predict(X_teste)
        
        # Calcular métricas
        mape = mean_absolute_percentage_error(y_teste, y_pred_teste) * 100
        rmse = np.sqrt(mean_squared_error(y_teste, y_pred_teste))
        mae = np.mean(np.abs(y_teste - y_pred_teste))
        r2 = r2_score(y_teste, y_pred_teste)
        
        # Exibir coeficientes (interpretação)
        print(f"   Coeficientes do modelo:")
        print(f"   - Intercepto: {modelo.intercept_:.2f} kg")
        for i, feature in enumerate(features):
            print(f"   - {feature}: {modelo.coef_[i]:+.2f} kg")
        
        # Gerar previsões futuras
        # Para isso, precisamos simular variáveis climáticas futuras
        X_futuro = self._gerar_features_futuras(dias_previsao)
        previsao_futura = modelo.predict(X_futuro)
        
        # Criar DataFrame de resultado
        datas_futuras = pd.date_range(
            start=self.df['data'].max() + pd.Timedelta(days=1),
            periods=dias_previsao,
            freq='D'
        )
        
        df_previsao = pd.DataFrame({
            'data': datas_futuras,
            'previsao': previsao_futura,
            'metodo': 'Regressão Linear Múltipla'
        })
        
        # Intervalo de confiança baseado no erro padrão
        erro_padrao = rmse
        df_previsao['ic_inferior'] = df_previsao['previsao'] - 1.96 * erro_padrao
        df_previsao['ic_superior'] = df_previsao['previsao'] + 1.96 * erro_padrao
        
        metricas = {
            'nome': 'Regressão Linear Múltipla',
            'mape': mape,
            'rmse': rmse,
            'mae': mae,
            'r2': r2,
            'modelo': modelo,
            'coeficientes': {
                'intercepto': modelo.intercept_,
                'temperatura': modelo.coef_[0],
                'chuva': modelo.coef_[1],
                'fim_de_semana': modelo.coef_[2]
            }
        }
        
        return df_previsao, metricas
    
    
    def _gerar_features_futuras(self, dias):
        """
        Gera features climáticas simuladas para previsão futura
        
        Args:
            dias (int): Número de dias
            
        Returns:
            np.array: Matriz de features
        """
        # Simular temperatura (média 25°C, variação ±5°C)
        temperatura = np.random.normal(25, 5, dias)
        
        # Simular chuva (20% de probabilidade)
        chuva = np.random.binomial(1, 0.2, dias)
        
        # Determinar fim de semana (padrão semanal)
        # Assumir que o próximo dia é segunda (dia_semana=0)
        dia_inicio = (self.df['data'].max().dayofweek + 1) % 7
        dias_semana = [(dia_inicio + i) % 7 for i in range(dias)]
        fim_de_semana = [1 if d >= 5 else 0 for d in dias_semana]  # Sábado=5, Domingo=6
        
        # Montar matriz de features
        X = np.column_stack([temperatura, chuva, fim_de_semana])
        
        return X
    
    
    def comparar_metodos(self, previsao_hw, metricas_hw, previsao_rlm, metricas_rlm):
        """
        Compara os dois métodos de previsão
        
        Returns:
            pd.DataFrame: Tabela comparativa
        """
        comparacao = pd.DataFrame({
            'Método': [metricas_hw['nome'], metricas_rlm['nome']],
            'MAPE (%)': [metricas_hw['mape'], metricas_rlm['mape']],
            'RMSE (kg)': [metricas_hw['rmse'], metricas_rlm['rmse']],
            'MAE (kg)': [metricas_hw['mae'], metricas_rlm['mae']]
        })
        
        return comparacao
