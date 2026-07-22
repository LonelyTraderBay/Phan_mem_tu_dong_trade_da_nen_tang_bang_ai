"""Shared Error body matching packages/contracts Error schema."""

from __future__ import annotations

from uuid import uuid4

from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    field: str
    reason: str


class ErrorBody(BaseModel):
    """Matches packages/contracts Error schema (code, message, trace_id, details)."""

    code: str
    message: str
    trace_id: str
    details: list[ErrorDetail] = Field(default_factory=list)


class GatewayError(Exception):
    """Raised from dependencies/routes; converted to Error JSONResponse."""

    def __init__(
        self,
        status_code: int,
        *,
        code: str,
        message: str,
        details: list[ErrorDetail] | None = None,
    ) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or []
        super().__init__(message)


def error_response(
    status_code: int,
    *,
    code: str,
    message: str,
    details: list[ErrorDetail] | None = None,
) -> JSONResponse:
    body = ErrorBody(
        code=code,
        message=message,
        trace_id=str(uuid4()),
        details=details or [],
    )
    return JSONResponse(status_code=status_code, content=body.model_dump())
