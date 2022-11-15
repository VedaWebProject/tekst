import sys

from fastapi import FastAPI, status
from textrig.config import TextRigConfig, get_config
from textrig.db import init_client as init_db_client
from textrig.db.indexes import create_indexes
from textrig.dependencies import get_db_client
from textrig.layer_types import init_layer_type_manager
from textrig.logging import log, setup_logging
from textrig.routers import get_routers
from textrig.tags import tags_metadata


# set up logging to match prod/dev requirements
setup_logging()

# get (possibly cached) config data
_cfg: TextRigConfig = get_config()


def pre_startup_routine() -> None:
    print(file=sys.stderr)  # blank line for visual separation of app runs

    # Hello World!
    log.info(
        f"TextRig Server v{_cfg.info.version} "
        f"running in {'DEVELOPMENT' if _cfg.dev_mode else 'PRODUCTION'} MODE"
    )

    # init layer type plugin manager
    init_layer_type_manager()

    # include routers
    log.info("Hooking up API routers")
    for router in get_routers():
        app.include_router(router)


async def startup_routine() -> None:
    init_db_client()
    await create_indexes()
    # log dev server info
    if _cfg.dev_mode:  # pragma: no cover
        log.info(
            "Development server bound to "
            f"http://{_cfg.dev_srv_host}:{_cfg.dev_srv_port}"
        )


async def shutdown_routine() -> None:
    log.info("Closing database client")
    get_db_client(_cfg).close()


# initialize FastAPI app
app = FastAPI(
    root_path=_cfg.root_path,
    title=_cfg.app_name,
    description=_cfg.info.description,
    version=_cfg.info.version,
    terms_of_service=_cfg.info.terms,
    contact={
        "name": _cfg.info.contact_name,
        "url": _cfg.info.contact_url,
        "email": _cfg.info.contact_email,
    },
    license_info={
        "name": _cfg.info.license,
        "url": _cfg.info.license_url,
    },
    openapi_tags=tags_metadata,
    openapi_url=_cfg.doc.openapi_url,
    docs_url=_cfg.doc.swaggerui_url,
    redoc_url=_cfg.doc.redoc_url,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid Request"},
    },
    on_startup=[startup_routine],
    on_shutdown=[shutdown_routine],
)

# run pre-startup routine
pre_startup_routine()
