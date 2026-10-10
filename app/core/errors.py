from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class AppError(Exception):
    """
    우리 서비스에서 일부러 내는 에러.

    사용 예:
        raise AppError(404, "USER_NOT_FOUND", "회원 정보를 찾을 수 없습니다.")
    """

    def __init__(self, status_code: int, code: str, message: str, details=None):
        super().__init__(message)
        self.status_code = status_code   # HTTP 상태 코드 (401, 404 ...)
        self.code = code                 # 프론트가 구분할 영어 코드
        self.message = message           # 사용자에게 보여 줄 문장
        self.details = details           # 추가 정보 (없으면 None)


def error_body(code: str, message: str, details=None) -> dict:
    """모든 에러 응답의 공통 모양을 만든다."""
    return {"error": {"code": code, "message": message, "details": details}}


def register_error_handlers(app: FastAPI) -> None:
    """
    서버에서 나는 모든 에러를 공통 모양으로 바꿔서 응답하도록 등록한다.
    main.py에서 한 번 호출한다.
    """

    # 1. 우리가 일부러 낸 에러 (AppError)
    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, e: AppError):
        return JSONResponse(
            status_code=e.status_code,
            content=error_body(e.code, e.message, e.details),
        )

    # 2. 요청 값이 형식에 안 맞을 때 (예: 숫자 자리에 글자)
    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, e: RequestValidationError):
        details = [
            {"loc": list(err.get("loc", [])), "msg": err.get("msg")}
            for err in e.errors()
        ]
        return JSONResponse(
            status_code=422,
            content=error_body("VALIDATION_ERROR", "요청 형식이 올바르지 않습니다.", details),
        )

    # 3. FastAPI가 기본으로 내는 에러 (토큰 없음, 없는 주소 등)
    @app.exception_handler(StarletteHTTPException)
    async def handle_http_error(request: Request, e: StarletteHTTPException):
        if e.status_code == 401:
            code, message = "AUTH_REQUIRED", "로그인이 필요합니다."
        elif e.status_code == 404:
            code, message = "NOT_FOUND", "요청한 주소를 찾을 수 없습니다."
        else:
            code, message = f"HTTP_{e.status_code}", str(e.detail)
        return JSONResponse(status_code=e.status_code, content=error_body(code, message))

    # 4. 예상하지 못한 에러 (코드 버그 등)
    @app.exception_handler(Exception)
    async def handle_unknown_error(request: Request, e: Exception):
        return JSONResponse(
            status_code=500,
            content=error_body("INTERNAL_ERROR", "서버 내부 오류가 발생했습니다."),
        )