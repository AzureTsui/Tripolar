from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import AITool, AIToolProductType, AIToolUseCase
from app.schemas import (
    AIToolOut,
    AIToolDetail,
    AIToolProductTypeOut,
    AIToolUseCaseOut,
    PaginatedResponse,
)

router = APIRouter(prefix="/api/tools", tags=["ai-tools"])


# Fixed routes must come before parameterized routes

@router.get("/meta/product-types", response_model=list[AIToolProductTypeOut])
def list_product_types(db: Session = Depends(get_db)):
    return (
        db.query(AIToolProductType)
        .filter(AIToolProductType.is_active == True)
        .order_by(AIToolProductType.sort_order)
        .all()
    )


@router.get("/meta/use-cases", response_model=list[AIToolUseCaseOut])
def list_use_cases(db: Session = Depends(get_db)):
    return (
        db.query(AIToolUseCase)
        .filter(AIToolUseCase.is_active == True)
        .order_by(AIToolUseCase.sort_order)
        .all()
    )


@router.get("", response_model=PaginatedResponse[AIToolOut])
def list_tools(
    page: int = Query(1, ge=1),
    per_page: int = Query(24, ge=1, le=100),
    product_type: int | None = Query(None, alias="product_type_id"),
    use_case: int | None = Query(None, alias="use_case_id"),
    search: str | None = Query(None, description="Search by name or company"),
    db: Session = Depends(get_db),
):
    q = db.query(AITool).options(
        joinedload(AITool.product_type),
        joinedload(AITool.use_case),
    )

    if product_type is not None:
        q = q.filter(AITool.product_type_id == product_type)
    if use_case is not None:
        q = q.filter(AITool.primary_use_case_id == use_case)
    if search:
        like = f"%{search}%"
        q = q.filter(
            (AITool.name.ilike(like)) | (AITool.company.ilike(like))
        )

    q = q.filter(AITool.status == "active")
    total = q.count()
    tools = (
        q.order_by(AITool.name)
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    return {
        "data": tools,
        "meta": {"page": page, "per_page": per_page, "total": total},
    }


@router.get("/{tool_id}", response_model=AIToolDetail)
def get_tool(tool_id: int, db: Session = Depends(get_db)):
    tool = (
        db.query(AITool)
        .options(
            joinedload(AITool.product_type),
            joinedload(AITool.use_case),
        )
        .filter(AITool.id == tool_id)
        .first()
    )
    if not tool:
        raise HTTPException(404, "Tool not found")
    return tool
