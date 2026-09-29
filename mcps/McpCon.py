import asyncio
import threading
import uuid
from queue import Queue

from loguru import logger
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


class McpCon:
    def __init__(self, server_name: str, url: str):
        self.server_name = server_name
        self.url = url
        self.reqQueue = Queue()
        self.resQueue = Queue()
        self.testConQueue = Queue()
        thread = threading.Thread(target=self._start, daemon=True)
        thread.start()
        msg = self.testConQueue.get(block=True)
        logger.info(msg)

    def _start(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._run_loop())

    async def _run_loop(self):
        async with streamable_http_client(self.url) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                msg = f'mcp【{self.url}】服务连接成功'
                self.testConQueue.put(msg)
                while True:
                    act, tool_name, tool_args, req_id = self.reqQueue.get(block=True)
                    if act == 'call_tool':
                        logger.info(f'开始执行mcp【{self.url}】【call_tool】')
                        res = await session.call_tool(tool_name, arguments=tool_args)
                        logger.info(f'结束执行mcp【{self.url}】【call_tool】')
                        self.resQueue.put((res.structured_content, req_id))
                    elif act == 'list_tools':
                        logger.info(f'开始执行mcp【{self.url}】【list_tools】')
                        resp = await session.list_tools()
                        logger.info(f'结束执行mcp【{self.url}】【list_tools】')
                        self.resQueue.put((resp.tools, req_id))
                    else:
                        logger.info(f'退出mcp【{self.url}】')
                        break

    def list_tools(self):
        logger.info('调用list_tools方法')
        req_id = uuid.uuid4().hex
        self.reqQueue.put(('list_tools', None, None, req_id))
        res = self.resQueue.get(block=True)
        return res

    def call_tool(self, tool_name, arguments):
        logger.info('调用call_tool方法')
        req_id = uuid.uuid4().hex
        self.reqQueue.put(('call_tool', tool_name, arguments, req_id))
        res, rq_id = self.resQueue.get()
        if rq_id == req_id:
            return res
        else:
            return None

    def close(self):
        logger.info('调用close方法')
        req_id = uuid.uuid4().hex
        self.reqQueue.put(('close', None, None, req_id))
        return None
