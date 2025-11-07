# newsletter_api/database.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def init_db():
    """Initialize the subscribers table if not exists."""
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS subscribers (
            id SERIAL PRIMARY KEY,
            email TEXT UNIQUE NOT NULL
        );
    """)
    conn.commit()
    conn.close()

def add_subscriber(email: str):
    """Add a new subscriber email (ignore duplicates)."""
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO subscribers (email) VALUES (%s)
        ON CONFLICT (email) DO NOTHING;
    """, (email,))
    conn.commit()
    conn.close()

def get_all_subscribers():
    """Return all subscriber emails."""
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    cur = conn.cursor()
    cur.execute("SELECT email FROM subscribers;")
    rows = [r["email"] for r in cur.fetchall()]
    conn.close()
    return rows
