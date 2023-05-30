from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory="templates")
router = APIRouter()

@router.get("/hypothesis")
async def hypothesis(request: Request):
	return templates.TemplateResponse("pages/hypothesis.html",{"request":request})