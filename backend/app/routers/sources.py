from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Source
from app.schemas import SourceCreate, SourceOut

router = APIRouter(prefix="/api/sources", tags=["sources"])


@router.get("", response_model=list[SourceOut])
def list_sources(db: Session = Depends(get_db)):
    return db.query(Source).order_by(Source.created_at.desc()).all()


@router.post("", response_model=SourceOut, status_code=201)
def create_source(body: SourceCreate, db: Session = Depends(get_db)):
    existing = db.query(Source).filter(Source.url == body.url).first()
    if existing:
        raise HTTPException(409, "Source URL already exists")
    source = Source(**body.model_dump())
    db.add(source)
    db.commit()
    db.refresh(source)
    return SourceOut.model_validate(source)


@router.delete("/{source_id}", status_code=204)
def delete_source(source_id: int, db: Session = Depends(get_db)):
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(404, "Source not found")
    db.delete(source)
    db.commit()
