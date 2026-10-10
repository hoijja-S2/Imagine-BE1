from fastapi import APIRouter, Depends, HTTPException, status
from firebase_admin import auth
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.user import User
from app.dependencies.auth import get_current_user, get_current_db_user

# 사용자 관련 API들을 묶어주는 Router
router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)

@router.get("/me")
def get_my_info(user: User = Depends(get_current_db_user)):
    """
    내 정보 조회 API.
    처음 로그인한 사용자는 get_current_db_user가 자동으로 DB에 등록한다.
    """

    return {
        "id": user.id,
        "uid": user.firebase_uid,
        "email": user.email,
        "name": user.name,
        "profile_image_url": user.profile_image_url,
        "created_at": user.created_at,
    }

@router.delete("/me")
def delete_my_account(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    회원 탈퇴 API.
    1. users 테이블에서 내 정보를 삭제한다.
    2. Firebase 계정을 삭제한다.

    DB를 먼저 지우고 Firebase 계정을 나중에 지운다.
    """

    uid = current_user.get("uid")

    # TODO: 시안 테이블이 생기면 내 시안도 여기서 먼저 삭제
    #1. db에서 내 정보 삭제
    user = db.query(User).filter(User.firebase_uid == uid).first()
    if user is not None:
        db.delete(user)
        db.commit()

    #2. Firebase 계정 삭제
    try:
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