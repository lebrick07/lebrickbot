from typing import List
from .models import RunRequest

ALLOWED_TOOLS = {
    "kubectl",
    "helm",
    "terraform",
    "git",
    "aws",
    "docker",
}

# deny obviously dangerous patterns for now (we'll improve later)
DENY_ARGS_SUBSTR = [
    "delete namespace kube-system",
    "rm -rf /",
]

def validate(req: RunRequest) -> None:
    if req.tool not in ALLOWED_TOOLS:
        raise PermissionError(f"Tool not allowed: {req.tool}")

    joined = " ".join([req.tool] + req.args).lower()
    for s in DENY_ARGS_SUBSTR:
        if s in joined:
            raise PermissionError("Denied by policy (dangerous command)")
