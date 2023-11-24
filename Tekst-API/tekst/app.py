import re
import sys

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette_csrf import CSRFMiddleware

from tekst.config import TekstConfig, get_config
from tekst.db import init_odm
from tekst.dependencies import get_db, get_db_client
from tekst.layer_types import init_layer_types_mgr
from tekst.logging import log, setup_logging
from tekst.openapi import customize_openapi
from tekst.routers import setup_routes
from tekst.settings import get_settings


_cfg: TekstConfig = get_config()  # get (possibly cached) config data
setup_logging()  # set up logging to match prod/dev requirements


async def startup_routine(app: FastAPI) -> None:
    # dev mode preparations
    if _cfg.dev_mode:
        # blank line for visual separation of app runs in dev mode
        print(file=sys.stderr)

    init_layer_types_mgr()
    setup_routes(app)

    # this is ugly, but unfortunately we don't have access to FastAPI's
    # dependency injection system in these lifecycle routines, so we have to
    # pass all these things by hand...
    await init_odm(get_db(get_db_client(_cfg), _cfg))

    settings = await get_settings()
    customize_openapi(app, _cfg, settings)

    # Hello World!
    log.info(
        f"{settings.info_platform_name} ({_cfg.tekst_name} "
        f"Server v{_cfg.tekst_version}) "
        f"running in {'DEVELOPMENT' if _cfg.dev_mode else 'PRODUCTION'} MODE"
    )


async def shutdown_routine(app: FastAPI) -> None:
    log.info(f"{_cfg.tekst_name} cleaning up and shutting down...")
    get_db_client(_cfg).close()  # again, no DI possible here :(


@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup_routine(app)
    yield
    await shutdown_routine(app)


# create FastAPI app instance
app = FastAPI(
    root_path=_cfg.api_path,
    openapi_url=_cfg.doc_openapi_url,
    docs_url=_cfg.doc_swaggerui_url,
    redoc_url=_cfg.doc_redoc_url,
    lifespan=lifespan,
)

# add and configure CSRF middleware
if not _cfg.dev_mode:
    app.add_middleware(
        CSRFMiddleware,
        secret=_cfg.security_secret,
        required_urls=[re.compile(r".*/auth/cookie/login.*")],
        exempt_urls=[re.compile(r".*/auth/cookie/logout.*")],
        sensitive_cookies={_cfg.security_auth_cookie_name},
        cookie_name="XSRF-TOKEN",
        cookie_path="/",
        cookie_domain=_cfg.security_auth_cookie_domain or None,
        cookie_secure=not _cfg.dev_mode,
        cookie_samesite="Lax",
        header_name="X-XSRF-TOKEN",
    )

# add and configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cfg.cors_allow_origins,
    allow_credentials=_cfg.cors_allow_credentials,
    allow_methods=_cfg.cors_allow_methods,
    allow_headers=_cfg.cors_allow_headers,
)
