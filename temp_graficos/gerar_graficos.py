import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Configuração para estética dos gráficos
plt.style.use('bmh') # Estilo "Business/Academic"

# 1. Simulação dos Dados (30 dias)
np.random.seed(42) # Para manter os resultados fixos
dias = np.arange(1, 31)
demanda = []
tipo_dia = []

# Simulando começando numa Segunda-feira (Dia 1)
# Dias 6, 7, 13, 14, 20, 21, 27, 28 são Sábado/Domingo
for dia in dias:
    dia_semana = (dia - 1) % 7
    
    if dia_semana < 5: # Segunda a Sexta (Dias 0 a 4)
        # Média 250kg, Desvio Padrão 20kg
        qtd = np.random.normal(250, 20)
        tipo_dia.append('Dia Útil')
    else: # Sábado e Domingo (Dias 5 e 6)
        # Média 500kg, Desvio Padrão 30kg
        qtd = np.random.normal(500, 30)
        tipo_dia.append('Fim de Semana')
    
    demanda.append(qtd)

df = pd.DataFrame({'Dia': dias, 'Demanda_kg': demanda, 'Tipo': tipo_dia})

# CRIANDO OS GRÁFICOS
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Gráfico 1: Histograma (Distribuição Bimodal)
# Mostra os dois "morros" de frequência
counts, bins, patches = ax1.hist(df['Demanda_kg'], bins=15, color='#2c3e50', alpha=0.7, rwidth=0.85)
ax1.set_title('Figura 1: Histograma de Frequência da Demanda', fontsize=12)
ax1.set_xlabel('Volume de Demanda Diária (kg)')
ax1.set_ylabel('Frequência (Dias)')
ax1.grid(axis='y', alpha=0.5)

# Adicionando anotações nos "morros"
ax1.text(250, 4, 'Dias Úteis\n(~250kg)', ha='center', color='black', fontweight='bold')
ax1.text(500, 3, 'Finais de Semana\n(~500kg)', ha='center', color='black', fontweight='bold')

# Gráfico 2: Série Temporal (Sazonalidade Semanal)
# Mostra os picos nos finais de semana
ax2.plot(df['Dia'], df['Demanda_kg'], marker='o', linestyle='-', color='#e74c3c', linewidth=2, markersize=5)
ax2.set_title('Figura 2: Comportamento da Demanda (Série Temporal - 1 Mês)', fontsize=12)
ax2.set_xlabel('Dia do Mês')
ax2.set_ylabel('Demanda (kg)')

ax2.set_xticks(np.arange(1, 31, 2)) # Marcações a cada 2 dias
ax2.grid(True, alpha=0.5)

# Destacar os picos (Opcional, mas fica bonito)
# Pega apenas os dias de fim de semana para marcar
fds = df[df['Tipo'] == 'Fim de Semana']
ax2.scatter(fds['Dia'], fds['Demanda_kg'], color='darkred', zorder=5, label='Picos de Fim de Semana')
ax2.legend()

plt.tight_layout()

# Salvar o gráfico ao invés de apenas mostrar
plt.savefig('graficos_demanda.png', dpi=300, bbox_inches='tight')
print("Gráfico salvo como 'graficos_demanda.png'")
plt.show()
