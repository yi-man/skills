#!/bin/bash
# video-transcribe 依赖安装脚本

echo "安装 Python 依赖..."

# Google 翻译 API
pip3 install googletrans==4.0.0-rc1 || pip install googletrans==4.0.0-rc1

# Whisper 语音识别
pip3 install openai-whisper || pip install openai-whisper

# ffmpeg (macOS)
if command -v brew &> /dev/null; then
    echo "安装 ffmpeg..."
    brew install ffmpeg
else
    echo "请手动安装 ffmpeg: https://ffmpeg.org/download.html"
fi

echo "安装完成！"