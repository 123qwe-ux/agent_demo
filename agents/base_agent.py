"""Agent 基类 - 实现 ReAct 推理循环"""
from __future__ import annotations
import json
from abc import ABC, abstractmethod
from typing import Any

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage

from config.settings import Settings


class BaseAgent(ABC):
    """
    所有 Agent 的基类
    实现 ReAct (Reasoning + Acting) 循环：
    Thought → Action → Observation → Thought → ... → Final Answer
    """

    def __init__(self, settings: Settings, name: str):
        self.name = name
        self.settings = settings
        self.llm = self._init_llm(settings)
        self.skills = self._register_skills()
        self.max_steps = settings.max_react_steps

    def _init_llm(self, settings: Settings) -> ChatOpenAI:
        return ChatOpenAI(
            model=settings.llm_model,
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url or None,
            temperature=settings.llm_temperature,
        )

    @abstractmethod
    def _register_skills(self) -> list:
        """子类注册自己需要的 Skills（作为 LLM tools）"""
        ...

    @abstractmethod
    def _system_prompt(self) -> str:
        """子类定义自己的系统提示词"""
        ...

    async def run(self, task: str, context: dict[str, Any] = None) -> str:
        """
        ReAct 主循环
        """
        messages = [
            SystemMessage(content=self._system_prompt()),
            HumanMessage(content=self._build_input(task, context)),
        ]

        tools = [skill.as_tool() for skill in self.skills]
        llm_with_tools = self.llm.bind_tools(tools) if tools else self.llm

        for step in range(self.max_steps):
            print(f"  [{self.name}] Step {step + 1}/{self.max_steps}")

            response = await llm_with_tools.ainvoke(messages)
            messages.append(response)

            if not response.tool_calls:
                print(f"  [{self.name}] ✅ 完成")
                return response.content

            for tool_call in response.tool_calls:
                skill = self._find_skill(tool_call["name"])
                print(f"  [{self.name}] 🔧 调用: {tool_call['name']}")

                result = await skill.execute(**tool_call["args"])

                messages.append(ToolMessage(
                    content=str(result),
                    tool_call_id=tool_call["id"],
                ))

        return messages[-1].content if messages else "达到最大步数，未能完成任务"

    def _find_skill(self, name: str):
        for skill in self.skills:
            if skill.name == name:
                return skill
        raise ValueError(f"Skill '{name}' not found in {self.name}")

    def _build_input(self, task: str, context: dict | None) -> str:
        parts = [f"## 任务\n{task}"]
        if context:
            parts.append(f"## 上下文\n```json\n{json.dumps(context, ensure_ascii=False, indent=2)}\n```")
        return "\n\n".join(parts)
