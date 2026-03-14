---
name: video-transcribe
description: 从视频URL提取文字并翻译。支持YouTube/B站等有字幕的平台，以及抖音/小红书等需要语音识别的平台。英文内容会提供中英文对照。
---

# 视频转文字 Skill

## 概述

从视频URL提取文字并翻译。复用 video-download 下载视频。

## 使用方式

```bash
python3 ~/.cursor/skills/video-transcribe/scripts/transcribe.py "<视频链接>"
```

## 支持平台

| 平台 | 文字提取方式 |
|------|-------------|
| YouTube | 直接下载字幕 |
| B站 | 直接下载字幕 |
| 抖音/小红书 | Whisper 语音识别 |

## 输出示例

```
英文原文:
This is the video content...

中文翻译:
这是视频内容...
```

## 依赖

首次使用需安装：
```bash
pip3 install googletrans==4.0.0-rc1
pip3 install openai-whisper
brew install ffmpeg
```

或运行安装脚本：
```bash
bash ~/.cursor/skills/video-transcribe/scripts/install_deps.sh
```