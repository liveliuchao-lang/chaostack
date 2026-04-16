#!/usr/bin/env python3
"""
自动扫描 reports/ 目录，生成索引页 index.html
"""
import os
import re
from datetime import datetime
from pathlib import Path

REPORTS_DIR = "reports"
OUTPUT_INDEX = "index.html"
TEMPLATE_FILE = "templates/index_template.html"

def extract_title(html_path):
    """从 HTML 文件中提取 <title> 标签内容"""
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        match = re.search(r'<title>(.*?)</title>', content)
        return match.group(1) if match else Path(html_path).stem
    except:
        return Path(html_path).stem

def extract_date_from_filename(filename):
    """从文件名提取日期，如 MiniMax-M2.7_2026-04-15.html"""
    date_pattern = r'(\d{4}-\d{2}-\d{2})'
    filename_str = str(filename)
    match = re.search(date_pattern, filename_str)
    if match:
        try:
            return datetime.strptime(match.group(1), '%Y-%m-%d')
        except:
            return datetime.min
    return datetime.min

def scan_reports():
    """扫描 reports/ 目录，获取所有报告信息"""
    reports = []
    reports_path = Path(REPORTS_DIR)
    
    if not reports_path.exists():
        return reports
    
    for html_file in reports_path.glob("*.html"):
        title = extract_title(html_file)
        date = extract_date_from_filename(html_file)
        file_path = html_file.name
        # 按日期排序，最新的在前
        reports.append({
            'title': title,
            'date': date,
            'file': file_path,
            'path': f"reports/{file_path}"
        })
    
    # 按日期降序排列
    reports.sort(key=lambda x: x['date'], reverse=True)
    return reports

def generate_index_html(reports):
    """生成 index.html 内容"""
    with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # 生成卡片 HTML
    cards_html = ""
    for report in reports:
        date_str = report['date'].strftime('%Y-%m-%d') if report['date'] != datetime.min else "未知日期"
        card = f"""
        <a href="{report['path']}" class="card">
            <div class="card-title">{report['title']}</div>
            <div class="card-meta">{date_str} · {report['file']}</div>
        </a>
        """
        cards_html += card
    
    # 替换模板占位符
    html = template.replace("{{REPORTS_CARDS}}", cards_html)
    html = html.replace("{{REPORT_COUNT}}", str(len(reports)))
    
    # 写入 index.html
    with open(OUTPUT_INDEX, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Generated {OUTPUT_INDEX} with {len(reports)} reports")

if __name__ == "__main__":
    reports = scan_reports()
    generate_index_html(reports)