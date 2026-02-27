"""摘要技能"""
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from config.settings import Settings


class SummarizeSkill:
    name = "summarize_text"
    description = "将长文本压缩为关键要点摘要"

    def __init__(self, settings: Settings):
        self.llm = ChatOpenAI(
            model=settings.llm_model,
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url or None,
            temperature=0.1,
        )

    def as_tool(self):
        @tool
        async def summarize_text(text: str, focus: str = "") -> str:
            """摘要长文本。text: 原文, focus: 摘要关注点"""
            return await self.execute(text=text, focus=focus)
        return summarize_text

    async def execute(self, text: str, focus: str = "") -> str:
        prompt = f"请提取以下文本的关键信息，生成结构化摘要。\n关注点：{focus}\n\n原文：\n{text[:8000]}"
        response = await self.llm.ainvoke([
            SystemMessage(content="你是一个专业的信息提取助手，善于从文本中提取关键事实、数据和观点。"),
            HumanMessage(content=prompt),
        ])
        return response.content
