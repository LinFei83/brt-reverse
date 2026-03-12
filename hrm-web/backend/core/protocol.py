"""蓝牙协议解析器"""

from typing import Dict, Any
from backend.core.utils import to_signed_byte
from backend.parsers import EcgParser, GSensorParser, RealtimeParser, SportModelParser


class ProtocolParser:
    """蓝牙数据包协议解析器"""
    
    @staticmethod
    def parse_packet(data: bytes) -> Dict[str, Any]:
        """解析20字节数据包
        
        Args:
            data: 原始字节数据
            
        Returns:
            解析后的数据字典，包含type和data字段
        """
        result = {"type": "Other", "data": list(data)}
        
        if len(data) != 20:
            return result

        command_byte = to_signed_byte(data[0])
        sub_command = data[1]
        payload = data[2:]

        # 0x0F (15) 配置命令组
        if command_byte == 0x0F:
            if sub_command == 0x12:
                return {
                    "type": "GSensor",
                    "data": GSensorParser.parse_gsensor(data[4:16]),
                }
            if sub_command == 0x60:
                return {
                    "type": "SportModel",
                    "data": SportModelParser.parse_sport_model(payload),
                }
            if sub_command == 0x61:
                return {"type": "XO", "data": SportModelParser.parse_xo(payload)}
            if sub_command == 0x62:
                return {"type": "SR", "data": SportModelParser.parse_sr(payload)}

        # 0x14 (20) 实时数据命令组
        elif command_byte == 0x14:
            if sub_command == 0x06:
                return {
                    "type": "HR",
                    "data": RealtimeParser.parse_hr(payload),
                }
            if sub_command == 0x07:
                return {
                    "type": "RRI",
                    "data": RealtimeParser.parse_rri(payload),
                }

        # 0x41 (65) 心电数据
        elif command_byte == 0x41:
            return {"type": "ECG", "data": EcgParser.parse_ecg(data[1:])}

        # 0x42 (66) 心电信息
        elif command_byte == 0x42:
            if sub_command == 0x01:
                return {"type": "ECGSignal", "data": EcgParser.parse_signal(payload)}
            if sub_command == 0x06:
                return {
                    "type": "ECGSpeed",
                    "data": EcgParser.parse_speed(payload),
                }
            if sub_command == 0x0B:
                return {
                    "type": "ECRSR",
                    "data": EcgParser.parse_sr(payload),
                }

        return result
