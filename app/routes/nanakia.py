from fastapi import APIRouter

nanakia_router = APIRouter()


@nanakia_router.get('/')
async def index():
    return 'Hello, World from nanakia!!'
