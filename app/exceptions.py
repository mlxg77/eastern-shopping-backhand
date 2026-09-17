"""
业务异常模块
定义全项目统一的业务状态码与业务异常

业务状态码取值对应接口文档 2.3 业务状态码表
"""


class BizCode:
    """业务状态码常量"""

    SUCCESS = 200             # 成功
    PARAM_ERROR = 201         # 请求参数错误
    USERNAME_EXISTS = 202     # 用户名已存在
    USERNAME_NOT_FOUND = 203  # 用户名不存在
    PASSWORD_ERROR = 204      # 用户名或密码错误
    SERVER_BUSY = 205         # 服务繁忙
    INVALID_TOKEN = 206       # 无效的 Token
    NEED_LOGIN = 207          # 需要登录
    MENU_HAS_CHILDREN = 208   # 该节点下有子节点，不可以删除
    PATH_NOT_FOUND = 209      # 请求路径不存在


# 业务状态码 → 默认提示信息
DEFAULT_MESSAGES: dict[int, str] = {
    BizCode.PARAM_ERROR: "请求参数错误",
    BizCode.USERNAME_EXISTS: "用户名已存在",
    BizCode.USERNAME_NOT_FOUND: "用户名不存在",
    BizCode.PASSWORD_ERROR: "用户名或密码错误",
    BizCode.SERVER_BUSY: "服务繁忙",
    BizCode.INVALID_TOKEN: "无效的 Token",
    BizCode.NEED_LOGIN: "需要登录",
    BizCode.MENU_HAS_CHILDREN: "该节点下有子节点，不可以删除",
    BizCode.PATH_NOT_FOUND: "请求路径不存在",
}


class BizException(Exception):
    """
    业务异常
    在 crud / 路由层主动抛出，由全局异常处理器统一转成规范响应
    用法：raise BizException(BizCode.USERNAME_NOT_FOUND)
    """

    def __init__(self, code: int, message: str | None = None):
        self.code = code
        # 不传 message 时使用错误码对应的默认提示
        self.message = message or DEFAULT_MESSAGES.get(code, "未知错误")
        super().__init__(self.message)