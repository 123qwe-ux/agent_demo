"""Planner Agent - 将调研话题拆解为子任务"""
from agents.base_agent import BaseAgent
from skills.analyze_skill import AnalyzeSkill
from config.settings import Settings


class PlannerAgent(BaseAgent):
    def __init__(self, settings: Settings):
        super().__init__(settings, name="Planner")

    def _register_skills(self) -> list:
        return [AnalyzeSkill()]

    def _system_prompt(self) -> str:
        return """你是一个专业的调研规划师。

你的职责：
1. 分析用户给定的调研话题
2. 将话题拆解为 3-6 个子任务（调研维度）
3. 为每个子任务生成精准的搜索查询词
4. 输出调研大纲

输出格式（严格 JSON）：
{
  "outline": "调研大纲（Markdown格式）",
  "sub_tasks": [
    {
      "id": "task_1",
      "aspect": "调研维度名称",
      "query": "搜索查询词",
      "description": "这个维度要研究什么"
    }
  ]
}

原则：
- 维度之间不要重叠
- 搜索查询词要具体、可执行
- 覆盖：定义/现状/技术/应用/挑战/趋势 等方面"""
