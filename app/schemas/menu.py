"""
菜单模块 Schema
定义菜单相关接口的请求体结构，以及 Menu 实体的序列化与组树
"""

from pydantic import BaseModel, Field

from app.models.menu import Menu


class MenuSaveRequest(BaseModel):
    """新增菜单请求体"""

    name: str = Field(min_length=1, max_length=100)
    pid: int = Field(ge=0, description="父级菜单 ID，一级菜单传 0")
    code: str = Field(min_length=1, max_length=100)
    type: int = Field(ge=1, le=2, description="1 路由节点，2 功能按钮")
    level: int = Field(ge=1, le=4, description="层级：1~3 为路由，4 为按钮")


class MenuUpdateRequest(BaseModel):
    """更新菜单请求体（契约 7.3 仅定义这 5 个字段，无 type）"""

    id: int
    name: str = Field(min_length=1, max_length=100)
    pid: int = Field(ge=0)
    code: str = Field(min_length=1, max_length=100)
    level: int = Field(ge=1, le=4)


def menu_to_dict(menu: Menu) -> dict:
    """Menu 实体 -> 契约树节点结构（children 预置空列表；select 预置 False，7.5 再标注）"""
    return {
        "id": menu.menu_id,
        "name": menu.name,
        "pid": menu.pid,
        "code": menu.code or "",
        "toCode": menu.to_code or "",
        "type": menu.type,
        "status": menu.status or "",
        "level": menu.level,
        "select": False,
        "children": [],
    }


def build_menu_tree(menus: list[Menu], selected_ids: set[int] | None = None) -> list[dict]:
    """
    平铺菜单列表 → 树形结构（一次查全表后的纯内存组装，零额外查库）
    :param selected_ids: 7.5 回显用，命中集合的节点 select=True；None 表示不回显（7.1 恒 False）
    """
    # 1. 全部实体先转成 dict 节点，并以 menu_id 建索引——O(1) 定位父节点是整个算法的关键
    nodes: dict[int, dict] = {m.menu_id: menu_to_dict(m) for m in menus}

    # 2. 回显勾选：只改标志位，不动结构（set 的 in 是 O(1)，且天然去重 role_menu 重复行）
    if selected_ids is not None:
        for node in nodes.values():
            if node["id"] in selected_ids:
                node["select"] = True

    # 3. 单循环挂树：pid 能在字典里找到爹的挂进爹的 children；pid=0 或父节点缺失（孤儿）视为根
    #    menus 已按 menu_id 升序，append 顺序即兄弟节点顺序；parent is not node 防自环脏数据
    roots: list[dict] = []
    for m in menus:
        node = nodes[m.menu_id]
        parent = nodes.get(m.pid)
        if parent is not None and parent is not node:
            parent["children"].append(node)
        else:
            roots.append(node)
    return roots