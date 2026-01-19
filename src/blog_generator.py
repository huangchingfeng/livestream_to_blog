"""部落格文章生成模組"""

import json
from typing import Any

import anthropic

from .utils import load_prompt


class BlogGenerator:
    """部落格文章生成器"""

    def __init__(self, api_key: str | None = None):
        """
        初始化生成器

        Args:
            api_key: Anthropic API key
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.prompt_template = load_prompt("generate_blog")

    def generate(self, analysis: dict[str, Any]) -> str:
        """
        根據分析結果生成部落格文章

        Args:
            analysis: 內容分析結果

        Returns:
            Markdown 格式的部落格文章
        """
        # 將分析結果轉為格式化的字串
        analysis_text = json.dumps(analysis, ensure_ascii=False, indent=2)
        prompt = self.prompt_template.replace("{analysis}", analysis_text)

        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return message.content[0].text

    def generate_with_style(
        self,
        analysis: dict[str, Any],
        style: str = "professional",
        tone: str = "friendly",
        length: str = "medium"
    ) -> str:
        """
        使用指定風格生成文章

        Args:
            analysis: 內容分析結果
            style: 文章風格 (professional/casual/academic)
            tone: 語調 (friendly/formal/enthusiastic)
            length: 長度 (short/medium/long)

        Returns:
            Markdown 格式的部落格文章
        """
        length_map = {
            "short": "500-800字",
            "medium": "800-1200字",
            "long": "1200-1800字"
        }

        style_prompt = f"""
## 寫作風格調整

- 文章風格：{style}
- 語調：{tone}
- 目標長度：{length_map.get(length, "800-1200字")}
"""

        analysis_text = json.dumps(analysis, ensure_ascii=False, indent=2)
        prompt = self.prompt_template.replace("{analysis}", analysis_text)
        prompt += style_prompt

        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return message.content[0].text

    def extract_image_placeholders(self, article: str) -> list[dict[str, str]]:
        """
        從文章中提取圖片位置標記

        Args:
            article: 部落格文章

        Returns:
            圖片需求列表
        """
        placeholders = []
        lines = article.split("\n")

        for i, line in enumerate(lines):
            if "[圖片位置：" in line:
                # 提取圖片描述
                start = line.find("：") + 1
                end = line.find("]", start)
                if end > start:
                    description = line[start:end].strip()
                    placeholders.append({
                        "line_number": i + 1,
                        "description": description,
                        "original_marker": line.strip()
                    })

        return placeholders
