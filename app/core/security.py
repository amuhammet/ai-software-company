from fastapi import Header, HTTPException, status


def get_current_tenant(
    x_tenant_id: str = Header(default="org_default", description="Tenant organization ID"),
    authorization: str | None = Header(default=None, description="Bearer token optional stub"),
) -> str:
    """
    Validates and extracts the tenant ID from request headers.
    Supports X-Tenant-ID header for transition/demo mode, with hooks for future JWT validation.
    """
    if not x_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing tenant identification header (X-Tenant-ID)",
        )

    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1]
        # Future JWT parsing logic can be injected here.
        _ = token

    return x_tenant_id


__all__ = ["get_current_tenant"]
