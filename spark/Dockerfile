FROM python:3.11-slim-bookworm
LABEL authors="matheusfga"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-17-jdk \
    curl \
    tar \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

ENV SPARK_VERSION=4.0.1
ENV HADOOP_VERSION=3

RUN curl -fsSL https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz \
    -o spark.tgz && \
    tar -xzf spark.tgz -C /opt/ && \
    mv /opt/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} /opt/spark && \
    rm spark.tgz

#RUN mkdir -p /opt/spark/jars
#
#RUN curl -L -o /opt/spark/jars/spark-sql-kafka-0-10_2.13-4.0.1.jar \
# https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.13/4.0.1/spark-sql-kafka-0-10_2.13-4.0.1.jar
#
#RUN curl -L -o /opt/spark/jars/spark-token-provider-kafka-0-10_2.13-4.0.1.jar \
# https://repo1.maven.org/maven2/org/apache/spark/spark-token-provider-kafka-0-10_2.13/4.0.1/spark-token-provider-kafka-0-10_2.13-4.0.1.jar
#
#RUN curl -L -o /opt/spark/jars/kafka-clients-3.4.0.jar \
# https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.4.0/kafka-clients-3.4.0.jar
#
#RUN curl -L -o /opt/spark/jars/commons-pool2-2.11.1.jar \
# https://repo1.maven.org/maven2/org/apache/commons/commons-pool2/2.11.1/commons-pool2-2.11.1.jar

ENV SPARK_HOME=/opt/spark
ENV PATH="$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin"

RUN pip install --no-cache-dir jupyterlab pyspark==4.0.1 vaderSentiment

COPY . .

EXPOSE 8888

CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]
