from fastapi import APIRouter
from fastapi import Request
from fastapi.templating import Jinja2Templates

from pypredict.core import config


templates = Jinja2Templates(directory=config.TEMPLATE_DIR)
router = APIRouter()

@router.get("/data_source")
async def data_source(request: Request):
	return templates.TemplateResponse("pages/data_source.html",{"request":request})