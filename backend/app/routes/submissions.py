from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from typing import Optional
from app.db.database import get_db
from app.models.submission import Submission, Contributor, QAStatus, FileType
from app.services.storage import upload_file
from app.services.qa import run_qa_pipeline
import mimetypes

router = APIRouter(prefix="/api/submissions", tags=["submissions"])

ALLOWED_MIME_TYPES = {
    "image/jpeg": FileType.IMAGE,
    "image/png": FileType.IMAGE,
    "image/webp": FileType.IMAGE,
    "audio/mpeg": FileType.AUDIO,
    "audio/wav": FileType.AUDIO,
    "audio/ogg": FileType.AUDIO,
    "audio/mp4": FileType.AUDIO,
    "video/mp4": FileType.VIDEO,
    "video/webm": FileType.VIDEO,
}


async def process_submission_background(submission_id: str, file_content: bytes, filename: str, file_type: FileType, file_size: int):
    """Background task to run QA pipeline."""
    from app.db.database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        try:
            # Update status to processing
            await db.execute(
                update(Submission)
                .where(Submission.id == submission_id)
                .values(status=QAStatus.PROCESSING)
            )
            await db.commit()

            # Run QA
            qa_result = await run_qa_pipeline(file_content, filename, file_type, file_size)

            # Update submission with results
            await db.execute(
                update(Submission)
                .where(Submission.id == submission_id)
                .values(
                    status=qa_result["status"],
                    qa_score=qa_result["qa_score"],
                    qa_results=qa_result["qa_results"],
                    ai_analysis=qa_result["ai_analysis"],
                    flag_reason=qa_result["flag_reason"],
                    processing_time_ms=qa_result["processing_time_ms"],
                )
            )

            # Update contributor stats
            submission = await db.get(Submission, submission_id)
            if submission:
                passed = qa_result["status"] == QAStatus.PASSED
                await db.execute(
                    update(Contributor)
                    .where(Contributor.id == submission.contributor_id)
                    .values(
                        total_submissions=Contributor.total_submissions + 1,
                        passed_submissions=Contributor.passed_submissions + (1 if passed else 0),
                        failed_submissions=Contributor.failed_submissions + (0 if passed else 1),
                    )
                )

            await db.commit()
        except Exception as e:
            await db.rollback()
            await db.execute(
                update(Submission)
                .where(Submission.id == submission_id)
                .values(status=QAStatus.FAILED, flag_reason=f"Processing error: {str(e)}")
            )
            await db.commit()


@router.post("/upload")
async def upload_submission(
    background_tasks: BackgroundTasks,
    contributor_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    # Validate contributor exists
    contributor = await db.get(Contributor, contributor_id)
    if not contributor:
        raise HTTPException(status_code=404, detail="Contributor not found")

    # Validate file type
    content_type = file.content_type or mimetypes.guess_type(file.filename)[0] or ""
    file_type = ALLOWED_MIME_TYPES.get(content_type)
    if not file_type:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {content_type}")

    # Read file
    file_content = await file.read()
    file_size = len(file_content)

    # Upload to storage
    file_url = await upload_file(file_content, file.filename, content_type)

    # Create submission record
    submission = Submission(
        contributor_id=contributor_id,
        file_type=file_type,
        file_url=file_url,
        file_name=file.filename,
        file_size=file_size,
        mime_type=content_type,
        status=QAStatus.PENDING,
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)

    # Queue background QA processing
    background_tasks.add_task(
        process_submission_background,
        submission.id,
        file_content,
        file.filename,
        file_type,
        file_size,
    )

    return {
        "submission_id": submission.id,
        "status": submission.status,
        "message": "Submission received. QA processing started."
    }


@router.get("/")
async def list_submissions(
    status: Optional[QAStatus] = None,
    file_type: Optional[FileType] = None,
    contributor_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = select(Submission)
    if status:
        query = query.where(Submission.status == status)
    if file_type:
        query = query.where(Submission.file_type == file_type)
    if contributor_id:
        query = query.where(Submission.contributor_id == contributor_id)

    total_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(total_query)

    query = query.order_by(Submission.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    submissions = result.scalars().all()

    return {
        "submissions": [
            {
                "id": s.id,
                "contributor_id": s.contributor_id,
                "file_type": s.file_type,
                "file_name": s.file_name,
                "file_size": s.file_size,
                "status": s.status,
                "qa_score": s.qa_score,
                "flag_reason": s.flag_reason,
                "processing_time_ms": s.processing_time_ms,
                "created_at": s.created_at,
            }
            for s in submissions
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{submission_id}")
async def get_submission(submission_id: str, db: AsyncSession = Depends(get_db)):
    submission = await db.get(Submission, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    return submission


@router.get("/stats/overview")
async def get_stats(db: AsyncSession = Depends(get_db)):
    total = await db.scalar(select(func.count(Submission.id)))
    pending = await db.scalar(select(func.count(Submission.id)).where(Submission.status == QAStatus.PENDING))
    processing = await db.scalar(select(func.count(Submission.id)).where(Submission.status == QAStatus.PROCESSING))
    passed = await db.scalar(select(func.count(Submission.id)).where(Submission.status == QAStatus.PASSED))
    failed = await db.scalar(select(func.count(Submission.id)).where(Submission.status == QAStatus.FAILED))
    flagged = await db.scalar(select(func.count(Submission.id)).where(Submission.status == QAStatus.FLAGGED))
    avg_score = await db.scalar(select(func.avg(Submission.qa_score)).where(Submission.qa_score.isnot(None)))
    avg_processing = await db.scalar(select(func.avg(Submission.processing_time_ms)).where(Submission.processing_time_ms.isnot(None)))

    return {
        "total": total or 0,
        "pending": pending or 0,
        "processing": processing or 0,
        "passed": passed or 0,
        "failed": failed or 0,
        "flagged": flagged or 0,
        "avg_qa_score": round(float(avg_score or 0), 1),
        "avg_processing_time_ms": round(float(avg_processing or 0), 1),
        "pass_rate": round((passed / total * 100) if total else 0, 1),
    }
