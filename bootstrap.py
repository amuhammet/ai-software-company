#!/usr/bin/env python3
"""Bootstrap database schema and seed the default tenant, admin, and agents."""

from __future__ import annotations

import os
import urllib.request
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import Base, SessionLocal
from app.core.security import hash_password
from app.models.agent import AgentRecord  # noqa: F401 - registers model metadata
from app.models.tenant import Organization, User

DEFAULT_AGENTS = (
    {
        "id": "agent_default_developer",
        "name": "Default Developer",
        "purpose": "Implement and improve software features from technical requirements.",
        "model_preference": "ollama/llama3",
        "system_prompt": "You are a careful senior software developer. Produce secure, maintainable code and explain important decisions.",
        "allowed_tools": ["code_sandbox", "test_runner"],
        "trust_score": 90.0,
        "metadata_tags": {"capabilities": ["development", "coding", "implementation"]},
    },
    {
        "id": "agent_default_qa",
        "name": "Default QA",
        "purpose": "Review software changes and design or run focused tests.",
        "model_preference": "ollama/llama3",
        "system_prompt": "You are a meticulous QA engineer. Identify regressions, edge cases, and missing tests. Never claim tests were run unless they actually were.",
        "allowed_tools": ["test_runner"],
        "trust_score": 90.0,
        "metadata_tags": {"capabilities": ["qa", "testing", "review"]},
    },
)


def verify_ollama() -> None:
    url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    try:
        with urllib.request.urlopen(f"{url}/api/tags", timeout=5) as response:
            print(f"[OK] Ollama reachable at {url} (status={response.status})")
    except Exception as exc:  # pragma: no cover
        print(f"[WARN] Could not reach Ollama at {url}: {exc}")


def seed_default_agents(db: Session, owner_id: str) -> None:
    """Create missing built-in agents without overwriting user-edited records."""
    created = 0
    for agent_data in DEFAULT_AGENTS:
        existing = db.get(AgentRecord, agent_data["id"])
        if existing is not None:
            continue
        db.add(
            AgentRecord(
                **agent_data,
                owner_id=owner_id,
                is_public=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
        )
        created += 1

    db.commit()
    print(f"[OK] Default agents present ({created} created)")


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

        seed_default_agents(db, owner_id=org.id)
        print(f"[OK] Organization budget: ${org.monthly_budget_usd:.2f}")
    finally:
        db.close()
        engine.dispose()


def main() -> None:
    print("=== AI Software Company Platform Bootstrap ===")
    print(f"Database URL: {settings.database_url}")
    verify_ollama()
    bootstrap_database()
    print("[OK] Bootstrap complete. You can now run the API service.")


if __name__ == "__main__":
    main()
