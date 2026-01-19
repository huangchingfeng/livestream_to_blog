"""主要 Agent 邏輯 - 整合所有模組的核心控制器"""

import json
import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from .blog_generator import BlogGenerator
from .content_analyzer import ContentAnalyzer
from .designer_prompt import DesignerPromptGenerator
from .image_generator import ImageGenerator
from .utils import read_input_file, save_output, ensure_output_dir


class ImageMode(Enum):
    """圖片處理模式"""
    GEMINI = "gemini"      # 使用 Gemini API 自動生成圖片
    DESIGNER = "designer"  # 生成設計師指令
    NONE = "none"          # 不處理圖片


@dataclass
class AgentResult:
    """Agent 執行結果"""
    success: bool
    article_path: str | None = None
    article_content: str | None = None
    analysis: dict[str, Any] | None = None
    images: list[dict[str, Any]] | None = None
    designer_brief: str | None = None
    designer_brief_path: str | None = None
    error: str | None = None


class LivestreamToBlogAgent:
    """直播內容轉部落格文章 AI Agent"""

    def __init__(
        self,
        anthropic_api_key: str | None = None,
        gemini_api_key: str | None = None
    ):
        """
        初始化 Agent

        Args:
            anthropic_api_key: Anthropic API key
            gemini_api_key: Gemini API key (用於圖片生成)
        """
        # 載入環境變數
        load_dotenv()

        self.anthropic_api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")

        # 初始化各模組
        self.content_analyzer = ContentAnalyzer(api_key=self.anthropic_api_key)
        self.blog_generator = BlogGenerator(api_key=self.anthropic_api_key)
        self.designer_prompt_generator = DesignerPromptGenerator(
            api_key=self.anthropic_api_key
        )

        # 只有在有 Gemini API key 時才初始化圖片生成器
        self.image_generator = None
        if self.gemini_api_key:
            self.image_generator = ImageGenerator(api_key=self.gemini_api_key)

    def run(
        self,
        input_path: str | Path,
        output_dir: str | Path = "./output",
        image_mode: ImageMode = ImageMode.DESIGNER,
        style: str = "professional",
        tone: str = "friendly",
        length: str = "medium"
    ) -> AgentResult:
        """
        執行完整的轉換流程

        Args:
            input_path: 輸入檔案路徑（逐字稿）
            output_dir: 輸出目錄
            image_mode: 圖片處理模式
            style: 文章風格
            tone: 文章語調
            length: 文章長度

        Returns:
            執行結果
        """
        try:
            output_path = ensure_output_dir(output_dir)

            # Step 1: 讀取輸入內容
            print("📖 讀取直播內容...")
            content = read_input_file(input_path)

            # Step 2: 分析內容
            print("🔍 分析內容中...")
            analysis = self.content_analyzer.analyze(content)

            # 儲存分析結果
            analysis_path = save_output(
                json.dumps(analysis, ensure_ascii=False, indent=2),
                output_path,
                "analysis.json"
            )
            print(f"  ✅ 分析結果已儲存：{analysis_path}")

            # Step 3: 生成部落格文章
            print("✍️ 生成部落格文章...")
            article = self.blog_generator.generate_with_style(
                analysis=analysis,
                style=style,
                tone=tone,
                length=length
            )

            # 儲存文章
            article_path = save_output(article, output_path, "blog_post.md")
            print(f"  ✅ 文章已儲存：{article_path}")

            # Step 4: 處理圖片
            images = None
            designer_brief = None
            designer_brief_path = None

            if image_mode == ImageMode.GEMINI:
                print("🎨 使用 Gemini API 生成配圖...")
                if self.image_generator:
                    # 從文章中提取圖片需求
                    image_requirements = self.blog_generator.extract_image_placeholders(
                        article
                    )
                    if image_requirements:
                        images = self.image_generator.generate_images(
                            article_content=article,
                            image_requirements=image_requirements,
                            output_dir=output_path / "images"
                        )
                        print(f"  ✅ 已生成 {len(images)} 張圖片")
                    else:
                        print("  ⚠️ 未在文章中找到圖片位置標記")
                else:
                    print("  ⚠️ Gemini API key 未設定，跳過圖片生成")

            elif image_mode == ImageMode.DESIGNER:
                print("📝 生成設計師指令...")
                designer_brief = self.designer_prompt_generator.generate_brief_markdown(
                    article_content=article,
                    analysis=analysis
                )

                # 儲存設計師指令
                designer_brief_path = save_output(
                    designer_brief,
                    output_path,
                    "designer_brief.md"
                )
                print(f"  ✅ 設計師指令已儲存：{designer_brief_path}")

                # 同時生成可用於 AI 的 prompts
                ai_prompts = self.designer_prompt_generator.generate_image_prompts_for_ai(
                    article_content=article,
                    analysis=analysis
                )
                save_output(
                    json.dumps(ai_prompts, ensure_ascii=False, indent=2),
                    output_path,
                    "ai_image_prompts.json"
                )

            print("\n🎉 完成！")
            print(f"📁 所有檔案已儲存至：{output_path}")

            return AgentResult(
                success=True,
                article_path=str(article_path),
                article_content=article,
                analysis=analysis,
                images=images,
                designer_brief=designer_brief,
                designer_brief_path=str(designer_brief_path) if designer_brief_path else None
            )

        except FileNotFoundError as e:
            return AgentResult(
                success=False,
                error=f"找不到輸入檔案：{e}"
            )
        except Exception as e:
            return AgentResult(
                success=False,
                error=f"執行時發生錯誤：{str(e)}"
            )

    def run_from_text(
        self,
        content: str,
        output_dir: str | Path = "./output",
        image_mode: ImageMode = ImageMode.DESIGNER,
        style: str = "professional",
        tone: str = "friendly",
        length: str = "medium"
    ) -> AgentResult:
        """
        從文字內容直接執行轉換

        Args:
            content: 直播內容文字
            output_dir: 輸出目錄
            image_mode: 圖片處理模式
            style: 文章風格
            tone: 文章語調
            length: 文章長度

        Returns:
            執行結果
        """
        try:
            output_path = ensure_output_dir(output_dir)

            # Step 1: 分析內容
            print("🔍 分析內容中...")
            analysis = self.content_analyzer.analyze(content)

            # 儲存分析結果
            save_output(
                json.dumps(analysis, ensure_ascii=False, indent=2),
                output_path,
                "analysis.json"
            )

            # Step 2: 生成部落格文章
            print("✍️ 生成部落格文章...")
            article = self.blog_generator.generate_with_style(
                analysis=analysis,
                style=style,
                tone=tone,
                length=length
            )

            # 儲存文章
            article_path = save_output(article, output_path, "blog_post.md")

            # Step 3: 處理圖片
            designer_brief = None
            designer_brief_path = None
            images = None

            if image_mode == ImageMode.GEMINI and self.image_generator:
                image_requirements = self.blog_generator.extract_image_placeholders(
                    article
                )
                if image_requirements:
                    images = self.image_generator.generate_images(
                        article_content=article,
                        image_requirements=image_requirements,
                        output_dir=output_path / "images"
                    )

            elif image_mode == ImageMode.DESIGNER:
                designer_brief = self.designer_prompt_generator.generate_brief_markdown(
                    article_content=article,
                    analysis=analysis
                )
                designer_brief_path = save_output(
                    designer_brief,
                    output_path,
                    "designer_brief.md"
                )

            return AgentResult(
                success=True,
                article_path=str(article_path),
                article_content=article,
                analysis=analysis,
                images=images,
                designer_brief=designer_brief,
                designer_brief_path=str(designer_brief_path) if designer_brief_path else None
            )

        except Exception as e:
            return AgentResult(
                success=False,
                error=str(e)
            )

    def analyze_only(self, content: str) -> dict[str, Any]:
        """
        僅執行內容分析

        Args:
            content: 直播內容

        Returns:
            分析結果
        """
        return self.content_analyzer.analyze(content)

    def generate_article_only(
        self,
        analysis: dict[str, Any],
        style: str = "professional",
        tone: str = "friendly",
        length: str = "medium"
    ) -> str:
        """
        僅執行文章生成

        Args:
            analysis: 內容分析結果
            style: 文章風格
            tone: 文章語調
            length: 文章長度

        Returns:
            Markdown 格式的文章
        """
        return self.blog_generator.generate_with_style(
            analysis=analysis,
            style=style,
            tone=tone,
            length=length
        )
