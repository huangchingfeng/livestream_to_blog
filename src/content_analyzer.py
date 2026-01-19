"""內容分析模組 - 從直播內容中提取關鍵資訊"""

import json
from typing import Any

import anthropic

from .utils import load_prompt


class ContentAnalyzer:
    """直播內容分析器"""

    def __init__(self, api_key: str | None = None):
        """
        初始化分析器

        Args:
            api_key: Anthropic API key，若未提供則從環境變數讀取
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.prompt_template = load_prompt("analyze_content")

    def analyze(self, content: str) -> dict[str, Any]:
        """
        分析直播內容

        Args:
            content: 直播逐字稿或摘要

        Returns:
            分析結果，包含重點、起心動念、特色等
        """
        prompt = self.prompt_template.replace("{content}", content)

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

        # 提取 JSON 結果
        response_text = message.content[0].text

        # 嘗試解析 JSON
        try:
            # 尋找 JSON 區塊
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass

        # 如果無法解析 JSON，返回原始文字
        return {
            "raw_analysis": response_text,
            "key_points": [],
            "motivation": {},
            "unique_features": [],
            "target_audience": {},
            "key_quotes": []
        }

    def analyze_with_custom_focus(
        self,
        content: str,
        focus_areas: list[str]
    ) -> dict[str, Any]:
        """
        使用自訂焦點分析內容

        Args:
            content: 直播內容
            focus_areas: 要特別關注的領域

        Returns:
            分析結果
        """
        focus_prompt = "\n\n## 特別關注\n請特別注意以下方面：\n"
        for area in focus_areas:
            focus_prompt += f"- {area}\n"

        prompt = self.prompt_template.replace("{content}", content)
        prompt += focus_prompt

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

        try:
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass

        return {"raw_analysis": response_text}
