import random
import time
import json
import requests
import socket
from bs4 import BeautifulSoup
from typing import Tuple
from kafka import KafkaProducer

SUBREDDIT = "news"
KAFKA_SERVER = "kafka:9092"
TOPIC = "input_topic"

KAFKA_SERVER = "kafka"
KAFKA_PORT = 9092
KAFKA_BOOTSTRAP = f"{KAFKA_SERVER}:{KAFKA_PORT}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.google.com/",
    "DNT": "1",
}

MIN_TIMEOUT = 10
MAX_TIMEOUT = 40

print("Scraper started...")

def wait_for_kafka(host, port, timeout=1, retries=30):
    for i in range(retries):
        try:
            s = socket.create_connection((host, port), timeout)
            s.close()
            print("Kafka reachable")
            return True
        except Exception as e:
            print(f"Waiting for kafka ({i+1}/{retries})... {e}")
            time.sleep(2)
    raise RuntimeError("Kafka not reachable after retries")

wait_for_kafka(KAFKA_SERVER, KAFKA_PORT, retries=60)

producer = KafkaProducer(
    bootstrap_servers = KAFKA_SERVER,
    value_serializer = lambda v: json.dumps(v).encode("utf-8")
)

def get_timeout() -> int:
    timeout = random.randint(MIN_TIMEOUT, MAX_TIMEOUT)
    print("Timeout:", timeout)
    return timeout

def scrape_post(url: str) -> Tuple[str, str, list]:
    print("Scraping post:", url)
    r = requests.get(url, headers=HEADERS)
    if r.status_code != 200:
        print("Blocked — status:", r.status_code)
        return "", "", []
    else:
        print("Scraped successfully")

    soup = BeautifulSoup(r.text, "html.parser")

    title_tag = soup.find("a", class_="title")
    title = title_tag.get_text(strip=True) if title_tag else ""

    content = soup.find("div", class_="expando")
    text = content.get_text(" ", strip=True) if content else ""

    comments_div = soup.find_all("div", class_="entry")

    comments = []
    for c in comments_div:
        body = c.find("form")
        if body:
            continue
        comment_text_tag = c.find("div", class_="md")
        if comment_text_tag:
            comment_text = comment_text_tag.get_text(" ", strip=True)
            comments.append(comment_text)

    print("Found", len(comments), "comments")
    return title, text, comments

def scrape_subreddit(subreddit: str = 'brasil') -> None:
    url = f"https://old.reddit.com/r/{subreddit}"
    print("Attempting to scrape subreddit:", url)
    r = requests.get(url, headers=HEADERS)
    if r.status_code != 200:
        print("Blocked on subreddit — status:", r.status_code)
        return
    else:
        print("Scraped successfully")

    soup = BeautifulSoup(r.text, "html.parser")

    posts = soup.find_all("div", class_="thing", attrs={"data-promoted": "false"})

    for post in posts:
        link = post.get("data-permalink")
        if not link:
            continue
        full_url = f"https://old.reddit.com{link}"

        print("Waiting to make next request...")
        time.sleep(get_timeout())
        title, text, comments = scrape_post(full_url)

        for comment in comments:
            message = {
                "post_title": title,
                "post_text": text,
                "comment": comment,
            }

            print("Sending:", message)
            producer.send(TOPIC, value=message)
            producer.flush()

    producer.flush()

while True:
    scrape_subreddit(SUBREDDIT)
    print("Waiting before next scrape...")
    time.sleep(get_timeout())
