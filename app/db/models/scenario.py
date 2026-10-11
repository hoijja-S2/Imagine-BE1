from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Scenario(Base):
    """
    scenarios 테이블.
    시안 1개 = 한 줄.
    만들어지면 초안(is_saved=False), 저장 버튼을 누르면 저장됨(is_saved=True).
    """
    __tablename__ = "scenarios"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # 어느 프로젝트(방 사진)로 만든 시안인지
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), index=True, nullable=False
    )

    # 주인 (users.id). 목록을 빠르게 찾으려고 프로젝트와 별도로 둔다.
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )

    # 시안 이름. 저장할 때 없으면 "시안 1"처럼 자동으로 붙인다.
    title: Mapped[str | None] = mapped_column(String(100))

    # 결과 이미지, 목록용 작은 이미지
    result_image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    thumbnail_url: Mapped[str | None] = mapped_column(String(500))

    # 어떤 AI 분석 결과로 만들었는지 (BE2가 넘겨주는 값)
    analysis_id: Mapped[str | None] = mapped_column(String(64))

    # 초안 / 저장 구분
    is_saved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    saved_at: Mapped[datetime | None] = mapped_column(DateTime)

    # 연결: 프로젝트, 영역별 마감재 목록
    project: Mapped["Project"] = relationship(back_populates="scenarios")
    materials: Mapped[list["ScenarioMaterial"]] = relationship(
        back_populates="scenario", cascade="all, delete-orphan"
    )