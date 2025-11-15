#!/bin/bash
set -e # Sai se algo der errado

echo "Subindo cluster (build se necessário)..."
docker compose up -d --build

# Ponto crucial: Dê um tempo para os serviços estabilizarem.
# Em um cluster real, isso seria mais sofisticado,
# mas um 'sleep' é o suficiente para testes locais.
echo "Aguardando 15 segundos para o HDFS sair do Safe Mode..."
sleep 15

echo "Cluster no ar. Iniciando ingestão de dados..."
./setup_hadoop.sh

echo "✅ Cluster totalmente pronto e dados carregados!"