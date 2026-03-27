---
name: summary-poster
description: 当用户提供文章内容、网页URL或本地文档，并要求生成设计精美的页面截图时使用。支持内容解析、页面设计和截图功能，默认语言为中文。
---

# Summary Poster Skill

## 概述

将文章内容或网页内容转换为设计精美的页面，并提供截图功能。完全使用 Claude Code 的现有工具链实现（WebFetch → frontend-design → agent-browser）。

## 使用场景

**适用场景：**
- 用户提供 URL 或文档并要求"设计一个页面"
- 用户想要将文章内容生成页面截图
- 用户为文档创建视觉化摘要
- 用户想要将网页内容转为可分享的图片
- 用户为特定内容设计海报式页面

**不适用场景：**
- 纯文本摘要（不需要设计页面）
- 不需要截图的情况

## 核心工作流程

### 步骤 1: 读取内容

**读取 URL 内容：**
```bash
# 读取完整内容
WebFetch --url "<URL>" --description "提取文章的主要内容"
# 读取指定部分
WebFetch --url "<URL>" --description "提取文档中第 3-5 部分，关于技术架构的内容"
```

**读取本地文档：**
```bash
# 使用 Read 工具直接读取
Read "<本地文件路径>"
# 使用 WebFetch 读取（需要 file:// 协议）
WebFetch --url "file://<本地文件绝对路径>" --description "提取文档内容"
```

**网络受限处理：** 如果 WebFetch 无法工作，可使用 Read 工具读取本地文件或让用户提供文本内容。

### 步骤 2: 设计页面

使用 frontend-design 设计页面，必须遵守以下原则：

1. **根据内容选择风格**：春节相关用中国红，科技内容用 cyberpunk，学术内容用 minimal
2. **一页完整显示**：所有内容必须在一页内完整显示
3. **禁止使用 tab**：不要使用标签页或折叠面板

```bash
frontend-design --input "<解析后的内容>" --style "modern" --layout "grid" --title "<页面标题>" --no-tabs
```

**设计选项：**
- `--style`: 页面风格（参考 Page Style Options）
- `--layout`: 布局类型（推荐 `grid` 或 `article`）
- `--title`: 页面标题（默认自动提取）
- `--no-tabs`: 强制不使用标签页（必须使用）
- `--colors`: 指定主色调（如春节用 `#FF0000,#FFD700`）

### 步骤 3: 截图保存

使用 agent-browser 访问设计好的页面并截图，**必须保存到当前执行目录**：

**⚠️ **重要：优先使用无头模式**
无头模式在后台运行，不显示浏览器窗口，速度更快且更稳定，完全支持截图功能。

```bash
# 推荐：使用 browser_run_code 的无头模式（推荐）
frontend-design 设计好页面后，使用以下代码截图：

# 示例 1: 直接使用 browser_take_screenshot
browser_take_screenshot --fullPage true --filename "output-screenshot.png"

# 示例 2: 使用 browser_run_code 更灵活的无头模式
async (page) => {
  await page.goto('http://localhost:8080/your-page.html');
  await page.waitForLoadState('networkidle');
  await page.screenshot({
    fullPage: true,
    path: 'output-screenshot.png',
    scale: 'css',
    type: 'png'
  });
}

# 传统 agent-browser 用法（如果需要显示窗口）
agent-browser --url "<页面URL>" --screenshot "full" --output "$(basename <页面URL> .html)-screenshot.png"
```

## 快速参考

| 任务 | 命令模式 |
|------|----------|
| 完整 URL + 内容说明 | `WebFetch → frontend-design → agent-browser` |
| 本地文档 + 自定义标题 | `WebFetch (file:///) → frontend-design --title → agent-browser` |
| 现代风格文章 | `--style "modern" --layout "article"` |
| 极简学术风格 | `--style "minimal" --layout "article"` |
| 海报式展示 | `--style "vintage" --layout "poster"` |

## 设计风格与布局

### 页面风格选项

| 风格 | 特点 | 适用内容 |
|------|------|----------|
| **modern** | 现代简洁，大留白 | 技术文章、新闻、产品展示 |
| **minimal** | 极简风格，纯文字 | 学术文档、研究报告 |
| **corporate** | 商务风格，结构化 | 企业报告、白皮书 |
| **vintage** | 复古风格，纹理装饰 | 历史文档、传统内容、节日海报 |
| **cyberpunk** | 赛博朋克，霓虹灯光 | 编程、黑客文化、网络安全 |
| **playful/toy-like** | 活泼明亮，玩具风格 | 儿童内容、娱乐主题 |

### 布局类型

| 布局 | 特点 | 适用内容 |
|------|------|----------|
| **article** | 传统文章布局 | 长文本内容 |
| **poster** | 海报式布局，强调视觉 | 内容摘要、展示 |
| **grid** | 网格布局，模块化 | 产品展示、列表 |

## 输出规格

### 截图要求
- **尺寸：** 全屏（1920×1080 或更大）
- **格式：** PNG（高质量）或 JPEG（高画质）
- **保存位置：** 必须保存到当前执行目录，不要保存到 `/tmp`

### 常见错误与解决方案

| 问题 | 解决方案 |
|------|----------|
| WebFetch 无法读取内容 | 使用 Read 工具读取本地文件或让用户提供文本内容 |
| frontend-design 使用 tab 布局 | 使用 --no-tabs 选项，确保所有内容全量显示 |
| 截图显示不全 | 使用 --full 选项；设计时避免使用 tab 布局 |

## 设计原则

### 语言要求
- 默认使用中文，所有页面元素都应该使用中文

### 布局要求
- 禁止使用标签页（Tabs）和折叠面板（Accordion）
- 所有内容一次性展示在页面上
- 推荐使用网格布局或文章布局

### 主色调选择

**季节/节日主题：**
- 春节/中国传统文化：中国红（#FF0000 或 #C8102E）
- 圣诞节：红绿搭配
- 秋天/丰收：金黄色（#FFD700）
- 春天/清新：绿色（#008000）

**内容类型主题：**
- 科技/未来：蓝色（#007BFF）、紫色（#9C27B0）
- 学术/专业：米黄色（#F8F4E9）、浅灰（#F5F5F5）
- 商务/正式：深蓝色（#003366）、深灰色（#333333）

### 风格选择指南

| 内容类型 | 推荐风格 | 不推荐风格 |
|---------|---------|-----------|
| 科技/编程/代码 | cyberpunk, modern | playful, soft/pastel |
| 学术/论文/研究 | minimal, editorial | retro-futuristic, brutalist |
| 文化/节日/传统 | vintage, organic | cyberpunk, corporate |
| 娱乐/游戏/儿童 | playful/toy-like, retro-futuristic | corporate, minimal |

## 设计检查清单

在生成截图之前，请确认：
- [ ] 页面是否有标签页？如有，改为全量显示
- [ ] 是否有折叠的内容？如有，展开显示
- [ ] 所有文字是否使用中文？
- [ ] 页面设计是否支持长页面截取？
- [ ] 主色调是否与内容主题匹配？
- [ ] 风格选择是否与内容类型匹配？
