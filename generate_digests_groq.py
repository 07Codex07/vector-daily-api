import json
import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ---------------- CONFIG ----------------
INPUT_JSON = "data/ai_news.json"
OUTPUT_JSON = "data/ai_news_digest.json"
MODEL = "llama-3.1-8b-instant"  # fast & free Groq model

# ---------------- HELPER FUNCTION ----------------
def generate_digest(article):
    """
    Generate 50–70 word digest for a single article using Groq API
    """
    prompt = f"""
You are summarizing AI articles for a daily newsletter.

Title: {article['title']}

Summary: {article.get('summary', '')}

Instructions:
- Write a concise 50–70 word summary using the summary content.
- Include the title at the start.
- Add the article URL at the end.
- Keep it engaging and newsletter-friendly.
- Output only plain text.

URL: {article['url']}
"""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=200
        )
        digest_text = response.choices[0].message.content.strip()
        return digest_text
    except Exception as e:
        print(f"❌ Error generating digest for {article['title']}: {e}")
        return f"{article.get('summary', '')} Read more: {article['url']}"

# ---------------- MAIN SCRIPT ----------------
def main():
    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        articles = json.load(f)

    digests = []
    for article in articles:
        print(f"📝 Generating digest for: {article['title']}")
        digest_text = generate_digest(article)
        digests.append({
            "title": article['title'],
            "digest": digest_text
        })

    os.makedirs("data", exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(digests, f, ensure_ascii=False, indent=2)

    print(f"✅ Saved {len(digests)} digest articles to {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
