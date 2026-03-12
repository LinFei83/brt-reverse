"""设备管理器"""

import asyncio
import logging
from datetime import datetime
from typing import Optional, Callable, Dict, Any
from bleak import BleakClient

from backend.core.protocol import ProtocolParser
from backend.core.utils import create_date_payload
from backend.core.models import DeviceMode, DeviceModeType
from backend.config import (
    DEVICE_ADDRESS,
    NOTIFY_UUID,
    WRITE_UUID,
    MODE_COMMANDS,
    READ_CONFIG_COMMANDS,
    START_COMMANDS,
)

logger = logging.getLogger(__name__)


class DeviceManager:
    """蓝牙心率带设备管理器"""
    
    def __init__(self):
        self.client: Optional[BleakClient] = None
        self.is_connected = False
        self.device_mode = DeviceMode()
        self.data_callback: Optional[Callable] = None
        self._mode_ready = asyncio.Event()
        
    async def connect(self) -> bool:
        """连接到设备"""
        try:
            logger.info(f"正在连接设备: {DEVICE_ADDRESS}")
            self.client = BleakClient(DEVICE_ADDRESS)
            await self.client.connect()
            
            await self.client.start_notify(NOTIFY_UUID, self._notification_handler)
            self.is_connected = True
            
            await self._initialize_device()
            
            logger.info("设备连接成功")
            return True
            
        except Exception as e:
            logger.error(f"设备连接失败: {e}")
            self.is_connected = False
            return False
    
    async def disconnect(self):
        """断开设备连接"""
        if self.client:
            try:
                if self.client.is_connected:
                    await self.client.stop_notify(NOTIFY_UUID)
                    await self.client.disconnect()
                self.is_connected = False
                self.device_mode = DeviceMode()
                logger.info("设备已断开")
            except Exception as e:
                logger.error(f"断开连接时出错: {e}")
                self.is_connected = False
    
    async def _initialize_device(self):
        """初始化设备，启动数据采集"""
        if not self.client:
            return
        
        await self._write_command(START_COMMANDS["accelerometer"])
        
        time_payload = create_date_payload(datetime.now())
        await self.client.write_gatt_char(WRITE_UUID, time_payload)
        
        for cmd in START_COMMANDS["query_ecg_info"]:
            await self._write_command(cmd)
            await asyncio.sleep(0.1)
        
        await self._read_current_mode()
    
    async def _read_current_mode(self):
        """读取当前设备模式"""
        self._mode_ready.clear()
        
        for cmd in READ_CONFIG_COMMANDS:
            await self._write_command(cmd)
            await asyncio.sleep(0.1)
        
        try:
            await asyncio.wait_for(self._mode_ready.wait(), timeout=5.0)
            logger.info(f"当前设备模式: {self.device_mode.mode_name}")
        except asyncio.TimeoutError:
            logger.warning("读取设备模式超时")
    
    async def set_mode(self, mode: DeviceModeType) -> bool:
        """设置设备工作模式
        
        Args:
            mode: 目标模式 (sport/ecg/hrv)
            
        Returns:
            是否设置成功
        """
        if not self.is_connected or not self.client:
            logger.error("设备未连接")
            return False
        
        commands = MODE_COMMANDS.get(mode)
        if not commands:
            logger.error(f"无效的模式: {mode}")
            return False
        
        logger.info(f"正在切换到 {mode} 模式...")
        
        try:
            if not self.client.is_connected:
                logger.error("蓝牙客户端已断开")
                self.is_connected = False
                return False
            
            for i, cmd in enumerate(commands):
                try:
                    await self._write_command(cmd, response=False)
                    await asyncio.sleep(0.3)
                except Exception as e:
                    logger.warning(f"命令 {i+1}/{len(commands)} 发送失败: {e}")
                    if "Not connected" in str(e) or "disconnected" in str(e).lower():
                        self.is_connected = False
                        raise
            
            await asyncio.sleep(1.0)
            
            if self.client.is_connected:
                self.device_mode = DeviceMode()
                await self._read_current_mode()
                logger.info(f"模式切换完成，当前模式: {self.device_mode.mode_name}")
            else:
                logger.warning("设备在模式切换过程中断开连接")
                self.is_connected = False
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"模式切换失败: {e}")
            self.is_connected = False
            return False
    
    def set_data_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """设置数据回调函数"""
        self.data_callback = callback
    
    async def _write_command(self, hex_str: str, response: bool = False):
        """发送蓝牙命令"""
        if not self.client:
            raise Exception("客户端未初始化")
        
        if not self.client.is_connected:
            raise Exception("设备未连接")
        
        await self.client.write_gatt_char(
            WRITE_UUID, bytes.fromhex(hex_str), response=response
        )
    
    def _notification_handler(self, sender: str, data: bytes):
        """处理蓝牙通知数据"""
        try:
            result = ProtocolParser.parse_packet(data)
            
            old_mode = self.device_mode.mode_name if self.device_mode.is_complete else None
            
            if result["type"] == "SportModel":
                self.device_mode.ecg = result["data"].get("ecg")
            elif result["type"] == "SR":
                self.device_mode.sr = result["data"].get("sr")
            elif result["type"] == "XO":
                self.device_mode.xo = result["data"].get("xo")
            
            if self.device_mode.is_complete:
                self._mode_ready.set()
                
                new_mode = self.device_mode.mode_name
                if old_mode != new_mode and self.data_callback:
                    logger.info(f"设备模式更新: {old_mode} -> {new_mode}")
                    self.data_callback({
                        "type": "ModeUpdate",
                        "data": {"mode": new_mode}
                    })
            
            if self.data_callback:
                self.data_callback(result)
                
        except Exception as e:
            logger.error(f"数据解析错误: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """获取设备状态"""
        return {
            "connected": self.is_connected,
            "mode": self.device_mode.mode_name if self.device_mode.is_complete else "unknown",
            "device_address": DEVICE_ADDRESS,
        }
