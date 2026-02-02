# RESUMO DO PROJETO - Sistema de Otimização Logística

## 📁 Estrutura de Arquivos Criada

```
ProjetoLogistica/
│
├── 📄 main.py                          # ⭐ ARQUIVO PRINCIPAL - Execute este
├── 📄 executar.ps1                     # Script de execução rápida (Windows)
├── 📄 requirements.txt                 # Dependências do projeto
├── 📄 README.md                        # Documentação completa
├── 📄 .gitignore                       # Arquivos ignorados pelo Git
│
├── 📂 modulos/                         # Módulos principais (4 módulos)
│   ├── __init__.py
│   ├── parametrizacao.py              # Módulo 1: Parâmetros e dados
│   ├── previsao_demanda.py            # Módulo 2: Holt-Winters + RLM
│   ├── otimizacao_espacial.py         # Módulo 3: Centro Gravidade + EOQ
│   └── analise_cenarios.py            # Módulo 4: Comparação A vs B
│
├── 📂 utils/                           # Utilitários
│   ├── __init__.py
│   ├── geracao_dados.py               # Geração de dados simulados
│   └── visualizacao.py                # Gráficos e mapas
│
└── 📂 resultados/                      # ⭐ RESULTADOS (gerado após execução)
    ├── previsao_demanda.png           # Gráfico de previsões
    ├── comparacao_cenarios.png        # Gráfico de custos
    ├── mapa_localizacao.html          # Mapa interativo
    └── relatorio_final.txt            # Relatório completo
```

---

## 🎯 Equações Implementadas

### ✅ 1. Centro de Gravidade (Seção 5.1)
```
X* = Σ(Vi · xi) / ΣVi
Y* = Σ(Vi · yi) / ΣVi
```
📍 Arquivo: `modulos/otimizacao_espacial.py` (linhas 57-59)

### ✅ 2. Lote Econômico (EOQ) (Seção 5.2)
```
Q* = √(2 · D · S / H)
```
📍 Arquivo: `modulos/otimizacao_espacial.py` (linha 125)

### ✅ 3. Custo Logístico Total (Seção 5.3)
```
LT = CTransporte + CArmazenagem + CInstalação
```
📍 Arquivo: `modulos/analise_cenarios.py` (linhas 88-90, 177-179)

---

## 🚀 Como Executar

### Opção 1: Script Automático (Windows)
```bash
.\executar.ps1
```

### Opção 2: Manual
```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Executar
python main.py

# 3. Ver resultados
cd resultados
start previsao_demanda.png
start comparacao_cenarios.png
start mapa_localizacao.html
notepad relatorio_final.txt
```

---

## 📊 Métodos de Previsão Implementados

### Método 1: Holt-Winters (Suavização Exponencial Tripla)
- ✅ Captura nível, tendência e sazonalidade
- ✅ Ideal para padrões semanais (picos de fim de semana)
- 📍 Arquivo: `modulos/previsao_demanda.py` (linhas 40-95)

### Método 2: Regressão Linear Múltipla
- ✅ Incorpora variáveis climáticas (temperatura, chuva)
- ✅ Modelo: Demanda = β₀ + β₁·temp + β₂·chuva + β₃·fds
- 📍 Arquivo: `modulos/previsao_demanda.py` (linhas 98-160)

---

## 📈 Fluxo de Execução

```
1. MÓDULO 1: Parametrização
   ↓
   - Carrega coordenadas (Fábrica, Lojas)
   - Define custos (transporte, armazenagem, instalação)
   - Gera 90 dias de histórico simulado

2. MÓDULO 2: Previsão de Demanda
   ↓
   - Treina Holt-Winters
   - Treina Regressão Linear Múltipla
   - Compara métodos (MAPE, RMSE)
   - Seleciona melhor método

3. MÓDULO 3: Otimização Espacial
   ↓
   - Calcula Centro de Gravidade (X*, Y*)
   - Calcula EOQ (Q*)
   - Determina estoque de segurança

4. MÓDULO 4: Análise de Cenários
   ↓
   - Cenário A: Operação atual (sem galpão)
   - Cenário B: Com galpão central
   - Compara CLT (Custo Logístico Total)
   - Recomendação: Viável ou Inviável

5. VISUALIZAÇÕES
   ↓
   - Gráficos de previsão e custos
   - Mapa interativo com localização ótima
   - Relatório completo em texto
```

---

## 📝 Parâmetros Principais (Editáveis)

Arquivo: `modulos/parametrizacao.py`

```python
# Coordenadas
Fábrica: Brazlândia (-15.6667, -48.2039)
Loja 1: Taguatinga (-15.8389, -48.0556)
Loja 2: Ceilândia (-15.8167, -48.1072)

# Custos
Transporte: R$ 1.40/km
Armazenagem: R$ 2.50/kg/ano
Galpão (fixo): R$ 84.000/ano

# Demanda
Dias úteis: 250 kg/dia (cada loja)
Fim de semana: 500 kg/dia (cada loja)
```

---

## 🎓 Referências do Documento

- **Seção 5.1:** Centro de Gravidade → `otimizacao_espacial.py`
- **Seção 5.2:** EOQ → `otimizacao_espacial.py`
- **Seção 5.3:** CLT → `analise_cenarios.py`
- **Seção 4.2:** Holt-Winters → `previsao_demanda.py`

---

## ✅ Checklist de Implementação

- [x] Estrutura de arquivos criada
- [x] Módulo 1: Parametrização
- [x] Módulo 2: Previsão (Holt-Winters + RLM)
- [x] Módulo 3: Otimização (Centro Gravidade + EOQ)
- [x] Módulo 4: Análise de Cenários
- [x] Utilitários (Geração de dados + Visualização)
- [x] Equação Centro de Gravidade implementada
- [x] Equação EOQ implementada
- [x] Equação CLT implementada
- [x] README com passo a passo completo
- [x] Script de execução rápida
- [x] Documentação das equações

---

## 📞 Suporte

Para dúvidas sobre o código:
1. Consulte o `README.md` (documentação completa)
2. Veja os comentários no código
3. Execute com `python main.py` e observe a saída

---

**Projeto:** Etapa 1 - Logística  
**Aluno:** Isadora da Silva Maciel - 190108991  
**Universidade:** UnB - Faculdade de Tecnologias
