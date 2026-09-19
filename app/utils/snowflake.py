"""
雪花 ID 生成器模块
生成全局唯一、趋势递增的整型业务 ID

位分配（共 53 位）：
| 40 位时间戳(毫秒) | 8 位机器位 | 5 位序列号 |

53 位 < 2^53，落在 JavaScript 安全整数范围内，前端 JSON 解析不会丢精度。
"""

import threading
import time

# 起始纪元（毫秒）：2024-01-01 00:00:00 UTC
# 时间戳部分 = 当前时间 - EPOCH，EPOCH 越晚 ID 越短
EPOCH = 1704067200000

TIMESTAMP_BITS = 40   # 毫秒时间戳，可用约 34.8 年
WORKER_ID_BITS = 8    # 机器位，最多 256 个部署实例
SEQUENCE_BITS = 5     # 毫秒内序列号，单机每秒最多 32000 个

MAX_WORKER_ID = (1 << WORKER_ID_BITS) - 1
SEQUENCE_MASK = (1 << SEQUENCE_BITS) - 1

WORKER_ID_SHIFT = SEQUENCE_BITS                      # 5
TIMESTAMP_SHIFT = SEQUENCE_BITS + WORKER_ID_BITS     # 13


class SnowflakeGenerator:
    """线程安全的雪花 ID 生成器"""

    def __init__(self, worker_id: int = 1):
        if not 0 <= worker_id <= MAX_WORKER_ID:
            raise ValueError(f"worker_id 必须在 0 ~ {MAX_WORKER_ID} 之间")
        self._worker_id = worker_id
        self._sequence = 0
        self._last_timestamp = -1
        self._lock = threading.Lock()

    def next_id(self) -> int:
        """生成下一个全局唯一的整型 ID"""
        with self._lock:
            timestamp = int(time.time() * 1000)

            # 时钟回拨保护：等待时间追平；回拨过大直接拒绝，宁可报错不可重复
            if timestamp < self._last_timestamp:
                offset = self._last_timestamp - timestamp
                if offset > 1000:
                    raise RuntimeError(f"检测到时钟回拨 {offset} ms，拒绝生成 ID")
                time.sleep(offset / 1000 + 0.001)
                timestamp = int(time.time() * 1000)

            if timestamp == self._last_timestamp:
                # 同一毫秒内：序列号 +1
                self._sequence = (self._sequence + 1) & SEQUENCE_MASK
                if self._sequence == 0:
                    # 序列号用尽（本毫秒已发满 32 个），等到下一毫秒
                    while timestamp <= self._last_timestamp:
                        timestamp = int(time.time() * 1000)
            else:
                # 进入新毫秒：序列号归零
                self._sequence = 0

            self._last_timestamp = timestamp

            # 三段左移腾位后按位或合并：
            # [40 位时间戳][8 位机器][5 位序列]
            return (
                ((timestamp - EPOCH) << TIMESTAMP_SHIFT)
                | (self._worker_id << WORKER_ID_SHIFT)
                | self._sequence
            )


# 全局单例：本项目所有业务 ID 都从这里取
# 多实例部署时各实例需配置不同的 worker_id（从环境变量读取即可）
snowflake = SnowflakeGenerator()