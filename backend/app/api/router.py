from fastapi import APIRouter

from app.api.routers import auth, brews, health, interactive_optimizer, leaderboard, optimization

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(optimization.router)
api_router.include_router(interactive_optimizer.router)
api_router.include_router(brews.router)
api_router.include_router(leaderboard.router)
