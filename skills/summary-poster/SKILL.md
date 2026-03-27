---
name: summary-poster
description: Use when user provides article content or web URLs and requests a designed page or screenshot output. Accepts URLs, text content, or documents with optional instructions on which sections to focus on.
---

# Summary Poster Skill

## Overview

将文章内容或网页内容转换为设计精美的页面，并提供截图功能。完全使用 Claude Code 的现有工具链实现（WebFetch → frontend-design → agent-browser）。

## When to Use

**使用场景：**
- 用户提供 URL 或文档并要求"设计一个页面"
- 用户想要将文章内容生成页面截图
- 用户为文档创建视觉化摘要
- 用户想要将网页内容转为可分享的图片
- 用户为特定内容设计海报式页面

**不使用场景：**
- 纯文本摘要（不需要设计页面）
- 不需要截图的情况

## Core Workflow

### Step 1: Read Content

读取和解析用户提供的内容：

#### 读取 URL 内容
```bash
# 读取完整 URL 内容
WebFetch --url "<URL>" --description "提取文章的主要内容"
```

```bash
# 读取指定部分内容（含用户说明）
WebFetch --url "<URL>" --description "提取文档中第 3-5 部分，关于技术架构的内容"
```

#### 读取本地文档内容
```bash
# 使用 Read 工具直接读取本地文本文件
Read "<本地文件路径>"
```

```bash
# 使用 WebFetch 读取本地文件（需要 file:// 协议）
WebFetch --url "file://<本地文件绝对路径>" --description "提取文档内容"
```

**注意：** 如果网络访问受限（如企业防火墙限制），建议直接使用 Read 工具读取本地文件

### Step 2: Design Page with frontend-design

根据解析的内容，使用 frontend-design 设计 HTML 页面：

```bash
frontend-design --input "<解析后的内容>" --style "modern" --layout "article" --title "<页面标题>"
```

**设计选项：**
- `--style`: 页面风格（`modern`, `minimal`, `corporate`, `vintage`）
- `--layout`: 布局类型（`article`, `poster`, `sidebar`, `grid`）
- `--title`: 页面标题（默认从内容中自动提取）

### Step 3: View and Screenshot with agent-browser

使用 agent-browser 访问设计好的页面并截图：

```bash
agent-browser --url "<页面URL>" --screenshot "full" --output "summary-poster.png"
```

## Quick Reference

| Task | Command Pattern |
|------|----------------|
| 完整 URL + 内容部分说明 | `WebFetch → frontend-design → agent-browser` |
| 本地文档 + 自定义标题 | `WebFetch (file:///) → frontend-design --title → agent-browser` |
| 现代风格文章布局 | `--style "modern" --layout "article"` |
| 极简学术风格 | `--style "minimal" --layout "article"` |
| 海报式展示 | `--style "vintage" --layout "poster"` |

## Input Examples

### Example 1: Full URL + Section Instructions

**User Input:**
```
https://example.com/ai-trends-2026
请提取文章中关于生成式AI应用的部分，设计一个现代风格的页面，并截图返回。
```

**Workflow:**
```bash
# Step 1: Read content
WebFetch --url "https://example.com/ai-trends-2026" --description "提取文章中关于生成式AI应用的部分"

# Step 2: Design page
frontend-design --input "<解析后的内容>" --style "modern" --layout "article" --title "2026生成式AI应用趋势"

# Step 3: Take screenshot
agent-browser --url "<设计好的页面URL>" --screenshot "full" --output "ai-trends-summary.png"
```

### Example 2: Local Content + Custom Title

**User Input:**
```
本地文档路径：~/Documents/research-paper.txt
请将文档的前两章内容设计成一个学术风格的页面，标题为"人工智能研究综述"。
```

**Workflow:**
```bash
# Step 1: Read content
WebFetch --url "file:///Users/user/Documents/research-paper.txt" --description "提取文档的前两章内容"

# Step 2: Design page
frontend-design --input "<解析后的内容>" --style "minimal" --layout "article" --title "人工智能研究综述"

# Step 3: Take screenshot
agent-browser --url "<设计好的页面URL>" --screenshot "full" --output "research-summary.png"
```

## Page Style Options

| Style | Characteristics | Best For |
|-------|----------------|----------|
| **modern** | 现代简洁风格，大留白 | 技术文章、新闻 |
| **minimal** | 极简风格，纯文字 | 学术文档、研究报告 |
| **corporate** | 商务风格，结构化 | 企业报告、白皮书 |
| **vintage** | 复古风格，纹理装饰 | 历史文档、传统内容 |

## Layout Types

| Layout | Characteristics | Best For |
|--------|----------------|----------|
| **article** | 传统文章布局 | 长文本内容 |
| **poster** | 海报式布局，强调视觉 | 内容摘要、展示 |
| **sidebar** | 侧边栏布局，多列 | 技术文档、教程 |
| **grid** | 网格布局，模块化 | 产品展示、列表 |

## Output Specifications

### Screenshot Specs
- **Size:** Full screen (1920×1080 or larger)
- **Format:** PNG (high quality)
- **Filename:** Auto-generated with content topic and timestamp

### Common Mistakes & Fixes

| Issue | Fix |
|-------|-----|
| WebFetch fails to read content | Check URL validity, verify content is publicly accessible, adjust description |
| WebFetch 网络访问受限 | 使用 Read 工具直接读取本地文件，或让用户直接提供文本内容 |
| frontend-design fails | Check content format completeness, try different style/layout, simplify design requirements |
| agent-browser screenshot fails | Verify page accessibility, adjust screenshot dimensions and format |
| agent-browser --allow-file-access 不起作用 | 先运行 `agent-browser close` 关闭 daemon，再使用新选项重启 |

### 网络受限环境处理

如果企业安全策略限制了外部网络访问，可以采用以下替代方案：

1. **使用本地文件**：让用户将需要处理的内容保存为本地文本文件
2. **直接提供文本**：用户可以直接粘贴或输入需要处理的文本内容
3. **简化工作流程**：跳过 WebFetch 步骤，直接使用提供的文本进行页面设计

#### 替代工作流程示例

```bash
# 步骤 1: 直接使用 Read 工具读取本地文件
Read "<本地文件路径>"

# 步骤 2: 使用 frontend-design 设计页面
frontend-design --input "<读取到的内容>" --style "minimal" --layout "article" --title "文档标题"

# 步骤 3: 使用 agent-browser 截图
agent-browser --url "file://<本地HTML文件路径>" --screenshot "full" --output "summary-poster.png"
```


## Implementation Notes

本技能为**纯文档型技能**，无需额外安装依赖，直接在 Claude Code 中引用并按照上述工作流程执行即可。

本技能通过调用以下现有工具实现：
- **WebFetch**：内容读取
- **frontend-design**：页面设计
- **agent-browser**：页面访问与截图

## Creating This Skill

This skill was created using the design document at `docs/superpowers/specs/2026-03-27-summary-poster-design.md`.

For updates or improvements:
1. Update the design document first
2. Update this `SKILL.md` file
3. Test the updated workflow
