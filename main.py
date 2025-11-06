import json
import os
from datetime import datetime, timezone

from scraper.scrape_utils import scrape_rss, scrape_article_full, scrape_arxiv_official
from scraper.ai_sources import AI_SOURCES

def main():
    all_articles = []

    for source in AI_SOURCES:
        print(f"🔍 Scraping from: {source['name']}")
        articles = []

        if source["type"] == "rss":
            articles = scrape_rss(source["url"], limit=5)
        elif source["type"] == "arxiv_official":
            articles = scrape_arxiv_official(limit=2)

        print(f"   ➤ Found {len(articles)} raw articles")

        # trending AI keywords
        trending_keywords = [
            "GPT", "Gemini", "OpenAI", "Claude", "Anthropic",
            "DeepMind", "LLM", "Agent", "Builder", "AI Studio",
            "Google", "Sam Altman", "Elon Musk", "Sora"
        ]

        articles = [
            a for a in articles
            if any(k.lower() in (a.get("title", "") + a.get("summary", "")).lower()
                   for k in trending_keywords)
        ]
        print(f"   ➤ Filtered to {len(articles)} trending articles")

        curated = articles[:2]  # top 2 per source
        all_articles.extend(curated)
        print(f"   ➤ Selected {len(curated)} top articles")

    ranked_articles = rank_articles(all_articles)

    # Save output
    os.makedirs("data", exist_ok=True)
    output_path = os.path.join("data", "ai_news.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(ranked_articles, f, ensure_ascii=False, indent=2)
    print(f"✅ Saved {len(ranked_articles)} curated & ranked articles to {output_path}")


def rank_articles(articles):
    important_terms = [
        "GPT", "Gemini", "OpenAI", "Anthropic", "LLM", "agents",
        "AI tool", "research", "Google", "Sora", "Sam Altman",
        "Elon Musk", "Musk AI", "DeepMind", "Claude", "Claude AI",
        "ChatGPT", "AI startup", "AI news"
    ]

    def score(article):
        text = (article.get("title", "") + " " + article.get("summary", "")).lower()
        keyword_score = sum(term.lower() in text for term in important_terms)
        freshness_score = 0
        pub_date = article.get("published_date")
        if pub_date:
            try:
                if "T" in pub_date:
                    dt = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
                else:
                    dt = datetime.strptime(pub_date[:25], "%a, %d %b %Y %H:%M:%S")
                delta_hours = (datetime.now(timezone.utc) - dt.replace(tzinfo=timezone.utc)).total_seconds() / 3600
                freshness_score = max(0, 24 - delta_hours) / 24
            except:
                pass
        return keyword_score + freshness_score

    ranked = sorted(articles, key=score, reverse=True)
    return ranked[:8]  # top 8 for daily digest


if __name__ == "__main__":
    main()
