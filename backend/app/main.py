from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.db.database import init_db
from app.routes import submissions, contributors
from app.core.config import settings 



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

if settings.environment == "production":

    if not settings.frontend_url or settings.frontend_url == "*":
        raise ValueError("PROD ERROR: settings.frontend_url must be a specific secure website URL!")
    allowed_origins = [settings.frontend_url]
else:
    allowed_origins = ["http://localhost:3000", "http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(submissions.router)
app.include_router(contributors.router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "contributor-qa-pipeline"}
