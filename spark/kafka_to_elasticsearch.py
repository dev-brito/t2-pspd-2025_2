import json
import time
import socket
import re
from collections import Counter
from kafka import KafkaConsumer
from elasticsearch import Elasticsearch
from datetime import datetime

KAFKA_SERVER = "kafka"
KAFKA_PORT = 9092
KAFKA_BOOTSTRAP = f"{KAFKA_SERVER}:{KAFKA_PORT}"
TOPIC = "output_topic"

ELASTICSEARCH_HOST = "elasticsearch"
ELASTICSEARCH_PORT = 9200
ELASTICSEARCH_URL = f"http://{ELASTICSEARCH_HOST}:{ELASTICSEARCH_PORT}"

INDEX_NAME = "reddit-sentiment"

print("Kafka to ElasticSearch consumer started...")

def wait_for_service(host, port, timeout=1, retries=60):
    """Wait for a service to be reachable."""
    for i in range(retries):
        try:
            s = socket.create_connection((host, port), timeout)
            s.close()
            print(f"{host}:{port} is reachable")
            return True
        except Exception as e:
            print(f"Waiting for {host}:{port} ({i+1}/{retries})... {e}")
            time.sleep(2)
    raise RuntimeError(f"{host}:{port} not reachable after retries")

# Wait for Kafka and ElasticSearch to be ready
wait_for_service(KAFKA_SERVER, KAFKA_PORT)
wait_for_service(ELASTICSEARCH_HOST, ELASTICSEARCH_PORT)

# Initialize ElasticSearch client
es = Elasticsearch(
    [ELASTICSEARCH_URL],
    verify_certs=False,
    ssl_show_warn=False,
    request_timeout=30,
    max_retries=3,
    retry_on_timeout=True
)

# Wait for ElasticSearch to be fully ready
max_retries = 30
for i in range(max_retries):
    try:
        health = es.cluster.health()
        if health:
            print("ElasticSearch is ready")
            print(f"Cluster status: {health.get('status', 'unknown')}")
            break
    except Exception as e:
        print(f"Waiting for ElasticSearch to be ready ({i+1}/{max_retries})... {e}")
        time.sleep(2)
else:
    print("WARNING: Could not verify ElasticSearch health, but continuing anyway...")

# Create index with mapping if it doesn't exist
if not es.indices.exists(index=INDEX_NAME):
    mapping = {
        "mappings": {
            "properties": {
                "post_title": {"type": "text"},
                "post_text": {"type": "text"},
                "comment": {"type": "text"},
                "sentiment": {
                    "properties": {
                        "neg": {"type": "float"},
                        "neu": {"type": "float"},
                        "pos": {"type": "float"},
                        "compound": {"type": "float"}
                    }
                },
                "timestamp": {"type": "date"},
                "sentiment_label": {"type": "keyword"},
                "keywords": {"type": "keyword"}
            }
        }
    }
    es.indices.create(index=INDEX_NAME, body=mapping)
    print(f"Created index: {INDEX_NAME}")
else:
    print(f"Index {INDEX_NAME} already exists")

# Initialize Kafka consumer
consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=KAFKA_BOOTSTRAP,
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='elasticsearch-consumer-group'
)

print(f"Consuming messages from topic: {TOPIC}")

def get_sentiment_label(compound_score):
    """Classify sentiment based on compound score."""
    if compound_score >= 0.05:
        return "positive"
    elif compound_score <= -0.05:
        return "negative"
    else:
        return "neutral"

def extract_keywords(text, min_length=4, top_n=20):
    """Extract keywords from text, removing common stopwords."""
    if not text:
        return []
    
    stopwords = {
        'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
        'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
        'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
        'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their',
        'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go',
        'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know',
        'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them',
        'see', 'other', 'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over',
        'think', 'also', 'back', 'after', 'use', 'two', 'how', 'our', 'work',
        'first', 'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these',
        'give', 'day', 'most', 'us', 'is', 'was', 'are', 'been', 'has', 'had',
        'were', 'said', 'did', 'having', 'may', 'should', 'am', 'being', 'does',
        'removed', 'deleted'
    }
    
    text = text.lower()
    words = re.findall(r'\b[a-z]+\b', text)
    words = [w for w in words if w not in stopwords and len(w) >= min_length]
    
    word_counts = Counter(words)
    return [word for word, count in word_counts.most_common(top_n)]

# Consume messages and send to ElasticSearch
for message in consumer:
    try:
        data = message.value
        print(f"Received message: {data}")
        
        # Parse sentiment JSON string
        if isinstance(data.get('sentiment'), str):
            sentiment_data = json.loads(data['sentiment'])
        else:
            sentiment_data = data.get('sentiment', {})
        
        # Extract keywords from title and comment
        title = data.get("post_title", "")
        comment = data.get("comment", "")
        combined_text = f"{title} {comment}"
        keywords = extract_keywords(combined_text)
        
        # Prepare document for ElasticSearch
        doc = {
            "post_title": title,
            "post_text": data.get("post_text", ""),
            "comment": comment,
            "sentiment": sentiment_data,
            "sentiment_label": get_sentiment_label(sentiment_data.get("compound", 0.0)),
            "keywords": keywords,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Index document in ElasticSearch
        response = es.index(index=INDEX_NAME, document=doc)
        print(f"Indexed document: {response['_id']}")
        
    except Exception as e:
        print(f"Error processing message: {e}")
        continue

