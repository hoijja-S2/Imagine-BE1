import firebase_admin
from firebase_admin import credentials
from pathlib import Path


# 현재 firebase.py 파일 위치를 기준으로
# 프로젝트 최상위 폴더(Imagine-BE1-main)를 찾는다.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# Firebase 서비스 계정 키 JSON 파일 경로
SERVICE_ACCOUNT_PATH = (
    BASE_DIR
    / "config"
    / "imagine-155a7-firebase-adminsdk-fbsvc-4c74a318b9.json"
)


def initialize_firebase():
    """
    Firebase Admin SDK를 초기화하는 함수.

    앱이 이미 초기화되어 있으면 다시 초기화하지 않는다.
    """

    # Firebase 앱이 아직 초기화되지 않은 경우에만 실행
    if not firebase_admin._apps:

        # 서비스 계정 JSON 파일을 이용해 인증 정보 생성
        cred = credentials.Certificate(str(SERVICE_ACCOUNT_PATH))

        # Firebase Admin SDK 초기화
        firebase_admin.initialize_app(cred)