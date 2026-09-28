from fastapi import APIRouter
from backend.api.schemas import HealthCheck
from backend.core.config import settings

router = APIRouter(tags=["Health"])

@router.get("/health", response_model=HealthCheck)
def get_health():
    """
    Liveness check endpoint returning system status and project metadata.
    """
    return HealthCheck(
        status="ok",
        project=settings.PROJECT_NAME,
        version="1.0.0"
    )
