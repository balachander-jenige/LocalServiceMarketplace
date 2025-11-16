import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api.routes import router
from .core.config import settings
from .dto.response_dto import ErrorResponse

# Configuration Logging.
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.SERVICE_NAME, version="1.0.0", description="API Gateway for Freelancer Marketplace")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routes
app.include_router(router, prefix="/api/v1")


# Global Exception Handling
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=ErrorResponse(detail=str(exc)).model_dump()
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(detail="Internal server error").model_dump(),
    )


# Health Check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.SERVICE_NAME, "version": "1.0.0"}


# Root Path
@app.get("/")
async def root():
    return {"service": settings.SERVICE_NAME, "version": "1.0.0", "docs": "/docs"}
