import sqlite3
import os
from datetime import datetime

DB_PATH = os.getenv("DB_PATH", "data/ai_saas.db")

def get_connection():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Tabel utama: semua AI tools
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            url TEXT,
            category TEXT,
            pricing TEXT,
            upvotes INTEGER DEFAULT 0,
            comments INTEGER DEFAULT 0,
            source TEXT,
            first_seen TEXT,
            last_updated TEXT,
            is_active INTEGER DEFAULT 1,
            UNIQUE(name, source)
        )
    """)

    # Tabel: sinyal pasar (trending, momentum)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS market_signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tool_id INTEGER,
            signal_type TEXT,
            signal_value TEXT,
            detected_at TEXT,
            FOREIGN KEY (tool_id) REFERENCES tools(id)
        )
    """)

    # Tabel: hasil analisis AI (Groq + Gemini)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS insights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT,
            insight_type TEXT,
            category TEXT,
            generated_at TEXT,
            model_used TEXT
        )
    """)

    # Tabel: log scraping runs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scrape_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            tools_found INTEGER,
            tools_added INTEGER,
            status TEXT,
            ran_at TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("[DB] Database initialized successfully")

def insert_tool(tool: dict) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    try:
        cursor.execute("""
            INSERT INTO tools (name, description, url, category, pricing,
                               upvotes, comments, source, first_seen, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            tool.get("name"),
            tool.get("description"),
            tool.get("url"),
            tool.get("category"),
            tool.get("pricing"),
            tool.get("upvotes", 0),
            tool.get("comments", 0),
            tool.get("source"),
            now,
            now
        ))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Tool sudah ada (duplicate), update saja
        cursor.execute("""
            UPDATE tools SET
                description = COALESCE(?, description),
                upvotes = MAX(upvotes, ?),
                comments = MAX(comments, ?),
                last_updated = ?
            WHERE name = ? AND source = ?
        """, (
            tool.get("description"),
            tool.get("upvotes", 0),
            tool.get("comments", 0),
            now,
            tool.get("name"),
            tool.get("source")
        ))
        conn.commit()
        return False
    finally:
        conn.close()

def bulk_insert_tools(tools: list) -> dict:
    added = 0
    updated = 0
    for tool in tools:
        if tool.get("name"):
            result = insert_tool(tool)
            if result:
                added += 1
            else:
                updated += 1
    return {"added": added, "updated": updated, "total": len(tools)}

def get_tools(limit=50, offset=0, source=None, category=None):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM tools WHERE is_active = 1"
    params = []
    if source:
        query += " AND source = ?"
        params.append(source)
    if category:
        query += " AND category LIKE ?"
        params.append(f"%{category}%")
    query += " ORDER BY last_updated DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_stats():
    conn = get_connection()
    cursor = conn.cursor()
    stats = {}
    cursor.execute("SELECT COUNT(*) as total FROM tools")
    stats["total_tools"] = cursor.fetchone()["total"]
    cursor.execute("SELECT source, COUNT(*) as count FROM tools GROUP BY source")
    stats["by_source"] = {row["source"]: row["count"] for row in cursor.fetchall()}
    cursor.execute("SELECT COUNT(*) as total FROM insights")
    stats["total_insights"] = cursor.fetchone()["total"]
    cursor.execute("SELECT MAX(last_updated) as last_run FROM tools")
    stats["last_updated"] = cursor.fetchone()["last_run"]
    conn.close()
    return stats

def log_scrape(source: str, found: int, added: int, status: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO scrape_logs (source, tools_found, tools_added, status, ran_at)
        VALUES (?, ?, ?, ?, ?)
    """, (source, found, added, status, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
