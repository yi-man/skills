# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

这是一个自定义 Claude Code Skills 的存储仓库。用于保存用户常用的技能定义,让 Claude Code 在对话中可以调用这些自定义技能。

## Project Structure

```
skills/
├── skills/              # 技能目录
│   ├── video-download/  # 视频下载技能
│   │   └── SKILL.md
│   └── video-transcribe/ # 视频转文字技能
│       ├── SKILL.md
│       ├── pyproject.toml
│       ├── uv.lock
│       ├── scripts/
│       └── evals/
├── docs/                # 文档
├── README.md
└── CLAUDE.md
```

每个技能的 `SKILL.md` 文件包含技能的完整定义，包括：
- name: 技能名称
- description: 触发条件的描述
- 详细的使用说明和工作流程

## Available Skills

- **video-download**: 使用 `yt-dlp` 下载各平台视频/音频，支持 YouTube、B 站等
- **video-transcribe**: 从视频URL提取文字并翻译，支持字幕下载和语音识别 (requires uv + Python)

## Adding New Skills

在 `skills/skills/` 目录下创建新的技能文件夹，添加 `SKILL.md` 文件即可。参考现有的 `video-download` 或 `video-transcribe` 技能作为模板。

对于需要依赖的技能：
- 使用 `uv` 管理 Python 依赖 (pyproject.toml + uv.lock)
- 将脚本放在 `scripts/` 目录下
- 添加 `evals/` 目录用于评估测试

## Common Commands

```bash
# 设置 video-transcribe 技能依赖
cd skills/video-transcribe
uv sync
source .venv/bin/activate

# 运行视频转文字
python scripts/transcribe.py "<视频链接>"
```

对于纯文档技能，无需构建或测试命令。