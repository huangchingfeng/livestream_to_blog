#!/usr/bin/env python3
"""簡化版示範 - 直播內容轉部落格文章"""

import json
import os
import anthropic

# 讀取範例逐字稿
with open("examples/sample_transcript.txt", "r", encoding="utf-8") as f:
    transcript = f.read()

client = anthropic.Anthropic()

print("=" * 60)
print("🎬 直播內容轉部落格文章 AI Agent 示範")
print("=" * 60)

# Step 1: 內容分析
print("\n📊 Step 1: 分析直播內容...\n")

analysis_prompt = f"""你是一位專業的內容分析師。請分析以下直播內容，並以 JSON 格式輸出分析結果。

## 直播內容
{transcript}

## 請分析以下項目

1. **title**: 為這篇內容取一個吸引人的標題
2. **key_points**: 列出 3-5 個核心重點（陣列）
3. **motivation**: 講師開這堂課的起心動念是什麼？
4. **features**: 這堂課有什麼特色？（陣列）
5. **target_audience**: 目標受眾是誰？
6. **quotes**: 值得引用的金句（陣列）
7. **action_items**: 聽眾可以採取的行動建議（陣列）

請直接輸出 JSON，不要加其他說明文字。
"""

analysis_response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=2000,
    messages=[{"role": "user", "content": analysis_prompt}]
)

analysis_text = analysis_response.content[0].text
print("✅ 內容分析完成！\n")

# 解析 JSON
try:
    # 找到 JSON 部分
    json_start = analysis_text.find("{")
    json_end = analysis_text.rfind("}") + 1
    analysis = json.loads(analysis_text[json_start:json_end])
except:
    analysis = {"raw": analysis_text}

print("-" * 40)
print("📋 分析結果：")
print("-" * 40)
print(json.dumps(analysis, ensure_ascii=False, indent=2))

# Step 2: 生成部落格文章
print("\n" + "=" * 60)
print("📝 Step 2: 生成部落格文章...\n")

blog_prompt = f"""你是一位專業的部落格作者。請根據以下內容分析，撰寫一篇精美的課後部落格文章。

## 內容分析
{json.dumps(analysis, ensure_ascii=False, indent=2)}

## 文章要求

1. 使用 Markdown 格式
2. 包含以下結構：
   - 吸引人的標題
   - 開場白（說明這堂課的價值）
   - 起心動念（為什麼開這堂課）
   - 課程重點（條列式整理）
   - 特色亮點
   - 金句分享
   - 結語與行動呼籲

3. 風格：專業但親切，讓讀者感受到課程的價值
4. 在適當位置加入 [圖片位置：描述] 標記，建議放圖的地方
5. 長度：800-1200 字

請直接輸出 Markdown 文章。
"""

blog_response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=3000,
    messages=[{"role": "user", "content": blog_prompt}]
)

blog_content = blog_response.content[0].text
print("✅ 文章生成完成！\n")

print("-" * 40)
print("📄 部落格文章：")
print("-" * 40)
print(blog_content)

# Step 3: 生成設計師指令
print("\n" + "=" * 60)
print("🎨 Step 3: 生成設計師指令...\n")

designer_prompt = f"""你是一位資深的創意總監。請根據以下部落格文章，為設計師撰寫詳細的配圖製作指令。

## 部落格文章
{blog_content}

## 請為以下圖片提供製作指令

### 1. 封面圖 (1200 x 630 px)
- 用途：文章封面、社群分享
- 請說明：風格、配色、視覺元素、文字內容

### 2. 重點摘要圖 (800 x 800 px)
- 用途：Instagram、重點整理
- 請說明：如何呈現 3-5 個重點

### 3. 金句卡 (1080 x 1080 px)
- 用途：社群分享、金句傳播
- 請說明：引用的金句、視覺設計

## 輸出格式

請同時提供：
1. **給人類設計師的指令** - 詳細的設計說明
2. **給 AI 圖片生成工具的 Prompt** - 可直接使用的英文 prompt
"""

designer_response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=3000,
    messages=[{"role": "user", "content": designer_prompt}]
)

designer_brief = designer_response.content[0].text
print("✅ 設計師指令生成完成！\n")

print("-" * 40)
print("🎨 設計師指令：")
print("-" * 40)
print(designer_brief)

# 儲存所有輸出
os.makedirs("test_output", exist_ok=True)

with open("test_output/analysis.json", "w", encoding="utf-8") as f:
    json.dump(analysis, f, ensure_ascii=False, indent=2)

with open("test_output/blog_post.md", "w", encoding="utf-8") as f:
    f.write(blog_content)

with open("test_output/designer_brief.md", "w", encoding="utf-8") as f:
    f.write(designer_brief)

print("\n" + "=" * 60)
print("🎉 完成！所有檔案已儲存至 test_output/ 目錄")
print("=" * 60)
print("  📄 test_output/analysis.json     - 內容分析")
print("  📄 test_output/blog_post.md      - 部落格文章")
print("  📄 test_output/designer_brief.md - 設計師指令")
