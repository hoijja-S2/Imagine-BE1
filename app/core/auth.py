from datetime import datetime

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import AppError
from app.users.user_table import User


# Authorization: Bearer <토큰> 형식의 인증 정보를 처리하기 위한 객체
security = HTTPBearer()


# [로그인 확인] 토큰이 진짜인지 확인하고 토큰 안의 정보(uid, 이메일 등)를 돌려준다
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        return auth.verify_id_token(credentials.credentials)
    except Exception:
        raise AppError(401, "INVALID_TOKEN", "로그인 정보가 올바르지 않거나 만료되었습니다.")


# [로그인 확인 + 내 정보] DB의 내 사용자 정보를 돌려준다 (회원·게스트 모두 사용 가능)
#   - 처음 보는 사용자면 등록 (익명 로그인이면 게스트로)
#   - 게스트가 정식 가입했으면 회원으로 바꿈
#   - 게스트는 마지막 활동 시각을 기록 (7일 정리 기준)
def get_current_db_user(current_user = Depends(get_current_user),
                        db: Session = Depends(get_db)) -> User:
    uid = current_user.get("uid")

    # 토큰 안의 로그인 방식이 'anonymous'면 게스트
    is_guest = current_user.get("firebase", {}).get("sign_in_provider") == "anonymous"

    user = db.query(User).filter(User.firebase_uid == uid).first()

    if user is None:
        # 처음 보는 사용자 → 등록
        user = User(firebase_uid=uid, email=current_user.get("email"),
                    name=current_user.get("name"), is_guest=is_guest)
        db.add(user)
    elif user.is_guest and not is_guest:
        # 게스트였는데 정식 가입함 (uid는 그대로) → 회원으로 바꾸기
        user.is_guest = False
        user.email = current_user.get("email")
        user.name = user.name or current_user.get("name")

    if user.is_guest:
        user.last_active_at = datetime.now()

    db.commit()
    db.refresh(user)
    return user


# [회원 전용] 게스트면 막는다 (시안 저장·목록·상세·삭제·비교에서 사용)
def get_member_user(user: User = Depends(get_current_db_user)) -> User:
    if user.is_guest:
        raise AppError(403, "GUEST_NOT_ALLOWED", "회원가입 후 이용할 수 있는 기능이에요.")
    return user