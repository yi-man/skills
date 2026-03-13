---
name: video-download
description: 使用yt-dlp下载视频。当用户给出视频链接（YouTube、B站等），或请求下载视频/音频时，必须使用此Skill。自动检查yt-dlp是否安装，获取视频信息让用户选择格式和画质，然后执行下载。也支持用户说"转成mp3"、"下载音频"等音频提取需求。
---

# yt-dlp 视频下载 Skill

## 概述

此Skill帮助用户使用yt-dlp工具下载视频。支持YouTube、B站等国内外主流视频平台。

**注意：抖音/ TikTok 目前无法通过 yt-dlp 下载**，因为抖音加强了反爬机制，需要特定的浏览器指纹（s_v_web_id）才能访问API。如需下载抖音视频，请使用抖音APP的"保存到本地"功能或手机录屏。

## 使用场景

- 用户给出视频链接并要求下载
- 用户说"帮我下载这个视频"
- 用户请求使用yt-dlp下载视频
- 用户提到"youtube-dl"或"yt-dlp"

## 完整工作流程

### 步骤1：检查yt-dlp是否已安装

执行以下命令检查：

```bash
which yt-dlp
```

或者：

```bash
yt-dlp --version
```

如果yt-dlp未安装，必须先告知用户安装方法：

**macOS (Homebrew):**

```bash
brew install yt-dlp
```

**Linux:**

```bash
sudo pip install yt-dlp
```

**Windows (winget):**

```bash
winget install yt-dlp.yt-dlp
```

### 步骤2：解析视频信息

用户给出视频链接后，使用以下命令获取视频信息：

```bash
yt-dlp --list-formats <视频链接>
```

或者使用更详细的输出：

```bash
yt-dlp -F <视频链接>
```

### 步骤3：展示可用格式给用户

将格式列表展示给用户，包含：

- 格式代码 (format code)
- 分辨率 (resolution)
- 文件大小/扩展名 (extension)
- 编码信息 (codec)

### 步骤4：让用户选择下载格式

询问用户希望下载的格式和质量，常见选项：

- **最佳质量视频+音频**: `--format best`
- **仅视频 (最佳画质)**: `--format bestvideo`
- **仅音频 (最佳音质)**: `--format bestaudio`
- **指定格式**: `--format <格式代码>` (如 `bv+ba/best`)
- **指定分辨率**: `--format "best[height<=1080]"` (限制1080p以下)

或者让用户从步骤2的列表中选择格式代码。

### 步骤5：执行下载

根据用户选择执行下载，命令示例：

```bash
# 下载到当前目录
yt-dlp -f <格式> <视频链接>

# 下载到指定目录
yt-dlp -f <格式> -o "~/Downloads/%(title)s.%(ext)s" <视频链接>

# 仅下载音频 (mp3)
yt-dlp -x --audio-format mp3 <视频链接>

# 下载字幕
yt-dlp --write-subs --sub-lang zh-CN <视频链接>

# 下载最佳质量 (视频+音频合并)
yt-dlp -f "bv+ba/best" <视频链接>
```

### 步骤6：显示下载结果

下载完成后，显示：

- 文件保存路径
- 文件大小
- 下载状态

## 常见下载选项

| 选项                        | 说明                                      |
| --------------------------- | ----------------------------------------- |
| `-f <format>`               | 指定格式代码                              |
| `-o <path>`                 | 指定输出路径模板                          |
| `-x`                        | 仅提取音频                                |
| `--audio-format mp3`        | 转换为MP3                                 |
| `--write-subs`              | 下载字幕                                  |
| `--write-auto-subs`         | 下载自动字幕                              |
| `--sub-lang <lang>`         | 指定字幕语言                              |
| `-k`                        | 保留视频/音频文件（下载分离的格式后合并） |
| `--merge-output-format mp4` | 合并时输出为MP4                           |

## 平台注意事项

- **YouTube**: 支持4K、HDR等
- **Bilibili**: 可能需要 `--cookies-from-browser chrome` 登录cookie
- **抖音/TikTok**: ⚠️ **暂不支持** - 由于抖音加强了反爬机制，目前无法通过 yt-dlp 下载
- **X (Twitter)**: 支持
- **小红书**: 可能需要cookie

## 常见用户意图识别

除了直接说"下载视频"，以下情况也应该触发此Skill：

- "把这个视频转成mp3" / "下载音频"
- "帮我下这首歌" (YouTube/Spotify链接)
- "只要音频，不要视频"
- "提取视频的背景音乐"

## 错误处理

如果下载失败：

1. 检查网络连接
2. 尝试更新yt-dlp: `pip install -U yt-dlp`
3. 某些网站可能需要cookie认证
4. 检查是否被网站封锁，尝试使用 `--user-agent` 参数
