"""加速度传感器数据解析器"""

from typing import Dict
from backend.core.utils import bytes_to_signed_short


class GSensorParser:
    """加速度传感器数据解析器"""
    
    @staticmethod
    def parse_gsensor(data: bytes) -> Dict[str, int]:
        """解析三轴加速度数据"""
        if len(data) < 12:
            return {}

        return {
            "x1": bytes_to_signed_short(data[0], data[1]),
            "y1": bytes_to_signed_short(data[2], data[3]),
            "z1": bytes_to_signed_short(data[4], data[5]),
            "x2": bytes_to_signed_short(data[6], data[7]),
            "y2": bytes_to_signed_short(data[8], data[9]),
            "z2": bytes_to_signed_short(data[10], data[11]),
        }
