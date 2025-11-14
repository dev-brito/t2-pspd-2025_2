#!/bin/bash
set -e # Sai se qualquer comando falhar

echo "Hadoop Setup (Runtime) Iniciado..."

# 1. Copiar arquivo de dados para o container
echo "➡️  Copiando 'big-file.txt' para o namenode..."
docker cp dados/big-file.txt namenode:/tmp/

# 2. Criar diretórios no HDFS
echo "➡️  Criando diretórios no HDFS..."
docker exec namenode hdfs dfs -mkdir -p /user/hadoop/input
docker exec namenode hdfs dfs -mkdir -p /user/hadoop/output

# 3. Mover arquivo do /tmp do container para o HDFS
echo "➡️  Movendo 'big-file.txt' para HDFS /user/hadoop/input/"
docker exec namenode hdfs dfs -put /tmp/big-file.txt /user/hadoop/input/

# 4. Verificação (Opcional, mas recomendado)
echo "➡️  Verificando se /tmp/wc.jar (criado no build) existe:"
docker exec namenode ls -l /tmp/wc.jar

echo "✅ Setup concluído! Os dados estão no HDFS."