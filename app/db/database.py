import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


# 프로젝트 최상위 폴더를 찾아서 .env 파일을 읽는다.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")


# .env에서 MariaDB 접속 주소를 읽는다.
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(".env 파일에 DATABASE_URL이 설정되어 있지 않습니다.")


# MariaDB와 연결하는 통로
# pool_pre_ping: 연결이 끊겼는지 사용 전에 확인한다.
# pool_recycle: 오래된 연결이 끊기기 전에 1시간마다 새로 연결한다.
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# DB 작업 단위(세션)를 만들어 주는 함수
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    """
    모든 테이블 모델(User, Scenario 등)이 상속할 부모 클래스.
    다음 단계에서 테이블을 만들 때 사용한다.
    """
    pass


def get_db():
    """
    API 요청 하나마다 DB 세션을 하나 열어 주고,
    요청이 끝나면 자동으로 닫아 주는 함수.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """
    models 폴더에 정의한 테이블 중
    DB에 아직 없는 테이블을 새로 만든다.
    서버가 시작될 때 main.py에서 한 번 호출한다.
    """
    import app.db.models  # 모든 테이블 모델 불러오기
    Base.metadata.create_all(bind=engine)