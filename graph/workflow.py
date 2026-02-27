"""LangGraph 工作流 - 编排多 Agent 协作"""
from __future__ import annotations
import json
from typing import Literal

from langgraph.graph import StateGraph, END

from config.settings import Settings
from graph.state import GraphState, WorkflowPhase
from agents.planner_agent import PlannerAgent
from agents.research_agent import ResearchAgent
from agents.writer_agent import WriterAgent
from agents.reviewer_agent import ReviewerAgent


class ResearchWorkflow:
    """
    工作流编排：
    [START] → plan → research → write → review → {通过→END, 不通过→write}
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self.planner = PlannerAgent(settings)
        self.researcher = ResearchAgent(settings)
        self.writer = WriterAgent(settings)
        self.reviewer = ReviewerAgent(settings)
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(GraphState)
        workflow.add_node("plan", self._plan_node)
        workflow.add_node("research", self._research_node)
        workflow.add_node("write", self._write_node)
        workflow.add_node("review", self._review_node)
        workflow.set_entry_point("plan")
        workflow.add_edge("plan", "research")
        workflow.add_edge("research", "write")
        workflow.add_edge("write", "review")
        workflow.add_conditional_edges(
            "review",
            self._should_continue,
            {"end": END, "revise": "write"},
        )
        return workflow.compile()

    async def _plan_node(self, state: GraphState) -> dict:
        print("\n📋 阶段 1/4: 规划调研任务...")
        result = await self.planner.run(
            task=f"请为以下话题制定调研计划: {state['topic']}",
            context={"depth": state["depth"]},
        )
        parsed = json.loads(result)
        return {
            "sub_tasks": parsed["sub_tasks"],
            "research_outline": parsed["outline"],
            "phase": WorkflowPhase.RESEARCHING,
        }

    async def _research_node(self, state: GraphState) -> dict:
        print("\n🔍 阶段 2/4: 执行调研...")
        all_findings = []
        all_sources = []
        for i, task in enumerate(state["sub_tasks"]):
            print(f"\n  📌 子任务 {i+1}/{len(state['sub_tasks'])}: {task['aspect']}")
            result = await self.researcher.run(
                task=f"调研以下内容: {task['query']}",
                context={
                    "aspect": task["aspect"],
                    "topic": state["topic"],
                    "description": task.get("description", ""),
                },
            )
            all_findings.append(f"## {task['aspect']}\n{result}")
        return {
            "raw_findings": all_findings,
            "sources": all_sources,
            "phase": WorkflowPhase.WRITING,
        }

    async def _write_node(self, state: GraphState) -> dict:
        print("\n✍️ 阶段 3/4: 撰写报告...")
        context = {
            "topic": state["topic"],
            "outline": state["research_outline"],
            "findings": state["raw_findings"],
        }
        if state.get("review_feedback"):
            context["revision_feedback"] = state["review_feedback"]
            context["previous_draft"] = state["draft_report"]
        draft = await self.writer.run(task="根据调研发现撰写研究报告", context=context)
        return {"draft_report": draft, "phase": WorkflowPhase.REVIEWING}

    async def _review_node(self, state: GraphState) -> dict:
        current_round = state.get("review_round", 0) + 1
        print(f"\n🔎 阶段 4/4: 审核报告 (第 {current_round} 轮)...")
        result = await self.reviewer.run(
            task="审核以下研究报告的质量",
            context={
                "report": state["draft_report"],
                "topic": state["topic"],
                "outline": state["research_outline"],
            },
        )
        parsed = json.loads(result)
        return {
            "review_feedback": json.dumps(parsed["revision_suggestions"], ensure_ascii=False),
            "review_passed": parsed["passed"],
            "review_round": current_round,
            "phase": WorkflowPhase.COMPLETED if parsed["passed"] else WorkflowPhase.REVISING,
        }

    def _should_continue(self, state: GraphState) -> Literal["end", "revise"]:
        if state["review_passed"]:
            return "end"
        if state["review_round"] >= self.settings.max_review_rounds:
            print("  ⚠️ 达到最大审核轮数，使用当前版本")
            return "end"
        return "revise"

    async def run(self, topic: str, depth: str = "standard", output_path: str = "output/report.md"):
        initial_state: GraphState = {
            "topic": topic,
            "depth": depth,
            "sub_tasks": [],
            "research_outline": "",
            "sources": [],
            "raw_findings": [],
            "draft_report": "",
            "review_feedback": "",
            "review_passed": False,
            "review_round": 0,
            "final_report": "",
            "phase": WorkflowPhase.PLANNING,
            "messages": [],
        }
        final_state = await self.graph.ainvoke(initial_state)
        report = final_state["draft_report"]
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)
        final_state["final_report"] = report
        return _ReportResult(report, final_state)


class _ReportResult:
    def __init__(self, report: str, state: dict):
        self.report = report
        self.state = state

    @property
    def sources_count(self) -> int:
        return len(self.state.get("sources", []))

    @property
    def word_count(self) -> int:
        return len(self.report)
