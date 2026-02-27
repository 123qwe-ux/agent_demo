"""FileSystem MCP Server 配置"""

FILESYSTEM_SERVER_CONFIG = {
    "name": "filesystem",
    "description": "提供文件系统读写能力",
    "command": "uvx",
    "args": ["filesystem-mcp-server", "./output"],
    "env": {},
}
