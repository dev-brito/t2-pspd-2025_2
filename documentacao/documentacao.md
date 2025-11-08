---
title: LAB2 - Programação para Sistemas Paralelos e Distribuídos T02
subtitle: Estudo sobre Hadoop e Spark
author:
  - ANA LUIZA RODRIGUES DA SILVA - 211030676
  - GUILHERME BRITO VILAS BOAS - 190108011
  - LAÍS RAMOS BARBOSA - 170107574
  - LUCAS LOPES ROCHA - 202023903
  - MATHEUS RAPHAEL SOARES DE OLIVEIRA - 190058587

lang: pt-BR
toc: true
numbersections: true
---

# Introdução

# Conhecendo o Apache Hadoop

## Montagem de um cluster Hadoop básico

Este repositório contém a implementação completa de um cluster Hadoop básico usando containers Docker, incluindo:

- 1 nó master (Namenode)
- 2 nós slaves (Datanodes)
- HDFS configurado e testado
- Interfaces Web funcionais (Namenode, ResourceManager)
- Exemplo WordCount

### Arquitetura do cluster

```
┌─────────────────────────────────────────────────┐
│              MASTER NODE (Namenode)             │
│  - Gerencia metadados do HDFS                   │
│  - Web UI: http://localhost:9870                │
│  - ResourceManager (YARN): http://localhost:8088│
└────────────────────────┬────────────────────────┘
                         │
                ┌────────┴────────┐
                │                 │
        ┌───────▼──────┐  ┌───────▼──────┐
        │ SLAVE NODE 1 │  │ SLAVE NODE 2 │
        │  (Datanode1) │  │  (Datanode2) │
        │ - DataNode   │  │ - DataNode   │
        │ - NodeMgr    │  │ - NodeMgr    │
        └──────────────┘  └──────────────┘
```

### Containers

**namenode:** Master node + ResourceManager
**datanode1 e datanode2:** Workers para HDFS
**nodemanager1 e nodemanager2:** Workers para YARN
**resourcemanager:** Gerenciador de recursos
**historyserver:** Histórico de jobs

## Estrutura de arquivos

```bash
hadoop-cluster/
├── docker-compose.yml                 # Definição dos serviços
├── hadoop.env                         # Configurações Hadoop
├── scripts/
│   ├── mapper.py                      # Mapper para WordCount
│   ├── reducer.py                     # Reducer para WordCount
│   └── WordCount.java                 # Versão Java
├── dados/
│   ├── teste.txt              # Arquivo de teste
```

## Configurações principais

### HDFS (Hadoop Distributed File System)

| Parâmetro | Valor | Descrição |
|-----------|-------|-----------|
| `fs.defaultFS` | `hdfs://namenode:9000` | URI do filesystem |
| `dfs.replication` | `2` | Fator de replicação |
| `dfs.namenode.name.dir` | `/hadoop/dfs/name` | Dir do Namenode |
| `dfs.datanode.data.dir` | `/hadoop/dfs/data` | Dir dos Datanodes |

### YARN (Resource Manager)

| Parâmetro | Valor | Descrição |
|-----------|-------|-----------|
| `yarn.resourcemanager.hostname` | `resourcemanager` | Hostname do RM |
| `yarn.nodemanager.resource.memory-mb` | `4096` | RAM por NodeManager |
| `yarn.nodemanager.resource.cpu-vcores` | `4` | CPUs por NodeManager |

### MapReduce

| Parâmetro | Valor | Descrição |
|-----------|-------|-----------|
| `mapreduce.framework.name` | `yarn` | Framework usado |
| `mapreduce.map.memory.mb` | `512` | RAM para Map tasks |
| `mapreduce.reduce.memory.mb` | `512` | RAM para Reduce tasks |

## Interfaces Web

### 1. Namenode Web UI
- **URL**: http://localhost:9870
- **Funcionalidades**:
  - Status do HDFS
  - DataNodes ativos
  - Uso de espaço
  - Explorador de arquivos
  - Logs do sistema

**Como acessar**:
1. Abra o navegador
2. Acesse `http://localhost:9870`

### 2. ResourceManager Web UI
- **URL**: http://localhost:8088
- **Funcionalidades**:
  - Aplicações em execução
  - Filas de recursos
  - Jobs MapReduce
  - Uso de CPU/Memória
  - Histórico

**Como monitorar um job**:
1. Acesse `http://localhost:8088`
2. Clique em "Applications"
3. Clique no ApplicationID do job em execução
4. Veja progresso de Map e Reduce

## Execução

```bash
cd hadoop-cluster
docker compose up -d

#verificar estado dos containers 
docker ps
```

### Executando Word Count (Python) 

1. Instalar o python nos containers `nodemanager1`, `nodemanager2`, `datanode1`, `datanode2`

```bash
docker exec -it nodemanager1 bash -c "
echo 'deb http://archive.debian.org/debian/ stretch main' > /etc/apt/sources.list && \
echo 'deb http://archive.debian.org/debian-security/ stretch/updates main' >> /etc/apt/sources.list && \
apt-get update && \
apt-get install -y python3 && \
python3 --version
"
```

```bash
docker exec -it nodemanager2 bash -c "
echo 'deb http://archive.debian.org/debian/ stretch main' > /etc/apt/sources.list && \
echo 'deb http://archive.debian.org/debian-security/ stretch/updates main' >> /etc/apt/sources.list && \
apt-get update && \
apt-get install -y python3 && \
python3 --version
"
```

```bash
docker exec -it datanode1 bash -c "
echo 'deb http://archive.debian.org/debian/ stretch main' > /etc/apt/sources.list && \
echo 'deb http://archive.debian.org/debian-security/ stretch/updates main' >> /etc/apt/sources.list && \
apt-get update && \
apt-get install -y python3 && \
python3 --version
"
```

```bash
docker exec -it datanode2 bash -c "
echo 'deb http://archive.debian.org/debian/ stretch main' > /etc/apt/sources.list && \
echo 'deb http://archive.debian.org/debian-security/ stretch/updates main' >> /etc/apt/sources.list && \
apt-get update && \
apt-get install -y python3 && \
python3 --version
"
```

2. Tornar Scripts Executáveis

```bash
chmod +x scripts/*.py
```
3. Copiar Scripts para o Container

```bash
docker cp scripts/mapper.py namenode:/tmp/
docker cp scripts/reducer.py namenode:/tmp/
```

4. Copiar o arquivo de teste para o container

```bash
docker cp dados/teste.txt namenode:/tmp/
```

5. Criar Diretórios no HDFS

```bash
docker exec -it namenode hdfs dfs -mkdir -p /user/hadoop/input
docker exec -it namenode hdfs dfs -mkdir -p /user/hadoop/output

#Fazer o upload do arquivo de teste
docker exec -it namenode hdfs dfs -put /tmp/teste.txt /user/hadoop/input/
```

6. Executar WordCount com Hadoop Streaming

```bash
#Limpar o diretório de saída
docker exec -it namenode hdfs dfs -rm -r /user/hadoop/output 2>/dev/null || true

# Tornar scripts executáveis dentro do container
docker exec -it namenode chmod +x /tmp/mapper.py /tmp/reducer.py

docker exec -it namenode hadoop jar \
  /opt/hadoop-3.1.3/share/hadoop/tools/lib/hadoop-streaming-3.1.3.jar \
  -files /tmp/mapper.py,/tmp/reducer.py \
  -input /user/hadoop/input/teste.txt \
  -output /user/hadoop/output \
  -mapper mapper.py \
  -reducer reducer.py
```

7. Verificar resultados

```bash
docker exec -it namenode hdfs dfs -ls /user/hadoop/output/
docker exec -it namenode hdfs dfs -cat /user/hadoop/output/part-00000
```

- Saída esperada

```
Big	2
Data	2
Hadoop	3
MapReduce	2
O	3
framework	1
importante	1
poderoso	1
processa	1
usa	1
é	3
```

8. Encerrar os containers

```bash
docker compose down
```

### Executando Word Count (Java)

1. Compilar WordCount.java

```bash
#Copiar código Java para o container
docker cp scripts/WordCount.java namenode:/tmp/

#Entrar no container
docker exec -it namenode bash

#Compilar
cd /tmp
javac -classpath `hadoop classpath` WordCount.java

# Criar JAR
jar cf wc.jar WordCount*.class

# Verificar
ls -l wc.jar
exit
```

2. Executar WordCount Java
```bash
#Limpar o diretório de saída
docker exec -it namenode hdfs dfs -rm -r /user/hadoop/output 2>/dev/null || true

# Executar MapReduce com Java
docker exec -it namenode hadoop jar /tmp/wc.jar WordCount \
  /user/hadoop/input/teste.txt \
  /user/hadoop/output

# Ver resultado
docker exec -it namenode hdfs dfs -cat /user/hadoop/output/part-r-00000
```

3. Encerrar os containers

```bash
docker compose down
```

## Materiais utilizados de base

> Notebook do professor disponível no Google Colab: [UnB/ESW/PSPD - Laboratório sobre Hadoop (HDFS e MapReduce)](https://colab.research.google.com/drive/160BLmEgto57pch16XLYqWeW493HYfqLh#scrollTo=f1UpCifppjNB)

> Imagens Docker: [big-data-europe/docker-hadoop](https://github.com/big-data-europe/docker-hadoop)

## Teste de comportamento do framework Hadoop

## Teste de Tolerância a faltas e performance de aplicações Hadoop

# Conhecendo o Apache Spark

# Conclusão
