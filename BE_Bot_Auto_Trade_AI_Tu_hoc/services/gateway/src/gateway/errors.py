"""Shared error response helpers matching docs/shared/error-model.md."""

from __future__ import annotations

from uuid import uuid4

from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    field: str
    reason: str


class ErrorBody(BaseModel):
    code: str
    message: str
    trace_id: str
    details: list[ErrorDetail] = Field(default_factory=list)


def error_response(
    status_code: int,
    code: str,
    message: str,
    *,
    details: list[dict[str, str]] | None = None,
) -> JSONResponse:
    body = ErrorBody(
        code=code,
        message=message,
        trace_id=str(uuid4()),
        details=[ErrorDetail(**d) for d in (details or [])],
    )
    return JSONResponse(
        status_code=status_code,
        content=body.model_dump(),
    )
