"""Research Agent - 执行搜索、抓取、整理信息"""
from agents.base_agent import BaseAgent
from skills.search_skill import SearchSkill
from skills.scrape_skill import ScrapeSkill
from skills.summarize_skill import SummarizeSkill
from config.settings import Settings


class ResearchAgent(BaseAgent):
    def __init__(self, settings: Settings):
        super().__init__(settings, name="Researcher")

    def _register_skills(self) -> list:
        return [
            SearchSkill(self.settings),
            ScrapeSkill(),
            SummarizeSkill(self.settings),
        ]

    def _system_prompt(self) -> str:
        return """你是一个专业的调研员，擅长从互联网搜索和整理信息。

工作流程（ReAct模式）：
1. Thought: 分析当前子任务，思考需要搜索什么
2. Action: 调用搜索工具获取信息
3. Observation: 分析搜索结果，判断是否需要深入
4. Thought: 如果信息不足，调整搜索策略继续搜索
5. Action: 如需要，抓取网页获取详细内容
6. Action: 使用摘要工具整理关键发现
7. 重复直到信息充足

最终输出：
- 关键发现（带来源引用）
- 数据和事实（尽量有数字支撑）
- 不同观点的对比

原则：
- 每个发现必须标注来源 URL
- 优先使用权威来源
- 区分事实和观点
- 注意信息的时效性"""
