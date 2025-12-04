好的，这是您项目 `README.md` 的内容，已重新生成在下方的文本框中，方便您复制粘贴：

# ArXiv Citation Bulk Export Tool (ArXiv 引用批量导出工具)

**Project Name (项目名称):** ArXiv Citation Bulk Export Tool / ArXiv 引用批量导出工具

## Introduction (简介)

**ArXiv Bulk Exporter** is a Python command-line utility designed to address the challenge of batch exporting **citation data** from ArXiv search results into formats like EndNote, BibTeX, or RIS.

Since the official ArXiv website does not natively support complex search queries and bulk export functionalities, this tool parses the user-provided search result URL, utilizes the official ArXiv API to retrieve essential metadata (title, authors, abstract, DOI, etc.), and accurately formats it into EndNote-compatible plain text files.

## Features (特性)

* **Supports Advanced Queries (支持复杂检索):** Automatically parses ArXiv **Simple Search** and **Advanced Search** result URLs.
* **Multi-Format Export (多格式导出):** Supports export to three major citation formats with high compatibility:
    1.  **RIS (.ris):** Recommended for EndNote import (follows strict RIS tagging conventions, e.g., `TAG  - Content`).
    2.  **BibTeX (.bib):** Standard format for LaTeX and general citation managers.
    3.  **EndNote Tagged (.enw):** EndNote-specific plain text format.
* **Result Filtering (结果筛选):** Reports the total number of search results and allows the user to specify the number of entries (N) to export (up to 1000).
* **Compatibility Optimized (兼容性优化):** RIS/ENW formats are specially optimized to mitigate common field mapping and reference type errors encountered when importing ArXiv pre-prints into EndNote.

## Usage (使用指南)

### 1. Installation (安装依赖)

The tool requires only the Python `requests` library:

```bash
pip install requests
```

### 2\. Obtaining the ArXiv URL (获取 ArXiv 搜索 URL)

Execute your search on ArXiv (either Simple or Advanced Search) and copy the **complete URL** from your browser's address bar.

**Example URL (Advanced Search):**
`https://arxiv.org/search/advanced?terms-0-term=%22UAV%22+OR+%22Drone%22&terms-0-field=all&terms-1-term=%22Reinforcement+Learning%22&terms-1-field=title...`

### 3\. Running the Script (运行脚本)

Execute `arxiv_batch_export.py` in your terminal:

```bash
python arxiv_batch_export.py
```

The script will launch an interactive prompt:

**Interactive Steps (交互式步骤):**

1.  **Select Search Type:** Choose `1` (Simple Search) or `2` (Advanced Search).
2.  **Paste URL:** Paste your complete ArXiv search result URL.
3.  **Select Export Format:** Choose `1` (RIS), `2` (BibTeX), or `3` (ENW).
4.  **Enter Export Count:** Input the number of papers (N) to download (Max 1000).

### 4\. Importing into EndNote (导入 EndNote)

After successful export, use the following filter settings in EndNote:

| **Export Format** | **Import EndNote Filter** |
| :--- | :--- |
| **RIS (.ris)** | **`RefMan RIS`** or **`Reference Manager (RIS)`** |
| **BibTeX (.bib)** | **`BibTeX`** |
| **EndNote Tagged (.enw)** | **`EndNote Import`** |

**Important Note:** When importing RIS files, selecting the **`RefMan RIS`** filter is crucial for proper field mapping, especially for abstracts and ArXiv IDs.

## File Structure (文件结构)

  * `arxiv_batch_export.py`: The core Python script containing the logic.
  * `README.md`: This documentation file.

<!-- end list -->
