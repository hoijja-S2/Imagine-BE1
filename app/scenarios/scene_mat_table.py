from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class ScenarioMaterial(Base):
    """
    scenario_materials 테이블.
    시안 하나에 쓴 마감재를 영역마다 한 줄씩 저장한다.
    예: 시안 1의 전체 벽 = 아이보리, 바닥 = 오크 → 두 줄

    저장할 때의 마감재 정보를 그대로 복사해 둔다(스냅샷).
    원래 마감재가 나중에 지워져도 저장된 시안은 그대로 보인다.
    """
    __tablename__ = "scenario_materials"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # 어느 시안의 마감재인지. 시안이 지워지면 함께 지워진다.
    scenario_id: Mapped[int] = mapped_column(
        ForeignKey("scenarios.id", ondelete="CASCADE"), index=True, nullable=False
    )

    # 영역: allWalls(전체 벽), wall1~3(포인트 벽지), floor(바닥),
    #       moldingTop(몰딩 상단), moldingBottom(몰딩 하단)
    area: Mapped[str] = mapped_column(String(30), nullable=False)

    # 마감재 번호 (기본 마감재 또는 사용자가 올린 벽지)
    material_id: Mapped[str | None] = mapped_column(String(60))

    # 마감재 이름과 대표 색 (예: "아이보리", "#eee3ce")
    # 사진 벽지도 목록·비교 화면의 색 표시용으로 대표 색을 넣는다.
    name: Mapped[str | None] = mapped_column(String(100))
    color_hex: Mapped[str] = mapped_column(String(7), nullable=False)

    # 사진 벽지일 때만: 패턴 사진 주소, 패턴 반복 횟수 (클수록 촘촘하게 반복)
    # 단색 마감재는 둘 다 비어 있다.
    texture_url: Mapped[str | None] = mapped_column(String(500))
    pattern_repeat: Mapped[float | None] = mapped_column(Float)

    scenario: Mapped["Scenario"] = relationship(back_populates="materials")