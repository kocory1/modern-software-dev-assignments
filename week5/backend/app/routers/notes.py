from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Note
from ..schemas import NoteCreate, NoteRead, NoteSearchResponse

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("/", response_model=list[NoteRead])
def list_notes(db: Session = Depends(get_db)) -> list[NoteRead]:
    rows = db.execute(select(Note)).scalars().all()
    return [NoteRead.model_validate(row) for row in rows]


@router.post("/", response_model=NoteRead, status_code=201)
def create_note(payload: NoteCreate, db: Session = Depends(get_db)) -> NoteRead:
    note = Note(title=payload.title, content=payload.content)
    db.add(note)
    db.flush()
    db.refresh(note)
    return NoteRead.model_validate(note)


@router.get("/search/", response_model=NoteSearchResponse)
def search_notes(
    q: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    sort: str = Query("created_desc"),
    db: Session = Depends(get_db),
) -> NoteSearchResponse:
    stmt = select(Note)

    # Filtering (case-insensitive on title and content)
    if q is not None:
        q_stripped = q.strip()
        if q_stripped:
            pattern = f"%{q_stripped}%"
            stmt = stmt.where(
                Note.title.ilike(pattern) | Note.content.ilike(pattern)
            )

    # Total count before pagination
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar_one()

    # Sorting
    if sort == "title_asc":
        stmt = stmt.order_by(Note.title.asc())
    else:
        # Default: newest first by id (proxy for created_desc)
        stmt = stmt.order_by(Note.id.desc())

    # Pagination
    offset = (page - 1) * page_size
    stmt = stmt.offset(offset).limit(page_size)

    rows = db.execute(stmt).scalars().all()
    items = [NoteRead.model_validate(row) for row in rows]

    return NoteSearchResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{note_id}", response_model=NoteRead)
def get_note(note_id: int, db: Session = Depends(get_db)) -> NoteRead:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return NoteRead.model_validate(note)
