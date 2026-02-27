"""工作流模块单元测试"""
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, mock_open

from config.settings import Settings
from graph.state import GraphState, WorkflowPhase, SubTask, Source
from graph.workflow import ResearchWorkflow, _ReportResult
from memory.research_memory import ResearchMemory, MemoryEntry


@pytest.fixture
def settings():
    return Settings(llm_api_key="test-key", search_api_key="test-search-key")


class TestGraphState:
    def test_workflow_phase_values(self):
        assert WorkflowPhase.PLANNING == "planning"
        assert WorkflowPhase.RESEARCHING == "researching"
        assert WorkflowPhase.WRITING == "writing"
        assert WorkflowPhase.REVIEWING == "reviewing"
        assert WorkflowPhase.REVISING == "revising"
        assert WorkflowPhase.COMPLETED == "completed"

    def test_subtask_dataclass(self):
        task = SubTask(id="task_1", query="测试查询", aspect="测试维度")
        assert task.id == "task_1"
        assert task.status == "pending"
        assert task.results == []

    def test_source_dataclass(self):
        source = Source(url="https://example.com", title="标题", snippet="摘要")
        assert source.url == "https://example.com"
        assert source.content == ""
        assert source.relevance_score == 0.0


class TestResearchMemory:
    def test_add_and_get_all(self):
        memory = ResearchMemory()
        memory.add("发现1", source="https://example.com")
        memory.add("发现2", entry_type="summary")
        entries = memory.get_all()
        assert len(entries) == 2

    def test_get_all_by_type(self):
        memory = ResearchMemory()
        memory.add("发现1", entry_type="finding")
        memory.add("总结1", entry_type="summary")
        findings = memory.get_all("finding")
        assert len(findings) == 1
        assert findings[0].content == "发现1"

    def test_search(self):
        memory = ResearchMemory()
        memory.add("关于人工智能的发现")
        memory.add("关于机器学习的内容")
        results = memory.search("人工智能")
        assert len(results) == 1
        assert "人工智能" in results[0].content

    def test_summarize_empty(self):
        memory = ResearchMemory()
        result = memory.summarize()
        assert "暂无" in result

    def test_summarize_with_entries(self):
        memory = ResearchMemory()
        memory.add("短内容")
        result = memory.summarize()
        assert "1 条发现" in result
        assert "短内容" in result

    def test_clear(self):
        memory = ResearchMemory()
        memory.add("发现1")
        memory.clear()
        assert len(memory.get_all()) == 0

    def test_memory_entry_defaults(self):
        entry = MemoryEntry(content="测试内容")
        assert entry.source == ""
        assert entry.entry_type == "finding"
        assert entry.timestamp is not None


class TestReportResult:
    def test_sources_count(self):
        result = _ReportResult("报告内容", {"sources": [{"url": "u1"}, {"url": "u2"}]})
        assert result.sources_count == 2

    def test_sources_count_empty(self):
        result = _ReportResult("报告内容", {})
        assert result.sources_count == 0

    def test_word_count(self):
        result = _ReportResult("报告内容", {})
        assert result.word_count == 4


class TestResearchWorkflow:
    @pytest.fixture
    def workflow(self, settings):
        with patch("agents.base_agent.ChatOpenAI"):
            with patch("skills.summarize_skill.ChatOpenAI"):
                with patch("graph.workflow.StateGraph") as mock_sg:
                    mock_compiled = MagicMock()
                    mock_sg.return_value.compile.return_value = mock_compiled
                    return ResearchWorkflow(settings)

    def test_should_continue_passed(self, workflow):
        state = {"review_passed": True, "review_round": 1}
        assert workflow._should_continue(state) == "end"

    def test_should_continue_max_rounds(self, settings):
        with patch("agents.base_agent.ChatOpenAI"):
            with patch("skills.summarize_skill.ChatOpenAI"):
                with patch("graph.workflow.StateGraph") as mock_sg:
                    mock_sg.return_value.compile.return_value = MagicMock()
                    wf = ResearchWorkflow(settings)
                    state = {
                        "review_passed": False,
                        "review_round": settings.max_review_rounds,
                    }
                    assert wf._should_continue(state) == "end"

    def test_should_continue_revise(self, settings):
        with patch("agents.base_agent.ChatOpenAI"):
            with patch("skills.summarize_skill.ChatOpenAI"):
                with patch("graph.workflow.StateGraph") as mock_sg:
                    mock_sg.return_value.compile.return_value = MagicMock()
                    wf = ResearchWorkflow(settings)
                    state = {
                        "review_passed": False,
                        "review_round": 0,
                    }
                    assert wf._should_continue(state) == "revise"

    @pytest.mark.asyncio
    async def test_plan_node(self, settings):
        with patch("agents.base_agent.ChatOpenAI"):
            with patch("skills.summarize_skill.ChatOpenAI"):
                with patch("graph.workflow.StateGraph") as mock_sg:
                    mock_sg.return_value.compile.return_value = MagicMock()
                    wf = ResearchWorkflow(settings)
                    plan_result = json.dumps({
                        "outline": "# 调研大纲",
                        "sub_tasks": [{"id": "task_1", "aspect": "维度1", "query": "查询1"}]
                    })
                    wf.planner.run = AsyncMock(return_value=plan_result)
                    state = {"topic": "人工智能", "depth": "standard"}
                    result = await wf._plan_node(state)
                    assert "sub_tasks" in result
                    assert result["research_outline"] == "# 调研大纲"

    @pytest.mark.asyncio
    async def test_run(self, settings):
        with patch("agents.base_agent.ChatOpenAI"):
            with patch("skills.summarize_skill.ChatOpenAI"):
                with patch("graph.workflow.StateGraph") as mock_sg:
                    mock_compiled = AsyncMock()
                    mock_compiled.ainvoke = AsyncMock(return_value={
                        "draft_report": "# 测试报告",
                        "sources": [],
                        "final_report": "",
                    })
                    mock_sg.return_value.compile.return_value = mock_compiled
                    wf = ResearchWorkflow(settings)

                    with patch("builtins.open", mock_open()):
                        result = await wf.run(topic="测试话题", output_path="/tmp/test_report.md")
                    assert result.report == "# 测试报告"
                    assert result.word_count == 6
