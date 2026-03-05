from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import init_db, get_tools, get_stats, get_connection

app = FastAPI(title="AI SaaS Intelligence API", version="1.0.0")

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

@app.get("/")
def root():
    return {"status": "online", "version": "1.0.0"}

@app.get("/health")
def health():
    stats = get_stats()
    return {"status": "healthy", "total_tools": stats.get("total_tools", 0)}

@app.get("/tools")
def list_tools(limit: int = Query(50), offset: int = Query(0), source: Optional[str] = None):
    tools = get_tools(limit=limit, offset=offset, source=source)
    return {"total": len(tools), "data": tools}

@app.get("/stats")
def stats():
    return get_stats()

@app.get("/sources")
def list_sources():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT source, COUNT(*) as count FROM tools GROUP BY source ORDER BY count DESC")
    rows = cursor.fetchall()
    conn.close()
    return {"sources": [dict(row) for row in rows]}

@app.get("/trending")
def trending(limit: int = Query(20)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tools WHERE upvotes > 0 ORDER BY upvotes DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return {"total": len(rows), "data": [dict(row) for row in rows]}

@app.get("/recent")
def recent(limit: int = Query(20)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tools ORDER BY first_seen DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return {"total": len(rows), "data": [dict(row) for row in rows]}

@app.get("/insights")
def list_insights(limit: int = Query(20)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM insights ORDER BY generated_at DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return {"total": len(rows), "data": [dict(row) for row in rows]}

@app.get("/categories")
def list_categories():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT category, COUNT(*) as count FROM tools WHERE category IS NOT NULL GROUP BY category ORDER BY count DESC LIMIT 50")
    rows = cursor.fetchall()
    conn.close()
    return {"categories": [dict(row) for row in rows]}

@app.post("/tools/add")
async def add_tool(request: Request):
    tool = await request.json()
    from backend.database import insert_tool
    result = insert_tool(tool)
    return {"added": result}

@app.get("/sherlock")
def sherlock_analysis():
    from backend.sherlock import SherlockAnalyzer
    analyzer = SherlockAnalyzer()
    return analyzer.run_full_analysis()

@app.get("/analyze")
def trigger_analysis():
    from backend.ai_engine import run_ai_analysis
    tools = get_tools(limit=200)
    stats = get_stats()
    if not tools:
        return {"error": "No tools yet"}
    return run_ai_analysis(tools, stats)
