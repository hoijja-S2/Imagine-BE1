from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth


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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired Firebase ID token",
        )

