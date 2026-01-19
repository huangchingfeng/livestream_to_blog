#!/usr/bin/env python3
"""
直播內容轉部落格文章 AI Agent

使用方式：
    python main.py --input transcript.txt
    python main.py --input transcript.txt --output ./blog_posts/ --image-mode gemini
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.agent import LivestreamToBlogAgent, ImageMode

console = Console()


@click.command()
@click.option(
    "--input", "-i",
    "input_path",
    required=True,
    type=click.Path(exists=True),
    help="輸入檔案路徑（直播逐字稿或摘要）"
)
@click.option(
    "--output", "-o",
    "output_dir",
    default="./output",
    type=click.Path(),
    help="輸出目錄 (預設: ./output)"
)
@click.option(
    "--image-mode", "-m",
    type=click.Choice(["gemini", "designer", "none"]),
    default="designer",
    help="圖片處理模式：gemini=自動生成, designer=設計師指令, none=不處理"
)
@click.option(
    "--style", "-s",
    type=click.Choice(["professional", "casual", "academic"]),
    default="professional",
    help="文章風格 (預設: professional)"
)
@click.option(
    "--tone", "-t",
    type=click.Choice(["friendly", "formal", "enthusiastic"]),
    default="friendly",
    help="文章語調 (預設: friendly)"
)
@click.option(
    "--length", "-l",
    type=click.Choice(["short", "medium", "long"]),
    default="medium",
    help="文章長度 (預設: medium)"
)
def main(
    input_path: str,
    output_dir: str,
    image_mode: str,
    style: str,
    tone: str,
    length: str
):
    """直播內容轉部落格文章 AI Agent"""

    console.print(Panel.fit(
        "[bold blue]直播內容轉部落格文章 AI Agent[/bold blue]\n"
        "自動將直播內容轉換為精美的部落格文章",
        border_style="blue"
    ))

    console.print(f"\n[dim]輸入檔案：{input_path}[/dim]")
    console.print(f"[dim]輸出目錄：{output_dir}[/dim]")
    console.print(f"[dim]圖片模式：{image_mode}[/dim]")
    console.print(f"[dim]文章風格：{style} / {tone} / {length}[/dim]\n")

    # 轉換 image_mode 字串為 enum
    mode_map = {
        "gemini": ImageMode.GEMINI,
        "designer": ImageMode.DESIGNER,
        "none": ImageMode.NONE
    }
    image_mode_enum = mode_map[image_mode]

    # 初始化 Agent
    try:
        agent = LivestreamToBlogAgent()
    except Exception as e:
        console.print(f"[red]初始化失敗：{e}[/red]")
        console.print("[yellow]請確認已設定 ANTHROPIC_API_KEY 環境變數[/yellow]")
        raise click.Abort()

    # 執行轉換
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("處理中...", total=None)

        result = agent.run(
            input_path=input_path,
            output_dir=output_dir,
            image_mode=image_mode_enum,
            style=style,
            tone=tone,
            length=length
        )

        progress.update(task, completed=True)

    # 顯示結果
    if result.success:
        console.print("\n[green]✅ 轉換完成！[/green]\n")

        console.print("[bold]輸出檔案：[/bold]")
        console.print(f"  📄 文章：{result.article_path}")

        if result.designer_brief_path:
            console.print(f"  🎨 設計師指令：{result.designer_brief_path}")

        if result.images:
            console.print(f"  🖼️ 圖片：共 {len(result.images)} 張")
            for img in result.images:
                if img.get("success"):
                    console.print(f"     - {img.get('filename')}")
                else:
                    console.print(f"     - [red]失敗：{img.get('error')}[/red]")

        # 顯示文章預覽
        if result.article_content:
            preview = result.article_content[:500]
            if len(result.article_content) > 500:
                preview += "..."
            console.print("\n[bold]文章預覽：[/bold]")
            console.print(Panel(preview, border_style="green"))

    else:
        console.print(f"\n[red]❌ 轉換失敗：{result.error}[/red]")
        raise click.Abort()


@click.group()
def cli():
    """直播內容轉部落格文章 AI Agent CLI"""
    pass


@cli.command()
@click.option("--input", "-i", "input_path", required=True, type=click.Path(exists=True))
@click.option("--output", "-o", "output_path", default="./analysis.json")
def analyze(input_path: str, output_path: str):
    """僅執行內容分析"""
    import json
    from src.utils import read_input_file, save_output
    from pathlib import Path

    console.print("[blue]分析直播內容中...[/blue]")

    agent = LivestreamToBlogAgent()
    content = read_input_file(input_path)
    analysis = agent.analyze_only(content)

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)

    console.print(f"[green]分析結果已儲存：{output_path}[/green]")


if __name__ == "__main__":
    main()
