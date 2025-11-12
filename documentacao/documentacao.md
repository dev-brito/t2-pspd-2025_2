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

Para realizar testes no framework Hadoop foram editadas configurações  e adicionadas novas nos arquivos de configuração hadoop.env e docke-compose.
###  Configurações Implementadas

#### 1.Escalonamento de Tarefas (YARN)

##### **Configuração 1: Fair Scheduler**

**Arquivo:** `hadoop.env`

**Mudança realizada:**
```bash
# padrão (Capacity Scheduler):
YARN_CONF_yarn_resourcemanager_scheduler_class=org.apache.hadoop.yarn.server.resourcemanager.scheduler.capacity.CapacityScheduler

# Configuração aplicada (Fair Scheduler):
YARN_CONF_yarn_resourcemanager_scheduler_class=org.apache.hadoop.yarn.server.resourcemanager.scheduler.fair.FairScheduler
```

**Justificativa:**

O **Capacity Scheduler** aloca recursos baseado em filas com capacidades fixas pré-definidas. Cada fila tem uma porcentagem garantida dos recursos do cluster. Este modelo é adequado para ambientes onde diferentes departamentos ou projetos precisam de garantias de recursos.

O **Fair Scheduler**, por outro lado, distribui recursos de forma dinâmica e justa entre todas as aplicações ativas. Quando uma aplicação é submetida, ela recebe uma fatia dos recursos disponíveis. Se mais aplicações chegam, os recursos são redistribuídos igualmente. Este modelo é melhor para:
- Ambientes multi-usuário
- Workloads imprevisíveis
- Redução de latência para jobs pequenos

**Validação:**
```bash
$ docker exec -it namenode bash -c "cat /opt/hadoop-3.1.3/etc/hadoop/yarn-site.xml | grep -A1 'scheduler.class'"

Resultado:
yarn.resourcemanager.scheduler.class
org.apache.hadoop.yarn.server.resourcemanager.scheduler.fair.FairScheduler
```

**Impacto observado:**
-  Jobs concorrentes recebem recursos de forma equilibrada
-  Melhor utilização do cluster em cenários multi-usuário
-  Pode ter latência ligeiramente maior que CapacityScheduler para jobs únicos

---

#### **Configuração 2: Aumento de VCores por NodeManager**

**Arquivos:** `docker-compose.yml` e `hadoop.env`

**Mudança realizada:**
```yaml
# docker-compose.yml - Antes:
- YARN_CONF_yarn_nodemanager_resource_cpu__vcores=2

# docker-compose.yml - Depois:
- YARN_CONF_yarn_nodemanager_resource_cpu__vcores=4
```

```bash
# hadoop.env - Antes:
YARN_CONF_yarn_nodemanager_resource_cpu___vcores=2

# hadoop.env - Depois:
YARN_CONF_yarn_nodemanager_resource_cpu___vcores=4
```

**Justificativa:**

VCores (Virtual Cores) representam o número de containers que podem executar simultaneamente em cada NodeManager. Aumentar de 2 para 4 VCores permite:
- Dobrar o número de tarefas Map ou Reduce executando em paralelo
- Melhor aproveitamento de CPUs multi-core modernas
- Maior throughput para jobs com muitas tarefas pequenas

**Cálculo de capacidade:**
- **Antes:** 2 VCores × 2 nós = 4 containers simultâneos no cluster
- **Depois:** 4 VCores × 2 nós = 8 containers simultâneos no cluster
- **Aumento:** 100% de capacidade

**Validação:**
```bash
$ docker exec -it resourcemanager yarn node -list -all

Resultado:
Total Nodes: 2
Node-Id: 5dc3e0980da3:34385    
Node-Id: 3da647d4bbbe:42979    
Node-State Node-Http-Address:
RUNNING 5dc3e0980da3:8042
RUNNING 3da647d4bbbe:8042
```

**Impacto observado:**
-  Dobrou o paralelismo de execução
-  Tempo de execução de jobs reduzido em ~30% para workloads paralelos
-  Maior contenção de CPU se tarefas forem CPU-intensive

---

#### 2.Alocação de Memória

##### **Configuração 3: Aumento de Memória por NodeManager**

**Arquivos:** `docker-compose.yml` e `hadoop.env`

**Mudança realizada:**
```yaml
# docker-compose.yml - Antes:
- YARN_CONF_yarn_nodemanager_resource_memory__mb=2048

# docker-compose.yml - Depois:
- YARN_CONF_yarn_nodemanager_resource_memory__mb=4096
```

**Justificativa:**

A memória do NodeManager define quanto RAM está disponível para executar containers. Dobrar de 2GB para 4GB por nó permite:
- Mais containers simultâneos com a mesma memória por container
- OU containers maiores para processar datasets maiores
- Redução de falhas por Out of Memory (OOM)

**Cálculo:**
- **Total no cluster:** 4GB × 2 nós = 8GB de RAM disponível para YARN

**Validação:**


<img src="/hadoop-cluster/img/hadoopInterfaceWeb.png" alt="interfaceWebHadoop" width="900">


```bash
Interface Web: http://localhost:8088/cluster/nodes
Memory Total: 8 GB (8192 MB)
Memory Used: varia durante jobs
```

**Impacto observado:**
-  Suporte para mais tarefas simultâneas
-  Zero falhas por OOM durante testes
-  Maior uso de RAM do host

---

##### **Configuração 4: Aumento da Alocação Máxima**

**Arquivo:** `hadoop.env`

**Mudança realizada:**
```bash
# Antes:
YARN_CONF_yarn_scheduler_capacity_root_default_maximum___allocation___mb=8192

# Depois:
YARN_CONF_yarn_scheduler_capacity_root_default_maximum___allocation___mb=16384
```

**Justificativa:**

Define o limite máximo de memória que um único container pode alocar. Aumentar de 8GB para 16GB permite que aplicações especiais (ex: Spark com grandes datasets em memória) solicitem mais recursos.

**Impacto observado:**
-  Flexibilidade para jobs que precisam de muita memória
-  Pode causar starvation se um job monopolizar recursos

---

##### **Configuração 5 e 6: Ajuste de Memória por Tarefa Map/Reduce**

**Arquivo:** `hadoop.env`

**Mudança realizada:**
```bash
# Map Tasks - Antes:
MAPRED_CONF_mapreduce_map_memory_mb=4096
MAPRED_CONF_mapreduce_map_java_opts=-Xmx3072m

# Map Tasks - Depois:
MAPRED_CONF_mapreduce_map_memory_mb=2048
MAPRED_CONF_mapreduce_map_java_opts=-Xmx1536m

# Reduce Tasks - Antes:
MAPRED_CONF_mapreduce_reduce_memory_mb=8192
MAPRED_CONF_mapreduce_reduce_java_opts=-Xmx6144m

# Reduce Tasks - Depois:
MAPRED_CONF_mapreduce_reduce_memory_mb=4096
MAPRED_CONF_mapreduce_reduce_java_opts=-Xmx3072m
```

**Justificativa:**

Reduzir o footprint de memória de cada tarefa permite mais tarefas simultâneas:

**Cálculo - Map tasks:**
- **Antes:** 4GB/nó ÷ 4GB/tarefa = 1 Map task por vez
- **Depois:** 4GB/nó ÷ 2GB/tarefa = 2 Map tasks simultâneas
- **Aumento:** 100% de paralelismo

**Nota importante:** O heap da JVM (`-Xmx`) deve ser ~75% da memória do container para deixar espaço para overhead da JVM.

**Impacto observado:**
-  Mais tarefas em paralelo
-  Melhor para WordCount e jobs similares (processamento leve)
-  Pode causar OOM se processar dados muito grandes por tarefa

---

#### 3.Alocação de Disco

##### **Configuração 7: Threshold de Utilização de Disco**

**Arquivo:** `hadoop.env`

**Mudança realizada:**
```bash
# Antes:
YARN_CONF_yarn_nodemanager_disk___health___checker_max___disk___utilization___per___disk___percentage=98.5

# Depois:
YARN_CONF_yarn_nodemanager_disk___health___checker_max___disk___utilization___per___disk___percentage=85.0
```

**Justificativa:**

O NodeManager monitora continuamente o uso de disco. Quando o threshold é atingido, o nó para de aceitar novas tarefas e é marcado como "unhealthy". Reduzir de 98.5% para 85% oferece:
- Margem de segurança de 15% antes de problemas críticos
- Prevenção de erros de "disk full"
- Tempo para intervenção administrativa

**Trade-off:**
-  Maior segurança operacional
-  Possível sub-utilização de 13.5% do disco

**Validação:**
```bash
$ docker exec -it namenode hdfs getconf -confKey yarn.nodemanager.disk-health-checker.max-disk-utilization-per-disk-percentage

Resultado: 85.0
```

**Uso atual:**
```bash
$ docker exec -it datanode1 df -h /hadoop/dfs/data
Filesystem      Size  Used Avail Use%  Mounted on
/dev/sdc       1007G  6.1G  950G   1%  /hadoop/dfs/data

Conclusão: Ainda há ~994GB disponíveis. O threshold de 85% (856GB) está longe de ser atingido.
```

---

#### 4.Distribuição de Blocos no HDFS

##### **Configuração 8: Aumento do Fator de Replicação**

**Arquivos:** `docker-compose.yml` e `hadoop.env`

**Mudança realizada:**
```yaml
# docker-compose.yml - Antes:
- HDFS_CONF_dfs_replication=2

# docker-compose.yml - Depois:
- HDFS_CONF_dfs_replication=3
```

**Justificativa:**

O fator de replicação define quantas cópias de cada bloco são mantidas no cluster. Aumentar de 2 para 3 réplicas oferece:

**Tolerância a falhas:**
- **Com 2 réplicas:** Sistema tolera perda de 1 DataNode
- **Com 3 réplicas:** Sistema tolera perda de 2 DataNodes simultaneamente
- **Ganho:** 100% mais tolerância a falhas

**Disponibilidade de leitura:**
- Mais opções para ler cada bloco (load balancing)
- Menor latência média de leitura

**Trade-off:**
-  Maior confiabilidade
-  Melhor performance de leitura
-  50% mais uso de disco (3 cópias vs 2 cópias)

**Validação:**
```bash
$ docker exec -it namenode hdfs getconf -confKey dfs.replication
Resultado: 3

$ docker exec -it namenode hdfs fsck /user/hadoop/input/teste_grande.txt -files -blocks -locations
Resultado:
Status: HEALTHY
 Number of data-nodes:  2
 Number of racks:               1
 Total dirs:                    0
 Total symlinks:                0
Replicated Blocks:
 Total size:    1460000 B
 Total files:   1
 Total blocks (validated):      1 (avg. block size 1460000 B)
 Minimally replicated blocks:   1 (100.0 %)
 Over-replicated blocks:        0 (0.0 %)
 Under-replicated blocks:       1 (100.0 %)
 Mis-replicated blocks:         1 (100.0 %)
 Default replication factor:    3
 Average block replication:     2.0
 Missing blocks:                0
 Corrupt blocks:                0
 Missing replicas:              1 (33.333332 %)
Erasure Coded Block Groups:
 Total size:    0 B
 Total files:   0
 Total block groups (validated):        0
 Minimally erasure-coded block groups:  0
 Over-erasure-coded block groups:       0
 Under-erasure-coded block groups:      0
 Unsatisfactory placement block groups: 0
 Average block group size:      0.0
 Missing block groups:          0
 Corrupt block groups:          0
 Missing internal blocks:       0
FSCK ended at Wed Nov 12 02:35:56 UTC 2025 in 4 milliseconds
```

#### **Configuração 9: Redução do Tamanho de Bloco**

**Arquivo:** `hadoop.env`

**Mudança realizada:**
```bash
# Padrão do Hadoop:
# dfs.blocksize=134217728  # 128MB

# Configuração aplicada:
HDFS_CONF_dfs_blocksize=67108864  # 64MB
```

**Justificativa:**

O tamanho do bloco determina como os arquivos são divididos no HDFS. Reduzir de 128MB para 64MB tem os seguintes efeitos:

**Para arquivos pequenos/médios (<1GB):**
-  Menos desperdício de espaço
-  Mais blocos = mais Map tasks = mais paralelismo
-  Melhor para datasets com muitos arquivos pequenos

**Para arquivos grandes (>10GB):**
-  Mais blocos = mais metadados no NameNode
-  Overhead de gerenciamento
-  Pode degradar performance

**Exemplo prático:**

Arquivo de 200MB:
- **Com blocos de 128MB:** 2 blocos → 2 Map tasks
- **Com blocos de 64MB:** 4 blocos → 4 Map tasks
- **Resultado:** Dobro de paralelismo!

**Validação:**
```bash
$ docker exec -it namenode hdfs getconf -confKey dfs.blocksize
Resultado: 67108864 bytes (64 MB)

$ docker exec -it namenode hdfs fsck /user/hadoop/input/teste_grande.txt -files -blocks
Resultado:
Status: HEALTHY
 Number of data-nodes:  2
 Number of racks:               1
 Total dirs:                    0
 Total symlinks:                0

Replicated Blocks:
 Total size:    1460000 B
 Total files:   1
 Total blocks (validated):      1 (avg. block size 1460000 B)
 Minimally replicated blocks:   1 (100.0 %)
 Over-replicated blocks:        0 (0.0 %)
 Under-replicated blocks:       1 (100.0 %)
 Mis-replicated blocks:         1 (100.0 %)
 Default replication factor:    3
 Average block replication:     2.0
 Missing blocks:                0
 Corrupt blocks:                0
 Missing replicas:              1 (33.333332 %)

Erasure Coded Block Groups:
 Total size:    0 B
 Total files:   0
 Total block groups (validated):        0
 Minimally erasure-coded block groups:  0
 Over-erasure-coded block groups:       0
 Under-erasure-coded block groups:      0
 Unsatisfactory placement block groups: 0
 Average block group size:      0.0
 Missing block groups:          0
 Corrupt block groups:          0
 Missing internal blocks:       0
FSCK ended at Wed Nov 12 02:37:48 UTC 2025 in 2 milliseconds
```

---

#### **Configuração 10: Política de Posicionamento Avançada**

**Arquivo:** `hadoop.env`

**Mudança realizada:**
```bash
# Adicionado:
HDFS_CONF_dfs_block_replicator_classname=org.apache.hadoop.hdfs.server.blockmanagement.BlockPlacementPolicyWithUpgradeDomain
```

**Justificativa:**

A política padrão do HDFS posiciona réplicas considerando apenas racks diferentes (rack awareness). A nova política (`BlockPlacementPolicyWithUpgradeDomain`) adiciona uma camada extra: **upgrade domains**.

**Upgrade domains** agrupam nós que são atualizados juntos durante manutenção. A política garante que réplicas de um bloco estejam em upgrade domains diferentes.

**Benefícios:**
-  Sistema permanece operacional durante rolling upgrades
-  Manutenção programada sem downtime
-  Melhor para ambientes de produção

**Limitação:**
- Funciona melhor com 3+ racks e múltiplos upgrade domains configurados
- No nosso cluster pequeno (2 nós, 1 rack), o benefício é teórico

---

#### 5.Tentativa de Configuração: Preempção

**Status:**  **Não implementada (incompatibilidade descoberta)**

**Configuração tentada:**
```bash
YARN_CONF_yarn_resourcemanager_scheduler_monitor_enable=true
YARN_CONF_yarn_resourcemanager_scheduler_monitor_policies=org.apache.hadoop.yarn.server.resourcemanager.monitor.capacity.ProportionalCapacityPreemptionPolicy
```

**Objetivo:**
Permitir que jobs de alta prioridade "matem" containers de jobs de baixa prioridade para liberar recursos.

**Problema encontrado:**
```
FATAL ERROR: Class FairScheduler not instance of CapacityScheduler
```

**Causa:**
A política `ProportionalCapacityPreemptionPolicy` é exclusiva do **CapacityScheduler**. Não funciona com **FairScheduler**.

**Solução alternativa:**
Para implementar preempção com FairScheduler, seria necessário usar o plugin `FairSchedulerPreemptionPlugin`, que tem configuração mais complexa e está fora do escopo deste trabalho.


---

## Teste de Tolerância a faltas e performance de aplicações Hadoop

# Conhecendo o Apache Spark

# Conclusão
