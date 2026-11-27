from fastapi import APIRouter

def tools_router(repository):
    router = APIRouter(prefix="/tools")
    @router.get("/observations")
    def observations():
        return repository.recent(100)
    return router
