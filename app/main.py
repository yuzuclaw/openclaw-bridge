from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.api.v1.health import router as health_router
from app.api.v1.capabilities import router as capabilities_router
from app.api.v1.tasks import router as tasks_router
from app.api.v1.mcp import router as mcp_router
from app.api.v1.agent_ws import router as agent_ws_router
from app.api.v1.agents import router as agents_router
from app.api.v1.task_execute import router as task_execute_router
from app.api.console import router as console_router
from app.repositories.task_repo import init_db

app = FastAPI(title="OpenClaw Bridge", version="0.1.0")


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/")
async def root() -> RedirectResponse:
    return RedirectResponse(url="/console", status_code=307)


app.include_router(health_router, prefix="/v1")
app.include_router(capabilities_router, prefix="/v1")
app.include_router(tasks_router, prefix="/v1")
app.include_router(mcp_router, prefix="/v1")
app.include_router(agent_ws_router, prefix="/v1")
app.include_router(agents_router, prefix="/v1")
app.include_router(task_execute_router, prefix="/v1")
app.include_router(console_router)
