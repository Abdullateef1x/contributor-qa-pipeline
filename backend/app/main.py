from fastapi import FastAPI
from app.routes import submissions


app = FastAPI(title="Contributor Qa Pipeline")



app.include_router(submissions.routers)

@app.get("/")
def health():
    return {"status": "healthy", "message":"Contributor Qa Pipeline is running"}


