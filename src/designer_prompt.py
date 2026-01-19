"""設計師指令生成模組 - 為設計師生成詳細的製圖指令"""

import json
from typing import Any

import anthropic

from .utils import load_prompt


class DesignerPromptGenerator:
    """設計師指令生成器"""

    def __init__(self, api_key: str | None = None):
        """
        初始化生成器

        Args:
            api_key: Anthropic API key
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.prompt_template = load_prompt("designer_brief")

    def generate_brief(
        self,
        article_content: str,
        analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """
        生成設計師指令

        Args:
            article_content: 部落格文章內容
            analysis: 內容分析結果

        Returns:
            設計師指令 (JSON 格式)
        """
        analysis_text = json.dumps(analysis, ensure_ascii=False, indent=2)

        prompt = self.prompt_template.replace(
            "{article_content}", article_content
        ).replace(
            "{analysis}", analysis_text
        )

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

        response_text = message.content[0].text

        # 嘗試解析 JSON
        try:
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass

        # 如果無法解析，返回原始內容
        return {"raw_brief": response_text}

    def generate_brief_markdown(
        self,
        article_content: str,
        analysis: dict[str, Any]
    ) -> str:
        """
        生成 Markdown 格式的設計師指令

        Args:
            article_content: 部落格文章內容
            analysis: 內容分析結果

        Returns:
            Markdown 格式的設計師指令
        """
        brief_data = self.generate_brief(article_content, analysis)

        if "raw_brief" in brief_data:
            return brief_data["raw_brief"]

        # 將 JSON 轉換為可讀的 Markdown 格式
        md_output = f"# 設計師指令：{brief_data.get('project_name', '部落格配圖')}\n\n"
        md_output += f"## 整體設計方向\n\n{brief_data.get('design_brief', '')}\n\n"

        for img in brief_data.get("images", []):
            md_output += f"---\n\n"
            md_output += f"## {img.get('name', '圖片')}\n\n"
            md_output += f"**ID**: {img.get('id', '')}\n\n"
            md_output += f"**用途**: {img.get('purpose', '')}\n\n"
            md_output += f"**尺寸**: {img.get('size', '')}\n\n"

            style = img.get("style", {})
            if style:
                md_output += f"### 設計風格\n\n"
                md_output += f"- 整體風格: {style.get('overall', '')}\n"
                md_output += f"- 配色: {', '.join(style.get('colors', []))}\n"
                md_output += f"- 視覺氛圍: {style.get('mood', '')}\n\n"

            elements = img.get("elements", {})
            if elements:
                md_output += f"### 必要元素\n\n"
                if elements.get("title"):
                    md_output += f"- 標題: {elements['title']}\n"
                if elements.get("subtitle"):
                    md_output += f"- 副標題: {elements['subtitle']}\n"
                if elements.get("visuals"):
                    md_output += f"- 視覺元素:\n"
                    for v in elements["visuals"]:
                        md_output += f"  - {v}\n"
                md_output += "\n"

            notes = img.get("notes", [])
            if notes:
                md_output += f"### 注意事項\n\n"
                for note in notes:
                    md_output += f"- {note}\n"
                md_output += "\n"

        return md_output

    def generate_image_prompts_for_ai(
        self,
        article_content: str,
        analysis: dict[str, Any]
    ) -> list[dict[str, str]]:
        """
        生成可直接用於 AI 圖片生成的 prompts

        Args:
            article_content: 部落格文章內容
            analysis: 內容分析結果

        Returns:
            圖片生成 prompts 列表
        """
        brief_data = self.generate_brief(article_content, analysis)

        prompts = []
        for img in brief_data.get("images", []):
            style = img.get("style", {})
            elements = img.get("elements", {})

            # 組合成 AI 圖片生成 prompt
            prompt = f"""Create a professional blog illustration.

Type: {img.get('name', 'Blog image')}
Purpose: {img.get('purpose', '')}
Aspect ratio: {'16:9' if 'cover' in img.get('id', '').lower() else '1:1'}

Style:
- Overall style: {style.get('overall', 'Modern, professional')}
- Color palette: {', '.join(style.get('colors', ['Blue', 'White']))}
- Mood: {style.get('mood', 'Professional, inspiring')}

Elements to include:
- Title area for: {elements.get('title', '')}
- Visual elements: {', '.join(elements.get('visuals', []))}

Design guidelines:
- Clean, modern aesthetic
- Good contrast for readability
- Professional look suitable for educational content
- Leave space for text overlay if needed
"""
            prompts.append({
                "id": img.get("id", ""),
                "name": img.get("name", ""),
                "prompt": prompt.strip(),
                "aspect_ratio": "16:9" if "cover" in img.get("id", "").lower() else "1:1"
            })

        return prompts
