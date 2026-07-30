from fastapi import Header, HTTPException, status

from app.core.config import settings


def require_token(x_forge_token: str = Header(default="")) -> None:
    """Shared-secret gate for every endpoint that can spend money or touch code.

    Submitting a task makes the runtime clone a repository with the platform's
    GitHub credential and run an AI provider against it on the org's Anthropic
    balance. Reading a task's events returns the prompt and the provider's
    output from a private repository. Neither belongs on an open endpoint.

    /health stays open so platform probes keep working.
    """
    if x_forge_token != settings.forge_shared_secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid or missing token"
        )
