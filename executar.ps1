# Script de Execução Rápida - Sistema de Otimização Logística
# Fulô do Açaí - Etapa 1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SISTEMA DE OTIMIZAÇÃO LOGÍSTICA" -ForegroundColor Cyan
Write-Host "Fulô do Açaí - Etapa 1" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar Python
Write-Host "Verificando instalação do Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Python encontrado: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Python não encontrado!" -ForegroundColor Red
    Write-Host "  Baixe em: https://www.python.org/downloads/" -ForegroundColor Yellow
    pause
    exit
}

Write-Host ""

# Verificar dependências
Write-Host "Verificando dependências..." -ForegroundColor Yellow
$pipList = pip list 2>&1
if ($pipList -match "numpy") {
    Write-Host "✓ Dependências já instaladas" -ForegroundColor Green
} else {
    Write-Host "⚠ Instalando dependências..." -ForegroundColor Yellow
    pip install -r requirements.txt
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Dependências instaladas com sucesso" -ForegroundColor Green
    } else {
        Write-Host "✗ Erro ao instalar dependências" -ForegroundColor Red
        pause
        exit
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "EXECUTANDO SISTEMA..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Executar o sistema
python main.py

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "EXECUÇÃO CONCLUÍDA!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Perguntar se deseja abrir resultados
$resposta = Read-Host "Deseja abrir os resultados? (S/N)"
if ($resposta -eq "S" -or $resposta -eq "s") {
    Write-Host ""
    Write-Host "Abrindo resultados..." -ForegroundColor Yellow
    
    # Abrir gráficos
    if (Test-Path "resultados\previsao_demanda.png") {
        Start-Process "resultados\previsao_demanda.png"
    }
    
    if (Test-Path "resultados\comparacao_cenarios.png") {
        Start-Process "resultados\comparacao_cenarios.png"
    }
    
    # Abrir mapa
    if (Test-Path "resultados\mapa_localizacao.html") {
        Start-Process "resultados\mapa_localizacao.html"
    }
    
    # Abrir relatório
    if (Test-Path "resultados\relatorio_final.txt") {
        Start-Process notepad "resultados\relatorio_final.txt"
    }
    
    Write-Host "✓ Resultados abertos!" -ForegroundColor Green
}

Write-Host ""
Write-Host "Pressione qualquer tecla para sair..."
pause
