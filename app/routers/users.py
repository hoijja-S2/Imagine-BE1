from fastapi import APIRouter, Depends, HTTPException, status
from firebase_admin import auth
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.user import User
from app.dependencies.auth import get_current_user

# 사용자 관련 API들을 묶어주는 Router
router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)

@router.get("/me")
def get_my_info(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    내 정보 조회 API.

    토큰의 Firebase UID로 users 테이블에서 사용자를 찾는다.
    처음 로그인한 사용자라서 없으면 새로 저장한다.
    """
    uid = current_user.get("uid")

    user = db.query(User).filter(User.firebase_uid == uid).first()

    if user is None:
        user = User(
            firebase_uid = uid,
            email = current_user.get("email"),
            name = current_user.get("name"),
        )
        db.add(user) # 저장할 목록에 추가
        db.commit()  # 실제로 DB에 저장
        db.refresh(user)  # DB가 채워 준 id, 가입 시각을 다시 읽어 옴

    return {
        "id": user.id,
        "uid": current_user.get("uid"),
        "email": current_user.get("email"),
        "name": user.name,
        "profile_image_url": user.profile_image_url,
        "created_at": user.created_at,
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