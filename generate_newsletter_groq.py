import json
import os
import re
from groq import Groq
from dotenv import load_dotenv

# ---------------- CONFIG ----------------
INPUT_JSON = "data/ai_news_digest.json"
OUTPUT_JSON = "data/ai_newsletter.json"
MODEL = "llama-3.1-8b-instant"

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def extract_url_and_summary(digest_text):
    """
    Extracts the URL from the end of the digest (if any)
    and returns (clean_summary, url).
    """
    url_match = re.search(r"(https?://\S+)", digest_text.strip().split()[-1])
    if url_match:
        url = url_match.group(0)
        # Remove the URL from the digest text
        clean_text = digest_text.replace(url, "").strip()
    else:
        url = None
        clean_text = digest_text.strip()
    return clean_text, url


def sanitize_text(text: str) -> str:
    """Cleans LLM output to make it JSON-safe."""
    text = text.strip()
    text = re.sub(r"```(?:json)?", "", text)
    text = text.strip("` \n")
    text = text.replace("\r", "")
    text = re.sub(r"[\x00-\x1F\x7F]", "", text)  # remove control chars
    return text


def safe_parse_json(text: str):
    """Tries to safely parse JSON output, falling back to plain text if invalid."""
    text = sanitize_text(text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]+\}", text)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass
        return {
            "subject": "AI Daily Newsletter",
            "newsletter_body": f"<html><body><pre>{text}</pre></body></html>",
        }


def create_newsletter(digests):
    # Extract title, clean digest, and URL properly
    structured_articles = []
    for d in digests:
        summary, url = extract_url_and_summary(d["digest"])
        structured_articles.append({
            "title": d["title"],
            "summary": summary,
            "url": url or "No link available"
        })

    digest_text = "\n\n".join(
        [
            f"Title: {a['title']}\nDigest: {a['summary']}\nURL: {a['url']}"
            for a in structured_articles
        ]
    )

    prompt = f"""
You are a professional AI journalist writing for *The Vector Daily*, a credible AI and technology newsletter.

Below are today's AI article digests:
{digest_text}

Generate a **formal, professional HTML newsletter** with this structure:

1. A 5–6 word professional **subject line**.
2. A **newsletter body (HTML)** that includes:
   - A 2–3 line introduction.
   - One section per article:
       - The article title in <b>bold</b>.
       - A rewritten summary of 4–6 sentences (clear, professional, not repetitive).
       - Then a line:  
         <i>To read the full article → <a href="ARTICLE_URL">Click here</a></i>
         (Replace ARTICLE_URL with the provided link.)
   - A **Final Summary paragraph** (4–5 sentences) connecting all major trends.
   - A **moderate or difficult AI algorithm riddle/question** at the end.
   - Close with: “Stay curious, The Vector Daily Team”.

Tone:
- Professional, informative, slightly conversational.
- No markdown, emojis, or code blocks.
- Keep formatting clean and email-friendly.

Output valid JSON:
{{
  "subject": "...",
  "newsletter_body": "<html> ... </html>"
}}
"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1800,
        )

        raw_output = response.choices[0].message.content.strip()
        clean_output = sanitize_text(raw_output)
        return safe_parse_json(clean_output)

    except Exception as e:
        print(f"❌ Error creating newsletter: {e}")
        return None


def main():
    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        digests = json.load(f)

    print("🧠 Generating newsletter summary...")
    result = create_newsletter(digests)

    if result:
        result["newsletter_body"] = style_newsletter(result["newsletter_body"])
        os.makedirs("data", exist_ok=True)
        with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"✅ Newsletter generated and saved to {OUTPUT_JSON}")

        with open("data/vector_daily.html", "w", encoding="utf-8") as f:
            f.write(result["newsletter_body"])
            print("🌐 Styled HTML preview saved to data/vector_daily.html")

    else:
        print("⚠️ Newsletter generation failed.")

def style_newsletter(html_content: str):
    """Wraps the generated newsletter HTML in a clean, responsive layout."""
    styled_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The Vector Daily</title>
<style>
  /* Base Styles */
  body {{
    font-family: 'Inter', Arial, sans-serif;
    background-color: #f5f7fa;
    margin: 0;
    padding: 0;
    color: #333;
    -webkit-font-smoothing: antialiased;
  }}
  .container {{
    max-width: 700px;
    margin: 30px auto;
    background: #ffffff;
    border-radius: 14px;
    overflow: hidden;
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
  }}

  /* Header */
  .header {{
    background: linear-gradient(135deg, #0057e7, #003ea3);
    color: #fff;
    text-align: center;
    padding: 50px 20px 40px;
  }}
  .header img {{
    max-height: 70px;
    margin-bottom: 20px;
    border-radius: 8px;
  }}
  .header h1 {{
    font-size: 36px;
    margin: 0;
    font-weight: 800;
    letter-spacing: 0.5px;
  }}

  /* Content */
  .content {{
    padding: 30px 40px;
    line-height: 1.8;
  }}
  .content h2 {{
    color: #111;
    font-size: 24px;
    margin-top: 35px;
    font-weight: 700;
  }}
  .content p {{
    margin: 12px 0;
    font-size: 17px;
    color: #444;
  }}
  .highlight {{
    background: #f0f5ff;
    border-left: 4px solid #0057e7;
    padding: 12px 16px;
    border-radius: 6px;
    font-size: 15px;
  }}
  a {{
    color: #0057e7;
    font-weight: 600;
    text-decoration: none;
  }}
  a:hover {{
    text-decoration: underline;
  }}
  hr {{
    border: 0;
    border-top: 1px solid #eaeaea;
    margin: 30px 0;
  }}

  /* Footer */
  .footer {{
    background-color: #f8f8f8;
    padding: 18px 25px;
    text-align: center;
    font-size: 14px;
    color: #666;
    border-top: 1px solid #e4e4e4;
  }}
  .footer a {{
    color: #0057e7;
    text-decoration: none;
  }}

  /* Responsive */
  @media (max-width: 600px) {{
    .content {{
      padding: 20px;
    }}
    .header h1 {{
      font-size: 28px;
    }}
    .content h2 {{
      font-size: 20px;
    }}
  }}
</style>
</head>
<body>
  <div class="container">
    <div class="header">
      <img src="cid:logo" alt="The Vector Daily Logo" style="width:120px; height:auto; border:none; margin-bottom:10px;">
      <h1>The Vector Daily</h1>
    </div>

    <div class="content">
      {html_content}
      <hr>
      <p class="highlight">
        Stay curious. Keep exploring AI and technology with <b>The Vector Daily</b> — your trusted digest for innovation, strategy, and breakthroughs.
      </p>
    </div>

    <div class="footer">
      You’re receiving this email because you subscribed to <b>The Vector Daily</b>.<br>
      <a href="#">Unsubscribe</a> • <a href="#">Privacy Policy</a>
    </div>
  </div>
</body>
</html>
"""
    return styled_html




if __name__ == "__main__":
    main()
