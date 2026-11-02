#!/usr/bin/env python3
"""Sprint 1 bootstrap script for the AI software company platform.

This script ensures the platform database exists, creates the default tenant and
admin user, and verifies that the required services are reachable.
"""

from __future__ import annotations

import os
import sys
import urllib.request
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import Base, SessionLocal
from app.core.security import hash_password
from app.models.tenant import Organization, User


def verify_ollama() -> None:
    url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    try:
        with urllib.request.urlopen(f"{url}/api/tags", timeout=5) as response:
            print(f"[OK] Ollama reachable at {url} (status={response.status})")
    except Exception as exc:  # pragma: no cover
        print(f"[WARN] Could not reach Ollama at {url}: {exc}")


def bootstrap_database() -> None:
    print("[INFO] Creating database schema...")
    engine = create_engine(settings.database_url, future=True, echo=False)
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()
    try:
        org = db.query(Organization).filter(Organization.name == "Default Platform Org").first()
        if org is None:
            org = Organization(
                id="org_default",
                name="Default Platform Org",
                monthly_budget_usd=float(os.getenv("DEFAULT_ORG_BUDGET_USD", "500.0")),
                current_spend_usd=0.0,
                created_at=datetime.utcnow(),
            )
            db.add(org)
            db.commit()
            db.refresh(org)
            print("[OK] Created default organization: org_default")

        user = db.query(User).filter(User.email == "admin@platform.local").first()
        if user is None:
            user = User(
                id="usr_admin",
                email="admin@platform.local",
                hashed_password=hash_password("admin123"),
                role="admin",
                is_active=True,
                org_id=org.id,
                created_at=datetime.utcnow(),
            )
            db.add(user)
            db.commit()
            print("[OK] Created default admin user: admin@platform.local")

        print(f"[OK] Organization budget: ${org.monthly_budget_usd:.2f}")
    finally:
        db.close()


def main() -> None:
    print("=== AI Software Company Platform Bootstrap ===")
    print(f"Database URL: {settings.database_url}")
    verify_ollama()
    bootstrap_database()
    print("[OK] Bootstrap complete. You can now run the API service.")


if __name__ == "__main__":
    main()
