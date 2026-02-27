"""智能调研 Agent - 主入口"""
import asyncio
import argparse
from dotenv import load_dotenv

from config.settings import Settings
from graph.workflow import ResearchWorkflow


async def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="智能调研 Agent")
    parser.add_argument("--topic", type=str, required=True, help="调研话题")
    parser.add_argument("--depth", type=str, default="standard",
                        choices=["quick", "standard", "deep"], help="调研深度")
    parser.add_argument("--output", type=str, default="output/report.md", help="输出路径")
    args = parser.parse_args()

    settings = Settings()
    workflow = ResearchWorkflow(settings)

    report = await workflow.run(
        topic=args.topic,
        depth=args.depth,
        output_path=args.output,
    )

    print(f"\n✅ 报告已生成: {args.output}")
    print(f"📊 共搜索 {report.sources_count} 个来源")
    print(f"📝 报告长度: {report.word_count} 字")


if __name__ == "__main__":
    asyncio.run(main())
