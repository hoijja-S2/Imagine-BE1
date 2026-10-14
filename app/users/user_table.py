from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    """
    users 테이블.
    Firebase 계정 한 개 = users 한 줄.
    비밀번호는 Firebase가 관리하므로 여기에는 저장하지 않는다.
    """
    __tablename__ = "users"

    # 우리 서비스의 사용자 번호 (1, 2, 3 ... 자동 증가)
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Firebase 사용자 UID. 같은 값이 두 번 들어갈 수 없다(unique).
    firebase_uid: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)

    # 이메일, 이름, 프로필 사진 주소 (없을 수 있음)
    email: Mapped[str | None] = mapped_column(String(255))
    name: Mapped[str | None] = mapped_column(String(100))
    profile_image_url: Mapped[str | None] = mapped_column(String(500))

    # 게스트(익명 로그인)인지. 가입하면 False로 바뀐다.
    is_guest: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # 마지막 활동 시각. 7일 넘게 활동 없는 게스트 데이터를 정리할 때 기준.
    last_active_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # 가입 시각, 수정 시각 (DB가 자동으로 채움)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default = func.now(), onupdate = func.now()
    )

    # 이 사용자의 프로젝트 목록. 사용자를 지우면 프로젝트도 함께 지워진다.
    projects: Mapped[list["Project"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )