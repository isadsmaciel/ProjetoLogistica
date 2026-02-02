# Sistema de Otimização Logística - Fulô do Açaí

**Projeto:** Etapa 1 - Implementação Determinística Clássica  
**Aluno:** Isadora da Silva Maciel - 190108991  
**Universidade:** Universidade de Brasília - UnB  
**Disciplina:** Engenharia de Produção

---

## 📋 Descrição do Projeto

Este projeto implementa um sistema de otimização logística para a rede de restaurantes "Fulô do Açaí", com foco na análise de viabilidade de implementação de um **Galpão Central (Centro de Distribuição)** para intermediar o fluxo entre a fábrica em Brazlândia e as lojas em Taguatinga e Ceilândia.

### Objetivos

1. **Prever demanda** utilizando métodos quantitativos (Holt-Winters e Regressão Linear Múltipla)
2. **Determinar localização ótima** do galpão usando o Método do Centro de Gravidade
3. **Dimensionar lotes** através do modelo EOQ (Economic Order Quantity)
4. **Comparar cenários** (operação atual vs. com galpão) para análise de viabilidade econômica

---

## 🏗️ Estrutura do Projeto

```
ProjetoLogistica/
│
├── main.py                          # Arquivo principal de execução
│
├── modulos/                         # Módulos principais do sistema
│   ├── __init__.py
│   ├── parametrizacao.py           # Módulo 1: Parâmetros e dados
│   ├── previsao_demanda.py         # Módulo 2: Previsão (Holt-Winters + RLM)
│   ├── otimizacao_espacial.py      # Módulo 3: Centro de Gravidade + EOQ
│   └── analise_cenarios.py         # Módulo 4: Comparação de cenários
│
├── utils/                           # Utilitários
│   ├── __init__.py
│   ├── geracao_dados.py            # Geração de dados simulados
│   └── visualizacao.py             # Gráficos e mapas
│
├── resultados/                      # Pasta de saída (gerada automaticamente)
│   ├── previsao_demanda.png        # Gráfico de previsões
│   ├── comparacao_cenarios.png     # Gráfico de custos
│   ├── mapa_localizacao.html       # Mapa interativo
│   └── relatorio_final.txt         # Relatório completo
│
├── requirements.txt                 # Dependências do projeto
└── README.md                        # Este arquivo
```

---

## 🚀 Como Executar - Passo a Passo Completo

### **⚡ Opção Rápida (Recomendado para Windows)**

Se você está no Windows, pode usar o script de execução automática:

```bash
.\executar.ps1
```

Este script irá:
1. ✅ Verificar se o Python está instalado
2. ✅ Instalar dependências automaticamente (se necessário)
3. ✅ Executar o sistema
4. ✅ Abrir os resultados automaticamente

**Nota:** Se aparecer erro de execução de scripts, execute primeiro:
```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

### **📋 Opção Manual (Passo a Passo Detalhado)**

### **Passo 1: Verificar Instalação do Python**

Abra o terminal (PowerShell no Windows) e verifique se o Python está instalado:

```bash
python --version
```

**Resultado esperado:** `Python 3.8.x` ou superior

Se não estiver instalado, baixe em: [https://www.python.org/downloads/](https://www.python.org/downloads/)

---

### **Passo 2: Navegar até a Pasta do Projeto**

```bash
cd d:\Apasta\Projetos\Isadora\ProjetoLogistica
```

---

### **Passo 3: Instalar Dependências**

Instale todas as bibliotecas necessárias:

```bash
pip install -r requirements.txt
```

**Bibliotecas que serão instaladas:**
- `numpy` - Cálculos numéricos
- `pandas` - Manipulação de dados
- `matplotlib` - Gráficos
- `statsmodels` - Holt-Winters
- `scikit-learn` - Regressão Linear
- `folium` - Mapas interativos

**Tempo estimado:** 1-3 minutos

---

### **Passo 4: Executar o Sistema**

Execute o arquivo principal:

```bash
python main.py
```

**O que acontece durante a execução:**

1. **Módulo 1:** Carrega parâmetros e gera 90 dias de histórico de demanda simulado
2. **Módulo 2:** Treina modelos de previsão (Holt-Winters e Regressão Linear)
3. **Módulo 3:** Calcula localização ótima do galpão e lote econômico (EOQ)
4. **Módulo 4:** Compara custos entre cenário atual e proposto
5. **Visualizações:** Gera gráficos e mapa interativo

**Tempo estimado de execução:** 10-30 segundos

---

### **Passo 5: Visualizar Resultados**

Após a execução, os resultados estarão na pasta `resultados/`:

#### **5.1 Gráficos (PNG)**

```bash
# Abrir pasta de resultados
cd resultados

# Visualizar gráficos
start previsao_demanda.png
start comparacao_cenarios.png
```

**Gráficos gerados:**
- `previsao_demanda.png` - Histórico e previsões de demanda
- `comparacao_cenarios.png` - Comparação de custos entre cenários

#### **5.2 Mapa Interativo (HTML)**

```bash
start mapa_localizacao.html
```

O mapa abrirá no navegador mostrando:
- 📍 Localização da Fábrica (Brazlândia)
- 📍 Localização das Lojas (Taguatinga e Ceilândia)
- 📍 Localização Ótima do Galpão (calculada)
- 🔗 Rotas de transporte com distâncias

#### **5.3 Relatório Completo (TXT)**

```bash
notepad relatorio_final.txt
```

O relatório contém:
- Métricas de previsão (MAPE, RMSE)
- Coordenadas do galpão otimizado
- Lote econômico (EOQ)
- Comparação detalhada de custos
- Recomendação final (viável ou inviável)

---

### **Passo 6: Interpretar os Resultados**

#### **✅ Cenário VIÁVEL (Galpão recomendado)**

Se o relatório mostrar:
```
✅ RECOMENDAÇÃO: Implementar o Galpão Central
Economia anual: R$ XX.XXX,XX
Redução de custos: XX.XX%
```

**Significa:** O custo total com galpão é MENOR que o custo atual.

#### **❌ Cenário INVIÁVEL (Manter operação atual)**

Se o relatório mostrar:
```
❌ RECOMENDAÇÃO: Manter operação atual
Custo adicional: R$ XX.XXX,XX
Aumento de custos: XX.XX%
```

**Significa:** O custo total com galpão é MAIOR que o custo atual.

---

### **Passo 7: Ajustar Parâmetros (Opcional)**

Para testar diferentes cenários, edite o arquivo:

```bash
notepad modulos\parametrizacao.py
```

**Parâmetros que você pode ajustar:**

```python
# Linha 22: Custo de transporte por km
'custo_total_km': 1.40  # Altere para testar outros valores

# Linha 67: Custo de aluguel do galpão
'aluguel_total_ano': 60000  # Altere para testar outros valores

# Linha 77: Demanda das lojas
'demanda_media_dia': 250  # Altere para testar outros volumes
```

Após alterar, execute novamente:

```bash
python main.py
```

---

### **Troubleshooting (Resolução de Problemas)**

#### **Erro: "ModuleNotFoundError: No module named 'numpy'"**

**Solução:** Instale as dependências:
```bash
pip install -r requirements.txt
```

#### **Erro: "FileNotFoundError: [Errno 2] No such file or directory"**

**Solução:** Certifique-se de estar na pasta correta:
```bash
cd d:\Apasta\Projetos\Isadora\ProjetoLogistica
```

#### **Gráficos não aparecem**

**Solução:** Verifique se a pasta `resultados/` foi criada:
```bash
dir resultados
```

Se não existir, o programa criará automaticamente na próxima execução.

---

### **Estrutura de Saída Esperada**

```
resultados/
├── previsao_demanda.png        # Gráfico de previsões
├── comparacao_cenarios.png     # Gráfico de custos
├── mapa_localizacao.html       # Mapa interativo
└── relatorio_final.txt         # Relatório completo
```

---

## 📐 Equações Matemáticas Implementadas

Este projeto implementa as equações matemáticas descritas no documento "Etapa 1: Logística" (Seção 5 - Modelagem Quantitativa Determinística).

### **5.1 Método do Centro de Gravidade**

**Localização no documento:** Seção 5.1 - Localização Contínua: Método do Centro de Gravidade

**Equações implementadas:**

```
X* = Σ(Vi · xi) / ΣVi

Y* = Σ(Vi · yi) / ΣVi
```

**Onde:**
- `X*, Y*` = Coordenadas ótimas do galpão (latitude, longitude)
- `Vi` = Volume (demanda anual em kg) do ponto i
- `xi, yi` = Coordenadas geográficas do ponto i

**Implementação no código:**

```python
# Arquivo: modulos/otimizacao_espacial.py
# Linhas: 57-59

lat_otima = np.sum(volumes * latitudes) / np.sum(volumes)
lon_otima = np.sum(volumes * longitudes) / np.sum(volumes)
```

**Objetivo:** Minimizar o "momento de transporte" (Volume × Distância), determinando a localização que reduz a distância total ponderada pela demanda.

---

### **5.2 Lote Econômico de Compra (EOQ)**

**Localização no documento:** Seção 5.2 - Dimensionamento de Lotes: Lote Econômico de Compra (EOQ)

**Equação implementada:**

```
Q* = √(2 · D · S / H)
```

**Onde:**
- `Q*` = Lote ótimo (kg)
- `D` = Demanda anual (kg/ano)
- `S` = Custo por pedido/viagem (R$)
  - **Nota:** Este custo é alto devido à restrição de não empilhamento dos baldes
- `H` = Custo de manutenção de estoque (R$/kg/ano)
  - Inclui: Custo de energia da câmara fria + Aluguel proporcional do m²

**Implementação no código:**

```python
# Arquivo: modulos/otimizacao_espacial.py
# Linha: 125

Q_otimo = np.sqrt((2 * D * S) / H)
```

**Custos derivados:**

```python
# Número de pedidos por ano
num_pedidos = D / Q_otimo

# Custo de pedidos anual
custo_pedidos_ano = num_pedidos * S

# Custo de manutenção anual (estoque médio = Q/2)
custo_manutencao_ano = (Q_otimo / 2) * H

# Custo total anual
custo_total_ano = custo_pedidos_ano + custo_manutencao_ano
```

**Objetivo:** Determinar o tamanho de lote que minimiza a soma dos custos de pedido e manutenção de estoque.

---

### **5.3 Custo Logístico Total (CLT)**

**Localização no documento:** Seção 5.3 - Função Objetivo: Minimização do Custo Logístico Total (CLT)

**Equação implementada:**

```
LT = CTransporte + CArmazenagem + CInstalação
```

**Onde:**
- `LT` = Custo Logístico Total (R$/ano)
- `CTransporte` = Custo de transporte (R$/ano)
- `CArmazenagem` = Custo de manutenção de estoque (R$/ano)
- `CInstalação` = Custo fixo de instalação do galpão (R$/ano)

**Implementação no código:**

```python
# Arquivo: modulos/analise_cenarios.py
# Cenário A (linhas 88-90):
custo_total = custo_transporte_total + custo_estoque + custo_instalacao

# Cenário B (linhas 177-179):
custo_total = custo_transporte_total + custo_estoque + custo_instalacao
```

**Comparação de cenários:**

| Componente | Cenário A (Atual) | Cenário B (Com Galpão) |
|-----------|------------------|----------------------|
| **Transporte** | Alto (viagens longas frequentes) | Reduzido (consolidação) |
| **Estoque** | Baixo (estoque mínimo) | Médio (estoque centralizado) |
| **Instalação** | Zero | Alto (aluguel + energia) |

**Objetivo:** Comparar o CLT entre os dois cenários para determinar a viabilidade econômica do galpão.

---

### **Equações Auxiliares**

#### **Distância Euclidiana com Fator de Correção**

```python
# Conversão: 1 grau ≈ 111 km
delta_lat = (lat2 - lat1) * 111
delta_lon = (lon2 - lon1) * 111 * cos((lat1 + lat2) / 2)

distancia_euclidiana = √(delta_lat² + delta_lon²)

# Fator de correção para distância rodoviária
distancia_rodoviaria = distancia_euclidiana * k
```

**Onde:** `k = 1.3` (fator de correção)

**Implementação:** `modulos/parametrizacao.py`, linhas 109-120

#### **Estoque de Segurança**

```python
ES = Z * σ * √LT
```

**Onde:**
- `ES` = Estoque de segurança (kg)
- `Z` = Fator de serviço (1.65 para 95% de nível de serviço)
- `σ` = Desvio padrão da demanda diária (kg)
- `LT` = Lead time de reposição (dias)

**Implementação:** `modulos/otimizacao_espacial.py`, linha 178

---

## 📊 Módulos Implementados

### **Módulo 1: Parametrização e Entrada de Dados**

Define todos os parâmetros do sistema:
- Coordenadas geográficas (Fábrica, Lojas)
- Custos operacionais (transporte, armazenagem, instalação)
- Capacidades e restrições físicas

**Arquivo:** `modulos/parametrizacao.py`

---

### **Módulo 2: Previsão de Demanda**

Implementa dois métodos de previsão:

#### **Método 1: Holt-Winters (Suavização Exponencial Tripla)**
- Captura **nível**, **tendência** e **sazonalidade**
- Ideal para padrões semanais (picos de fim de semana)
- Biblioteca: `statsmodels`

#### **Método 2: Regressão Linear Múltipla**
- Incorpora variáveis climáticas (temperatura, chuva)
- Modelo: `Demanda = β₀ + β₁*temperatura + β₂*chuva + β₃*fim_de_semana`
- Biblioteca: `scikit-learn`

**Métricas calculadas:** MAPE, RMSE, MAE, R²

**Arquivo:** `modulos/previsao_demanda.py`

---

### **Módulo 3: Otimização Espacial**

#### **3.1 Método do Centro de Gravidade**
Determina as coordenadas (X*, Y*) que minimizam o momento de transporte:

```
X* = Σ(Vᵢ * Xᵢ) / Σ(Vᵢ)
Y* = Σ(Vᵢ * Yᵢ) / Σ(Vᵢ)
```

Onde:
- Vᵢ = Volume (demanda anual) do ponto i
- Xᵢ, Yᵢ = Coordenadas do ponto i

#### **3.2 Lote Econômico de Compra (EOQ)**
Determina o lote Q* que minimiza o custo total:

```
Q* = √(2 * D * S / H)
```

Onde:
- D = Demanda anual (kg/ano)
- S = Custo por pedido/viagem (R$)
- H = Custo de manutenção de estoque (R$/kg/ano)

**Arquivo:** `modulos/otimizacao_espacial.py`

---

### **Módulo 4: Análise Comparativa de Cenários**

Compara o **Custo Logístico Total (CLT)** entre:

#### **Cenário A: Operação Atual**
- Entregas diretas Fábrica → Lojas
- Viagens frequentes (quase diárias)
- Sem custo de instalação
- Estoque mínimo nas lojas

#### **Cenário B: Com Galpão Central**
- Entregas consolidadas Fábrica → Galpão
- Distribuição curta Galpão → Lojas
- Custo fixo de instalação
- Estoque centralizado (Risk Pooling)

**Fórmula do CLT:**
```
CLT = Custo_Transporte + Custo_Estoque + Custo_Instalação
```

**Arquivo:** `modulos/analise_cenarios.py`

---

## 📈 Dados Simulados

O sistema gera dados históricos de demanda com características realistas:

- **Sazonalidade semanal:** Picos aos fins de semana (500 kg/dia vs 250 kg/dia útil)
- **Correlação climática:** 
  - Dias quentes (>28°C): +25% demanda
  - Dias chuvosos: -30% demanda
- **Variabilidade aleatória:** ±10% de ruído
- **Período:** 90 dias de histórico

**Arquivo:** `utils/geracao_dados.py`

---

## 📊 Visualizações

### 1. Gráfico de Previsão de Demanda
- Histórico de 90 dias
- Comparação entre Holt-Winters e Regressão Linear
- Intervalos de confiança

### 2. Gráfico de Comparação de Cenários
- Custo total anual (Cenário A vs B)
- Decomposição por categoria (Transporte, Estoque, Instalação)

### 3. Mapa Interativo
- Localização da Fábrica, Lojas e Galpão Otimizado
- Rotas de transporte com distâncias
- Tecnologia: Folium (OpenStreetMap)

**Arquivo:** `utils/visualizacao.py`

---

## 🔧 Tecnologias Utilizadas

| Biblioteca | Versão | Uso |
|-----------|--------|-----|
| **NumPy** | ≥1.24.0 | Cálculos numéricos |
| **Pandas** | ≥2.0.0 | Manipulação de dados |
| **Matplotlib** | ≥3.7.0 | Gráficos |
| **Statsmodels** | ≥0.14.0 | Holt-Winters |
| **Scikit-learn** | ≥1.3.0 | Regressão Linear |
| **Folium** | ≥0.14.0 | Mapas interativos |

---

## 📝 Exemplo de Saída

```
======================================================================
SISTEMA DE OTIMIZAÇÃO LOGÍSTICA - FULÔ DO AÇAÍ
======================================================================

📊 MÓDULO 1: Carregando parâmetros do sistema...
----------------------------------------------------------------------
📍 LOCALIZAÇÃO DOS PONTOS:
   Fábrica: Fábrica Brazlândia
   - Lat: -15.6667, Lon: -48.2039
   - Capacidade: 1000 kg/dia

🔄 Gerando dados históricos de demanda...
✅ 90 dias de histórico gerados
   Demanda média: 512.34 kg/dia

======================================================================
📈 MÓDULO 2: Previsão de Demanda
----------------------------------------------------------------------
🔮 Método 1: Holt-Winters (Suavização Exponencial Tripla)
   MAPE: 8.45%
   RMSE: 42.31 kg

📊 Método 2: Regressão Linear Múltipla (com variáveis climáticas)
   MAPE: 9.12%
   RMSE: 45.67 kg
   R²: 0.8234

🏆 Melhor método: Holt-Winters

======================================================================
📍 MÓDULO 3: Otimização Espacial
----------------------------------------------------------------------
🎯 Calculando Centro de Gravidade...
   Localização ótima do galpão:
   Latitude: -15.8278
   Longitude: -48.0814
   Distância total ponderada: 8.45 km

📦 Calculando Lote Econômico de Compra (EOQ)...
   Lote ótimo: 1245.67 kg
   Número de pedidos/ano: 150

======================================================================
💰 MÓDULO 4: Análise Comparativa de Cenários
----------------------------------------------------------------------
📌 Cenário A: Operação Atual (Fábrica → Lojas direto)
   Custo de Transporte: R$ 125,340.00/ano
   Custo de Estoque: R$ 2,500.00/ano
   Custo de Instalação: R$ 0.00/ano
   ➡️  CUSTO TOTAL: R$ 127,840.00/ano

📌 Cenário B: Com Galpão Central (Fábrica → Galpão → Lojas)
   Custo de Transporte: R$ 68,450.00/ano
   Custo de Estoque: R$ 4,120.00/ano
   Custo de Instalação: R$ 84,000.00/ano
   ➡️  CUSTO TOTAL: R$ 156,570.00/ano

======================================================================
🎯 RESULTADO DA ANÁLISE
======================================================================
❌ INVIÁVEL: Manter operação atual é mais econômico
   Custo adicional: R$ 28,730.00
   Aumento de custos: 22.47%
```

---

## 🎓 Referências Teóricas

### Métodos de Previsão
- **Holt-Winters:** Winters, P. R. (1960). "Forecasting Sales by Exponentially Weighted Moving Averages"
- **Regressão Linear:** Montgomery, D. C. (2012). "Introduction to Linear Regression Analysis"

### Otimização Logística
- **Centro de Gravidade:** Ballou, R. H. (2006). "Gerenciamento da Cadeia de Suprimentos"
- **EOQ:** Harris, F. W. (1913). "How Many Parts to Make at Once"

---

## 👨‍💻 Autor

**Isadora da Silva Maciel**  
Matrícula: 190108991  
Universidade de Brasília - UnB  
Faculdade de Tecnologias - FT

---

## 📄 Licença

Este projeto foi desenvolvido para fins acadêmicos como parte da disciplina de Engenharia de Produção.

---

## 🤝 Contribuições

Para dúvidas ou sugestões sobre o projeto, entre em contato através do email institucional.

---

**Última atualização:** Fevereiro de 2026
