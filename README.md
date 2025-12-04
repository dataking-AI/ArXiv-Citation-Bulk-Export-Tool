# ArXiv Citation Bulk Export Tool

**Project Name:** ArXiv Citation Bulk Export Tool

## Introduction

The **ArXiv Bulk Exporter** is a Python command-line utility designed to solve the challenge of batch exporting **citation data** from ArXiv search result pages into formats compatible with citation managers like EndNote, BibTeX, and RIS.

Since the official ArXiv website does not natively support complex search queries and bulk export functionalities, this tool works by parsing the user-provided search result URL, utilizing the official ArXiv API to retrieve essential metadata (title, authors, abstract, DOI, etc.), and accurately formatting it into EndNote-compatible plain text files.

## Features

* **Advanced Query Support:** Automatically parses ArXiv **Simple Search** and **Advanced Search** result URLs.

* **Multi-Format Export:** Supports export to three major citation formats with high compatibility:

  1. **RIS (.ris):** Recommended for EndNote import (follows strict RIS tagging conventions, e.g., `TAG  - Content`).

  2. **BibTeX (.bib):** Standard format for LaTeX and general citation managers.

  3. **EndNote Tagged (.enw):** EndNote-specific plain text format.

* **Result Filtering:** Reports the total number of search results and allows the user to specify the number of entries (N) to export (up to 1000).

* **Compatibility Optimized:** RIS/ENW formats are specially optimized to mitigate common field mapping and reference type errors encountered when importing ArXiv pre-prints into EndNote.

## Usage

### 1. Installation

The tool requires only the Python `requests` library:

```bash
pip install requests
```

### 2\. Obtaining the ArXiv URL

Execute your search on ArXiv (either Simple or Advanced Search) and copy the **complete URL** from your browser's address bar.

**Example URL (Advanced Search):**
`https://arxiv.org/search/advanced?terms-0-term=%22UAV%22+OR+%22Drone%22&terms-0-field=all&terms-1-term=%22Reinforcement+Learning%22&terms-1-field=title...`

### 3\. Running the Script

Execute `arxiv_batch_export.py` in your terminal:

```bash
python arxiv_batch_export.py
```

The script will launch an interactive prompt to guide you through the process:

**Interactive Steps:**

1.  **Select Search Type:** Choose `1` (Simple Search) or `2` (Advanced Search).

2.  **Paste URL:** Paste your complete ArXiv search result URL.

3.  **Select Export Format:** Choose `1` (RIS), `2` (BibTeX), or `3` (ENW).

4.  **Enter Export Count:** Input the number of papers (N) to download (Max 1000).

### 4\. Importing into EndNote

After successful export, use the following filter settings in EndNote:

| **Export Format** | **Import EndNote Filter** |
| :--- | :--- |
| **RIS (.ris)** | **`RefMan RIS`** or **`Reference Manager (RIS)`** |
| **BibTeX (.bib)** | **`BibTeX`** |
| **EndNote Tagged (.enw)** | **`EndNote Import`** |

**Important Note:** When importing RIS files, selecting the **`RefMan RIS`** filter is crucial for proper field mapping, especially for abstracts and ArXiv IDs.

## File Structure

  * `arxiv_batch_export.py`: The core Python script containing the logic.
  * `README.md`: The English version of the project description document.
  * `README_ZH.md`: The Chinese version of the project description document.
<!-- end list -->
