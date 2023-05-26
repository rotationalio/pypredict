from fastapi import APIRouter

from api.endpoints import homepage, about, data_source, hypothesis, online_learning


api_router = APIRouter()
api_router.include_router(homepage.router, prefix="", tags=["homepage"])
api_router.include_router(about.router, prefix="", tags=["about"])
api_router.include_router(data_source.router, prefix="", tags=["data_source"])
api_router.include_router(hypothesis.router, prefix="", tags=["hypothesis"])
api_router.include_router(online_learning.router, prefix="", tags=["online_learning"])

