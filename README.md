# OmniAgent

万象智能体

## 简介

OmniAgent（万象智能体）是一个基于 LangGraph 和 LangChain 的全能 AI 助手框架，支持：

- LLM agent 编排与对话管理
- 静态工具与动态工具生成
- MCP（Model Context Protocol）服务动态连接与管理
- 对话历史持久化
- 工具热更新（无需重启即可生效）

## 环境要求

- Python 3.12+
- Windows

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env` 文件并根据需要修改模型配置：

```bash
# 编辑 .env 文件
MODEL_KEY=your_api_key
MODEL_MODEL=your_model_name
MODEL_URL=https://your-api-endpoint.com/v1
```

### 3. 运行应用

```bash
python Application.py
```

进入交互式对话模式后：

| 输入 | 功能 |
|------|------|
| 普通文本 | 与智能体对话 |
| `1` | 查看所有已连接的 MCP 列表 |
| `2` | 连接新的 MCP 服务 |
| `3` | 列举所有 MCP 工具 |
| `quit` | 退出程序 |

## 项目结构

```
.
├── OmniAgent.py          # 主模块，智能体核心编排器
├── Application.py        # 入口文件，提供交互式 CLI
├── base.py               # LLM 模型初始化（基于环境变量配置）
├── agent.md              # Agent 运行规则与编码约定
├── .env                  # 环境变量配置（模型 Key、URL 等）
├── requirements.txt      # 依赖列表
├── tools/
│   ├── static_tools.py   # 静态工具（内置，不可修改）
│   ├── dynamic_tools.py  # 动态工具（运行时生成，支持热更新）
│   ├── tool_act.md       # 动态工具规范文档
│   └── tools_config.json # 工具配置（need_reload 标志）
└── mcps/
    ├── mcp_utils.py      # MCP 工具函数封装
    ├── McpCon.py         # MCP 连接管理
    ├── mcp_act.md        # MCP 规范文档
    └── mcps_config.json  # MCP 服务配置
```

## 工具系统

### 静态工具

内置固定工具，位于 `tools/static_tools.py`，当前提供：

| 工具 | 说明 |
|------|------|
| `get_city_coordinate(city)` | 查询城市经纬度 |
| `get_city_weather(city)` | 查询城市天气信息 |

### 动态工具

动态工具支持运行时生成，由 AI 根据用户需求自动编写代码并注册。

**创建规范**：参考 `tools/tool_act.md`

**关键要求**：
- 动态工具代码写入 `tools/dynamic_tools.py`
- 工具函数需添加到文件底部的 `dynamic_tools` 列表
- 新增/修改/删除工具后，需将 `need_reload` 设为 `"True"` 以触发重新加载
- 提供 `reset()` 方法用于重置 `need_reload`

## MCP 系统

MCP 支持通过 HTTP 协议连接外部工具服务，实现工具能力的动态扩展。

**配置规范**：参考 `mcps/mcp_act.md`

**配置格式**（`mcps/mcps_config.json`）：

```json
{
  "mcpServers": {
    "server-name": {
      "type": "streamable_http",
      "url": "http://127.0.0.1:8080/mcp",
      "connected": "False"
    }
  },
  "need_reload": "False"
}
```

**操作说明**：
- 只有新增或删除 MCP 服务时才能编辑配置文件
- 其他文件不允许编辑
- 删除服务前需确保已断开连接

## 架构设计

```
Application.py (CLI 入口)
    └── OmniAgent.py (核心编排器)
            ├── base.py (LLM 配置)
            ├── tools/
            │   ├── static_tools.py (静态工具)
            │   └── dynamic_tools.py (动态工具)
            └── mcps/
                └── mcp_utils.py (MCP 管理)
```

## 注意事项

1. **运行环境**：当前为 Windows 平台，使用 `python` 命令执行脚本（`python3` 不可用）
2. **路径映射**：工具中看到的根目录 `/` 实际映射到项目根目录 `D:\codes\pythoncode\omniAgent`
3. **编码规范**：所有生成的 Python 文件必须以 `# -*- coding: utf-8 -*-` 开头，文件读写统一使用 UTF-8 编码
