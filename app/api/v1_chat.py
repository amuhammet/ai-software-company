from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.gateway.router import LLMGatewayRouter
from app.models.tenant import Organization, User
from app.schemas.router_schema import LLMRequestDTO, LLMResponseDTO

router = APIRouter(prefix="/api/v1/llm", tags=["LLM Gateway"])
llm_router = LLMGatewayRouter()


@router.post("/chat", response_model=LLMResponseDTO)
def route_llm_request(payload: LLMRequestDTO, db: Session = Depends(get_db)) -> LLMResponseDTO:
    # Simple tenant guard for demonstration purposes
    org = db.query(Organization).first()
    if org is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No organization found")

    if org.current_spend_usd >= org.monthly_budget_usd:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Organization budget exhausted: ${org.current_spend_usd:.2f}/${org.monthly_budget_usd:.2f}",
        )

    # This is a placeholder for actual adapter wiring. Real deployment should inject a provider implementation.
    try:
        result = llm_router.dispatch(
            task_type="coding",
            messages=[{"role": msg.role, "content": msg.content} for msg in payload.messages],
            preferred_model=payload.model,
            temperature=payload.temperature,
            max_tokens=payload.max_tokens,
        )
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    org.current_spend_usd += float(result.get("cost_usd", 0.0) or 0.0)
    db.commit()

    return LLMResponseDTO(
        status="success",
        data=result.get("content", ""),
        model_used=result.get("model_used", payload.model),
        cost_usd=float(result.get("cost_usd", 0.0) or 0.0),
        remaining_budget=org.monthly_budget_usd - org.current_spend_usd,
    )


__all__ = ["router"]
