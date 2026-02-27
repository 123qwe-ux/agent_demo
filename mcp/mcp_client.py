"""MCP (Model Context Protocol) 客户端 - 统一工具调用协议"""
from __future__ import annotations
import json
from typing import Any
from dataclasses import dataclass, field

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from config.settings import Settings


@dataclass
class MCPServerConfig:
    name: str
    command: str
    args: list[str] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)


class MCPClient:
    """MCP 客户端 - 管理多个 MCP Server 连接"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.sessions: dict[str, ClientSession] = {}
        self.server_configs: dict[str, MCPServerConfig] = {}
        self._parse_config(settings)

    def _parse_config(self, settings: Settings):
        for name, config in settings.mcp_servers.items():
            self.server_configs[name] = MCPServerConfig(
                name=name,
                command=config["command"],
                args=config.get("args", []),
                env=config.get("env", {}),
            )

    async def connect(self, server_name: str) -> ClientSession:
        if server_name in self.sessions:
            return self.sessions[server_name]
        config = self.server_configs[server_name]
        server_params = StdioServerParameters(
            command=config.command,
            args=config.args,
            env=config.env or None,
        )
        read_stream, write_stream = await stdio_client(server_params).__aenter__()
        session = ClientSession(read_stream, write_stream)
        await session.__aenter__()
        await session.initialize()
        self.sessions[server_name] = session
        return session

    async def list_tools(self, server_name: str) -> list[dict]:
        session = await self.connect(server_name)
        result = await session.list_tools()
        return [
            {"name": tool.name, "description": tool.description, "input_schema": tool.inputSchema}
            for tool in result.tools
        ]

    async def call_tool(self, server_name: str, tool_name: str, arguments: dict[str, Any]) -> str:
        session = await self.connect(server_name)
        result = await session.call_tool(tool_name, arguments=arguments)
        contents = []
        for content in result.content:
            if hasattr(content, "text"):
                contents.append(content.text)
        return "\n".join(contents)

    async def disconnect_all(self):
        for session in self.sessions.values():
            await session.__aexit__(None, None, None)
        self.sessions.clear()
