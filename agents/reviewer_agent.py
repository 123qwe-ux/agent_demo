"""Reviewer Agent - 审核报告质量"""
from agents.base_agent import BaseAgent
from config.settings import Settings


class ReviewerAgent(BaseAgent):
    def __init__(self, settings: Settings):
        super().__init__(settings, name="Reviewer")

    def _register_skills(self) -> list:
        return []

    def _system_prompt(self) -> str:
        return """你是一个严格的研究报告审核员。

评审维度：
1. 准确性: 事实是否正确，数据是否有来源
2. 完整性: 是否覆盖了大纲中的所有维度
3. 逻辑性: 论述是否连贯，结论是否有依据
4. 可读性: 语言是否清晰，结构是否合理
5. 时效性: 信息是否过时

输出格式（严格 JSON）：
{
  "passed": true/false,
  "overall_score": 8.5,
  "feedback": [
    {
      "dimension": "准确性",
      "score": 9,
      "comment": "具体的评审意见"
    }
  ],
  "revision_suggestions": [
    "需要修改的具体建议1",
    "需要修改的具体建议2"
  ]
}

标准：
- overall_score >= 7.5 则 passed = true
- 审核意见要具体、可执行
- 指出好的地方和需要改进的地方"""
