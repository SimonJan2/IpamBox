import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import auth
from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.db import SessionLocal
from app.core.deps import require_auth

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if settings.ipambox_allow_insecure:
        logger.warning(
            "IPAMBOX_ALLOW_INSECURE is on — the API is unauthenticated. "
            "Only use this behind a trusted reverse proxy."
        )
    else:
        async with SessionLocal() as s:
            await auth.ensure_env_password_user(s)
    yield


app = FastAPI(title="IpamBox", version="0.1.0", docs_url="/docs", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# /auth/* stays open (it gates itself); everything else requires a session.
app.include_router(auth.router, prefix="/api/v1")
app.include_router(
    api_router, prefix="/api/v1", dependencies=[Depends(require_auth)]
)


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}
