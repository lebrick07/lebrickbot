from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal

Mode = Literal["explain", "plan", "apply"]

class RunRequest(BaseModel):
    tool: str = Field(..., description="Tool name, e.g. kubectl/helm/terraform/git/aws/docker")
    args: List[str] = Field(default_factory=list, description="CLI args")
    context: str = Field(default="pi5", description="Execution context (cluster/cloud profile)")
    mode: Mode = Field(default="plan", description="Execution mode")
    env: Optional[Dict[str, str]] = Field(default=None, description="Optional env overrides (no secrets)")
    cwd: Optional[str] = Field(default=None, description="Optional working directory")

class RunResult(BaseModel):
    run_id: str
    status: Literal["queued", "running", "succeeded", "failed", "denied"]
    exit_code: Optional[int] = None
    stdout: str = ""
    stderr: str = ""
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
