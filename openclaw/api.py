from fastapi import APIRouter, HTTPException
from .models import RunRequest, RunResult
from .executor import run as run_exec

router = APIRouter(prefix="/openclaw", tags=["openclaw"])

@router.get("/healthz")
def healthz():
    return {"ok": True, "service": "openclaw"}

@router.post("/runs", response_model=RunResult)
def create_run(req: RunRequest):
    try:
        return run_exec(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
