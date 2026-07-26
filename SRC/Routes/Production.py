from fastapi import APIRouter, UploadFile, File, Request, status
from fastapi.responses import JSONResponse, StreamingResponse
from Controllers.ProductionReportController import ProductionReportController
from Controllers.SecurityController import SecurityController, limiter
from Stores.LLM.Templates.Locales.en.section_registry import get_available_sections
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Helpers.Config import get_settings
from fastapi import Depends
import logging

def get_db():
    settings = get_settings()
    db_url = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_MAIN_DB}"
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

logger = logging.getLogger("uvicorn.error")

production_router = APIRouter(
    prefix="/api/v1/production",
    tags=["api_v1", "production"]
)

@production_router.get("/sections")
async def list_sections():
    """Return all available production sections and their readiness status."""
    return get_available_sections()

@production_router.post("/upload/{section}")
@limiter.limit("10/minute")
async def upload_production_report(
    request: Request, 
    section: str,
    file: UploadFile = File(...),
    db = Depends(get_db)
):
    try:
        controller = ProductionReportController()
        buffer, filename = await controller.process_report_to_excel(file, db, section=section)
        
        # Stream the in-memory Excel directly to the browser — nothing saved to disk
        return StreamingResponse(
            buffer,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except ValueError as e:
        logger.error(f"Value Error processing report: {e}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": str(e)}
        )
    except Exception as e:
        logger.error(f"Error processing report: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "An error occurred while processing the report."}
        )
