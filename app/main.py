from fastapi import FastAPI
from app.core.firebase import initialize_firebase
from app.routers.scenarios import router as scenarios_router
from app.routers.users import router as users_router

initialize_firebase()

app = FastAPI()

app.include_router(scenarios_router) #시안 관련 API.
app.include_router(users_router) #사용자 관련 API.

@app.get("/")
def root():
    return {"message": "Imagine BE1 server is running"}


@app.get("/health") #이거는 사용자 토큰 발급이 잘 이루어지는지 테스트용도
def health_check():
    return {"status": "ok"}

