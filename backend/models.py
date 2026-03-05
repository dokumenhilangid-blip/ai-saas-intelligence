from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Tool(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    url: Optional[str] = None
    category: Optional[str] = None
    pricing: Optional[str] = None
    upvotes: Optional[int] = 0
    comments: Optional[int] = 0
    source: Optional[str] = None
    first_seen: Optional[str] = None
    last_updated: Optional[str] = None

class Insight(BaseModel):
    id: Optional[int] = None
    title: str
    content: str
    insight_type: str
    category: Optional[str] = None
    generated_at: Optional[str] = None
    model_used: Optional[str] = None

class StatsResponse(BaseModel):
    total_tools: int
    by_source: dict
    total_insights: int
    last_updated: Optional[str] = None

class ScrapeLog(BaseModel):
    source: str
    tools_found: int
    tools_added: int
    status: str
    ran_at: str
