import logging

import aiohttp_jinja2
import jinja2
from aiohttp import web
from aiohttp_apispec import setup_aiohttp_apispec, validation_middleware

from app.base.middlewares import error_middleware
from app.settings import config, BASE_DIR
from app.store.database.models import database_accessor
from app.store.telegram.accessor import TelegramAccessor


def setup_config(application: web.Application) -> None:
    application["config"] = config


def setup_routes(application: web.Application) -> None:
    from app.forum.routes import setup_routes as setup_forum_routes

    setup_forum_routes(application)


def setup_accessors(application: web.Application) -> None:
    database_accessor.setup(application)
    TelegramAccessor().setup(application)


def setup_middlewares(application: web.Application) -> None:
    application.middlewares.append(error_middleware)
    application.middlewares.append(validation_middleware)


def setup_external_libraries(application: web.Application) -> None:
    aiohttp_jinja2.setup(
        application, loader=jinja2.FileSystemLoader(f"{BASE_DIR}/templates")
    )
    setup_aiohttp_apispec(
        app=application,
        title="Forum documentation",
        version="v1",
        url="/swagger.json",
        swagger_path="/swagger",
    )


def setup_logging(_: web.Application) -> None:
    logging.basicConfig(level=logging.INFO)


def setup_app(application: web.Application) -> None:
    setup_config(application)
    setup_routes(application)
    setup_accessors(application)
    setup_external_libraries(application)
    setup_middlewares(application)
    setup_logging(application)


app = web.Application()

if __name__ == "__main__":
    setup_app(app)
    web.run_app(app, port=config["common"]["port"])
