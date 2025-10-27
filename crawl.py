#!/usr/bin/env python3
"""
crawl_nirmauni_refined.py
More complete text + URL extractor for www.nirmauni.ac.in
- Crawls entire domain (following internal links)
- Extracts visible text from each page
- Saves two .txt files:
    * all_texts.txt  (page-by-page full text)
    * all_urls.txt   (every unique discovered URL)
"""

import time
import requests
from bs4 import BeautifulSoup, Comment
from urllib.parse import urljoin, urlparse, urldefrag
from collections import deque
import urllib.robotparser
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# ---------------- CONFIG -----------------
START_URL = "https://nirmauni.ac.in/"
TARGET_DOMAIN = "nirmauni.ac.in"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; GPTSiteCrawler/1.0)"}
TIMEOUT = 15
DELAY = 0.5
MAX_PAGES = 2000  # increase as needed
OUTPUT_TEXT_FILE = "nirmauni_all_texts.txt"
OUTPUT_URLS_FILE = "nirmauni_urls.txt"
# -----------------------------------------

def normalize_url(base, link):
    try:
        abs_url = urljoin(base, link)
        clean, _ = urldefrag(abs_url)
        return clean.rstrip("/")
    except Exception:
        return None

def same_domain(url):
    try:
        return urlparse(url).netloc.endswith(TARGET_DOMAIN)
    except Exception:
        return False

def visible_text(soup):
    for elem in soup(["script", "style", "noscript", "header", "footer", "meta", "link", "svg", "iframe"]):
        elem.decompose()
    for c in soup.find_all(string=lambda text: isinstance(text, Comment)):
        c.extract()
    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)

def extract_links(soup, base):
    links = set()
    for tag in soup.find_all("a", href=True):
        href = normalize_url(base, tag["href"])
        if href:
            links.add(href)
    return links

def fetch(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT, verify=False)
        r.raise_for_status()
        if "html" not in r.headers.get("Content-Type", "").lower():
            return None
        return r.text
    except Exception as e:
        print(f"[WARN] {url} -> {e}")
        return None

def get_robots_parser(base_url):
    try:
        parsed = urlparse(base_url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(robots_url)
        rp.read()
        return rp
    except Exception:
        return None

def allowed_by_robots(rp, url):
    if rp is None:
        return True
    try:
        return rp.can_fetch("*", url)
    except Exception:
        return True

def crawl(start_url):
    rp = get_robots_parser(start_url)
    visited = set()
    discovered = set()
    queue = deque([start_url])
    pages = []

    while queue and len(visited) < MAX_PAGES:
        url = queue.popleft()
        if url in visited:
            continue
        if not same_domain(url):
            discovered.add(url)
            continue
        if not allowed_by_robots(rp, url):
            print(f"[SKIP] Blocked by robots.txt: {url}")
            continue

        print(f"[CRAWL] {len(visited)+1}: {url}")
        html = fetch(url)
        if not html:
            visited.add(url)
            time.sleep(DELAY)
            continue

        soup = BeautifulSoup(html, "html.parser")
        title = soup.title.string.strip() if soup.title and soup.title.string else ""
        text = visible_text(soup)
        pages.append({"url": url, "title": title, "text": text})

        # extract and enqueue new links
        links = extract_links(soup, url)
        for link in links:
            discovered.add(link)
            if same_domain(link) and link not in visited:
                queue.append(link)

        visited.add(url)
        time.sleep(DELAY)

    return pages, discovered

def save_results(pages, urls):
    with open(OUTPUT_TEXT_FILE, "w", encoding="utf-8") as f:
        for i, p in enumerate(pages, 1):
            f.write("=" * 100 + "\n")
            f.write(f"PAGE {i}: {p['url']}\n")
            f.write(f"TITLE: {p['title']}\n")
            f.write("-" * 100 + "\n")
            f.write(p['text'] + "\n\n")

    with open(OUTPUT_URLS_FILE, "w", encoding="utf-8") as f:
        for u in sorted(urls):
            f.write(u + "\n")

def main():
    print(f"[START] Crawling {START_URL} within domain {TARGET_DOMAIN}")
    pages, urls = crawl(START_URL)
    print(f"[DONE] Crawled {len(pages)} pages, found {len(urls)} URLs.")
    save_results(pages, urls)
    print(f"[SAVED] Text -> {OUTPUT_TEXT_FILE}")
    print(f"[SAVED] URLs -> {OUTPUT_URLS_FILE}")

if __name__ == "__main__":
    main()
