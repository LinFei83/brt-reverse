"""FastAPI 应用主入口"""

import logging
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from backend.core import DeviceManager
from backend.api import router, websocket_endpoint
from backend.api.routes import set_device_manager
from backend.api.websocket import create_data_callback, get_connection_manager
from backend.config import HOST, PORT

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="心率带监测系统",
    description="实时心率带数据采集与可视化API",
    version="1.0.0"
)

device_manager = DeviceManager()
set_device_manager(device_manager)

connection_manager = get_connection_manager()
device_manager.set_data_callback(create_data_callback(connection_manager))

app.include_router(router)

frontend_path = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")


@app.get("/")
async def root():
    """返回前端页面"""
    return FileResponse(str(frontend_path / "index.html"))


@app.websocket("/ws")
async def websocket_route(websocket: WebSocket):
    """WebSocket 路由"""
    await websocket_endpoint(websocket)


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("应用启动")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("正在关闭应用...")
    await device_manager.disconnect()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=HOST,
        port=PORT,
        reload=True,
        log_level="info"
    )
