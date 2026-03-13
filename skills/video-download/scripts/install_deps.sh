#!/bin/bash
# 视频下载依赖安装脚本
# 支持 macOS / Linux

set -e

echo "开始安装视频下载依赖..."

# 检查 Python 版本
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 python3，请先安装 Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "检测到 Python 版本: $PYTHON_VERSION"

# 安装 yt-dlp
echo "[1/4] 安装 yt-dlp..."
if command -v brew &> /dev/null; then
    brew install yt-dlp 2>/dev/null || pip3 install -U yt-dlp
else
    pip3 install -U yt-dlp
fi

# 安装 Playwright
echo "[2/4] 安装 Playwright..."
pip3 install --user --break-system-packages playwright

# 安装 Playwright 浏览器
echo "[3/4] 安装 Playwright Chromium 浏览器..."
python3 -m playwright install chromium

# 安装 ffmpeg (用于B站音视频合并)
echo "[4/4] 检查 ffmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo "ffmpeg 未安装，B站下载的音视频合并可能失败"
    if command -v brew &> /dev/null; then
        echo "运行以下命令安装: brew install ffmpeg"
    fi
else
    echo "ffmpeg 已安装"
fi

# 创建配置目录
mkdir -p ~/.config/video-download

echo ""
echo "安装完成！"
echo ""
echo "使用方法:"
echo "  python3 ~/.cursor/skills/video-download/scripts/download.py <视频链接> [输出文件名]"
echo ""
echo "可选操作 (B站高清视频需要登录):"
echo "  python3 ~/.cursor/skills/video-download/scripts/download.py login bilibili"
echo "  python3 ~/.cursor/skills/video-download/scripts/download.py login douyin"
echo "  python3 ~/.cursor/skills/video-download/scripts/download.py login xiaohongshu"