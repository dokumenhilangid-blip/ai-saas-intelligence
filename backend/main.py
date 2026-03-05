from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import init_db, get_tools, get_stats, get_connection

app = FastAPI(
    title="AI SaaS Intelligence API",
    description="Market intelligence engine for AI SaaS tools",
    version="1.0.0"
)

# CORS — izinkan dashboard Vercel akses API ini
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()
    print("[API] Database ready")

# ─────────────────────────────────────────
# ROOT
# ─────────────────────────────────────────
@app.get("/")
def root():
    return {
        "status": "online",
        "service": "AI SaaS Intelligence API",
        "version": "1.0.0",
        "endpoints": [
            "/tools",
            "/tools/{id}",
            "/stats",
            "/insights",
            "/sources",
            "/categories",
            "/health"
        ]
    }

# ─────────────────────────────────────────
# HEALTH CHECK
# ─────────────────────────────────────────
@app.get("/health")
def health():
    stats = get_stats()
    return {
        "status": "healthy",
        "total_tools": stats.get("total_tools", 0),
        "last_updated": stats.get("last_updated")
    }

# ─────────────────────────────────────────
# TOOLS
# ─────────────────────────────────────────
@app.get("/tools")
def list_tools(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    source: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None
):
    tools = get_tools(limit=limit, offset=offset, source=source, category=category)
    
    # Filter pencarian
    if search:
        search_lower = search.lower()
        tools = [
            t for t in tools
            if search_lower in (t.get("name") or "").lower()
            or search_lower in (t.get("description") or "").lower()
        ]
    
    return {
        "total": len(tools),
        "limit": limit,
        "offset": offset,
        "data": tools
    }

@app.get("/tools/{tool_id}")
def get_tool(tool_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tools WHERE id = ?", (tool_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Tool not found")
    return dict(row)

# ─────────────────────────────────────────
# STATS
# ─────────────────────────────────────────
@app.get("/stats")
def stats():
    return get_stats()

# ─────────────────────────────────────────
# SOURCES
# ─────────────────────────────────────────
@app.get("/sources")
def list_sources():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT source, COUNT(*) as count, MAX(last_updated) as last_updated
        FROM tools
        GROUP BY source
        ORDER BY count DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return {"sources": [dict(row) for row in rows]}

# ─────────────────────────────────────────
# CATEGORIES
# ─────────────────────────────────────────
@app.get("/categories")
def list_categories():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT category, COUNT(*) as count
        FROM tools
        WHERE category IS NOT NULL
        GROUP BY category
        ORDER BY count DESC
        LIMIT 50
    """)
    rows = cursor.fetchall()
    conn.close()
    return {"categories": [dict(row) for row in rows]}

# ─────────────────────────────────────────
# INSIGHTS
# ─────────────────────────────────────────
@app.get("/insights")
def list_insights(
    limit: int = Query(20, ge=1, le=100),
    insight_type: Optional[str] = None
):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM insights"
    params = []
    if insight_type:
        query += " WHERE insight_type = ?"
        params.append(insight_type)
    query += " ORDER BY generated_at DESC LIMIT ?"
    params.append(limit)
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return {
        "total": len(rows),
        "data": [dict(row) for row in rows]
    }

# ─────────────────────────────────────────
# TRENDING
# ─────────────────────────────────────────
@app.get("/trending")
def trending(limit: int = Query(20, ge=1, le=100)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM tools
        WHERE upvotes > 0
        ORDER BY upvotes DESC, comments DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return {
        "total": len(rows),
        "data": [dict(row) for row in rows]
    }

# ─────────────────────────────────────────
# RECENT
# ─────────────────────────────────────────
@app.get("/recent")
def recent(limit: int = Query(20, ge=1, le=100)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM tools
        ORDER BY first_seen DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return {
        "total": len(rows),
        "data": [dict(row) for row in rows]
  }
