from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Imagine BE1 server is running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}