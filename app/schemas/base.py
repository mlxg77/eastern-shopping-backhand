from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    """VO 公共基类：字段定义用 snake_case，序列化出口自动驼峰（API.md 2.4）"""
    model_config = ConfigDict(
        # alias_generator=to_camel: 给每个字段自动起驼峰别名
        alias_generator=to_camel,
        # populate_by_name: 为 True 时，支持传入 snake_case 的字段名，自动转换为驼峰
        populate_by_name=True,
    )