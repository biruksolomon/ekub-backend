from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class EkubDomainException(Exception):
    """Base exception for all domain business logic errors."""
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundException(EkubDomainException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message=message, status_code=status.HTTP_404_NOT_FOUND)


class UnauthorizedException(EkubDomainException):
    def __init__(self, message: str = "Unauthorized access"):
        super().__init__(message=message, status_code=status.HTTP_401_UNAUTHORIZED)


class ForbiddenException(EkubDomainException):
    def __init__(self, message: str = "Action forbidden"):
        super().__init__(message=message, status_code=status.HTTP_403_FORBIDDEN)


class BusinessRuleException(EkubDomainException):
    def __init__(self, message: str):
        super().__init__(message=message, status_code=status.HTTP_400_BAD_REQUEST)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(EkubDomainException)
    async def domain_exception_handler(request: Request, exc: EkubDomainException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message},
        )
