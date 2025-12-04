# ArXiv 引用批量导出工具

**项目名称：** ArXiv Citation Bulk Export Tool

## 简介

**ArXiv 批量导出工具** 是一个 Python 命令行程序，专门用于解决从 ArXiv 搜索结果页面批量导出**引用数据**到 EndNote、BibTeX 或 RIS 等格式的难题。

由于 ArXiv 官方网站本身缺少复杂的检索和批量导出功能，本工具通过解析用户提供的搜索结果 URL，利用 ArXiv 官方 API 高效获取论文的标题、作者、摘要、DOI 等元数据，并将其准确格式化为兼容文献管理软件的纯文本文件。

## 功能特性

* **高级查询支持：** 自动解析 ArXiv **简单搜索**和**高级搜索**结果页面的 URL。

* **多格式导出：** 支持导出为三种主流引用格式，确保高兼容性：

  1. **RIS (.ris)：** 推荐用于 EndNote 导入（遵循严格的 RIS 标签规范，例如 `TAG  - Content`）。

  2. **BibTeX (.bib)：** 适用于 LaTeX 和通用文献管理软件。

  3. **EndNote Tagged (.enw)：** EndNote 专用的纯文本格式。

* **结果过滤：** 自动报告搜索结果总数，并允许用户指定希望导出的文章数量（N 篇，上限 1000 篇）。

* **兼容性优化：** RIS 和 ENW 格式经过特殊优化，以解决导入 ArXiv 预印本时 EndNote 常见的格式和类型识别错误。

## 使用指南

### 1. 安装依赖

本工具仅需要 Python 的 `requests` 库：

```bash
pip install requests
```

### 2\. 获取 ArXiv URL

在浏览器中执行您的搜索（无论是简单搜索还是使用布尔逻辑的高级搜索），然后复制浏览器地址栏中的**完整 URL**。

**高级搜索 URL 示例：**
`https://arxiv.org/search/advanced?terms-0-term=%22UAV%22+OR+%22Drone%22&terms-0-field=all&terms-1-term=%22Reinforcement+Learning%22&terms-1-field=title...`

### 3\. 运行脚本

在终端中执行 `arxiv_batch_export.py` 脚本：

```bash
python arxiv_batch_export.py
```

程序将进入交互模式，引导您完成以下步骤：

**交互式步骤：**

1.  **选择搜索类型：** 选择 `1`（简单搜索）或 `2`（高级搜索）。

2.  **粘贴 URL：** 粘贴您复制的 ArXiv 搜索结果完整 URL。

3.  **选择导出格式：** 选择 `1` (RIS)、`2` (BibTeX) 或 `3` (ENW)。

4.  **输入导出数量：** 输入您希望下载的论文数量（N 篇，最大 1000）。

### 4\. 导入 EndNote

导出成功后，您将获得一个 `.ris`、`.bib` 或 `.enw` 文件。请在 EndNote 中使用以下过滤器设置：

| **导出格式** | **EndNote 导入过滤器 (Import Filter)** |
| :--- | :--- |
| **RIS (.ris)** | **`RefMan RIS`** 或 **`Reference Manager (RIS)`** |
| **BibTeX (.bib)** | **`BibTeX`** |
| **EndNote Tagged (.enw)** | **`EndNote Import`** |

**重要提示：** 导入 RIS 文件时，必须选择 **`RefMan RIS`** 过滤器，这对于正确映射字段（尤其是摘要和 ArXiv ID）至关重要。

## 文件结构

  * `arxiv_batch_export.py`：包含核心逻辑的 Python 脚本。
  * `README.md`：本项目英文版说明文件。
  * `README_ZH.md`：本项目中文版说明文件。
<!-- end list -->
