"""工具函數"""

import os
from pathlib import Path


def get_project_root() -> Path:
    """取得專案根目錄"""
    return Path(__file__).parent.parent


def load_prompt(prompt_name: str) -> str:
    """
    載入 prompt 模板

    Args:
        prompt_name: prompt 檔案名稱（不含副檔名）

    Returns:
        prompt 模板內容
    """
    prompt_path = get_project_root() / "prompts" / f"{prompt_name}.md"
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def ensure_output_dir(output_path: str | Path) -> Path:
    """
    確保輸出目錄存在

    Args:
        output_path: 輸出路徑

    Returns:
        Path 物件
    """
    path = Path(output_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_input_file(file_path: str | Path) -> str:
    """
    讀取輸入檔案

    Args:
        file_path: 檔案路徑

    Returns:
        檔案內容
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def save_output(content: str, output_path: str | Path, filename: str) -> Path:
    """
    儲存輸出內容

    Args:
        content: 輸出內容
        output_path: 輸出目錄
        filename: 檔案名稱

    Returns:
        完整檔案路徑
    """
    output_dir = ensure_output_dir(output_path)
    file_path = output_dir / filename
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    return file_path
