---
name: video-transcribe
description: 根据本地视频文件路径提取文字并翻译。当用户要给视频转文字时，应先触发 video-download Skill 得到本地视频路径，再使用本 Skill 传入该路径。英文内容会提供中英文对照。
---

# 视频转文字 Skill

## 概述

根据**本地视频路径**提取文字并翻译。本 Skill 不负责下载视频，下载由 **video-download** Skill 完成。

**正确工作流**：先触发 **video-download** Skill 下载视频并得到本地路径 → 再使用本 Skill 传入该路径进行转写与翻译。

## 使用方式

### 1. 安装依赖

```bash
cd <skill安装目录>
uv sync
```

### 2. 运行（传入本地视频路径）

```bash
cd <skill安装目录>
uv run python scripts/transcribe.py "<本地视频路径>"
```

**注意**：`<本地视频路径>` 应为 video-download 下载后的文件路径（如 `~/Downloads/xxx.mp4`），不要直接传视频链接。若用户只提供链接，请先调用 **video-download** Skill 完成下载，再用返回的路径调用本脚本。

## 文字提取方式

| 情况           | 方式                     |
| -------------- | ------------------------ |
| 有现成字幕文件 | 从视频/字幕提取文字      |
| 无字幕         | 使用 faster-whisper 语音识别 |

## 输出示例

```
中文翻译:
这是视频内容...

---

英文原文:
This is the video content...
```
