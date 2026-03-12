"""工具函数"""

from datetime import datetime
from typing import Tuple


def datetime_to_bcd_bytes(dt: datetime) -> Tuple[int, ...]:
    """将日期时间转换为BCD编码字节"""
    def to_bcd(n: int, digits: int = 2) -> int:
        return int(f"{n:0{digits}d}", 16)

    return (
        0xFC,
        0x00,
        to_bcd(dt.year % 100),
        to_bcd(dt.month),
        to_bcd(dt.day),
        to_bcd(dt.hour),
        to_bcd(dt.minute),
        to_bcd(dt.second),
        to_bcd(dt.isoweekday() % 7),
        0x55,
    )


def create_date_payload(target_date: datetime) -> bytes:
    """创建日期载荷数据包"""
    bcd_values = datetime_to_bcd_bytes(target_date)
    return bytes(bcd_values).ljust(20, b"\x00")


def bytes_to_hex_string(data: bytes) -> str:
    """字节转十六进制字符串"""
    return " ".join(f"{b:02X}" for b in data)


def to_signed_byte(unsigned_byte: int) -> int:
    """无符号字节转有符号字节"""
    return unsigned_byte - 256 if unsigned_byte > 127 else unsigned_byte


def bytes_to_signed_short(high: int, low: int) -> int:
    """双字节转有符号短整型"""
    value = (high << 8) | low
    return value - 0x10000 if value >= 0x8000 else value
