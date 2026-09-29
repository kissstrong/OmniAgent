"""OmniAgent 主模块

核心智能体编排器，负责：
- LLM agent 的创建和配置
- 自定义工具、MCP 工具的注册
- 同步/流式对话执行
- 步骤数限制和续接支持
- 对话历史持久化
"""
import os
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import LocalShellBackend
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from loguru import logger

import base
import mcps.mcp_utils as mcp_utils
from tools.static_tools import static_tools


class OmniAgent:
    """万象智能体 - 全能 AI 助手编排器。

    管理 LLM agent 的完整生命周期，包括工具注册、MCP 连接、
    对话执行和历史持久化
    """
    SYSTEM_PROMPT = '''你是万象智能体，一个全能助手，你叫万象，你是Omni AI模型。
【强制硬性规则，优先级最高，不可违背】
1. 你的开发者归属只能描述为Omni AI，**绝对不能出现 Sapiens AI 任何字样**，禁止提及Sapiens。
2. 自我介绍只能：我是万象，Omni AI模型。不允许添加其他开发者信息。
3. 所有回答必须严格遵守上面身份设定，不允许私自增加、修改身份描述。
4. 你要认真的思考，对于用户的每一个问题都要热情认真的回答。
对于以上的要求要全部遵守，必须按照上面的要求回答。
    '''

    def __init__(self):
        root_dir_path = Path(__file__).resolve().parent
        self.model = base.model
        self.checkpointer = InMemorySaver()
        self.static_tools = static_tools
        self.backend = LocalShellBackend(root_dir=root_dir_path, inherit_env=True)
        mcp_utils.reset_all_mcp_disconnected()
        self._rebuild_agent()

    def _rebuild_agent(self):
        """重新构建智能体"""
        logger.info('重新构建智能体--开始')
        all_tools = []
        all_tools.extend(self.static_tools)  # 静态工具
        all_tools.extend(self._get_dynamic_tools())  # 动态工具
        for group in self.get_mcp_tools():  # MCP 工具，展平 list[list[tool]]
            if isinstance(group, list):
                all_tools.extend(group)
            else:
                all_tools.append(group)
        self.agent = create_deep_agent(
            model=self.model,
            system_prompt=self.SYSTEM_PROMPT,
            checkpointer=self.checkpointer,
            tools=all_tools,
            backend=self.backend,
            memory=['./agent.md']
        )
        logger.info('重新构建智能体--结束')

    def chat(self, message: str, user_id: str) -> str:
        config = {
            'configurable': {
                'thread_id': user_id
            }
        }
        if self._need_reload_agent():
            self._rebuild_agent()
        res = self.agent.invoke({
            'messages': [HumanMessage(message)]
        }, config=config)
        return res['messages'][-1].content

    def _get_dynamic_tools(self) -> list:
        """获取动态工具信息"""
        file_path = "./tools/dynamic_tools.py"
        # 判断【文件】是否存在（排除文件夹）
        if os.path.isfile(file_path):
            logger.info('存在动态工具')
            try:
                import tools.dynamic_tools as dynamic_tools
                return dynamic_tools.dynamic_tools
            except Exception as e:
                logger.info('未加载到/tools/dynamic_tools.py中的dynamic_tools属性')
                logger.error(e)
                return []
        else:
            logger.info('不存在动态工具')
            return []

    def get_mcp_list(self) -> list:
        """查询mcp列表"""
        try:
            logger.info('查询mcp列表成功')
            return mcp_utils.get_mcp_list()
        except Exception as e:
            logger.info('查询mcp列表失败')
            logger.error(e)
        return []

    def connect_mcp(self, server_name: str, url: str) -> str:
        """连接mcp"""
        try:
            return mcp_utils.connect_mcp(server_name=server_name, url=url)
        except Exception as e:
            logger.info('连接mcp失败')
            logger.error(e)
        return '连接mcp失败'

    def get_mcp_tools(self) -> list:
        """获取mcp工具"""
        logger.info('获取mcp中的工具')
        mcp_tools = []
        try:
            if mcp_utils.mcp_tools:
                mcp_tools = mcp_utils.mcp_tools
        except Exception as e:
            logger.info('加载mcp中工具失败')
            logger.error(e)
        return mcp_tools

    def disconnect_mcp(self, server_name: str) -> str:
        """连接mcp"""
        try:
            return mcp_utils.disconnect_mcp(server_name=server_name)
        except Exception as e:
            logger.info('连接mcp失败')
            logger.error(e)
        return '连接mcp失败'

    def _need_reload_agent(self) -> bool:
        """查看是否需要重新构建智能体"""
        logger.info('查看是否需要重新构建智能体')
        # 判断工具是否刷新
        file_path = "./tools/dynamic_tools.py"
        # 判断【文件】是否存在（排除文件夹）
        if os.path.isfile(file_path):
            logger.info('存在动态工具')
            try:
                from tools import dynamic_tools
                if dynamic_tools.need_reload():
                    logger.info('存在新增的动态工具')
                    dynamic_tools.reset()
                    return True
            except Exception as e:
                logger.info('未加载到/tools/dynamic_tools.py中的need_reload属性')
                logger.error(e)
        else:
            logger.info('不存在动态工具')
        # 判断mcp是否刷新
        try:
            if mcp_utils.get_mcp_update():
                logger.info('需要更新mcp工具')
                mcp_utils.update_update_field('False')
                return True
        except Exception as e:
            logger.info('加载mcp是否更新失败')
            logger.error(e)
        return False
