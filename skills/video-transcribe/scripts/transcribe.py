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

# Google 翻译
try:
    from googletrans import Translator
    GOOGLE_TRANSLATOR_AVAILABLE = True
except ImportError:
    GOOGLE_TRANSLATOR_AVAILABLE = False

VIDEO_DOWNLOAD_SCRIPT = os.path.expanduser('~/.cursor/skills/video-download/scripts/download.py')
DOWNLOADS_DIR = os.path.expanduser('~/Downloads')


def detect_language(text):
    """简单检测文本语言"""
    # 统计中文字符
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    total_chars = len(text.strip())
    if total_chars == 0:
        return 'en'
    return 'zh' if chinese_chars / total_chars > 0.3 else 'en'


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
    # video-download 输出 "下载完成: /path/to/file.mp4"
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
    """尝试用 yt-dlp 下载字幕"""
    print("[2/4] 尝试下载字幕...")

    # 创建临时目录存放字幕
    with tempfile.TemporaryDirectory() as tmpdir:
        # yt-dlp --write-subs --skip-download --output template
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

    for line in lines:
        line = line.strip()
        # 跳过时间轴和空行
        if not line or '-->' in line or line.isdigit():
            continue
        # 跳过标签
        if line.startswith('<'):
            continue
        text_lines.append(line)

    return '\n'.join(text_lines)


def transcribe_with_whisper(video_path):
    """使用 Whisper 语音识别"""
    print("[2/4] 使用 Whisper 识别语音...")

    try:
        import whisper
    except ImportError:
        print("错误: 请先安装 whisper")
        print("  pip3 install openai-whisper")
        return None

    # 加载模型 (使用 base 模型以提高速度)
    print("  加载 Whisper 模型...")
    model = whisper.load_model("base")

    # 转写
    print("  识别中...")
    result = model.transcribe(video_path, language=None)  # 自动检测语言

    return result.get('text', '').strip()


def translate_to_chinese(text):
    """使用 Google API 翻译成中文"""
    print("[3/4] 翻译成中文...")

    if not GOOGLE_TRANSLATOR_AVAILABLE:
        print("  错误: 请先安装 googletrans")
        print("  pip3 install googletrans==4.0.0-rc1")
        return None

    try:
        translator = Translator()
        # 分段翻译以避免超限
        paragraphs = text.split('\n\n')
        translated = []

        for para in paragraphs:
            if para.strip():
                result = translator.translate(para, src='en', dest='zh-cn')
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
    # 1. 下载视频
    video_path = download_video(url)
    if not video_path:
        print("错误: 视频下载失败")
        return

    print(f"  视频路径: {video_path}")

    # 2. 尝试获取字幕
    text = get_subtitles_with_ytdlp(video_path)

    # 3. 失败则用 Whisper
    if not text:
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
    save_result(text, translated, video_path)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python3 transcribe.py <视频链接>")
        sys.exit(1)

    transcribe(sys.argv[1])