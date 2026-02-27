"""Agent 模块单元测试"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from config.settings import Settings
from agents.base_agent import BaseAgent
from agents.planner_agent import PlannerAgent
from agents.research_agent import ResearchAgent
from agents.writer_agent import WriterAgent
from agents.reviewer_agent import ReviewerAgent


class ConcreteAgent(BaseAgent):
    """用于测试的具体 Agent 实现"""

    def _register_skills(self) -> list:
        return []

    def _system_prompt(self) -> str:
        return "测试 Agent"


@pytest.fixture
def settings():
    return Settings(llm_api_key="test-key", search_api_key="test-search-key")


class TestBaseAgent:
    def test_init(self, settings):
        with patch("agents.base_agent.ChatOpenAI"):
            agent = ConcreteAgent(settings, name="TestAgent")
            assert agent.name == "TestAgent"
            assert agent.max_steps == settings.max_react_steps

    def test_build_input_without_context(self, settings):
        with patch("agents.base_agent.ChatOpenAI"):
            agent = ConcreteAgent(settings, name="TestAgent")
            result = agent._build_input("任务内容", None)
            assert "任务内容" in result

    def test_build_input_with_context(self, settings):
        with patch("agents.base_agent.ChatOpenAI"):
            agent = ConcreteAgent(settings, name="TestAgent")
            result = agent._build_input("任务内容", {"key": "value"})
            assert "任务内容" in result
            assert "key" in result

    def test_find_skill_not_found(self, settings):
        with patch("agents.base_agent.ChatOpenAI"):
            agent = ConcreteAgent(settings, name="TestAgent")
            with pytest.raises(ValueError, match="not found"):
                agent._find_skill("nonexistent_skill")

    @pytest.mark.asyncio
    async def test_run_without_tools(self, settings):
        with patch("agents.base_agent.ChatOpenAI") as mock_llm_class:
            mock_llm = MagicMock()
            mock_response = MagicMock()
            mock_response.tool_calls = []
            mock_response.content = "完成任务"
            mock_llm.ainvoke = AsyncMock(return_value=mock_response)
            mock_llm_class.return_value = mock_llm

            agent = ConcreteAgent(settings, name="TestAgent")
            result = await agent.run("测试任务")
            assert result == "完成任务"


class TestPlannerAgent:
    def test_init(self, settings):
        with patch("agents.base_agent.ChatOpenAI"):
            with patch("skills.analyze_skill.AnalyzeSkill"):
                agent = PlannerAgent(settings)
                assert agent.name == "Planner"

    def test_system_prompt(self, settings):
        with patch("agents.base_agent.ChatOpenAI"):
            agent = PlannerAgent(settings)
            prompt = agent._system_prompt()
            assert "调研规划师" in prompt
            assert "JSON" in prompt

    def test_register_skills(self, settings):
        with patch("agents.base_agent.ChatOpenAI"):
            agent = PlannerAgent(settings)
            skills = agent._register_skills()
            assert len(skills) == 1
            assert skills[0].name == "analyze_topic"


class TestResearchAgent:
    def test_init(self, settings):
        with patch("agents.base_agent.ChatOpenAI"):
            with patch("skills.summarize_skill.ChatOpenAI"):
                agent = ResearchAgent(settings)
                assert agent.name == "Researcher"

    def test_register_skills(self, settings):
        with patch("agents.base_agent.ChatOpenAI"):
            with patch("skills.summarize_skill.ChatOpenAI"):
                agent = ResearchAgent(settings)
                skill_names = [s.name for s in agent._register_skills()]
                assert "web_search" in skill_names
                assert "scrape_webpage" in skill_names
                assert "summarize_text" in skill_names


class TestWriterAgent:
    def test_init(self, settings):
        with patch("agents.base_agent.ChatOpenAI"):
            agent = WriterAgent(settings)
            assert agent.name == "Writer"

    def test_no_skills(self, settings):
        with patch("agents.base_agent.ChatOpenAI"):
            agent = WriterAgent(settings)
            assert agent._register_skills() == []

    def test_system_prompt(self, settings):
        with patch("agents.base_agent.ChatOpenAI"):
            agent = WriterAgent(settings)
            prompt = agent._system_prompt()
            assert "研究报告" in prompt


class TestReviewerAgent:
    def test_init(self, settings):
        with patch("agents.base_agent.ChatOpenAI"):
            agent = ReviewerAgent(settings)
            assert agent.name == "Reviewer"

    def test_no_skills(self, settings):
        with patch("agents.base_agent.ChatOpenAI"):
            agent = ReviewerAgent(settings)
            assert agent._register_skills() == []

    def test_system_prompt(self, settings):
        with patch("agents.base_agent.ChatOpenAI"):
            agent = ReviewerAgent(settings)
            prompt = agent._system_prompt()
            assert "审核员" in prompt
            assert "JSON" in prompt
