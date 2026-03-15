---
name: video-transcribe
description: 从视频URL提取文字并翻译。支持YouTube/B站等有字幕的平台，以及抖音/小红书等需要语音识别的平台。英文内容会提供中英文对照。
---

# 视频转文字 Skill

## 概述

从视频URL提取文字并翻译。复用 video-download 下载视频，使用 faster-whisper 进行语音识别。

## 使用方式

### 1. 安装依赖

```bash
cd <skill安装目录>
uv sync
```

### 2. 运行

```bash
cd <skill安装目录>
source .venv/bin/activate
python3 scripts/transcribe.py "<视频链接>"
```

## 支持平台

| 平台        | 文字提取方式            |
| ----------- | ----------------------- |
| YouTube     | 直接下载字幕            |
| B站         | 直接下载字幕            |
| 抖音/小红书 | faster-whisper 语音识别 |

## 输出示例

```
中文翻译:
这是视频内容...

---

英文原文:
This is the video content...
```
