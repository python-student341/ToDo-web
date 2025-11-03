from fastapi import APIRouter

from backend.api.api import router as api_router
from backend.api.task_api import router as task_api_router
from backend.api.subtask_api import router as subtask_api_router

main_router = APIRouter()

main_router.include_router(api_router)
main_router.include_router(task_api_router)
main_router.include_router(subtask_api_router)