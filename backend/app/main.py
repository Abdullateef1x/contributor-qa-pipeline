from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.db.database import init_db
from app.routes import submissions, contributors


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Contributor QA Pipeline",
    description="Real-world training data QA system for AI companies",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(submissions.router)
app.include_router(contributors.router)

@app.get("/")
def health():
    return {"status": "healthy", "message":"Contributor Qa Pipeline is running"}


