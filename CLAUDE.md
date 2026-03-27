### Project: Claude Code Skills

自定义 Claude Code Skills 的存储仓库，用于保存用户常用的技能定义，让 Claude Code 在对话中可以调用这些自定义技能。

---

### Code Style

- SKILL.md 要保持精简，时常优化

---

### Commands
- **技能评估**: 使用 `/skill-creator:skill-creator` 技能进行评估

---

### Architecture

- `/skills/`: 技能存储目录（包含所有自定义技能）
  - `/video-download/`: 视频下载技能（使用 yt-dlp）
  - `/video-transcribe/`: 视频转文字技能（使用 Python + Whisper）
  - `/summary-poster/`: 文档内容转页面设计与截图技能
- `/docs/`: 项目文档
- `/README.md`: 项目说明文档
- `/CLAUDE.md`: Claude Code 配置和使用指南

---

### Important Notes
- 有依赖的技能使用 uv 管理 Python 依赖
- evals 目录下的示例要真实可用
- 优先使用无头模式进行截图操作（参考 summary-poster 技能）