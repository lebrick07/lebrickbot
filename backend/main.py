from fastapi import FastAPI
from openclaw.ci.github_actions import generate_github_actions
from openclaw.api import router as openclaw_router

app = FastAPI(title="lebrickbot")
from openclaw.ci.github_actions import generate_github_actions

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.get("/")
def root():
    return {"service": "lebrickbot", "status": "running"}

# OpenClaw runtime API
app.include_router(openclaw_router)

@app.post("/openclaw/ci/github-actions")
def github_actions(payload: dict):
    return generate_github_actions(payload)
