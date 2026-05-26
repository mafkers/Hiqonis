import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import socketio

from apps.api.config import settings
from apps.api.api.v1.router import router as api_v1_router
from libs.infrastructure.database.models import Base
from libs.infrastructure.database.session import engine

# Structured logging mock
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("hiqonis")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables for local development
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialized successfully.")
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Socket.io ASGI integration
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
sio_app = socketio.ASGIApp(sio)
app.mount("/ws", sio_app)

@sio.event
async def connect(sid, environ):
    logger.info(f"Socket.io client connected: {sid}")

@sio.event
async def disconnect(sid):
    logger.info(f"Socket.io client disconnected: {sid}")

# RFC 7807 Problem Details Error Handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "type": f"https://api.hiqonis.com/errors/{exc.status_code}",
            "title": exc.detail if exc.status_code >= 400 else "HTTP Exception",
            "status": exc.status_code,
            "detail": exc.detail,
            "instance": request.url.path,
        },
        headers={"Content-Type": "application/problem+json"},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "type": "https://api.hiqonis.com/errors/validation-error",
            "title": "Validation Error",
            "status": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "detail": "The request body or query parameters are invalid.",
            "errors": exc.errors(),
            "instance": request.url.path,
        },
        headers={"Content-Type": "application/problem+json"},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled server exception caught by RFC 7807 middleware:")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "type": "https://api.hiqonis.com/errors/internal-server-error",
            "title": "Internal Server Error",
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "detail": "An unexpected error occurred. Please contact system administrator.",
            "instance": request.url.path,
        },
        headers={"Content-Type": "application/problem+json"},
    )

@app.get("/")
async def root():
    return {
        "name": settings.PROJECT_NAME,
        "status": "healthy",
        "version": "0.1.0"
    }

app.include_router(api_v1_router, prefix=settings.API_V1_STR)
