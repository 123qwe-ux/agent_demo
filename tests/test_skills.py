"""Skills 模块单元测试"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from config.settings import Settings
from skills.analyze_skill import AnalyzeSkill
from skills.scrape_skill import ScrapeSkill
from skills.search_skill import SearchSkill, SearchResult
from skills.summarize_skill import SummarizeSkill


@pytest.fixture
def settings():
    return Settings(llm_api_key="test-key", search_api_key="test-search-key")


class TestAnalyzeSkill:
    def test_name(self):
        skill = AnalyzeSkill()
        assert skill.name == "analyze_topic"

    def test_description(self):
        skill = AnalyzeSkill()
        assert skill.description

    @pytest.mark.asyncio
    async def test_execute(self):
        skill = AnalyzeSkill()
        result = await skill.execute(topic="人工智能")
        assert "人工智能" in result
        assert len(result) > 0

    def test_as_tool(self):
        skill = AnalyzeSkill()
        tool = skill.as_tool()
        assert tool is not None
        assert tool.name == "analyze_topic"


class TestScrapeSkill:
    def test_name(self):
        skill = ScrapeSkill()
        assert skill.name == "scrape_webpage"

    def test_description(self):
        skill = ScrapeSkill()
        assert skill.description

    def test_as_tool(self):
        skill = ScrapeSkill()
        tool = skill.as_tool()
        assert tool is not None
        assert tool.name == "scrape_webpage"

    @pytest.mark.asyncio
    async def test_execute_mock(self):
        skill = ScrapeSkill()
        mock_response = MagicMock()
        mock_response.text = "<html><body><p>测试内容</p></body></html>"
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client:
            mock_ctx = AsyncMock()
            mock_ctx.__aenter__ = AsyncMock(return_value=mock_ctx)
            mock_ctx.__aexit__ = AsyncMock(return_value=None)
            mock_ctx.get = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_ctx

            with patch("skills.scrape_skill.Document") as mock_doc:
                mock_doc.return_value.summary.return_value = "<p>测试内容</p>"
                result = await skill.execute(url="https://example.com")
                assert isinstance(result, str)


class TestSearchSkill:
    def test_name(self, settings):
        skill = SearchSkill(settings)
        assert skill.name == "web_search"

    def test_description(self, settings):
        skill = SearchSkill(settings)
        assert skill.description

    def test_as_tool(self, settings):
        skill = SearchSkill(settings)
        tool = skill.as_tool()
        assert tool is not None
        assert tool.name == "web_search"

    @pytest.mark.asyncio
    async def test_execute_via_api_tavily(self, settings):
        skill = SearchSkill(settings)
        mock_client = AsyncMock()
        mock_client.search = AsyncMock(return_value={
            "results": [
                {"title": "测试标题", "url": "https://example.com", "content": "测试内容"}
            ]
        })

        with patch("skills.search_skill.AsyncTavilyClient", return_value=mock_client):
            result = await skill.execute(query="测试查询", max_results=3)
            assert "测试标题" in result
            assert "https://example.com" in result

    @pytest.mark.asyncio
    async def test_execute_via_mcp(self, settings):
        skill = SearchSkill(settings)
        mock_mcp = AsyncMock()
        mock_mcp.call_tool = AsyncMock(return_value="MCP搜索结果")
        skill.mcp_client = mock_mcp

        result = await skill.execute(query="测试查询")
        assert result == "MCP搜索结果"

    def test_search_result_dataclass(self):
        result = SearchResult(title="标题", url="https://example.com", snippet="摘要")
        assert result.title == "标题"
        assert result.url == "https://example.com"
        assert result.score == 0.0


class TestSummarizeSkill:
    def test_name(self, settings):
        with patch("skills.summarize_skill.ChatOpenAI"):
            skill = SummarizeSkill(settings)
            assert skill.name == "summarize_text"

    def test_description(self, settings):
        with patch("skills.summarize_skill.ChatOpenAI"):
            skill = SummarizeSkill(settings)
            assert skill.description

    def test_as_tool(self, settings):
        with patch("skills.summarize_skill.ChatOpenAI"):
            skill = SummarizeSkill(settings)
            tool = skill.as_tool()
            assert tool is not None
            assert tool.name == "summarize_text"

    @pytest.mark.asyncio
    async def test_execute(self, settings):
        with patch("skills.summarize_skill.ChatOpenAI") as mock_llm_class:
            mock_llm = MagicMock()
            mock_response = MagicMock()
            mock_response.content = "摘要内容"
            mock_llm.ainvoke = AsyncMock(return_value=mock_response)
            mock_llm_class.return_value = mock_llm

            skill = SummarizeSkill(settings)
            result = await skill.execute(text="长文本内容", focus="关键点")
            assert result == "摘要内容"
