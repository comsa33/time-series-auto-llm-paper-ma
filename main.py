import os
import re
import glob
import yaml
import html
from datetime import datetime
import shutil
import subprocess
import traceback
from pathlib import Path

# Pillow를 통한 이미지 생성 추가
try:
    from PIL import Image, ImageDraw
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# 기본 경로 설정
paper_dir = 'paper'
results_dir = 'research_results'
output_dir = 'output'
plots_dir = os.path.join(results_dir, 'analysis_plots')

# 출력 디렉토리 생성
os.makedirs(output_dir, exist_ok=True)
markdown_file = os.path.join(output_dir, 'thesis.md')
pdf_file = os.path.join(output_dir, 'thesis.pdf')
html_file = os.path.join(output_dir, 'thesis.html')

# 파일 내용 읽기 함수
def read_file_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        print(f"파일 읽기 오류 {file_path}: {e}")
        return ""

# 이미지 처리 함수
def prepare_images():
    """원본 이미지 파일을 output/images로 복사하는 함수"""
    images_output_dir = os.path.join(output_dir, 'images')
    os.makedirs(images_output_dir, exist_ok=True)
    
    # 복사할 이미지 파일 목록
    image_filenames = [
        "model_performance_comparison_plots_pm25.png",
        "model_forecast_comparision_plot_pm25.png",
        "model_forecast_comparision_plot_pm25_zoomin.png",
        "ai_tuned_lstm_forecast_comparision_plot_pm25.png",
        "timeseries_decomposition_plot_pm25.png",
        "acf_pacf_plot_pm25.png",
        "timeseries_corelation_heatmap_plot.png",
        "timeseries_granger_plot_pm10_to_pm25.png"
    ]
    
    # 원본 이미지 경로
    original_plots_dir = plots_dir
    
    copied_images = []
    
    try:
        # 먼저 plots_dir에서 모든 PNG 파일을 찾아서 복사
        all_plot_images = glob.glob(os.path.join(original_plots_dir, "*.png"))
        for src_path in all_plot_images:
            filename = os.path.basename(src_path)
            dst_path = os.path.join(images_output_dir, filename)
            shutil.copy2(src_path, dst_path)
            copied_images.append(dst_path)
            print(f"이미지 복사: {src_path} -> {dst_path}")
        
        # 지정된 이미지들이 없으면 더미 이미지 생성
        for filename in image_filenames:
            dst_path = os.path.join(images_output_dir, filename)
            if not os.path.exists(dst_path):
                print(f"지정된 이미지 파일 없음: {filename}, 더미 생성")
                if PIL_AVAILABLE:
                    img = Image.new('RGB', (800, 600), color=(255, 255, 255))
                    draw = ImageDraw.Draw(img)
                    draw.text((50, 300), f"Image not found: {filename}", fill=(0, 0, 0))
                    img.save(dst_path, 'PNG')
                    copied_images.append(dst_path)
                else:
                    # PIL이 없는 경우 최소한의 PNG 파일 생성
                    with open(dst_path, 'wb') as f:
                        f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\r\x49\x48\x44\x52\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0bIDAT\x08\xd7c\xf8\xff\xff?\x00\x05\xfe\x02\xfe\xdc\xcc\x59\xe7\x00\x00\x00\x00IEND\xaeB`\x82')
                    copied_images.append(dst_path)
        
        print(f"\n이미지 처리 완료: {len(copied_images)}개 이미지 준비됨")
        
    except Exception as e:
        print(f"이미지 처리 중 오류: {e}")
        traceback.print_exc()
    
    return images_output_dir

# 논문 각 섹션 내용 수집
def collect_sections():
    sections = {}
    
    # 타이틀
    title_file = os.path.join(paper_dir, '0_overview', '0_0_title.md')
    if os.path.exists(title_file):
        sections['title'] = read_file_content(title_file)
    else:
        sections['title'] = "생성형 인공지능 기반 시계열 예측 자동화 연구"
    
    # 저자 정보
    author_file = os.path.join(paper_dir, '0_overview', '0_1_author.md')
    if os.path.exists(author_file):
        sections['author'] = read_file_content(author_file)
    else:
        sections['author'] = "이름: 이루오\n학번: 2426527021\n전임교수: 오태연 교수\n전공: AI 빅데이터 석사과정\n학교: aSSIST(서울과학종합대학원)"
    
    # 초록
    abstract_file = os.path.join(paper_dir, '0_overview', '0_3_abstract.md')
    if os.path.exists(abstract_file):
        sections['abstract'] = read_file_content(abstract_file).replace('# 초록', '').replace('초록', '').strip()
    else:
        sections['abstract'] = "초록 내용이 없습니다."
    
    # 서론
    intro_file = os.path.join(paper_dir, '1_introduction', '1_introduction.md')
    if os.path.exists(intro_file):
        sections['introduction'] = read_file_content(intro_file).replace('# 1. 서론', '').replace('1. 서론', '').strip()
    else:
        sections['introduction'] = "서론 내용이 없습니다."
    
    # 이론적 배경
    background_files = sorted(glob.glob(os.path.join(paper_dir, '2_background', '*.md')))
    background_content = "\n\n".join([read_file_content(f) for f in background_files])
    sections['background'] = re.sub(r'^# ?2\. 이론적 배경.*$', '', background_content, flags=re.MULTILINE).strip()
    
    # 연구 방법
    method_files = sorted(glob.glob(os.path.join(paper_dir, '3_method', '*.md')))
    method_content = "\n\n".join([read_file_content(f) for f in method_files])
    sections['method'] = re.sub(r'^# ?3\. 연구 방법.*$', '', method_content, flags=re.MULTILINE).strip()
    
    # 실험 및 결과
    results_files = sorted(glob.glob(os.path.join(paper_dir, '4_experiments_and_results', '*.md')))
    results_content = "\n\n".join([read_file_content(f) for f in results_files])
    sections['results'] = re.sub(r'^# ?4\. 실험 및 결과.*$', '', results_content, flags=re.MULTILINE).strip()
    
    # 결론
    conclusion_file = os.path.join(paper_dir, '5_conclusion', '5_conclusion.md')
    if os.path.exists(conclusion_file):
        sections['conclusion'] = read_file_content(conclusion_file).replace('# 5. 결론 및 향후 연구', '').replace('5. 결론 및 향후 연구', '').strip()
    else:
        sections['conclusion'] = "결론 내용이 없습니다."
    
    # 참고문헌
    reference_file = os.path.join(paper_dir, '6_reference', '6_reference.md')
    if os.path.exists(reference_file):
        sections['references'] = read_file_content(reference_file).replace('# 6. 참고 문헌', '').replace('6. 참고 문헌', '').strip()
    else:
        sections['references'] = "참고문헌 내용이 없습니다."
    
    return sections

# 마크다운 이미지 경로 수정 함수
def fix_image_paths(content, image_dir):
    """마크다운 내 이미지 경로를 수정하는 함수"""
    # 이미지 디렉토리 절대 경로
    image_dir_abs = os.path.abspath(image_dir).replace('\\', '/')
    
    # 다양한 이미지 패턴에 대한 정규식 처리
    patterns = [
        # GitHub 경로
        (r'!\[(.*?)\]\((https://github\.com/.*?/blob/.*?/research_results/analysis_plots/(.*?))\)', 
         r'![\1](images/\3)'),
        
        # 상대 경로
        (r'!\[(.*?)\]\((.*?/analysis_plots/(.*?))\)', 
         r'![\1](images/\3)'),
        
        # 이미 images/ 경로인 경우는 유지
        (r'!\[(.*?)\]\(images/(.*?)\)', 
         r'![\1](images/\2)'),
        
        # 직접 파일명만 있는 경우
        (r'!\[\]\(([^/]+\.png)\)', 
         r'![](images/\1)'),
         
        # 기타 절대 경로
        (r'!\[(.*?)\]\(/.*?/([^/]+\.png)\)', 
         r'![\1](images/\2)')
    ]
    
    updated_content = content
    for pattern, replacement in patterns:
        updated_content = re.sub(pattern, replacement, updated_content)
    
    return updated_content

# 논문 메타데이터 생성
def generate_metadata(sections):
    return {
        'title': sections.get('title', '생성형 인공지능 기반 시계열 예측 자동화 연구'),
        'author': '이루오',
        'date': datetime.now().strftime('%Y년 %m월 %d일'),
        'lang': 'ko',
        'documentclass': 'report',
        'papersize': 'a4',
        'fontsize': '12pt',
        'linestretch': 1.6,
        'mainfont': 'NanumMyeongjo',
        'sansfont': 'NanumGothic',
        'monofont': 'D2Coding',
        'geometry': [
            'top=30mm',
            'bottom=25mm',
            'left=30mm',
            'right=25mm'
        ],
        'colorlinks': True,
        'toccolor': 'Maroon',
        'linkcolor': 'NavyBlue',
        'urlcolor': 'Blue',
        'toc': True,
        'toc-depth': 3,
        'numbersections': True,
        'header-includes': [
            '\\usepackage{kotex}',
            '\\usepackage{setspace}',
            '\\usepackage{titlesec}',
            '\\titleformat{\\chapter}[display]{\\normalfont\\huge\\bfseries}{\\chaptertitlename\\ \\thechapter}{20pt}{\\Huge}',
            '\\usepackage{fancyhdr}',
            '\\pagestyle{fancy}',
            '\\fancyhf{}',
            '\\fancyhead[R]{\\slshape \\leftmark}',
            '\\fancyfoot[C]{\\thepage}',
            '\\renewcommand{\\headrulewidth}{0.4pt}',
            '\\renewcommand{\\footrulewidth}{0.4pt}'
        ]
    }

# 논문 마크다운 생성
def generate_thesis_markdown(sections, images_dir):
    """논문 마크다운 생성 함수"""
    # 이미지 경로 수정
    for key in sections:
        sections[key] = fix_image_paths(sections[key], images_dir)
    
    # 메타데이터
    metadata = generate_metadata(sections)
    
    with open(markdown_file, 'w', encoding='utf-8') as f:
        # YAML 메타데이터
        f.write('---\n')
        yaml.dump(metadata, f, allow_unicode=True, default_flow_style=False)
        f.write('---\n\n')
        
        # 표지
        f.write('\\begin{titlepage}\n')
        f.write('\\begin{center}\n')
        f.write('\\vspace*{2cm}\n\n')
        f.write(f'\\Huge\\textbf{{{sections.get("title", "")}}}\\\\\n\n')
        f.write('\\vspace{1.5cm}\n\n')
        f.write('\\LARGE 석사학위 논문\\\\\n\n')
        f.write('\\vspace{2cm}\n\n')
        
        # 저자 정보 처리
        author_info = sections.get('author', '').split('\n')
        for line in author_info:
            if line.strip():
                parts = line.split(':')
                if len(parts) > 1:
                    f.write(f'\\large {parts[0].strip()}: {parts[1].strip()}\\\\\n')
                else:
                    f.write(f'\\large {line.strip()}\\\\\n')
        
        f.write('\\vspace{3cm}\n\n')
        f.write('\\large\\today\\\\\n\n')
        f.write('\\vspace{2cm}\n\n')
        f.write('\\large aSSIST(서울과학종합대학원)\\\\\n')
        f.write('\\end{center}\n')
        f.write('\\end{titlepage}\n\n')
        
        # 초록 (새 페이지)
        f.write('\\chapter*{초록}\n\\addcontentsline{toc}{chapter}{초록}\n\n')
        f.write(sections.get('abstract', ''))
        f.write('\n\n')
        
        # 목차 페이지
        f.write('\\newpage\n')
        f.write('\\tableofcontents\n')
        f.write('\\newpage\n\n')
        
        # 그림 목차 추가
        f.write('\\listoffigures\n')
        f.write('\\newpage\n\n')
        
        # 표 목차 추가
        f.write('\\listoftables\n')
        f.write('\\newpage\n\n')
        
        # 본문 챕터들
        # 서론
        f.write('\\chapter{서론}\n\n')
        f.write(sections.get('introduction', ''))
        f.write('\n\n')
        
        # 이론적 배경
        f.write('\\chapter{이론적 배경}\n\n')
        f.write(sections.get('background', ''))
        f.write('\n\n')
        
        # 연구 방법
        f.write('\\chapter{연구 방법}\n\n')
        f.write(sections.get('method', ''))
        f.write('\n\n')
        
        # 실험 및 결과
        f.write('\\chapter{실험 및 결과}\n\n')
        f.write(sections.get('results', ''))
        f.write('\n\n')
        
        # 결론
        f.write('\\chapter{결론 및 향후 연구}\n\n')
        f.write(sections.get('conclusion', ''))
        f.write('\n\n')
        
        # 참고문헌
        f.write('\\chapter*{참고 문헌}\n\\addcontentsline{toc}{chapter}{참고 문헌}\n\n')
        f.write(sections.get('references', ''))
    
    print(f"마크다운 파일이 생성되었습니다: {markdown_file}")
    return markdown_file

# HTML 변환 함수 (개선)
def convert_to_thesis_html(markdown_file, html_file):
    """마크다운 파일을 학위 논문 형식의 HTML로 변환하는 함수"""
    try:
        # 이미지 디렉토리 경로 설정
        images_dir = os.path.join(output_dir, 'images')
        
        # 논문 스타일 CSS
        thesis_css = """
        @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;700&family=Noto+Sans+KR:wght@400;700&family=D2Coding:wght@400;700&display=swap');
        
        * {
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Noto Serif KR', serif;
            font-size: 12pt;
            line-height: 1.8;
            max-width: 210mm; /* A4 width */
            margin: 0 auto;
            padding: 0;
            color: #333;
            background-color: #fff;
        }
        
        .container {
            padding: 25mm 30mm; /* A4 margins */
        }
        
        /* 논문 타이틀 페이지 */
        .title-page {
            height: 297mm; /* A4 height */
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            align-items: center;
            text-align: center;
            padding: 30mm 0;
            page-break-after: always;
        }
        
        .title-content {
            margin-top: 50mm;
        }
        
        .title-page h1 {
            font-size: 24pt;
            font-weight: bold;
            margin-bottom: 30mm;
        }
        
        .degree-text {
            font-size: 16pt;
            margin-bottom: 40mm;
        }
        
        .author-info {
            font-size: 14pt;
            line-height: 2;
            margin-bottom: 40mm;
        }
        
        .date-university {
            margin-top: auto;
            font-size: 14pt;
        }
        
        /* 초록 페이지 */
        .abstract-page {
            page-break-after: always;
        }
        
        .abstract-page h2 {
            font-size: 18pt;
            text-align: center;
            margin-bottom: 20mm;
        }
        
        /* 목차 페이지 */
        .toc-page {
            page-break-after: always;
        }
        
        .toc-title {
            font-size: 18pt;
            text-align: center;
            margin-bottom: 15mm;
        }
        
        .toc-list {
            list-style-type: none;
            padding-left: 0;
        }
        
        .toc-list ul {
            list-style-type: none;
        }
        
        .toc-h1 {
            font-weight: bold;
            margin-top: 10mm;
            margin-bottom: 5mm;
        }
        
        .toc-h2 {
            padding-left: 10mm;
            margin: 3mm 0;
        }
        
        .toc-h3 {
            padding-left: 20mm;
            margin: 2mm 0;
        }
        
        /* 본문 스타일 */
        .chapter {
            page-break-before: always;
        }
        
        .chapter h1 {
            font-family: 'Noto Sans KR', sans-serif;
            font-size: 18pt;
            font-weight: bold;
            border-bottom: 2px solid #333;
            padding-bottom: 5mm;
            margin-top: 15mm;
            margin-bottom: 10mm;
        }
        
        .chapter h2 {
            font-family: 'Noto Sans KR', sans-serif;
            font-size: 16pt;
            margin-top: 10mm;
            margin-bottom: 5mm;
        }
        
        .chapter h3 {
            font-family: 'Noto Sans KR', sans-serif;
            font-size: 14pt;
            margin-top: 8mm;
            margin-bottom: 4mm;
        }
        
        /* 본문 서식 */
        .chapter-content p {
            margin-bottom: 1em;
            text-align: justify;
        }
        
        /* 테이블 스타일 */
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 10mm 0;
            font-size: 11pt;
        }
        
        table, th, td {
            border: 1px solid #000;
        }
        
        th {
            background-color: #f5f5f5;
            font-weight: bold;
            padding: 3mm 2mm;
            text-align: center;
        }
        
        td {
            padding: 3mm 2mm;
            vertical-align: middle;
        }
        
        caption {
            caption-side: top;
            text-align: center;
            font-weight: bold;
            margin-bottom: 3mm;
        }
        
        /* 이미지 스타일 */
        figure {
            text-align: center;
            margin: 10mm 0;
            page-break-inside: avoid;
        }
        
        figure img {
            max-width: 100%;
            height: auto;
            margin: 0 auto;
            display: block;
            border: 1px solid #eee;
        }
        
        figcaption {
            margin-top: 3mm;
            font-style: italic;
            font-size: 11pt;
        }
        
        /* 코드 블록 스타일 */
        pre {
            background-color: #f8f8f8;
            border: 1px solid #ddd;
            border-radius: 3px;
            padding: 10px;
            margin: 10px 0;
            overflow-x: auto;
            font-family: 'D2Coding', monospace;
            font-size: 0.9em;
            line-height: 1.5;
            white-space: pre-wrap;
        }
        
        code {
            font-family: 'D2Coding', monospace;
            background-color: #f0f0f0;
            padding: 2px 4px;
            border-radius: 3px;
            font-size: 0.9em;
        }
        
        pre code {
            background-color: transparent;
            padding: 0;
            border-radius: 0;
        }
        
        /* 강조 텍스트 스타일 */
        em {
            font-style: italic;
        }
        
        strong {
            font-weight: bold;
        }
        
        /* 인용문 스타일 */
        blockquote {
            margin: 10px 0;
            padding: 10px 20px;
            border-left: 5px solid #ddd;
            background-color: #f9f9f9;
            font-style: italic;
        }
        
        /* 목록 스타일 */
        ul, ol {
            margin: 1em 0;
            padding-left: 2em;
        }
        
        ul li, ol li {
            margin-bottom: 0.5em;
        }
        
        /* 인쇄 설정 */
        @page {
            size: A4;
            margin: 0;
        }
        
        @media print {
            body {
                margin: 0;
                padding: 0;
            }
            
            h1, h2, h3 {
                page-break-after: avoid;
            }
            
            table, figure {
                page-break-inside: avoid;
            }
            
            .page-break {
                page-break-after: always;
            }
        }
        """
        
        # 마크다운 내용 읽기
        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 제목 추출 (YAML 메타데이터에서)
        title_match = re.search(r'title:\s*([^\n]+)', content)
        title = title_match.group(1).strip() if title_match else "생성형 인공지능 기반 시계열 예측 자동화 연구"
        
        # 저자 정보
        author_info = []
        sections = collect_sections()
        author_text = sections.get('author', '')
        for line in author_text.split('\n'):
            if ':' in line:
                author_info.append(line.strip())
        
        # 현재 날짜
        today = datetime.now().strftime('%Y년 %m월 %d일')
        
        # 마크다운 테이블을 HTML로 변환하는 함수
        def convert_table_to_html(table_md, table_num=None):
            rows = [row for row in table_md.strip().split('\n') if row.strip()]
            
            if len(rows) < 2:
                return f"<p>테이블 형식 오류: {table_md}</p>"
            
            html_table = '<table>\n'
            if table_num:
                html_table += f'<caption>표 {table_num}</caption>\n'
            
            # 헤더 행
            header_cells = [cell.strip() for cell in rows[0].split('|')]
            header_cells = [cell for cell in header_cells if cell != '']  # 빈 셀 제거
            
            html_table += '<thead>\n<tr>\n'
            for cell in header_cells:
                html_table += f'<th>{cell}</th>\n'
            html_table += '</tr>\n</thead>\n'
            
            # 본문 행
            html_table += '<tbody>\n'
            for row in rows[2:]:  # 첫 행(헤더)과 두 번째 행(구분선)을 건너뜀
                if not row.strip() or not '|' in row:
                    continue
                cells = [cell.strip() for cell in row.split('|')]
                cells = [cell for cell in cells if cell != '']  # 빈 셀 제거
                
                html_table += '<tr>\n'
                for cell in cells:
                    html_table += f'<td>{cell}</td>\n'
                html_table += '</tr>\n'
            
            html_table += '</tbody>\n</table>'
            return html_table
        
        # 마크다운을 HTML로 변환하는 함수 (특수 태그 처리)
        def convert_markdown(text):
            # 이미지 처리
            def process_image(match):
                alt = match.group(1) or "그림"
                path = match.group(2)
                
                # 상대 경로 처리
                if not path.startswith(('http://', 'https://')):
                    filename = os.path.basename(path)
                    path = f'images/{filename}'
                
                return f'<figure><img src="{path}" alt="{alt}"><figcaption>{alt}</figcaption></figure>'
            
            # 코드 블록 처리
            def process_code_block(match):
                lang = match.group(1) or ""
                code = match.group(2)
                return f'<pre><code class="language-{lang}">{html.escape(code)}</code></pre>'
            
            # 인라인 코드 처리
            def process_inline_code(match):
                return f'<code>{html.escape(match.group(1))}</code>'
                
            # 강조 처리
            def process_bold(match):
                return f'<strong>{match.group(1)}</strong>'
                
            def process_italic(match):
                return f'<em>{match.group(1)}</em>'
            
            # 테이블 처리
            def process_table(match):
                table_content = match.group(0)
                return convert_table_to_html(table_content)
                
            # 순서 없는 목록 처리
            def process_unordered_list(match):
                list_text = match.group(0)
                items = re.findall(r'[\*\-\+]\s+(.*?)(?=\n[\*\-\+]|\n\n|\Z)', list_text + '\n\n', re.DOTALL)
                html_list = '<ul>\n'
                for item in items:
                    html_list += f'  <li>{item.strip()}</li>\n'
                html_list += '</ul>'
                return html_list
                
            # 순서 있는 목록 처리
            def process_ordered_list(match):
                list_text = match.group(0)
                items = re.findall(r'\d+\.\s+(.*?)(?=\n\d+\.|\n\n|\Z)', list_text + '\n\n', re.DOTALL)
                html_list = '<ol>\n'
                for item in items:
                    html_list += f'  <li>{item.strip()}</li>\n'
                html_list += '</ol>'
                return html_list
            
            # 처리 순서가 중요함: 블록 요소 → 인라인 요소
            
            # 먼저 코드 블록 처리 (다른 마크다운 서식의 영향을 받지 않도록)
            text = re.sub(r'```([a-z]*)\n(.*?)```', process_code_block, text, flags=re.DOTALL)
            
            # 테이블 처리
            text = re.sub(r'(\|.*\|\n)(\|[\s\-:]*\|\n)(\|.*\|\n)+', process_table, text)
            
            # 목록 처리
            text = re.sub(r'(?:^|\n)(?:[\*\-\+]\s+.*\n)+', process_unordered_list, text)
            text = re.sub(r'(?:^|\n)(?:\d+\.\s+.*\n)+', process_ordered_list, text)
            
            # 제목 처리는 별도로 수행하므로 여기서는 생략
            
            # 인라인 요소 처리
            text = re.sub(r'!\[(.*?)\]\((.*?)\)', process_image, text)  # 이미지
            text = re.sub(r'`(.*?)`', process_inline_code, text)  # 인라인 코드
            text = re.sub(r'\*\*(.*?)\*\*|__(.*?)__', lambda m: f'<strong>{m.group(1) or m.group(2)}</strong>', text)  # 강조
            text = re.sub(r'\*(.*?)\*|_(.*?)_', lambda m: f'<em>{m.group(1) or m.group(2)}</em>', text)  # 기울임
            text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', text)  # 링크
            
            # 문단 처리: 빈 줄로 구분된 텍스트 블록을 <p> 태그로 감싸기
            paragraphs = []
            for para in re.split(r'\n\s*\n', text):
                if para.strip():
                    # 이미 HTML 태그로 시작하는 콘텐츠는 그대로 두기
                    if re.match(r'^\s*<(pre|ul|ol|table|h[1-6]|blockquote|div|figure)', para.strip()):
                        paragraphs.append(para.strip())
                    else:
                        # 줄바꿈 처리
                        formatted_para = para.replace('\n', '<br>')
                        paragraphs.append(f'<p>{formatted_para}</p>')
            
            return '\n\n'.join(paragraphs)
        
        # 목차 및 챕터 내용 생성
        chapters = [
            {"number": "1", "title": "서론", "content": sections.get('introduction', '')},
            {"number": "2", "title": "이론적 배경", "content": sections.get('background', '')},
            {"number": "3", "title": "연구 방법", "content": sections.get('method', '')},
            {"number": "4", "title": "실험 및 결과", "content": sections.get('results', '')},
            {"number": "5", "title": "결론 및 향후 연구", "content": sections.get('conclusion', '')},
            {"number": "6", "title": "참고 문헌", "content": sections.get('references', '')}
        ]
        
        # 목차 항목 생성
        toc_entries = []
        for chapter in chapters:
            chapter_num = chapter["number"]
            chapter_title = chapter["title"]
            toc_entries.append(f'<div class="toc-h1"><a href="#chapter{chapter_num}">{chapter_num}. {chapter_title}</a></div>')
            
            # H2 레벨 제목 추출
            h2_pattern = r'^##\s+(.+?)$'
            h2_matches = re.findall(h2_pattern, chapter["content"], re.MULTILINE)
            
            for i, h2 in enumerate(h2_matches):
                section_id = f"section-{chapter_num}-{i+1}"
                section_num = f"{chapter_num}.{i+1}"
                # 섹션 제목에서 이미 있는 번호 제거
                clean_h2 = re.sub(r'^\d+\.\d+\s+', '', h2)
                toc_entries.append(f'<div class="toc-h2"><a href="#{section_id}">{section_num} {clean_h2}</a></div>')
                
                # 해당 섹션 내의 H3 제목 찾기
                section_start = chapter["content"].find(f"## {h2}")
                if section_start >= 0:
                    next_h2_match = re.search(r'^##\s+', chapter["content"][section_start+len(h2):], re.MULTILINE)
                    section_end = next_h2_match.start() + section_start + len(h2) if next_h2_match else len(chapter["content"])
                    section_content = chapter["content"][section_start:section_end]
                    
                    h3_pattern = r'^###\s+(.+?)$'
                    h3_matches = re.findall(h3_pattern, section_content, re.MULTILINE)
                    
                    for j, h3 in enumerate(h3_matches):
                        subsection_id = f"section-{chapter_num}-{i+1}-{j+1}"
                        subsection_num = f"{chapter_num}.{i+1}.{j+1}"
                        # H3 제목에서 이미 있는 번호 제거
                        clean_h3 = re.sub(r'^\d+\.\d+\.\d+\s+', '', h3)
                        toc_entries.append(f'<div class="toc-h3"><a href="#{subsection_id}">{subsection_num} {clean_h3}</a></div>')
        
        toc_content = '\n'.join(toc_entries)
        
        # HTML 파일 시작 부분
        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
    {thesis_css}
    </style>
</head>
<body>
    <!-- 표지 -->
    <div class="title-page">
        <div class="title-content">
            <h1>{title}</h1>
            <div class="degree-text">석사학위 논문</div>
        </div>
        
        <div class="author-info">
            {'<br>'.join(author_info)}
        </div>
        
        <div class="date-university">
            <p>{today}</p>
            <p>aSSIST(서울과학종합대학원)</p>
        </div>
    </div>
    
    <div class="container">
        <!-- 초록 -->
        <div class="abstract-page">
            <h2>초록</h2>
            <div class="abstract-content">
                {convert_markdown(sections.get('abstract', ''))}
            </div>
        </div>
        
        <!-- 목차 -->
        <div class="toc-page">
            <div class="toc-title">목차</div>
            <div class="toc-list">
                {toc_content}
            </div>
        </div>
        
        <!-- 본문 -->
"""
        
        # 챕터 내용 추가
        for chapter in chapters:
            chapter_num = chapter["number"]
            chapter_title = chapter["title"]
            chapter_content = chapter["content"]
            
            # 챕터 번호가 이미 있는 제목을 제거
            chapter_content = re.sub(r'^#\s+\d+\.\s+.+$', '', chapter_content, flags=re.MULTILINE).strip()
            
            html_content += f"""
        <div class="chapter" id="chapter{chapter_num}">
            <h1>{chapter_num}. {chapter_title}</h1>
            <div class="chapter-content">
"""
            
            # 섹션 처리
            if "##" in chapter_content:
                # 섹션(H2) 추출 및 처리
                sections_pattern = r'##\s+(.+?)(?=\n##|\Z)'
                sections_with_titles = re.split(sections_pattern, chapter_content, flags=re.DOTALL)
                
                # 첫 번째 요소가 ## 앞의 내용이라면 처리
                if sections_with_titles and not sections_with_titles[0].startswith('##'):
                    intro_content = sections_with_titles.pop(0).strip()
                    if intro_content:
                        html_content += convert_markdown(intro_content) + "\n"
                
                # 나머지 요소들은 제목과 내용이 번갈아가며 나옴
                for i in range(0, len(sections_with_titles), 2):
                    if i+1 < len(sections_with_titles):
                        section_title = sections_with_titles[i].strip()
                        section_content = sections_with_titles[i+1].strip()
                        
                        # 섹션 번호 제거
                        clean_title = re.sub(r'^\d+\.\d+\s+', '', section_title)
                        section_id = f"section-{chapter_num}-{i//2+1}"
                        section_num = f"{chapter_num}.{i//2+1}"
                        
                        html_content += f'<h2 id="{section_id}">{section_num} {clean_title}</h2>\n'
                        
                        # 섹션 내 서브섹션(H3) 처리
                        if "###" in section_content:
                            subsections_pattern = r'###\s+(.+?)(?=\n###|\Z)'
                            subsections_with_titles = re.split(subsections_pattern, section_content, flags=re.DOTALL)
                            
                            # 첫 번째 요소가 ### 앞의 내용이라면 처리
                            if subsections_with_titles and not subsections_with_titles[0].startswith('###'):
                                subsection_intro = subsections_with_titles.pop(0).strip()
                                if subsection_intro:
                                    html_content += convert_markdown(subsection_intro) + "\n"
                            
                            # 나머지 요소들은 제목과 내용이 번갈아가며 나옴
                            for j in range(0, len(subsections_with_titles), 2):
                                if j+1 < len(subsections_with_titles):
                                    subsection_title = subsections_with_titles[j].strip()
                                    subsection_content = subsections_with_titles[j+1].strip()
                                    
                                    # 서브섹션 번호 제거
                                    clean_subsection_title = re.sub(r'^\d+\.\d+\.\d+\s+', '', subsection_title)
                                    subsection_id = f"section-{chapter_num}-{i//2+1}-{j//2+1}"
                                    subsection_num = f"{chapter_num}.{i//2+1}.{j//2+1}"
                                    
                                    html_content += f'<h3 id="{subsection_id}">{subsection_num} {clean_subsection_title}</h3>\n'
                                    html_content += convert_markdown(subsection_content) + "\n"
                        else:
                            # 서브섹션이 없으면 섹션 내용 전체를 변환
                            html_content += convert_markdown(section_content) + "\n"
            else:
                # 섹션이 없으면 챕터 내용 전체를 변환
                html_content += convert_markdown(chapter_content)
            
            html_content += """
            </div>
        </div>"""
        
        # HTML 문서 마무리
        html_content += """
    </div>
</body>
</html>"""
        
        # HTML 파일 저장
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"HTML 파일이 생성되었습니다: {html_file}")
        
        # 브라우저에서 자동 열기
        try:
            import webbrowser
            webbrowser.open('file://' + os.path.abspath(html_file))
            print("생성된 HTML 파일이 브라우저에서 열렸습니다.")
        except Exception as e:
            print(f"브라우저에서 파일을 열지 못했습니다: {e}")
        
        return True
    
    except Exception as e:
        print(f"HTML 변환 중 오류 발생: {e}")
        traceback.print_exc()
        return False

# PDF 변환 함수
def convert_to_pdf(markdown_file, pdf_file):
    """마크다운 파일을 PDF로 변환하는 함수"""
    try:
        print("PDF로 변환 중...")
        
        # 템플릿 디렉토리 생성
        templates_dir = os.path.join(output_dir, 'templates')
        os.makedirs(templates_dir, exist_ok=True)
        
        # LaTeX 템플릿 파일 생성
        template_path = os.path.join(templates_dir, 'thesis_template.tex')
        
        # 간단한 LaTeX 템플릿 작성
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(r"""
\documentclass[$if(fontsize)$$fontsize$,$endif$$if(lang)$$lang$,$endif$$if(papersize)$$papersize$,$endif$$for(classoption)$$classoption$$sep$,$endfor$]{$documentclass$}

% 한국어 지원
\usepackage{kotex}

% 폰트 설정
$if(fontfamily)$
\usepackage[$for(fontfamilyoptions)$$fontfamilyoptions$$sep$,$endfor$]{$fontfamily$}
$endif$

$if(linestretch)$
\usepackage{setspace}
\setstretch{$linestretch$}
$endif$

% 여백 설정
\usepackage[
$for(geometry)$
  $geometry$$sep$,
$endfor$
]{geometry}

% 색상 설정
\usepackage{xcolor}
$if(colorlinks)$
\usepackage{hyperref}
\hypersetup{
  colorlinks=true,
  linkcolor=$if(linkcolor)$$linkcolor$$else$Maroon$endif$,
  citecolor=$if(citecolor)$$citecolor$$else$Blue$endif$,
  urlcolor=$if(urlcolor)$$urlcolor$$else$Blue$endif$
}
$endif$

% 이미지 지원
\usepackage{graphicx}
\usepackage{float}
\usepackage{wrapfig}
\usepackage{grffile}

% 표 지원
\usepackage{longtable,booktabs,tabularx,colortbl}
\usepackage{multirow}

% 코드 블록 지원
\usepackage{listings}
\lstset{
  basicstyle=\ttfamily\small,
  keywordstyle=\color{blue},
  commentstyle=\color{gray},
  stringstyle=\color{red},
  breaklines=true,
  breakatwhitespace=true,
  tabsize=2
}

% 제목 스타일
\usepackage{titlesec}
\titleformat{\chapter}[display]
  {\normalfont\huge\bfseries}
  {\chaptertitlename\ \thechapter}
  {20pt}
  {\Huge}

% 헤더/푸터
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[R]{\slshape \leftmark}
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0.4pt}
\renewcommand{\footrulewidth}{0.4pt}

$for(header-includes)$
$header-includes$
$endfor$

\begin{document}

% 표지
\begin{titlepage}
\begin{center}
\vspace*{2cm}

{\Huge\textbf{$title$}}\\

\vspace{1.5cm}

{\LARGE 석사학위 논문}\\

\vspace{2cm}

$if(author)$
{\large 이름: $author$}\\
$endif$

\vspace{3cm}

{\large \today}\\

\vspace{2cm}

{\large aSSIST(서울과학종합대학원)}\\
\end{center}
\end{titlepage}

% 초록
\chapter*{초록}
\addcontentsline{toc}{chapter}{초록}

$abstract$

% 목차
\newpage
\tableofcontents
\newpage

% 그림 목차
\listoffigures
\newpage

% 표 목차
\listoftables
\newpage

% 본문 시작
$body$

\end{document}
""")
        
        print(f"LaTeX 템플릿 파일이 생성되었습니다: {template_path}")
        
        # PDF 변환을 위한 명령어 구성
        resource_paths = [
            os.path.abspath(output_dir),
            os.path.join(os.path.abspath(output_dir), 'images'),
            os.path.join(os.path.abspath(results_dir), 'analysis_plots')
        ]
        
        resource_path_args = " ".join([f"--resource-path {path}" for path in resource_paths])
        
        # xelatex 확인
        xelatex_available = shutil.which("xelatex") is not None
        pdf_engine = "xelatex" if xelatex_available else "pdflatex"
        
        # PDF 생성 명령어
        cmd = f"pandoc {markdown_file} -o {pdf_file} --pdf-engine={pdf_engine} --template {template_path} --listings --number-sections --toc --top-level-division=chapter {resource_path_args}"
        
        print(f"PDF 변환을 위한 명령어:\n{cmd}")
        
        # 명령어 실행
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        # 결과 확인
        if result.returncode != 0:
            print(f"표준 오류:\n{result.stderr}")
            print(f"\nPDF 변환 실패: 종료 코드 {result.returncode}")
            
            # 실패 시 LaTeX 중간 파일 생성 시도
            latex_file = os.path.join(output_dir, 'thesis.tex')
            latex_cmd = f"pandoc {markdown_file} -o {latex_file} --template {template_path} --listings --number-sections --toc --top-level-division=chapter {resource_path_args}"
            print("\n더 자세한 오류 검사를 위해 LaTeX 중간 파일 생성 시도...")
            subprocess.run(latex_cmd, shell=True)
            
            # 사용자에게 팁 제공
            if not xelatex_available:
                print("\n팁: xelatex이 설치되어 있지 않아 PDF 생성에 실패했을 수 있습니다.")
                print("Ubuntu/Debian: 'sudo apt-get install texlive-xetex texlive-lang-korean'")
                print("Mac: MacTeX 패키지를 설치하세요 (https://www.tug.org/mactex/)")
                print("Windows: MikTeX 또는 TeX Live를 설치하세요")
                print("\n혹은 다른 PDF 변환 도구를 사용해보세요:")
                print("1. 웹에서 Markdown to PDF 변환 서비스 이용")
                print("2. VS Code의 Markdown PDF 확장 기능 사용")
            
            return False
        else:
            print(f"PDF 파일이 성공적으로 생성되었습니다: {pdf_file}")
            return True
        
    except Exception as e:
        print(f"PDF 변환 중 오류 발생: {e}")
        traceback.print_exc()
        return False

def main():
    print("논문 생성 프로세스 시작...")
    
    # 이미지 준비
    print("\n1. 이미지 준비 중...")
    images_dir = prepare_images()
    
    # 섹션 내용 수집
    print("\n2. 논문 섹션 수집 중...")
    sections = collect_sections()
    
    # 마크다운 생성
    print("\n3. 마크다운 파일 생성 중...")
    md_file = generate_thesis_markdown(sections, images_dir)
    
    print("\n논문 마크다운 생성이 완료되었습니다!")
    print(f"마크다운 파일: {md_file}")
    
    # 변환 옵션 제공
    print("\n다음 단계를 선택하세요:")
    print("1. HTML로 변환 (석사논문 스타일)")
    print("2. PDF로 변환 (xelatex 필요)")
    print("3. HTML과 PDF 모두 생성")
    print("4. 종료 (나중에 수동으로 변환)")
    
    try:
        choice = input("\n선택 (1-4): ")
        
        if choice == '1':
            # HTML 변환
            convert_to_thesis_html(md_file, html_file)
        elif choice == '2':
            # PDF 변환
            print("\nPDF로 변환 중...")
            convert_to_pdf(md_file, pdf_file)
        elif choice == '3':
            # 둘 다 변환
            print("\nHTML 변환 중...")
            convert_to_thesis_html(md_file, html_file)
            print("\nPDF 변환 중...")
            convert_to_pdf(md_file, pdf_file)
        else:
            print("\n변환을 건너뛰었습니다. 나중에 수동으로 변환할 수 있습니다.")
    except Exception as e:
        print(f"\n오류 발생: {e}")
        # 기본 선택지로 HTML 변환 시도
        print("\nHTML 변환을 시도합니다...")
        convert_to_thesis_html(md_file, html_file)
    
    print("\n프로세스 완료!")
    print(f"마크다운 파일: {md_file}")
    print(f"HTML 파일: {html_file}")
    print(f"PDF 파일: {pdf_file} (생성에 성공했다면)")

if __name__ == "__main__":
    main()
