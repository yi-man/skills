---
name: video-download
description: 使用 Playwright + yt-dlp 下载视频。支持抖音、小红书、B站等国内平台及 YouTube、Twitter 等国际平台。当用户给出视频链接或请求下载视频/音频时使用此Skill。
---

# 视频下载 Skill

## 概述

此 Skill 帮助用户下载视频。支持以下平台：

| 平台          | 下载方式   | 说明               |
| ------------- | ---------- | ------------------ |
| 抖音          | Playwright | 支持短链和完整链接 |
| 小红书        | Playwright | 支持图文和视频笔记 |
| B站           | Playwright | 支持登录获取高清   |
| YouTube       | yt-dlp     | 4K、HDR 等         |
| Twitter/X     | yt-dlp     |                    |
| Instagram     | yt-dlp     |                    |
| 其他1700+站点 | yt-dlp     |                    |

## 使用场景

- 用户给出视频链接并要求下载
- 用户说"帮我下载这个视频"
- 用户请求下载抖音/小红书/B站视频

## 完整工作流程

### 步骤1：检查依赖是否已安装

首次使用需安装依赖，运行：

```bash
bash ~/.agents/skills/video-download/scripts/install_deps.sh
```

此脚本会安装：

- yt-dlp
- Playwright + Chromium 浏览器
- ffmpeg (可选，B站合并音视频需要)

### 步骤2：检测平台并下载

用户提供视频链接后，使用以下命令下载：

```bash
python3 ~/.agents/skills/video-download/scripts/download.py "<视频链接>"
```

**自动识别平台：**

- 抖音: `v.douyin.com/xxx` 或 `www.douyin.com/video/xxx`
- 小红书: `xhslink.com/xxx` 或 `xiaohongshu.com/discovery/item/xxx`
- B站: `b23.tv/xxx` 或 `bilibili.com/video/BVxxx`
- YouTube/Twitter等: 自动使用 yt-dlp

### 步骤3：指定输出文件名（可选）

```bash
python3 ~/.agents/skills/video-download/scripts/download.py "<链接>" "我的视频"
```

文件会保存到 `~/Downloads/` 目录。

## 登录支持

B站需要登录才能下载高清视频。

### 登录命令

```bash
python3 ~/.agents/skills/video-download/scripts/login.py login bilibili
python3 ~/.agents/skills/video-download/scripts/login.py login douyin
python3 ~/.agents/skills/video-download/scripts/login.py login xiaohongshu
```

登录后会打开浏览器，用户完成登录后关闭浏览器即可自动保存 cookie。

### 检查登录状态

```bash
python3 ~/.agents/skills/video-download/scripts/download.py check-login bilibili
```

## 常见下载选项

### 仅下载音频（MP3）

使用 yt-dlp 的 `-x` 选项：

```bash
yt-dlp -x --audio-format mp3 "<YouTube链接>"
```

注意：抖音/小红书视频不支持此方式。

### 下载字幕

```bash
yt-dlp --write-subs --sub-lang zh-CN "<链接>"
```

## 平台注意事项

| 平台    | 注意事项                                  |
| ------- | ----------------------------------------- |
| B站     | 登录后可下载高清；番剧/付费内容可能不支持 |
| 抖音    | 使用 Playwright 模拟浏览器访问            |
| 小红书  | 图文笔记无法下载视频                      |
| YouTube | 支持 4K、HDR                              |

## 错误处理

1. **Playwright 未安装**：运行 `bash ~/.agents/skills/video-download/scripts/install_deps.sh`
2. **ffmpeg 未安装**（B站下载失败）：`brew install ffmpeg`
3. **下载失败**：检查网络连接，或尝试更新 yt-dlp: `pip3 install -U yt-dlp`
