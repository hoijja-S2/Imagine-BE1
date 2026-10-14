from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.auth import get_current_db_user
from app.core.database import get_db
from app.core.errors import AppError
from app.scenarios.scene_table import Scenario
from app.users.user_table import User

router = APIRouter(prefix="/api/scenarios", tags=["Scenarios"])


# [응답 모양] 시안 안의 영역별 마감재 (전체 벽 아이보리, 바닥 오크 …)
class MaterialOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    area: str
    name: str | None
    color_hex: str
    material_id: str | None
    texture_url: str | None
    pattern_repeat: float | None


# [응답 모양] 시안 하나 (목록·상세·저장·비교가 모두 이 모양으로 응답)
class ScenarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    title: str | None
    is_saved: bool
    result_image_url: str
    thumbnail_url: str | None
    saved_at: datetime | None
    materials: list[MaterialOut]


# [저장된 시안 목록 화면] 내가 저장한 시안들을 최근 저장한 순서로 보여 준다
@router.get("")
def get_saved_list(user: User = Depends(get_current_db_user), db: Session = Depends(get_db)):
    scenarios = (db.query(Scenario)
                 .filter(Scenario.user_id == user.id, Scenario.is_saved.is_(True))
                 .order_by(Scenario.saved_at.desc())
                 .all())
    return [ScenarioOut.model_validate(s) for s in scenarios]


# [시안 비교 화면] 목록에서 고른 시안 2~3개를 나란히 비교한다 (예: ?ids=1,2,3)
@router.get("/compare")
def compare(ids: str, user: User = Depends(get_current_db_user), db: Session = Depends(get_db)):
    try:
        scenario_ids = [int(x) for x in ids.split(",")]
    except ValueError:
        raise AppError(422, "VALIDATION_ERROR", "ids는 1,2,3처럼 숫자를 쉼표로 이어서 보내 주세요.")

    if not 2 <= len(set(scenario_ids)) <= 3:
        raise AppError(422, "COMPARE_COUNT_INVALID", "비교는 서로 다른 시안 2~3개로 할 수 있어요.")

    scenarios = (db.query(Scenario)
                 .filter(Scenario.id.in_(scenario_ids),
                         Scenario.user_id == user.id,
                         Scenario.is_saved.is_(True))
                 .all())
    if len(scenarios) != len(set(scenario_ids)):
        raise AppError(404, "SCENARIO_NOT_FOUND", "비교할 시안을 찾을 수 없습니다.")

    by_id = {s.id: s for s in scenarios}
    return [ScenarioOut.model_validate(by_id[i]) for i in scenario_ids]


# [시안 상세 화면]
@router.get("/{scenario_id}")
def get_detail(scenario_id: int, user: User = Depends(get_current_db_user), db: Session = Depends(get_db)):
    s = db.get(Scenario, scenario_id)
    if s is None or s.user_id != user.id:
        raise AppError(404, "SCENARIO_NOT_FOUND", "시안을 찾을 수 없습니다.")
    return ScenarioOut.model_validate(s)


# [최종 시안 화면 - 저장하기 버튼] 시안을 저장, "시안 N" 이름을 붙임
@router.post("/{scenario_id}/save")
def save(scenario_id: int, user: User = Depends(get_current_db_user), db: Session = Depends(get_db)):
    s = db.get(Scenario, scenario_id)
    if s is None or s.user_id != user.id:
        raise AppError(404, "SCENARIO_NOT_FOUND", "시안을 찾을 수 없습니다.")

    if not s.is_saved:
        count = (db.query(func.count(Scenario.id))
                 .filter(Scenario.user_id == user.id, Scenario.is_saved.is_(True))
                 .scalar())
        s.title = f"시안 {count + 1}"
        s.is_saved = True
        s.saved_at = datetime.now()
        db.commit()
        db.refresh(s)

    return ScenarioOut.model_validate(s)


# [저장된 시안 목록 - 삭제 버튼] 시안, 그 마감재 정보 함께 삭제.
@router.delete("/{scenario_id}")
def delete(scenario_id: int, user: User = Depends(get_current_db_user), db: Session = Depends(get_db)):
    s = db.get(Scenario, scenario_id)
    if s is None or s.user_id != user.id:
        raise AppError(404, "SCENARIO_NOT_FOUND", "시안을 찾을 수 없습니다.")

    db.delete(s)
    db.commit()
    return {"deleted": True, "id": scenario_id}