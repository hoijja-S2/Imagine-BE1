from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.firebase import initialize_firebase
from app.core.database import SessionLocal, create_tables, get_db
from app.scenarios.scene_API import router as scenarios_router
from app.users.user_API import delete_old_guests, router as users_router
from app.core.errors import register_error_handlers

initialize_firebase()
create_tables()  # DB에 없는 테이블 자동 생성

with SessionLocal() as db:
    delete_old_guests(db)  # 7일 넘게 활동 없는 게스트 정리

app = FastAPI()
register_error_handlers(app)  # 모든 에러를 공통 모양으로

app.include_router(scenarios_router) #시안 관련 API.
app.include_router(users_router) #사용자 관련 API.

@app.get("/")
def root():
    return {"message": "Imagine BE1 server is running"}


@app.get("/health") #이거는 사용자 토큰 발급이 잘 이루어지는지 테스트용도
def health_check():
    return {"status": "ok"}

@app.get("/health/db") #DB 연결 확인용
def health_check_db(db: Session = Depends(get_db)):
    """
    MariaDB 연결 확인용 API.
    DB에 간단한 질문(SELECT 1)을 보내서 대답이 오면 연결 성공.
    """
    db.execute(text("SELECT 1"))
    return {"db": "ok"}