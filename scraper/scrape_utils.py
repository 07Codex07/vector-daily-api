# scrape_utils.py
import requests
from bs4 import BeautifulSoup
from newspaper import Article
from requests_html import HTMLSession
import re
from langdetect import detect
from datetime import datetime, timezone

# --------------------------- CLEANING ---------------------------
def clean_text(text):
    """Remove extra spaces, non-ASCII characters, and URLs."""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    return text.strip()

# --------------------------- RELEVANCE FILTER ---------------------------
def is_relevant_article(title, summary):
    text = f"{title} {summary}".lower()
    try:
        if detect(title) != "en":
            return False
    except:
        return False
    bad_terms = ["poem", "fiction", "story", "artwork", "painting",
                 "religion", "culture", "movie", "music"]
    if any(term in text for term in bad_terms):
        return False
    return True

# --------------------------- RSS SCRAPER ---------------------------
def scrape_rss(feed_url, limit=5):
    """Scrape RSS feed and return top `limit` English AI articles."""
    try:
        response = requests.get(feed_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        soup = BeautifulSoup(response.text, 'xml')
        items = soup.find_all('item')
    except:
        return []

    articles = []
    for item in items:
        title = item.title.text if item.title else "Untitled"
        desc = item.description.text if item.description else ""
        if not is_relevant_article(title, desc):
            continue

        link = item.link.text if item.link else None
        pub_date = item.pubDate.text if item.pubDate else None
        image = None

        if '<img' in desc:
            img_soup = BeautifulSoup(desc, 'html.parser')
            img_tag = img_soup.find('img')
            if img_tag:
                image = img_tag.get('src')

        articles.append({
            "title": clean_text(title),
            "url": link,
            "image": image,
            "published_date": pub_date,
            "summary": None
        })
        if len(articles) >= limit:
            break

    for a in articles:
        full = scrape_article_full(a["url"])
        if full:
            a["summary"] = full.get("summary")
            a["image"] = a.get("image") or full.get("image")
    return articles

# --------------------------- OFFICIAL ARXIV SCRAPER ---------------------------
def scrape_arxiv_official(limit=2):
    """Fetch latest cs.AI papers from official Arxiv API."""
    url = f"https://export.arxiv.org/api/query?search_query=cat:cs.AI&sortBy=submittedDate&max_results={limit}"
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'xml')
        entries = soup.find_all('entry')
    except:
        return []

    articles = []
    for e in entries:
        title = e.title.text.strip()
        summary = e.summary.text.strip()
        link = e.id.text.strip()
        published = e.published.text.strip()
        articles.append({
            "title": title,
            "summary": " ".join(summary.split()[:200]),
            "url": link,
            "image": "https://arxiv.org/static/browse/0.3.4/images/arxiv-logo-fb.png",
            "published_date": published
        })
    return articles

# --------------------------- FULL ARTICLE SCRAPER ---------------------------
def scrape_article_full(url, max_words=200):
    """Fetch full article; handles dynamic pages with JS if needed."""
    try:
        # static scrape
        article = Article(url)
        article.download()
        article.parse()
        text = clean_text(article.text)
        if len(text.split()) < 50:
            raise ValueError("Too short, fallback to JS render")
    except:
        try:
            # dynamic render
            session = HTMLSession()
            r = session.get(url)
            r.html.render(timeout=20)
            text = clean_text(r.html.text)
        except:
            # fallback empty
            return {"title": "", "summary": "Summary not available.", "image": None, "url": url}

    words = text.split()
    summary = " ".join(words[:max_words])
    return {"title": article.title if article else url, "summary": summary,
            "image": article.top_image if article else None, "url": url}
