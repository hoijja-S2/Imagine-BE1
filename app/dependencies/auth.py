from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.db.database import get_db
from app.db.models.user import User


# Authorization: Bearer <토큰>
# 형식의 인증 정보를 처리하기 위한 객체
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Firebase ID Token을 검증하고
    현재 로그인한 사용자 정보를 반환한다.
    """

    # FastAPI가 Authorization 헤더에서
    # 실제 토큰 부분만 꺼내준다.
    id_token = credentials.credentials

    try:
        # Firebase Admin SDK로 ID Token 검증
        decoded_token = auth.verify_id_token(id_token)

        # 검증 성공 시 uid, email 등이 들어 있는 정보 반환
        return decoded_token

    except Exception:
        # 잘못됐거나 만료된 토큰이면 401 반환
        raise AppError(401, "INVALID_TOKEN", "로그인 정보가 올바르지 않거나 만료되었습니다.")

def get_current_db_user(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    """
    토큰을 확인한 뒤, users 테이블에서 그 사용자를 찾아 돌려준다.
    처음 보는 사용자라서 없으면 새로 저장한 뒤 돌려준다.

    로그인한 사용자의 DB 정보가 필요한 API는 이 함수를 쓴다.
    """

    uid = current_user.get("uid")

    # users 테이블에서 firebase_uid가 같은 사용자 찾기
    user = db.query(User).filter(User.firebase_uid == uid).first()

    # 없으면 처음 보는 사용자 → 새로 저장
    if user is None:
        user = User(
            firebase_uid=uid,
            email=current_user.get("email"),
            name=current_user.get("name"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return user

