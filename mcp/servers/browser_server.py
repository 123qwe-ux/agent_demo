"""Browser MCP Server 配置"""

BROWSER_SERVER_CONFIG = {
    "name": "browser",
    "description": "提供浏览器操作能力（页面访问、内容提取）",
    "command": "uvx",
    "args": ["browser-mcp-server"],
    "env": {},
}
