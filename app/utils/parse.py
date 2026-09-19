"""
参数解析工具模块
请求参数的容错解析
"""


def parse_path_int(value: str, default: int) -> int:
    """解析路径参数中的正整数；非法值（非数字 / 小于 1）按默认值兜底"""
    return int(value) if value.isdigit() and int(value) > 0 else default