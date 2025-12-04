import requests
import xml.etree.ElementTree as ET
import re
import os
import sys
from datetime import datetime
from urllib.parse import urlparse, parse_qs, unquote

# ==============================================================================
# 配置文件
# ==============================================================================

# 设置命名空间，用于解析 arXiv API 返回的 XML
NS = {
    'atom': 'http://www.w3.org/2005/Atom',
    'arxiv': 'http://arxiv.org/schemas/atom',
    'opensearch': 'http://a9.com/-/spec/opensearch/1.1/'
}

# ArXiv 网页字段名到 API 字段名的映射
API_FIELD_MAP = {
    'title': 'ti',
    'author': 'au',
    'abstract': 'abs',
    'comments': 'comm',
    'journal_ref': 'jr',
    'acm_class': 'acm',
    'msc_class': 'msc',
    'report_num': 'rpt',
    'paper_id': 'id',
    'doi': 'doi',
    'orcid': 'orcid',
    'all': 'all' # 默认全部字段
}

API_BASE_URL = "http://export.arxiv.org/api/query"

# ==============================================================================
# 辅助函数：数据安全提取与格式化
# ==============================================================================

def safe_get_element(element, xpath, default=''):
    """安全地从 XML 元素中获取指定 XPath 的文本内容。"""
    try:
        if 'atom:summary' in xpath:
             # 确保摘要内容没有换行符或多余空格
             text = element.find(xpath, NS).text
             # 清理摘要中的 LaTeX/特殊字符，并用空格连接
             clean_text = re.sub(r'[\\{}$]', '', text) 
             return ' '.join(clean_text.split()) if text is not None else default
        
        return element.find(xpath, NS).text.strip()
    except AttributeError:
        return default

def format_authors_for_bibtex(authors_list):
    """将作者列表格式化为 BibTeX 所需的 'Lastname, Firstname and ...' 格式。"""
    if not authors_list: return ""
    formatted_authors = []
    for author_name in authors_list:
        # 尽量转换为 Lastname, Firstname 格式
        name_parts = author_name.split()
        if len(name_parts) > 1:
            last_name = name_parts[-1]
            first_names = " ".join(name_parts[:-1])
            formatted_authors.append(f"{last_name}, {first_names}")
        else:
            formatted_authors.append(author_name)
    return ' and '.join(formatted_authors)

def generate_bibtex_key(title, year):
    """根据标题和年份生成一个唯一的 BibTeX 引用键 (Key)。"""
    words = re.findall(r'\b[a-zA-Z0-9]+\b', title)
    key_parts = words[:2] if words else ['arxiv']
    key = "".join(key_parts).lower() + str(year)
    return key[:25] 

def extract_paper_data(entry):
    """从单个 XML entry 中提取所有需要的元数据。"""
    
    title = safe_get_element(entry, 'atom:title')
    arxiv_id_url = safe_get_element(entry, 'atom:id')
    summary = safe_get_element(entry, 'atom:summary')
    published_date_str = safe_get_element(entry, 'atom:published')
    
    doi = safe_get_element(entry, "arxiv:doi")
    
    arxiv_id_match = re.search(r'(\d{4}\.\d{5}v\d+|\d{4}\.\d{5})', arxiv_id_url)
    arxiv_id = arxiv_id_match.group(0) if arxiv_id_match else 'unknown'
    arxiv_url = f"https://arxiv.org/abs/{arxiv_id}"

    authors = [author.find('atom:name', NS).text.strip()
               for author in entry.findall('atom:author', NS)]

    # 尝试提取 primary category (用于 BibTeX 的 primaryClass)
    primary_category_tag = entry.find('arxiv:primary_category', NS)
    primary_category = primary_category_tag.get('{http://arxiv.org/schemas/atom}term') if primary_category_tag is not None else ''
    
    year = ''
    submission_date = ''
    ris_date = ''
    enw_date_8 = ''
    if published_date_str:
        try:
            dt = datetime.strptime(published_date_str, '%Y-%m-%dT%H:%M:%SZ')
            year = str(dt.year)
            # RIS/ENW 需要 YYYY/MM/DD 或 YYYY/MM/DD/ 格式。这里使用带末尾斜杠的 ScienceDirect 风格。
            submission_date = dt.strftime('%Y/%m/%d/') 
            ris_date = dt.strftime('%Y/%m/01/') 
            enw_date_8 = dt.strftime('%B %d, %Y') # ENW %8 Date (Month Day, Year)
        except ValueError:
            pass

    return {
        'title': title,
        'summary': summary,
        'doi': doi,
        'arxiv_id': arxiv_id,
        'arxiv_url': arxiv_url,
        'authors': authors,
        'year': year,
        'submission_date': submission_date,
        'ris_date': ris_date,
        'primary_category': primary_category,
        'enw_date_8': enw_date_8,
    }

# ==============================================================================
# 格式化函数：BibTeX, RIS, ENW
# ==============================================================================

def format_to_bibtex(data):
    """将数据格式化为 BibTeX 字符串。"""
    bibkey = generate_bibtex_key(data['title'], data['year'])
    bibtex_authors = format_authors_for_bibtex(data['authors'])
    
    # 确保摘要中的特殊字符被转义或移除（已在 safe_get_element 中进行初步清理）
    summary = data['summary'].replace('{', '\\{').replace('}', '\\}')
    
    # 构建兼容的 BibTeX 字段
    bibtex_body = f"""
title = {{{{{data['title']}}}}},
author = {{{bibtex_authors}}},
journal = {{arXiv}},
archivePrefix = {{arXiv}},
eprint = {{{data['arxiv_id']}}},"""
    
    if data['primary_category']:
        bibtex_body += f"\n  primaryClass = {{{data['primary_category']}}},"

    if data['doi']:
        bibtex_body += f"\n  doi = {{{data['doi']}}},"
        
    bibtex_body += f"""
year = {{{data['year']}}},
abstract = {{{{{summary}}}}}
"""

    bibtex_entry = f"""
@article{{{bibkey},{bibtex_body}
}}
"""
    return bibtex_entry.strip()

def format_to_ris(data):
    """将数据格式化为 RIS 字符串。 (TY - JOUR 兼容 ScienceDirect 风格)"""
    ris_entry = []
    
    # 关键点：RIS 标签后使用两个空格 + 横杠 + 一个空格 (TAG  - 内容)
    
    # TY - Reference Type: JOUR (Journal Article, 兼容性最佳)
    ris_entry.append("TY  - JOUR")
    
    # T1 - Primary Title
    ris_entry.append(f"T1  - {data['title']}")
    
    # AU - Author (RIS 每个作者一行)
    for author_name in data['authors']:
        ris_entry.append(f"AU  - {author_name}")
        
    # AB - Abstract (摘要)
    ris_entry.append(f"AB  - {data['summary']}")
    
    # PY - Publication Year
    if data['year']:
        ris_entry.append(f"PY  - {data['year']}")
        
    # DA - Date (RIS 日期格式, YYYY/MM/DD/ 风格)
    if data['submission_date']:
         ris_entry.append(f"DA  - {data['submission_date']}")
        
    # DO - DOI
    if data['doi']:
        ris_entry.append(f"DO  - {data['doi']}")
        
    # UR - URL (官方链接)
    ris_entry.append(f"UR  - {data['arxiv_url']}")
    
    # JO - Journal (设置为 arXiv)
    ris_entry.append(f"JO  - arXiv")

    # PB - Publisher (设置为 arXiv)
    ris_entry.append(f"PB  - arXiv")

    # KW - Keywords (使用 primary category)
    if data['primary_category']:
        ris_entry.append(f"KW  - {data['primary_category']}")
        
    # EP - Eprint ID (存放 ArXiv ID，作为页面范围)
    ris_entry.append(f"EP  - {data['arxiv_id']}")
    
    # 记录结束
    ris_entry.append("ER  - ")
    
    return '\n'.join(ris_entry)

def format_to_enw(data):
    """将数据格式化为 EndNote Tagged 格式 (.enw)。"""
    enw_entry = []
    
    # %0 - Reference Type: Journal Article (匹配用户模板，使用 %0 Journal Article)
    enw_entry.append("%0 Journal Article")
    
    # %T - Title
    enw_entry.append(f"%T {data['title']}")
    
    # %A - Author (ENW 每个作者一行)
    for author_name in data['authors']:
        enw_entry.append(f"%A {author_name}")
        
    # %Y - Year (新的年份字段)
    if data['year']:
        enw_entry.append(f"%Y {data['year']}")
        
    # %8 - Date (EndNote 标准日期格式)
    if data['enw_date_8']:
         enw_entry.append(f"%8 {data['enw_date_8']}")

    # %J - Journal Name
    enw_entry.append("%J arXiv")
    
    # %K - Keywords (使用 arXiv ID/Category 作为关键词)
    enw_entry.append(f"%K arXiv; {data['primary_category']}")

    # %R - DOI
    if data['doi']:
        enw_entry.append(f"%R {data['doi']}")
        
    # %Z - Notes (用于存放 ArXiv ID)
    enw_entry.append(f"%Z arXiv:{data['arxiv_id']}")
    
    # %U - URL
    enw_entry.append(f"%U {data['arxiv_url']}")
    
    # %X - Abstract (摘要)
    enw_entry.append(f"%X {data['summary']}")
    
    # 记录结束 (空行分隔)
    
    return '\n'.join(enw_entry)

# ==============================================================================
# 解析主函数
# ==============================================================================

def parse_arxiv_xml(xml_content, formatter):
    """解析 API XML 并使用指定的格式化函数进行转换。"""
    root = ET.fromstring(xml_content)
    formatted_entries = []

    error_tag = root.find('atom:entry/atom:title', NS)
    if error_tag is not None and "Error" in error_tag.text:
         raise Exception(f"API 返回错误：{error_tag.text.strip()}")
    
    for entry in root.findall('atom:entry', NS):
        # 1. 提取数据
        data = extract_paper_data(entry)
        
        # 2. 格式化
        formatted_entry = formatter(data)
        
        # 3. 添加到列表
        formatted_entries.append(formatted_entry)

    # RIS/BibTeX/ENW 之间使用空行或换行符分隔
    separator = '\n\n'
    return separator.join(formatted_entries)

# ==============================================================================
# URL 解析函数 (保持不变)
# ==============================================================================

def parse_simple_search_url(url):
    """解析简单搜索 URL，提取 query 和 searchtype 参数。"""
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    
    query_list = query_params.get('query', [])
    searchtype_list = query_params.get('searchtype', [])
    
    if not query_list or not searchtype_list:
        raise ValueError("URL 中未找到 'query' 或 'searchtype' 参数。")

    raw_query = unquote(query_list[0])
    search_field = searchtype_list[0]
    
    # 转换字段名，并构建 API 查询字符串
    api_field = API_FIELD_MAP.get(search_field, 'all')
    api_query = f'{api_field}:({raw_query})'
    
    return api_query

def parse_advanced_search_url(url):
    """解析高级搜索 URL 中的所有 'terms' 参数，并构建 API 要求的复杂查询字符串。"""
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    
    complex_query_parts = []
    i = 0
    while True:
        term_key = f'terms-{i}-term'
        field_key = f'terms-{i}-field'
        operator_key = f'terms-{i}-operator'
        
        if term_key not in query_params:
            break
            
        term_value_list = query_params.get(term_key)
        field_value_list = query_params.get(field_key)
        operator_list = query_params.get(operator_key)
        
        if not term_value_list or not field_value_list:
            i += 1
            continue

        term = unquote(term_value_list[0]).strip()
        field = field_value_list[0].strip()
        
        api_field = API_FIELD_MAP.get(field, 'all')
        
        # 移除 '+' 并将整个 OR 组视为一个查询单元
        term_clean = term.replace('+', ' ')
        query_part = f'({api_field}:({term_clean}))'
        
        # 添加布尔操作符 (用于连接上一个和当前查询部分)
        if i > 0 and operator_list:
            operator = operator_list[0].upper()
            complex_query_parts.append(operator)

        complex_query_parts.append(query_part)
        i += 1
        
    final_api_query = ' '.join(complex_query_parts)
    
    if not final_api_query:
        raise ValueError("URL 中未找到有效的 'terms-N-term' 参数。")
        
    return final_api_query


def build_api_query(url, search_type):
    """根据用户选择的搜索类型调用相应的解析函数。"""
    if search_type == 1:
        return parse_simple_search_url(url)
    elif search_type == 2:
        return parse_advanced_search_url(url)
    else:
        raise ValueError("无效的搜索类型选择。")

# ==============================================================================
# 结果统计与 API 调用
# ==============================================================================

def get_total_results(api_query):
    """调用 API 获取查询结果总数。"""
    print("  > 正在连接 ArXiv API 统计结果数量...")
    params = {
        'search_query': api_query,
        'start': 0,
        'max_results': 1 # 只请求 1 条结果以获取总数
    }
    
    try:
        response = requests.get(API_BASE_URL, params=params, timeout=15)
        response.raise_for_status()
        
        root = ET.fromstring(response.text)
        
        # 提取总结果数
        total_results_tag = root.find('opensearch:totalResults', NS)
        if total_results_tag is not None:
            return int(total_results_tag.text)
        
        # 如果找不到 opensearch:totalResults，检查是否有 entry，至少返回 1
        if root.find('atom:entry', NS) is not None:
             return 1
        return 0

    except Exception as e:
        print(f"警告：无法获取结果总数。原因：{e}")
        return 0

# ==============================================================================
# 最终执行函数
# ==============================================================================

def run_batch_export(api_query, max_results, output_format, output_dir='.'):
    """根据 API 查询、最大结果数和导出格式执行最终导出。"""
    
    FORMAT_MAP = {
        1: ('ris', format_to_ris, "RIS"),
        2: ('bib', format_to_bibtex, "BibTeX"),
        3: ('enw', format_to_enw, "EndNote Tagged (ENW)")
    }
    
    extension, formatter, format_name = FORMAT_MAP[output_format]

    API_PARAMS = {
        'search_query': api_query,
        'start': 0,
        'max_results': max_results,
        'sortBy': 'submittedDate', 
        'sortOrder': 'descending'
    }

    print(f"\n[1/3] 正在发送 API 请求，获取前 {max_results} 篇论文数据...")
    
    try:
        response = requests.get(API_BASE_URL, params=API_PARAMS, timeout=45) 
        response.raise_for_status() 
    except requests.exceptions.RequestException as e:
        print(f"错误：API 请求失败或超时。原因：{e}")
        return

    try:
        print(f"[2/3] 成功获取数据，正在解析并转换为 {format_name} 格式...")
        # 调用多格式解析主函数
        output_content = parse_arxiv_xml(response.text, formatter)
    except Exception as e:
        print(f"解析错误：{e}")
        return
        
    if not output_content:
        print("未找到任何论文或 XML 解析失败。")
        return

    # 5. 保存到文件
    filename = f"arxiv_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{extension}"
    output_path = os.path.join(output_dir, filename)

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output_content)
        
        # 统计结果数量 (简单计数 TY/@@article/%0)
        if extension == 'ris':
            count_tag = 'TY - JOUR' # RIS 改为 JOUR
        elif extension == 'enw':
            # 统计 %0 Journal Article (ENW 更改为 Journal Article)
            count_tag = '%0 Journal Article'
        else: # bib
            count_tag = '@article'
            
        count = output_content.count(count_tag.split(' ')[0]) # 计数时只用TY/@article/%0
        print(f"\n[3/3] 导出成功！")
        print(f"  > 成功导出了 {count} 篇论文的 {format_name} 记录。")
        print(f"  > 文件已保存到: {os.path.abspath(output_path)}")
        
    except IOError as e:
        print(f"错误：无法写入文件。原因：{e}")

# ==============================================================================
# 交互式主程序
# ==============================================================================

def main():
    """交互式主程序，引导用户完成搜索和导出流程。"""
    print("\n===============================================")
    print("  ArXiv 批量多格式导出工具 (支持 EndNote/BibTeX)")
    print("===============================================")
    
    # 1. 选择搜索类型
    while True:
        try:
            choice = input("请选择您的搜索 URL 类型 (1: 简单搜索, 2: 高级搜索): ")
            search_type = int(choice)
            if search_type in [1, 2]:
                break
            else:
                print("无效的选择，请输入 1 或 2。")
        except ValueError:
            print("输入错误，请确保输入的是数字。")
            
    # 获取 URL
    arxiv_url = input("请粘贴您在 ArXiv 搜索后跳转的完整 URL: ")
    output_dir = input(f"请输入保存文件的目录 (留空则为当前目录: .): ") or '.'
    
    try:
        api_query = build_api_query(arxiv_url, search_type)
        print("\n[✔] URL 解析成功。")
    except ValueError as e:
        print(f"致命错误：URL 解析失败。原因：{e}")
        print("请检查您粘贴的 URL 是否与您选择的搜索类型匹配。")
        sys.exit(1)

    # 统计结果总数
    total_results = get_total_results(api_query)
    if total_results == 0:
        print("[✖] 搜索结果总数为 0，无法导出。请检查您的检索式。")
        sys.exit(1)
        
    print(f"\n[i] 搜索结果总计：{total_results} 篇论文。")
    
    # 2. 选择导出格式
    while True:
        try:
            print("\n请选择导出格式：")
            print("  1: RIS (.ris) - 推荐导入 EndNote")
            print("  2: BibTeX (.bib) - 常用LaTeX/通用")
            print("  3: EndNote Tagged (.enw) - EndNote 专用")
            format_choice = input("请输入格式编号 (1, 2, 或 3): ")
            output_format = int(format_choice)
            if output_format in [1, 2, 3]:
                break
            else:
                print("无效的选择，请输入 1, 2, 或 3。")
        except ValueError:
            print("输入错误，请确保输入的是数字。")

    # 3. 询问导出数量
    while True:
        try:
            print(f"注意：ArXiv API 默认最大只能返回 1000 条记录。")
            max_input = input(f"请输入要爬取的前 N 篇论文数量 (最大 {total_results}，上限 1000): ")
            max_results = int(max_input)
            
            if max_results <= 0:
                print("数量必须大于 0。")
            elif max_results > min(total_results, 1000):
                print(f"数量超出范围。将自动设置为 {min(total_results, 1000)}。")
                max_results = min(total_results, 1000)
            break
        except ValueError:
            print("输入错误，请确保输入的是数字。")
            
    # 执行导出
    run_batch_export(api_query, max_results, output_format, output_dir)


if __name__ == "__main__":
    # 检查 requests 库
    try:
        import requests
    except ImportError:
        print("错误：缺少 'requests' 库。请运行 'pip install requests' 进行安装。")
        sys.exit(1)
    
    main()