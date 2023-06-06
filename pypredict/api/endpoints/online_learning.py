from fastapi import APIRouter
from fastapi import Request
from fastapi.templating import Jinja2Templates

from pypredict.core import config


templates = Jinja2Templates(directory=config.TEMPLATE_DIR)
router = APIRouter()

@router.get("/online_learning")
async def online_learning(request: Request):
	return templates.TemplateResponse("pages/online_learning.html",{"request":request})