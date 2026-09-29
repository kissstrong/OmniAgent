import json
from pathlib import Path
from typing import List, Any

import mcp_types
from langchain_core.tools import StructuredTool
from loguru import logger
from pydantic import create_model

from mcps.McpCon import McpCon

path = Path(__file__).resolve().parent


def load_json_file():
    with open(path / "mcps_config.json", "r", encoding="utf-8") as f:
        data = json.load(f)  # json.load 读文件对象，直接转python dict/list
    return data


def update_json_file(data):
    with open(path / "mcps_config.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# mcp服务对应的http，session，tool的映射
mcp_to_tool_dic: dict[str, dict[str, Any]] = {}
mcp_tools = []


def get_mcp_list() -> list:
    """查询mcp列表"""
    logger.info('加载mcp列表')
    mcp_list = []
    try:
        # 你的 mcpServers 配置
        config_json = load_json_file()
        mcp_list = config_json["mcpServers"].items()
        logger.info('加载mcp成功')
    except Exception as e:
        logger.info('加载mcp失败')
        logger.error(e)
    return mcp_list


def get_mcp_update() -> bool:
    """查询mcp是否更新了"""
    logger.info('查询mcp是否更新了')
    need_reload = False
    try:
        # 你的 mcpServers 配置
        config_json = load_json_file()
        need_reload = config_json["need_reload"] == 'True'
    except Exception as e:
        logger.info('加载mcp失败')
        logger.error(e)
    logger.info('mcp是否更新:', need_reload)
    return need_reload


def update_connected_field(server_name: str, val: str):
    """更新connected属性值"""
    data = load_json_file()
    data['mcpServers'][server_name]['connected'] = val
    update_json_file(data)


def update_update_field(val: str):
    """更新connected属性值"""
    data = load_json_file()
    data['need_reload'] = val
    update_json_file(data)


def reset_all_mcp_disconnected():
    data = load_json_file()
    for name, cfg in data["mcpServers"].items():
        cfg['connected'] = 'False'
    update_json_file(data)


# 包装mcp的tool为agent的tool
def wrap_mcp_tool_to_agent_tool(tools: list, con: McpCon) -> List[StructuredTool]:
    """将 MCP Tool 列表转换为 Agent 所需的 Tool 列表（闭包实现）"""
    agent_tools: List[StructuredTool] = []
    for tool_list in tools:
        logger.info(f'type(tool)=>{type(tool_list)}')
        if type(tool_list) != list:
            logger.info(f'类型不是list=>{type(tool_list)}')
            continue
        tool = None
        for tool_item in tool_list:
            if type(tool_item) != mcp_types._types.Tool:
                continue
            else:
                tool = tool_item
            break
        if tool is None:
            continue

        # ⚠️ 核心：通过默认参数 _tool=tool 捕获当前循环变量，避免晚期绑定陷阱
        def make_call(_tool=tool, **kwargs: Any) -> str:
            result = con.call_tool(tool_name=_tool.name, arguments=kwargs)
            return result['result']

        # 定义 JSON Schema 到 Python 类型的映射
        TYPE_MAPPING = {
            "string": str,
            "integer": int,
            "number": float,
            "boolean": bool,
            "array": list,
            "object": dict,
        }
        # 动态生成 Pydantic Model（等价于 @tool 自动从函数签名推导参数模型）
        schema = tool.input_schema or {}
        properties = schema.get("properties", {})
        required = set(schema.get("required", []))
        field_definitions = {}
        for field_name, field_schema in properties.items():
            # 1. 获取 JSON Schema 类型
            json_type = field_schema.get('type', 'string')  # 默认为 string
            # 2. 映射为 Python 类型
            python_type = TYPE_MAPPING.get(json_type, Any)
            field_type = python_type
            default = ... if field_name in required else None
            field_definitions[field_name] = (field_type, default)
        ArgsModel = create_model(f"{tool.name}_Args", **field_definitions)
        # 组装为 StructuredTool（完全等价于 @tool 注解生成的对象）
        lc_tool = StructuredTool(
            name=con.server_name + '_mcp_' + tool.name,
            description=tool.description or "",
            func=make_call,  # 异步执行体（闭包）
            args_schema=ArgsModel,  # 参数校验模型
        )
        agent_tools.append(lc_tool)
    return agent_tools  # ← 返回 Agent 需要的 list


def connect_mcp(server_name, url):
    """连接mcp服务"""
    con = McpCon(server_name, url)
    mcp_tool = con.list_tools()
    agent_tools = wrap_mcp_tool_to_agent_tool(mcp_tool, con)
    mcp_to_tool_dic[server_name] = {
        'con': con,
        'tools': agent_tools
    }
    mcp_tools.append(agent_tools)
    update_connected_field(server_name, 'True')
    update_update_field('True')
    return f'mcp【{server_name}】服务连接成功'


def disconnect_mcp(server_name) -> str:
    mcp = mcp_to_tool_dic[server_name]
    if mcp is None:
        return f'mcp【{server_name}】服务未连接'
    con = mcp.get('con')
    con.close()
    tools = mcp.get('tools')
    mcp_tools.remove(tools)
    update_connected_field(server_name, 'False')
    update_update_field('True')
    return f'mcp【{server_name}】服务连接断开成功'
