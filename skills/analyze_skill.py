"""分析技能"""
from langchain_core.tools import tool


class AnalyzeSkill:
    name = "analyze_topic"
    description = "分析话题的关键维度和子问题"

    def as_tool(self):
        @tool
        async def analyze_topic(topic: str) -> str:
            """分析调研话题，识别关键维度。topic: 调研话题"""
            return await self.execute(topic=topic)
        return analyze_topic

    async def execute(self, topic: str) -> str:
        return f"话题「{topic}」的建议调研维度：定义与背景、技术现状、应用场景、市场数据、挑战与风险、未来趋势"
