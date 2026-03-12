"""REST API 路由"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api")

device_manager = None


def set_device_manager(manager):
    """设置设备管理器实例"""
    global device_manager
    device_manager = manager


class ModeRequest(BaseModel):
    """模式切换请求"""
    mode: str


class StatusResponse(BaseModel):
    """状态响应"""
    connected: bool
    mode: str
    device_address: str


class ModeResponse(BaseModel):
    """模式响应"""
    mode: str
    success: bool
    message: Optional[str] = None


@router.get("/status", response_model=StatusResponse)
async def get_status():
    """获取设备状态"""
    if not device_manager:
        raise HTTPException(status_code=500, detail="设备管理器未初始化")
    
    status = device_manager.get_status()
    return StatusResponse(**status)


@router.post("/connect")
async def connect_device():
    """连接设备"""
    if not device_manager:
        raise HTTPException(status_code=500, detail="设备管理器未初始化")
    
    if device_manager.is_connected:
        return {"success": True, "message": "设备已连接"}
    
    success = await device_manager.connect()
    
    if success:
        return {"success": True, "message": "设备连接成功"}
    else:
        raise HTTPException(status_code=500, detail="设备连接失败")


@router.post("/disconnect")
async def disconnect_device():
    """断开设备连接"""
    if not device_manager:
        raise HTTPException(status_code=500, detail="设备管理器未初始化")
    
    await device_manager.disconnect()
    return {"success": True, "message": "设备已断开"}


@router.get("/mode", response_model=ModeResponse)
async def get_mode():
    """获取当前工作模式"""
    if not device_manager:
        raise HTTPException(status_code=500, detail="设备管理器未初始化")
    
    if not device_manager.is_connected:
        raise HTTPException(status_code=400, detail="设备未连接")
    
    mode = device_manager.device_mode.mode_name
    return ModeResponse(mode=mode, success=True)


@router.post("/mode", response_model=ModeResponse)
async def set_mode(request: ModeRequest):
    """设置工作模式"""
    if not device_manager:
        raise HTTPException(status_code=500, detail="设备管理器未初始化")
    
    if not device_manager.is_connected:
        raise HTTPException(status_code=400, detail="设备未连接")
    
    mode = request.mode.lower()
    if mode not in ["sport", "ecg", "hrv"]:
        raise HTTPException(status_code=400, detail="无效的模式，必须是 sport/ecg/hrv")
    
    success = await device_manager.set_mode(mode)
    
    if success:
        return ModeResponse(
            mode=device_manager.device_mode.mode_name, 
            success=True, 
            message=f"已切换到 {device_manager.device_mode.mode_name} 模式"
        )
    else:
        error_msg = "模式切换失败"
        if not device_manager.is_connected:
            error_msg = "设备在切换过程中断开连接，请重新连接设备"
        raise HTTPException(status_code=500, detail=error_msg)
