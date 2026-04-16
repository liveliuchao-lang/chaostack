#!/usr/bin/env python3
"""
自动扫描 reports/ 目录，生成索引页 index.html
"""
import os
import sys
import re
from datetime import datetime
from pathlib import Path

# 获取脚本所在目录的绝对路径
SCRIPT_DIR = Path(__file__).parent.resolve()
REPO_DIR = SCRIPT_DIR.parent
REPORTS_DIR = REPO_DIR / "reports"
OUTPUT_INDEX = REPO_DIR / "index.html"
TEMPLATE_FILE = REPO_DIR / "templates" / "index_template.html"

def log(msg):
    """打印日志到 stderr"""
    print(msg, file=sys.stderr)

def extract_title(html_path):
    """从 HTML 文件中提取 <title> 标签内容"""
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        match = re.search(r'<title>(.*?)</title>', content)
        return match.group(1) if match else html_path.stem
    except Exception as e:
        log(f"Error reading title from {html_path}: {e}")
        return html_path.stem

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
    
    log(f"Scanning reports directory: {REPORTS_DIR}")
    log(f"Reports dir exists: {REPORTS_DIR.exists()}")
    
    if not REPORTS_DIR.exists():
        log(f"ERROR: Reports directory does not exist: {REPORTS_DIR}")
        return reports
    
    html_files = list(REPORTS_DIR.glob("*.html"))
    log(f"Found {len(html_files)} HTML files")
    
    for html_file in html_files:
        title = extract_title(html_file)
        date = extract_date_from_filename(html_file.name)
        file_path = html_file.name
        reports.append({
            'title': title,
            'date': date,
            'file': file_path,
            'path': f"reports/{file_path}"
        })
        log(f"  Report: {file_path} -> {title} ({date})")
    
    # 按日期降序排列
    reports.sort(key=lambda x: x['date'], reverse=True)
    return reports

def generate_index_html(reports):
    """生成 index.html 内容"""
    log(f"Template file: {TEMPLATE_FILE}")
    log(f"Template exists: {TEMPLATE_FILE.exists()}")
    
    if not TEMPLATE_FILE.exists():
        log(f"ERROR: Template file does not exist: {TEMPLATE_FILE}")
        sys.exit(1)
    
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
    
    # 如果没有报告，显示空状态
    if not reports:
        empty_state = '''
        <div class="empty-state">
            <p>暂无报告</p>
        </div>'''
        template = template.replace('<div class="empty-state" style="display: none;">', f'<div class="empty-state">')
        template = template.replace('style="display: none;"', '')
    
    # 替换模板占位符
    html = template.replace("{{REPORTS_CARDS}}", cards_html)
    html = html.replace("{{REPORT_COUNT}}", str(len(reports)))
    
    # 写入 index.html
    with open(OUTPUT_INDEX, 'w', encoding='utf-8') as f:
        f.write(html)
    
    log(f"Generated {OUTPUT_INDEX} with {len(reports)} reports")

if __name__ == "__main__":
    log(f"Script directory: {SCRIPT_DIR}")
    log(f"Repo directory: {REPO_DIR}")
    log(f"Current working directory: {os.getcwd()}")
    
    reports = scan_reports()
    generate_index_html(reports)
    
    log("Script completed successfully")