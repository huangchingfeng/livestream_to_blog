"""圖片生成模組 - 使用 Gemini API 生成配圖"""

import base64
import io
from pathlib import Path
from typing import Any

import google.generativeai as genai

from .utils import load_prompt


class ImageGenerator:
    """使用 Gemini API 生成部落格配圖"""

    def __init__(self, api_key: str | None = None):
        """
        初始化圖片生成器

        Args:
            api_key: Gemini API key
        """
        if api_key:
            genai.configure(api_key=api_key)

        # 使用 Gemini 2.0 Flash 進行圖片生成
        self.model = genai.GenerativeModel("gemini-2.0-flash-exp")
        self.image_model = genai.ImageGenerationModel("imagen-3.0-generate-002")
        self.prompt_template = load_prompt("generate_image")

    def generate_image_prompt(
        self,
        article_content: str,
        image_type: str,
        image_description: str
    ) -> str:
        """
        為 Gemini 生成詳細的圖片生成 prompt

        Args:
            article_content: 文章內容
            image_type: 圖片類型 (cover/concept/summary)
            image_description: 圖片描述

        Returns:
            優化後的圖片生成 prompt
        """
        type_specs = {
            "cover": {
                "style": "現代專業的部落格封面圖",
                "size": "1200x630",
                "elements": "標題文字區域、主題相關視覺元素、吸引眼球的設計"
            },
            "concept": {
                "style": "簡潔清晰的概念說明圖",
                "size": "800x600",
                "elements": "流程圖、圖標、簡短說明文字"
            },
            "summary": {
                "style": "重點摘要卡片設計",
                "size": "800x800",
                "elements": "條列式重點、圖標、標題"
            }
        }

        spec = type_specs.get(image_type, type_specs["cover"])

        prompt = f"""Create a {spec['style']} for a blog post.

Image specifications:
- Aspect ratio suitable for {spec['size']}
- Style: Professional, modern, clean design
- Purpose: {image_description}

Design requirements:
- Elements needed: {spec['elements']}
- Color scheme: Professional blues and whites, or warm inviting tones
- Text: Minimal, leave space for overlay text
- Mood: Educational, inspiring, professional

Context from the article:
{article_content[:500]}...

Generate an image that:
1. Captures the essence of the topic
2. Is visually appealing and professional
3. Works well as a blog illustration
4. Has good contrast and readability
"""
        return prompt

    def generate_images(
        self,
        article_content: str,
        image_requirements: list[dict[str, str]],
        output_dir: str | Path
    ) -> list[dict[str, Any]]:
        """
        根據文章需求生成配圖

        Args:
            article_content: 文章內容
            image_requirements: 圖片需求列表
            output_dir: 輸出目錄

        Returns:
            生成結果列表
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        results = []

        for i, req in enumerate(image_requirements):
            description = req.get("description", "")
            image_type = self._detect_image_type(description)

            try:
                # 生成圖片 prompt
                prompt = self.generate_image_prompt(
                    article_content,
                    image_type,
                    description
                )

                # 使用 Imagen 3 生成圖片
                response = self.image_model.generate_images(
                    prompt=prompt,
                    number_of_images=1,
                    aspect_ratio="16:9" if image_type == "cover" else "1:1",
                    safety_filter_level="block_only_high",
                    person_generation="allow_adult"
                )

                # 儲存圖片
                if response.images:
                    image_data = response.images[0]
                    filename = f"image_{i+1}_{image_type}.png"
                    filepath = output_path / filename

                    # 將圖片資料寫入檔案
                    with open(filepath, "wb") as f:
                        f.write(image_data._pil_image.tobytes())

                    results.append({
                        "success": True,
                        "description": description,
                        "type": image_type,
                        "filename": filename,
                        "filepath": str(filepath)
                    })
                else:
                    results.append({
                        "success": False,
                        "description": description,
                        "error": "No image generated"
                    })

            except Exception as e:
                results.append({
                    "success": False,
                    "description": description,
                    "error": str(e)
                })

        return results

    def generate_single_image(
        self,
        prompt: str,
        output_path: str | Path,
        aspect_ratio: str = "16:9"
    ) -> dict[str, Any]:
        """
        生成單張圖片

        Args:
            prompt: 圖片生成 prompt
            output_path: 輸出路徑
            aspect_ratio: 圖片比例

        Returns:
            生成結果
        """
        try:
            response = self.image_model.generate_images(
                prompt=prompt,
                number_of_images=1,
                aspect_ratio=aspect_ratio,
                safety_filter_level="block_only_high"
            )

            if response.images:
                image = response.images[0]
                output_file = Path(output_path)
                output_file.parent.mkdir(parents=True, exist_ok=True)

                # 儲存圖片
                image._pil_image.save(str(output_file))

                return {
                    "success": True,
                    "filepath": str(output_file)
                }
            else:
                return {
                    "success": False,
                    "error": "No image generated"
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _detect_image_type(self, description: str) -> str:
        """
        根據描述判斷圖片類型

        Args:
            description: 圖片描述

        Returns:
            圖片類型
        """
        description_lower = description.lower()

        if any(word in description_lower for word in ["封面", "cover", "首圖"]):
            return "cover"
        elif any(word in description_lower for word in ["概念", "流程", "concept", "diagram"]):
            return "concept"
        elif any(word in description_lower for word in ["摘要", "重點", "summary", "card"]):
            return "summary"
        else:
            return "cover"
