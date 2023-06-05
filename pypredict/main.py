from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from pypredict.api.base import api_router
from pypredict.core import config


def include_router(app):
	app.include_router(api_router)

def configure_static(app):
    app.mount("/static", StaticFiles(directory=config.STATIC_DIR), name="static")

def start_application():
	app = FastAPI(title=config.PROJECT_NAME,version=config.PROJECT_VERSION)
	include_router(app)
	configure_static(app)
	return app 

app = start_application()
