from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory="templates")
router = APIRouter()

@router.get("/online_learning")
async def online_learning(request: Request):
	return templates.TemplateResponse("pages/online_learning.html",{"request":request})