"""运动模式解析器"""

from typing import Dict


class SportModelParser:
    """运动模式参数解析器"""
    
    @staticmethod
    def parse_sport_model(payload: bytes) -> Dict[str, int]:
        """解析运动模式配置 (0x0F 0x60)"""
        return {"en": payload[0], "ecg": payload[1]} if len(payload) >= 2 else {}

    @staticmethod
    def parse_xo(payload: bytes) -> Dict[str, int]:
        """解析XO参数 (0x0F 0x61)"""
        return {"en": payload[0], "xo": payload[1]} if len(payload) >= 2 else {}

    @staticmethod
    def parse_sr(payload: bytes) -> Dict[str, int]:
        """解析SR参数 (0x0F 0x62)"""
        return {"en": payload[0], "sr": payload[1]} if len(payload) >= 2 else {}
