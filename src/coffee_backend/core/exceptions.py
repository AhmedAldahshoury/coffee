from http import HTTPStatus


class APIError(Exception):
    def __init__(self, detail: str, *, code: str, status_code: int, fields: dict[str, str] | None = None):
        super().__init__(detail)
        self.detail = detail
        self.code = code
        self.status_code = status_code
        self.fields = fields


class NotFoundError(APIError):
    def __init__(self, detail: str, *, code: str = "not_found", fields: dict[str, str] | None = None):
        super().__init__(
            detail,
            code=code,
            status_code=HTTPStatus.NOT_FOUND,
            fields=fields,
        )


class ValidationError(APIError):
    def __init__(
        self,
        detail: str,
        *,
        code: str = "validation_error",
        fields: dict[str, str] | None = None,
    ):
        super().__init__(
            detail,
            code=code,
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            fields=fields,
        )


class ConflictError(APIError):
    def __init__(self, detail: str, *, code: str = "conflict", fields: dict[str, str] | None = None):
        super().__init__(
            detail,
            code=code,
            status_code=HTTPStatus.CONFLICT,
            fields=fields,
        )
