import subprocess
import uuid
from datetime import datetime, timezone
from .models import RunRequest, RunResult
from .policies import validate

def run(req: RunRequest) -> RunResult:
    run_id = str(uuid.uuid4())[:8]
    started = datetime.now(timezone.utc).isoformat()

    try:
        validate(req)
    except PermissionError as e:
        return RunResult(run_id=run_id, status="denied", stderr=str(e), started_at=started, finished_at=started)

    cmd = [req.tool] + req.args

    try:
        p = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=req.cwd or None,
            env=None,  # we’ll add safe env merging later
            timeout=600,
        )
        finished = datetime.now(timezone.utc).isoformat()
        status = "succeeded" if p.returncode == 0 else "failed"
        return RunResult(
            run_id=run_id,
            status=status,
            exit_code=p.returncode,
            stdout=p.stdout or "",
            stderr=p.stderr or "",
            started_at=started,
            finished_at=finished,
            metadata={"cmd": cmd, "context": req.context, "mode": req.mode},
        )
    except Exception as e:
        finished = datetime.now(timezone.utc).isoformat()
        return RunResult(
            run_id=run_id,
            status="failed",
            exit_code=1,
            stderr=str(e),
            started_at=started,
            finished_at=finished,
            metadata={"cmd": cmd, "context": req.context, "mode": req.mode},
        )
