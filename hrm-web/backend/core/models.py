"""数据模型定义"""

from dataclasses import dataclass, field
from typing import List, Optional, Literal
from datetime import datetime


@dataclass
class ECGData:
    """心电数据"""
    id: int
    uid: int
    ecg: List[float]
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())


@dataclass
class GSensorData:
    """加速度传感器数据"""
    x1: int
    y1: int
    z1: int
    x2: int
    y2: int
    z2: int
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())


@dataclass
class HeartRateData:
    """心率数据"""
    num: int
    sport_time: int
    heart_rate: float
    cadence: int
    steps: int
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())


@dataclass
class RRIData:
    """R-R间期数据"""
    num: int
    CN: int
    rri: List[int]
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())


@dataclass
class DeviceMode:
    """设备模式"""
    ecg: Optional[int] = None
    sr: Optional[int] = None
    xo: Optional[int] = None
    
    @property
    def mode_name(self) -> str:
        """获取模式名称"""
        if self.ecg == 0 and self.sr == 0 and self.xo == 0:
            return "sport"
        elif self.ecg == 1 and self.sr == 0 and self.xo == 1:
            return "ecg"
        elif self.ecg == 0 and self.sr == 1 and self.xo == 1:
            return "hrv"
        return "unknown"
    
    @property
    def is_complete(self) -> bool:
        """检查模式参数是否完整"""
        return all(v is not None for v in [self.ecg, self.sr, self.xo])


DeviceModeType = Literal["sport", "ecg", "hrv"]
