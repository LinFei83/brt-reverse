"""WebSocket 实时数据推送"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Set
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket 连接管理器"""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket):
        """接受新的 WebSocket 连接"""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"新的 WebSocket 连接，当前连接数: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """移除 WebSocket 连接"""
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket 连接断开，当前连接数: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """广播消息到所有连接的客户端"""
        if not self.active_connections:
            return
        
        message_json = json.dumps(message)
        disconnected = set()
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                logger.error(f"发送消息失败: {e}")
                disconnected.add(connection)
        
        for conn in disconnected:
            self.disconnect(conn)


manager = ConnectionManager()


def get_connection_manager() -> ConnectionManager:
    """获取连接管理器实例"""
    return manager


async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 端点处理函数"""
    await manager.connect(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except json.JSONDecodeError:
                logger.warning(f"收到无效的 JSON 数据: {data}")
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket 错误: {e}")
        manager.disconnect(websocket)


def create_data_callback(connection_manager: ConnectionManager):
    """创建数据回调函数，用于设备管理器"""
    
    def callback(result: dict):
        """处理设备数据并广播"""
        message = {
            "type": result["type"],
            "timestamp": datetime.now().timestamp(),
            "data": result["data"]
        }
        
        asyncio.create_task(connection_manager.broadcast(message))
    
    return callback
