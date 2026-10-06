import os
import firebase_admin
from firebase_admin import credentials
from pathlib import Path
from dotenv import load_dotenv

# 현재 firebase.py 파일 위치를 기준으로
# 프로젝트 최상위 폴더(Imagine-BE1-main)를 찾는다.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# Firebase 서비스 계정 키 JSON 파일 경로
load_dotenv(BASE_DIR / ".env")


def initialize_firebase():
    """
    Firebase Admin SDK를 초기화하는 함수.

    앱이 이미 초기화되어 있으면 다시 초기화하지 않는다.
    """

    # Firebase 앱이 아직 초기화되지 않은 경우에만 실행
    if not firebase_admin._apps:

        # .env에서 키 파일 경로를 읽는다.
        key_path = os.getenv("FIREBASE_KEY_PATH")

        if not key_path:
            raise RuntimeError(".env 파일에 FIREBASE_KEY_PATH가 설정되어 있지 않습니다.")

        # 서비스 계정 JSON 파일을 이용해 인증 정보 생성
        cred = credentials.Certificate(str(BASE_DIR / key_path))

        # Firebase Admin SDK 초기화
        firebase_admin.initialize_app(cred)
