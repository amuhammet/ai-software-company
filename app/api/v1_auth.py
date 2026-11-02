from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.models.tenant import Organization, User
from app.schemas.auth_schema import LoginRequest, RegisterRequest, TokenResponse

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse)
def register_user(payload: RegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

    org_name = payload.organization or f"{payload.email.split('@')[0]}-org"
    org = db.query(Organization).filter(Organization.name == org_name).first()
    if org is None:
        org = Organization(id=f"org-{org_name}", name=org_name, monthly_budget_usd=100.0)
        db.add(org)
        db.commit()
        db.refresh(org)

    user = User(
        id=f"user-{payload.email}",
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=payload.role,
        org_id=org.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(subject=user.id, extra_claims={"role": user.role, "org_id": org.id})
    return TokenResponse(access_token=token, user_id=user.id, organization=org.name, role=user.role)


@router.post("/login", response_model=TokenResponse)
def login_user(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.query(User).filter(User.email == payload.email).first()
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(subject=user.id, extra_claims={"role": user.role, "org_id": user.org_id})
    return TokenResponse(access_token=token, user_id=user.id, organization=user.organization.name, role=user.role)


__all__ = ["router"]
