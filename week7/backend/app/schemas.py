from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Note title")
    content: str = Field(..., min_length=1, description="Note content")

    @field_validator("title", "content")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Check that the string is not empty or only whitespace."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or contain only whitespace")
        return v.strip()


class NoteRead(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotePatch(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200, description="Note title")
    content: str | None = Field(None, min_length=1, description="Note content")

    @field_validator("title", "content")
    @classmethod
    def validate_not_empty_if_provided(cls, v: str | None) -> str | None:
        """If provided, check that the string is not empty or only whitespace."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Field cannot be empty or contain only whitespace")
            return v.strip()
        return v


class ActionItemCreate(BaseModel):
    description: str = Field(..., min_length=1, description="Action item description")

    @field_validator("description")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Check that the string is not empty or only whitespace."""
        if not v or not v.strip():
            raise ValueError("Description cannot be empty or contain only whitespace")
        return v.strip()


class ActionItemRead(BaseModel):
    id: int
    description: str
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ActionItemPatch(BaseModel):
    description: str | None = Field(None, min_length=1, description="Action item description")
    completed: bool | None = None

    @field_validator("description")
    @classmethod
    def validate_not_empty_if_provided(cls, v: str | None) -> str | None:
        """If provided, check that the string is not empty or only whitespace."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Description cannot be empty or contain only whitespace")
            return v.strip()
        return v


class ErrorResponse(BaseModel):
    """Standard error response schema."""
    detail: str
    error_code: str | None = None


