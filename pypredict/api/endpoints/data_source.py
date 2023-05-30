from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory="templates")
router = APIRouter()

@router.get("/data_source")
async def data_source(request: Request):
	return templates.TemplateResponse("pages/data_source.html",{"request":request})