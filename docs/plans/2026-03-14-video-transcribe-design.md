# video-transcribe 设计文档

## 概述

从视频URL提取文字并翻译。复用 video-download 下载视频，根据平台选择字幕下载或语音识别，最后输出纯文本。

## 流程

```
视频URL → video-download 下载 → 尝试 yt-dlp 获取字幕 →
失败则 Whisper 识别 → 是英文则 Google 翻译 → 输出文本
```

## 依赖

| 工具 | 用途 |
|------|------|
| video-download | 下载视频 |
| yt-dlp | 尝试下载字幕 |
| openai-whisper | 本地语音识别 |
| googletrans | Google API 翻译 |

## 输出格式

```
英文原文:
这是视频中的英文文字内容...

中文翻译:
这是视频中的中文翻译...
```

（如果本来就是中文，只输出中文）

## 错误处理

1. 视频下载失败 → 提示用户检查链接
2. 无字幕 + 识别失败 → 提示安装 ffmpeg
3. 翻译失败 → 仅输出原文