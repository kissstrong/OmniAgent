MCP 调用:
- 连接mcp或调用mcp服务的时候不容许创建脚本执行，必须使用使用程序代码执行
- 只有新增或删除mcp访问的时候才容许编辑/mcps/mcps_config.json文件，别的文件都不容许编辑
- 配置见 /mcps/mcps_config.json,格式如下
  {
    "mcpServers": {
      "test-mcp-server": {
        "type": "streamable_http",
        "url": "http://127.0.0.1:8080/mcp",
        "connected": "True"
      }
    },
    "need_reload": "False"
  }
  其中mcpServers是所有mcp服务存放的位置，一个服务一个kv，例如test-mcp-server的mcp服务配置
   "test-mcp-server": {
     "type": "streamable_http",
     "url": "http://127.0.0.1:8080/mcp",
     "connected": "True"
   }
   其中type都是固定的streamable_http，url是mcp的服务地址，connected属性是是否连接，默认是False，如果后续有动态新增mcp服务，则必须补充服务名称，服务地址，connected属性为'False',必须按照如上规则添加， 如果删除某个mcp服务则查看是否已经断开连接，如果没有断开则提示必须断开才能删除
