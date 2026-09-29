Agent 运行规则：
- 工具方面要支持动态生成工具，并实时生效，具体要求和规范参考./tool/tool_act.md文件。
- mcp要支持动态加载，并实时生效，具体要求和规范参考./mcps/mcp_act.md文件。
编码约定，必须遵守:
- 所有生成的py文件都必须在开头加上# -*- coding: utf-8 -*-，用来保证编码是utf8
- 所有文件操作必须全部是utf-8编码，包含读文件，写文件
环境信息:
- 运行环境为Windows，Python 3.12.14
- 执行校验命令时必须用 `python` 命令，`python3`、`which` 等命令不可用（会静默无输出或报错）
- 用户提供的工具代码若缺少return语句等明显笔误，应补全修正后再校验，并在反馈中说明修改点
- 文件工具(ls/read_file/write_file/delete)看到的根目录 `/` 实际映射到磁盘路径 `D:\codes\pythoncode\omniAgent`。
  因此在 execute 中运行脚本时，`cd /` 无效（会落到 D:\ 根目录），必须用真实绝对路径，例如：
  `python D:\codes\pythoncode\omniAgent\xxx.py`