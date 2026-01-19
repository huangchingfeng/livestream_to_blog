# 直播內容轉部落格文章 AI Agent

這是一個 AI agent，能夠將直播內容自動轉換成精美的課後部落格文章。

## 功能特色

- 📝 **自動生成部落格文章**：從直播逐字稿或摘要生成完整文章
- 🎯 **重點提取**：自動識別並整理課程重點
- 💡 **起心動念**：捕捉講師的教學初衷和動機
- 🎨 **圖片設計**：支援兩種模式
  - **Gemini API 自動生成**：直接生成配圖
  - **設計師指令**：輸出給設計師的詳細製圖指令

## 架構設計

```
┌─────────────────────────────────────────────────────────────────┐
│                    Livestream to Blog Agent                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐   │
│  │   輸入處理    │ -> │   內容分析    │ -> │    文章生成      │   │
│  │              │    │              │    │                  │   │
│  │ - 逐字稿     │    │ - 重點提取   │    │ - 標題          │   │
│  │ - 影片/音檔  │    │ - 起心動念   │    │ - 摘要          │   │
│  │ - 摘要       │    │ - 特色識別   │    │ - 完整內容      │   │
│  └──────────────┘    └──────────────┘    └──────────────────┘   │
│                                                                  │
│                              ↓                                   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                      圖片生成模組                          │   │
│  │                                                           │   │
│  │   ┌─────────────────┐    ┌─────────────────────────────┐ │   │
│  │   │  Gemini API     │ OR │  設計師指令生成器             │ │   │
│  │   │  (自動生成圖片)  │    │  (輸出詳細製圖說明)          │ │   │
│  │   └─────────────────┘    └─────────────────────────────┘ │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│                              ↓                                   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                        輸出                                │   │
│  │   - Markdown 部落格文章                                    │   │
│  │   - 配圖 (PNG/JPG) 或 設計師指令文檔                       │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 安裝

```bash
# 安裝依賴
pip install -r requirements.txt

# 設定環境變數
cp .env.example .env
# 編輯 .env 填入你的 API keys
```

## 使用方式

```bash
# 基本使用 - 從逐字稿生成文章
python main.py --input transcript.txt

# 指定輸出目錄
python main.py --input transcript.txt --output ./blog_posts/

# 使用 Gemini API 自動生成圖片
python main.py --input transcript.txt --image-mode gemini

# 生成設計師指令（不自動生成圖片）
python main.py --input transcript.txt --image-mode designer
```

## 環境變數

| 變數名稱 | 說明 | 必填 |
|---------|------|------|
| `ANTHROPIC_API_KEY` | Anthropic API Key (用於文章生成) | 是 |
| `GEMINI_API_KEY` | Google Gemini API Key (用於圖片生成) | 否 |

## 專案結構

```
livestream_to_blog/
├── main.py                    # 主程式入口
├── requirements.txt           # Python 依賴
├── .env.example              # 環境變數範例
├── README.md                 # 說明文件
├── src/
│   ├── __init__.py
│   ├── agent.py              # 主要 Agent 邏輯
│   ├── content_analyzer.py   # 內容分析模組
│   ├── blog_generator.py     # 部落格文章生成
│   ├── image_generator.py    # 圖片生成 (Gemini API)
│   ├── designer_prompt.py    # 設計師指令生成
│   └── utils.py              # 工具函數
├── prompts/
│   ├── analyze_content.md    # 內容分析 prompt
│   ├── generate_blog.md      # 文章生成 prompt
│   ├── generate_image.md     # 圖片生成 prompt
│   └── designer_brief.md     # 設計師指令 prompt
└── examples/
    ├── sample_transcript.txt # 範例逐字稿
    └── sample_output/        # 範例輸出
```

## License

MIT License
