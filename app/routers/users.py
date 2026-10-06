from fastapi import APIRouter, Depends, HTTPException, status
from firebase_admin import auth
from app.dependencies.auth import get_current_user

# 사용자 관련 API들을 묶어주는 Router
router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)

@router.get("/me")
def get_my_info(current_user = Depends(get_current_user)):
    """
    Firebase ID Token 검증 테스트용 API.

    토큰 검증에 성공하면
    현재 로그인한 사용자의 Firebase UID와 이메일을 반환한다.
    """

    return {
        "uid": current_user.get("uid"),
        "email": current_user.get("email"),
    }

@router.delete("/me")
def delete_my_account(current_user = Depends(get_current_user)):
    """
    회원 탈퇴 API.
    로그인한 사용자 본인의 Firebase 계정을 삭제한다.

    DB가 연결되면 Firebase 계정을 지우기 전에
    이 사용자의 DB 데이터(시안 등)를 먼저 삭제해야 한다.
    """

    uid = current_user.get("uid")

    # TODO: DB 연결 후 이 사용자의 시안, 사용자 정보 삭제

    try:
        # Firebase에서 계정 삭제
        auth.delete_user(uid)

    except auth.UserNotFoundError:
        # 이미 삭제된 계정이면 404 반환
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return {
        "message": "User deleted successfully",
        "uid": uid
    }