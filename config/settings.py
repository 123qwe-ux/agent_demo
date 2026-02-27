"""全局配置"""
import os
from dataclasses import dataclass, field


@dataclass
class Settings:
    # LLM 配置
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o"
    llm_api_key: str = field(default_factory=lambda: os.getenv("LLM_API_KEY", ""))
    llm_base_url: str = field(default_factory=lambda: os.getenv("LLM_BASE_URL", ""))
    llm_temperature: float = 0.3

    # 搜索配置
    search_api: str = "tavily"
    search_api_key: str = field(default_factory=lambda: os.getenv("SEARCH_API_KEY", ""))
    max_search_results: int = 10

    # MCP 配置
    mcp_servers: dict = field(default_factory=lambda: {
        "web_search": {"command": "uvx", "args": ["tavily-mcp-server"]},
        "browser": {"command": "uvx", "args": ["browser-mcp-server"]},
        "filesystem": {"command": "uvx", "args": ["filesystem-mcp-server", "./output"]},
    })

    # Agent 配置
    max_react_steps: int = 10
    max_review_rounds: int = 2

    # 输出配置
    output_dir: str = "output"
