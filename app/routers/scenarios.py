from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.dependencies.auth import get_current_user

# 시안 관련 API들을 묶어주는 Router
router = APIRouter(
    prefix="/api/scenarios",
    tags=["Scenarios"]
)


class ScenarioSaveRequest(BaseModel):
    """
    시안을 저장할 때 프론트에서 보내는 데이터 구조.
    아직 DB가 정해지지 않았기 때문에
    실제 저장보다는 요청 데이터 형식 확인용으로 사용한다.
    """
    # 사용자가 처음 업로드한 방 사진의 저장 위치
    room_image_url: str
    # AI가 생성한 최종 시안 이미지의 저장 위치
    result_image_url: str

    # 사용자가 각 영역에 선택한 마감재 ID
    # 아직 선택되지 않은 영역이 있을 수 있으므로 None 허용
    wall_material_id: int | None = None
    floor_material_id: int | None = None
    ceiling_material_id: int | None = None
    molding_material_id: int | None = None


@router.post("")
def save_scenario(
    request: ScenarioSaveRequest,
    current_user = Depends(get_current_user),
    ):
    """
    시안 저장 API.
    DB에 실제로 저장X,
    로그인한 사용자만 사용가능,
    프론트에서 전달한 값을 정상적으로 받는지만 확인.
    """

    return {
        "message": "Scenario data received successfully",
        "uid": current_user.get("uid"),
        "data": request
    }

@router.get("")
def get_scenarios(current_user = Depends(get_current_user)):
    """
    저장된 시안 목록 조회 API.
    아직 DB가 연결되지 않았으므로 임시 데이터를 반환.
    로그인한 사용자만 사용가능.
    """

    return {
        "message": "Scenario list retrieved successfully",
        "uid": current_user.get("uid"),
        "data": [
            {
                "scenario_id": 1,
                "result_image_url": "https://example.com/result1.jpg"
            },
            {
                "scenario_id": 2,
                "result_image_url": "https://example.com/result2.jpg"
            }
        ]
    }

@router.delete("/{scenario_id}") #시안 삭제 API. scenario_id=지울 시안 넘버
def delete_scenario(
    scenario_id: int,
    current_user = Depends(get_current_user),
):
    """
    시안 삭제 API.
    로그인한 사용자만 사용가능.
    아직 DB가 연결되지 않았으므로 실제로 삭제하지 않고,
    삭제 요청을 정상적으로 받는지만 확인.
    """

    return {
        "message": "Scenario deleted successfully",
        "uid": current_user.get("uid"),
        "scenario_id": scenario_id
    }

@router.get("/{scenario_id}")
def get_scenario(
    scenario_id: int,
    current_user = Depends(get_current_user),
):
    """
    시안 하나 조회 API.
    로그인한 사용자만 사용가능.
    아직 DB가 연결되지 않았으므로 임시 데이터를 반환.
    """

    return {
        "message": "Scenario retrieved successfully",
        "uid": current_user.get("uid"),
        "data": {
            "scenario_id": scenario_id,
            "room_image_url": "https://example.com/room.jpg",
            "result_image_url": "https://example.com/result.jpg",
            "wall_material_id": 1,
            "floor_material_id": 2,
            "ceiling_material_id": None,
            "molding_material_id": 3
        }
    }