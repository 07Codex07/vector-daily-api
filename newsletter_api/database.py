# newsletter_api/database.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_conn():
    """Helper: get a new DB connection."""
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


# ======================================================
# INIT
# ======================================================
def init_db():
    """Initialize the subscribers table if not exists."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS subscribers (
            id SERIAL PRIMARY KEY,
            email TEXT UNIQUE NOT NULL
        );
    """)
    conn.commit()
    conn.close()


# ======================================================
# SUBSCRIBE
# ======================================================
def add_subscriber(email: str):
    """Add a new subscriber email (ignore duplicates)."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO subscribers (email)
        VALUES (%s)
        ON CONFLICT (email) DO NOTHING;
    """, (email,))
    conn.commit()
    conn.close()


# ======================================================
# CHECK
# ======================================================
def is_subscribed(email: str) -> bool:
    """Return True if email exists in DB."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM subscribers WHERE email = %s;", (email,))
    exists = cur.fetchone() is not None
    conn.close()
    return exists


# ======================================================
# UNSUBSCRIBE
# ======================================================
def remove_subscriber(email: str):
    """Remove a subscriber email."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM subscribers WHERE email = %s;", (email,))
    conn.commit()
    conn.close()


# ======================================================
# FETCH ALL
# ======================================================
def get_all_subscribers():
    """Return all subscriber emails."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT email FROM subscribers;")
    rows = [r["email"] for r in cur.fetchall()]
    conn.close()
    return rows
