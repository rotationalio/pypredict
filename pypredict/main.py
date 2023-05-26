import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from api.base import api_router
from core import config


def include_router(app):
	app.include_router(api_router)

def configure_static(app):
    app.mount("/static", StaticFiles(directory="static"), name="static")

def start_application():
	app = FastAPI(title=config.PROJECT_NAME,version=config.PROJECT_VERSION)
	include_router(app)
	configure_static(app)
	return app 

app = start_application()
