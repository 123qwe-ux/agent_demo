"""Web Search MCP Server 配置"""

WEB_SEARCH_SERVER_CONFIG = {
    "name": "web_search",
    "description": "提供互联网搜索能力",
    "command": "uvx",
    "args": ["tavily-mcp-server"],
    "env": {
        "TAVILY_API_KEY": "",  # 从环境变量注入
    },
}
