"""全局状态定义 - LangGraph StateGraph 的核心"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages


class WorkflowPhase(str, Enum):
    PLANNING = "planning"
    RESEARCHING = "researching"
    WRITING = "writing"
    REVIEWING = "reviewing"
    REVISING = "revising"
    COMPLETED = "completed"


@dataclass
class SubTask:
    id: str
    query: str
    aspect: str
    status: str = "pending"
    results: list[str] = field(default_factory=list)


@dataclass
class Source:
    url: str
    title: str
    snippet: str
    content: str = ""
    relevance_score: float = 0.0


class GraphState(TypedDict):
    topic: str
    depth: str
    sub_tasks: list[dict]
    research_outline: str
    sources: list[dict]
    raw_findings: list[str]
    draft_report: str
    review_feedback: str
    review_passed: bool
    review_round: int
    final_report: str
    phase: str
    messages: Annotated[list, add_messages]
