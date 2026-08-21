from fastapi import APIRouter
from app.api.routes import health, feedback, roadmaps, tasks, notifications, dashboard

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
api_router.include_router(feedback.router)
api_router.include_router(roadmaps.router)
api_router.include_router(tasks.router)
api_router.include_router(notifications.router)
api_router.include_router(dashboard.router)
