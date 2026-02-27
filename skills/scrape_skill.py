"""网页抓取技能"""
import re
from langchain_core.tools import tool


class ScrapeSkill:
    name = "scrape_webpage"
    description = "抓取指定 URL 的网页正文内容"

    def as_tool(self):
        @tool
        async def scrape_webpage(url: str) -> str:
            """抓取网页正文内容。url: 目标网页地址"""
            return await self.execute(url=url)
        return scrape_webpage

    async def execute(self, url: str) -> str:
        import httpx
        from readability import Document

        async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
            resp = await client.get(url, headers={"User-Agent": "ResearchAgent/1.0"})
            resp.raise_for_status()

        doc = Document(resp.text)
        text = re.sub(r"<[^>]+>", "", doc.summary())
        return text[:5000]
