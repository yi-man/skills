# video-transcribe 实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 从视频URL提取文字并翻译，复用 video-download 下载视频，输出中英对照纯文本

**Architecture:** 视频URL → video-download 下载 → 尝试 yt-dlp 字幕 → 失败则 Whisper 识别 → Google 翻译 → 输出文本

**Tech Stack:** Python, yt-dlp, openai-whisper, googletrans

---

### Task 1: 创建 SKILL.md 技能定义

**Files:**
- Create: `skills/video-transcribe/SKILL.md`

**Step 1: 写入 skill 定义**

```markdown
---
name: video-transcribe
description: 从视频URL提取文字并翻译。支持YouTube/B站等有字幕的平台，以及抖音/小红书等需要语音识别的平台。英文内容会提供中英文对照。
---

# 视频转文字 Skill

## 概述

从视频URL提取文字并翻译。复用 video-download 下载视频。

## 使用方式

```bash
python3 ~/.cursor/skills/video-transcribe/transcribe.py "<视频链接>"
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
```

**Step 2: 提交**

```bash
git add skills/video-transcribe/SKILL.md
git commit -m "feat: add video-transcribe skill definition"
```

---

### Task 2: 创建安装脚本

**Files:**
- Create: `skills/video-transcribe/scripts/install_deps.sh`

**Step 1: 写入安装脚本**

```bash
#!/bin/bash
# video-transcribe 依赖安装脚本

echo "安装 Python 依赖..."

# Google 翻译 API
pip3 install googletrans==4.0.0-rc1 || pip install googletrans==4.0.0-rc1

# Whisper 语音识别
pip3 install openai-whisper || pip install openai-whisper

# ffmpeg (macOS)
if command -v brew &> /dev/null; then
    brew install ffmpeg
else
    echo "请手动安装 ffmpeg: https://ffmpeg.org/download.html"
fi

echo "安装完成！"
```

**Step 2: 添加执行权限并提交**

```bash
chmod +x skills/video-transcribe/scripts/install_deps.sh
git add skills/video-transcribe/scripts/install_deps.sh
git commit -m "feat: add install_deps.sh"
```

---

### Task 3: 创建主转写脚本

**Files:**
- Create: `skills/video-transcribe/scripts/transcribe.py`

**Step 1: 写入完整脚本**

```python
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
```

**Step 2: 添加执行权限并提交**

```bash
chmod +x skills/video-transcribe/scripts/transcribe.py
git add skills/video-transcribe/scripts/transcribe.py
git commit -m "feat: add transcribe.py script"
```

---

### Task 4: 创建 evals 测试用例

**Files:**
- Create: `skills/video-transcribe/evals/evals.json`

**Step 1: 写入测试用例**

```json
{
  "skill_name": "video-transcribe",
  "evals": [
    {
      "id": 1,
      "prompt": "提取这个YouTube视频的文字 https://www.youtube.com/watch?v=dQw4w9WgXcQ",
      "expected_output": "Skill应该: 1)调用video-download下载视频 2)用yt-dlp下载字幕 3)是英文则翻译成中文 4)输出到txt文件",
      "files": []
    },
    {
      "id": 2,
      "prompt": "帮我把这个B站视频转成文字 https://www.bilibili.com/video/BV1xx411c7XD",
      "expected_output": "Skill应该处理B站视频，尝试下载字幕后转写",
      "files": []
    },
    {
      "id": 3,
      "prompt": "下载这个抖音视频的文字 https://v.douyin.com/abc123",
      "expected_output": "Skill应该使用Whisper进行语音识别",
      "files": []
    }
  ]
}
```

**Step 2: 提交**

```bash
git add skills/video-transcribe/evals/evals.json
git commit -m "feat: add evals for video-transcribe"
```

---

### Task 5: 更新 README（可选）

**Files:**
- Modify: `skills/video-download/SKILL.md`

**添加一行到表格：**

```markdown
| 视频转文字 | video-transcribe | 需要先下载视频再提取文字 |
```

---

**Plan complete and saved to `docs/plans/2026-03-14-video-transcribe-plan.md`.**

Two execution options:

1. **Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

2. **Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

Which approach?