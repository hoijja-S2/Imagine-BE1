from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Project(Base):
    """
    projects 테이블.
    방 사진 1장 = 프로젝트 1개.
    같은 사진으로 시안을 여러 개 만들 수 있다.
    """
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # 주인 (users.id). 사용자가 지워지면 DB가 프로젝트도 함께 지운다.
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )

    # 프로젝트 이름 (없을 수 있음)
    title: Mapped[str | None] = mapped_column(String(100))

    # 원본 방 사진 주소와 크기 (AI 분석, 브러시 수정에 필요)
    original_image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    width: Mapped[int | None] = mapped_column(Integer)
    height: Mapped[int | None] = mapped_column(Integer)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # 연결: 주인, 이 사진으로 만든 시안 목록
    user: Mapped["User"] = relationship(back_populates="projects")
    scenarios: Mapped[list["Scenario"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )