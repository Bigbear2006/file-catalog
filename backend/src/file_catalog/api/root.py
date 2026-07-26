from fastapi import APIRouter

from file_catalog.api.admin import admin_router
from file_catalog.api.file import file_router

api_router = APIRouter(prefix='/api')

routers = [file_router, admin_router]
for router in routers:
    api_router.include_router(router)
