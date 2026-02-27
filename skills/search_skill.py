"""搜索技能 - 支持 MCP 协议和直接 API 调用"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any

from langchain_core.tools import tool
from config.settings import Settings


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    score: float = 0.0


class SearchSkill:
    name = "web_search"
    description = "搜索互联网获取最新信息"

    def __init__(self, settings: Settings):
        self.settings = settings
        self.mcp_client = None

    def as_tool(self):
        @tool
        async def web_search(query: str, max_results: int = 5) -> str:
            """搜索互联网获取信息。query: 搜索关键词, max_results: 最大结果数"""
            results = await self.execute(query=query, max_results=max_results)
            return results
        return web_search

    async def execute(self, query: str, max_results: int = 5) -> str:
        if self.mcp_client:
            return await self._search_via_mcp(query, max_results)
        return await self._search_via_api(query, max_results)

    async def _search_via_mcp(self, query: str, max_results: int) -> str:
        result = await self.mcp_client.call_tool(
            server_name="web_search",
            tool_name="search",
            arguments={"query": query, "max_results": max_results},
        )
        return result

    async def _search_via_api(self, query: str, max_results: int) -> str:
        if self.settings.search_api == "tavily":
            from tavily import AsyncTavilyClient
            client = AsyncTavilyClient(api_key=self.settings.search_api_key)
            response = await client.search(query=query, max_results=max_results)
            results = []
            for item in response.get("results", []):
                results.append(f"**{item['title']}**\nURL: {item['url']}\n{item['content']}\n")
            return "\n---\n".join(results)
        raise ValueError(f"Unsupported search API: {self.settings.search_api}")
