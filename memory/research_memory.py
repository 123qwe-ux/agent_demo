"""调研过程记忆 - 存储中间结果"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class MemoryEntry:
    content: str
    source: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    entry_type: str = "finding"  # finding / summary / feedback


class ResearchMemory:
    """管理调研过程中的中间结果和记忆"""

    def __init__(self):
        self._entries: list[MemoryEntry] = []

    def add(self, content: str, source: str = "", entry_type: str = "finding"):
        entry = MemoryEntry(content=content, source=source, entry_type=entry_type)
        self._entries.append(entry)

    def get_all(self, entry_type: str = None) -> list[MemoryEntry]:
        if entry_type:
            return [e for e in self._entries if e.entry_type == entry_type]
        return self._entries.copy()

    def search(self, keyword: str) -> list[MemoryEntry]:
        return [e for e in self._entries if keyword.lower() in e.content.lower()]

    def summarize(self) -> str:
        findings = self.get_all("finding")
        if not findings:
            return "暂无调研发现"
        parts = [f"- {e.content[:200]}..." if len(e.content) > 200 else f"- {e.content}" for e in findings]
        return f"共 {len(findings)} 条发现:\n" + "\n".join(parts)

    def clear(self):
        self._entries.clear()
