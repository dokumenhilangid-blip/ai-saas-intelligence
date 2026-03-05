from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "online"}

@app.get("/health")
def health():
    return {"status": "healthy", "total_tools": 0}

@app.get("/stats")
def stats():
    return {"total_tools": 0}

@app.get("/tools")
def tools():
    return {"total": 0, "data": []}

@app.get("/sources")
def sources():
    return {"sources": []}

@app.get("/trending")
def trending():
    return {"total": 0, "data": []}

@app.get("/insights")
def insights():
    return {"total": 0, "data": []}
