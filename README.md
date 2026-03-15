# 我的 Agent Skills 仓库

这是我的个人 Agent Skills 集合仓库，用于在 Cursor / Claude Code 等支持 Skills 的 IDE 或 Agent 中复用常用能力。

每个 Skill 都放在 `skills/<skill-name>/SKILL.md` 中，包含完整的使用说明和触发条件。

## 当前包含的 Skills

- **video-download**：使用 `yt-dlp` 下载各平台视频/音频，支持 YouTube、B 站等，支持格式选择、仅音频（mp3）、字幕下载等功能。
  - 详情见：`skills/video-download/SKILL.md`
- **video-transcribe**：从视频URL提取文字并翻译，支持字幕下载（YouTube/B站）和语音识别（抖音/小红书），使用 faster-whisper 进行语音转录。
  - 详情见：`skills/video-transcribe/SKILL.md`

## 使用方式（建议）

- 将本仓库作为你的「个人 Skill 库」，在本地或云端同步。
- 在支持自定义 Skills 的 Agent 中，根据各自平台的文档，把对应的 `SKILL.md` 引入或引用。
- 新增 Skill 时，在 `skills/skills/` 目录下新建子文件夹，并添加对应的 `SKILL.md` 即可。

## 目录结构示例

```text
skills/
├── README.md
├── CLAUDE.md
├── skills/
│   ├── video-download/
│   │   └── SKILL.md
│   └── video-transcribe/
│       ├── SKILL.md
│       ├── pyproject.toml
│       ├── uv.lock
│       ├── scripts/
│       └── evals/
├── docs/
└── .gitignore
```

