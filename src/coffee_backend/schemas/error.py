from pydantic import BaseModel


class APIErrorResponse(BaseModel):
    detail: str
    code: str
    fields: dict[str, str] | None = None
