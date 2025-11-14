# 1. Parta da imagem original que você já usa
FROM bde2020/hadoop-namenode:2.0.0-hadoop3.1.3-java8

COPY scripts/WordCount.java /tmp/WordCount.java

WORKDIR /tmp

RUN echo "Compilando WordCount.java..." && \
    javac -classpath `hadoop classpath` WordCount.java && \
    echo "Criando wc.jar..." && \
    jar cf wc.jar WordCount*.class && \
    echo "Limpando arquivo .java..." && \
    rm WordCount.java

WORKDIR /