from fastapi import APIRouter
from fastapi import Request
from fastapi.templating import Jinja2Templates

from pypredict.core import config


templates = Jinja2Templates(directory=config.TEMPLATE_DIR)
router = APIRouter()

@router.get("/about")
async def about(request: Request):
	return templates.TemplateResponse("pages/about.html",{"request":request})