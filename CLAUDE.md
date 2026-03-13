# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

这是一个自定义 Claude Code Skills 的存储仓库。用于保存用户常用的技能定义,让 Claude Code 在对话中可以调用这些自定义技能。

## Project Structure

```
skills/
└── <skill-name>/
    ├── SKILL.md          # 技能定义文件
    └── evals/            # 可选的评估测试
        └── evals.json
```

每个技能的 `SKILL.md` 文件包含技能的完整定义，包括：
- name: 技能名称
- description: 触发条件的描述
- 详细的使用说明和工作流程

## Adding New Skills

在 `skills/` 目录下创建新的技能文件夹，添加 `SKILL.md` 文件即可。参考现有的 `video-download` 技能作为模板。

## Common Commands

无需构建、测试或 lint 命令。这是一个纯文档存储仓库。