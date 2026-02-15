
import numpy as np
import pandas as pd

class SimulacaoMonteCarlo:
    """
    Simulação Estocástica para Logística
    Incorpora variabilidade na Demanda e no Lead Time.
    """
    
    def __init__(self, params, variabilidade_demanda_pct, lead_time_medio, lead_time_var):
        self.params = params
        self.sigma_pct = variabilidade_demanda_pct
        self.lt_medio = lead_time_medio
        self.lt_var = lead_time_var
        
    def gerar_demanda_diaria(self, media):
        """Gera demanda diária com distribuição Normal"""
        demanda = np.random.normal(media, media * self.sigma_pct)
        return max(0, demanda) # Não existe demanda negativa
        
    def gerar_lead_time(self):
        """Gera lead time com variabilidade (pode ser discreta ou normal arredondada)"""
        if self.lt_var == 0:
            return int(self.lt_medio)
        lt = np.random.normal(self.lt_medio, self.lt_var)
        return max(1, int(round(lt))) # Mínimo 1 dia
        
    def rodar_cenario(self, com_galpao=False, iteracoes=100, dias_ano=365):
        """
        Executa a simulação de Monte Carlo por N iterações (anos).
        """
        custos_transporte = []
        custos_estoque = []
        custos_falta = []
        
        dias_com_ruptura_acumulado = 0 # Contador de dias totais de falta
        
        # Parâmetros básicos de custo
        custo_transporte_km = self.params.transporte['custo_total_km']
        custo_estoque_kg_ano = self.params.armazenagem['custo_manutencao_kg_ano']
        custo_falta = 10.0 # R$/kg (Custo de oportunidade por falta)

        custos_totais = [] # Lista para armazenar o custo total de cada iteração
        
        for i in range(iteracoes):
            custo_anual_transporte = 0
            custo_estoque_acumulado = 0
            custo_anual_falta = 0
            
            # Estado inicial
            estoque_atual = 1000
            em_transito = 0
            dias_para_chegar = 0
            
            # Política de Revisão (r, Q) simplificada
            demanda_media_total = sum([p['demanda_anual_kg'] for p in self.params.get_pontos_demanda()]) / 365
            
            if com_galpao:
                # GALPÃO CENTRAL
                lote_compra = 2000 # Lote econômico aproximado
                # Ponto de pedido mais robusto para o galpão
                ponto_pedido = demanda_media_total * self.lt_medio + (demanda_media_total * 0.5) 
            else:
                # LOJAS DIRETAS (Soma)
                lote_compra = 800 # Capacidade do veículo (limitante)
                ponto_pedido = demanda_media_total * self.lt_medio + (demanda_media_total * 0.3)
            
            estoque_diario = []
            
            for dia in range(dias_ano):
                # 1. Chegada de pedidos
                if dias_para_chegar > 0:
                    dias_para_chegar -= 1
                    if dias_para_chegar == 0:
                        estoque_atual += em_transito
                        em_transito = 0
                
                # 2. Consumo (Demanda Estocástica)
                demanda_dia = self.gerar_demanda_diaria(demanda_media_total)
                
                # Atender demanda
                if estoque_atual >= demanda_dia:
                    estoque_atual -= demanda_dia
                    vendido = demanda_dia
                    perdido = 0
                else:
                    vendido = estoque_atual
                    perdido = demanda_dia - estoque_atual
                    estoque_atual = 0
                    dias_com_ruptura_acumulado += 1 # Conta 1 dia de ruptura
                
                # Custo Falta
                custo_anual_falta += perdido * custo_falta
                
                # 3. Revisão de Estoque e Pedido
                if estoque_atual <= ponto_pedido and em_transito == 0:
                    qtd_pedido = lote_compra
                    em_transito = qtd_pedido
                    dias_para_chegar = self.gerar_lead_time()
                    
                    # Calcular custo transporte
                    if com_galpao:
                        # Fábrica -> Galpão + Distribuição Capilar
                        dist = 50 
                    else:
                        # Fábrica -> Lojas (direto e fragmentado)
                        dist = 80 
                    
                    # Custo viagem
                    custo_anual_transporte += dist * 2 * custo_transporte_km
                
                # Custo Estoque (manutenção diária)
                custo_estoque_acumulado += (estoque_atual * custo_estoque_kg_ano) / 365
                
                if i == 0: # Salvar histórico da primeira iteração
                    estoque_diario.append(estoque_atual)
            
            # Custo Fixo do Galpão
            custo_fixo = self.params.galpao['custo_fixo_total_ano'] if com_galpao else 0
            
            total_ano = custo_anual_transporte + custo_estoque_acumulado + custo_anual_falta + custo_fixo
            
            custos_totais.append(total_ano)
            custos_transporte.append(custo_anual_transporte)
            custos_estoque.append(custo_estoque_acumulado)
            custos_falta.append(custo_anual_falta)
            
            if i == 0:
                historico_exemplo = estoque_diario

        return {
            'custo_medio': np.mean(custos_totais),
            'custo_transporte_medio': np.mean(custos_transporte),
            'custo_estoque_medio': np.mean(custos_estoque),
            'custo_falta_medio': np.mean(custos_falta),
            'custo_fixo': self.params.galpao['custo_fixo_total_ano'] if com_galpao else 0,
            
            'desvio_padrao_custo': np.std(custos_totais),
            'prob_ruptura': (dias_com_ruptura_acumulado / (iteracoes * dias_ano)) * 100, # % de dias com ruptura
            'distribuicao_custos': custos_totais,
            'historico_estoque_exemplo': historico_exemplo
        }
