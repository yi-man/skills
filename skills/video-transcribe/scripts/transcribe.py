#!/usr/bin/env python3
"""
视频转文字脚本

用法:
  python3 transcribe.py "<视频链接>"
"""
import sys
import os
import re
import subprocess
import tempfile

# 获取脚本所在目录的相对路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILLS_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))
VIDEO_DOWNLOAD_SCRIPT = os.path.join(SKILLS_DIR, 'video-download', 'scripts', 'download.py')
DOWNLOADS_DIR = os.path.expanduser('~/Downloads')


def detect_language(text):
    """简单检测文本语言"""
    # 统计中文字符
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    total_chars = len(text.strip())
    if total_chars == 0:
        return 'en'
    return 'zh' if chinese_chars / total_chars > 0.3 else 'en'


def download_subtitles(url):
    """尝试用 yt-dlp 直接下载字幕"""
    print("[2/4] 尝试下载字幕...")

    with tempfile.TemporaryDirectory() as tmpdir:
        cmd = [
            'yt-dlp',
            '--write-subs',
            '--write-auto-subs',
            '--sub-lang', 'en,zh-CN',
            '--skip-download',
            '--output', os.path.join(tmpdir, 'subtitle'),
            url
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        print(f"  yt-dlp: {result.returncode}")

        if result.returncode == 0:
            for f in os.listdir(tmpdir):
                if f.endswith('.vtt') or f.endswith('.srt'):
                    subtitle_path = os.path.join(tmpdir, f)
                    with open(subtitle_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    text = extract_text_from_subtitle(content)
                    if text:
                        print(f"  成功下载字幕")
                        return text

    return None


def download_video(url):
    """使用 video-download 下载视频"""
    print(f"[1/4] 下载视频: {url}")

    # 调用 video-download
    result = subprocess.run(
        ['python3', VIDEO_DOWNLOAD_SCRIPT, url],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"下载失败: {result.stderr}")
        return None

    # 查找下载的文件
    match = re.search(r'下载完成:?\s+(.+\.mp4)', result.stdout)
    if match:
        return match.group(1).strip()

    # 尝试在 Downloads 目录找最新的 mp4 文件
    mp4_files = []
    if os.path.exists(DOWNLOADS_DIR):
        for f in os.listdir(DOWNLOADS_DIR):
            if f.endswith('.mp4'):
                path = os.path.join(DOWNLOADS_DIR, f)
                mp4_files.append((path, os.path.getmtime(path)))

    if mp4_files:
        mp4_files.sort(key=lambda x: x[1], reverse=True)
        return mp4_files[0][0]

    print(f"无法找到下载的视频文件")
    return None


def get_subtitles_with_ytdlp(video_path):
    """用本地视频路径下载字幕（yt-dlp 也支持本地文件）"""
    print("[2/4] 尝试从本地视频下载字幕...")

    with tempfile.TemporaryDirectory() as tmpdir:
        cmd = [
            'yt-dlp',
            '--write-subs',
            '--write-auto-subs',
            '--sub-lang', 'en,zh-CN',
            '--skip-download',
            '--output', os.path.join(tmpdir, 'subtitle'),
            video_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            # 查找生成的字幕文件
            for f in os.listdir(tmpdir):
                if f.endswith('.vtt') or f.endswith('.srt'):
                    subtitle_path = os.path.join(tmpdir, f)
                    with open(subtitle_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 提取纯文本
                    text = extract_text_from_subtitle(content)
                    if text:
                        print(f"  成功下载字幕")
                        return text

    return None


def extract_text_from_subtitle(content):
    """从字幕文件中提取纯文本"""
    lines = content.split('\n')
    text_lines = []
    skip_metadata = True  # 跳过 WEBVTT 头部

    for line in lines:
        line = line.strip()
        # 跳过 WEBVTT 头部和元数据
        if skip_metadata:
            if line == 'WEBVTT' or line.startswith('Kind:') or line.startswith('Language:'):
                continue
            if line and not line.startswith('[') and '-->' not in line:
                skip_metadata = False
        # 跳过时间轴和空行
        if not line or '-->' in line or line.isdigit():
            continue
        # 跳过标签和音符符号
        if line.startswith('<') or line == '♪' or line == '[]':
            continue
        # 清理音符
        line = line.replace('♪', '').strip()
        if line:
            text_lines.append(line)

    return '\n'.join(text_lines)


def transcribe_with_whisper(video_path):
    """使用 faster-whisper 语音识别"""
    print("[2/4] 使用 Whisper 识别语音...")

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("错误: 请先安装 faster-whisper")
        print("  uv sync")
        return None

    # 加载模型 (使用 large-v3 模型以提高精度)
    print("  加载 Whisper 模型...")
    model = WhisperModel("large-v3", device="cpu", compute_type="int8")

    # 转写
    print("  识别中...")
    segments, info = model.transcribe(video_path, language=None)  # 自动检测语言

    # 合并所有段落
    text_parts = []
    for segment in segments:
        text_parts.append(segment.text.strip())

    return ' '.join(text_parts)


def translate_to_chinese(text):
    """使用 Google API 翻译成中文"""
    print("[3/4] 翻译成中文...")

    try:
        import asyncio
        from googletrans import Translator
    except ImportError:
        print("  错误: 请先安装 googletrans")
        print("  pip3 install googletrans")
        return None

    try:
        translator = Translator()
        # 分段翻译以避免超限
        paragraphs = text.split('\n\n')
        translated = []

        for para in paragraphs:
            if para.strip():
                # 新版 googletrans 是异步的
                result = asyncio.run(translator.translate(para, src='en', dest='zh-cn'))
                translated.append(result.text)

        return '\n\n'.join(translated)
    except Exception as e:
        print(f"  翻译失败: {e}")
        return None


def save_result(original_text, translated_text, video_path):
    """保存结果到文件"""
    # 用视频名作为输出文件名
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    output_path = os.path.join(DOWNLOADS_DIR, f"{video_name}_transcript.txt")

    with open(output_path, 'w', encoding='utf-8') as f:
        if translated_text:
            f.write("中文翻译:\n")
            f.write(translated_text)
            f.write("\n\n---\n\n")
            f.write("英文原文:\n")
            f.write(original_text)
        else:
            f.write(original_text)

    print(f"[4/4] 结果已保存到: {output_path}")
    return output_path


def transcribe(url):
    """主流程"""
    video_path = None

    # 1. 先尝试直接用 URL 下载字幕（更高效）
    text = download_subtitles(url)

    # 2. 字幕失败，再下载视频用 Whisper
    if not text:
        video_path = download_video(url)
        if not video_path:
            print("错误: 视频下载失败")
            return
        print(f"  视频路径: {video_path}")
        text = transcribe_with_whisper(video_path)

    if not text:
        print("错误: 无法提取文字，请确保视频有声音")
        return

    print(f"  提取文字长度: {len(text)} 字符")

    # 4. 检测语言并翻译
    lang = detect_language(text)
    print(f"  检测语言: {'中文' if lang == 'zh' else '英文'}")

    translated = None
    if lang == 'en':
        translated = translate_to_chinese(text)

    # 5. 保存结果
    # 用视频名或时间戳作为文件名
    if not video_path:
        video_path = f"video_{int(__import__('time').time())}"
    save_result(text, translated, video_path)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python3 transcribe.py <视频链接>")
        sys.exit(1)

    transcribe(sys.argv[1])