import os
import re
import glob
import yaml
from datetime import datetime
import shutil
import subprocess

# Pillow를 통한 이미지 생성 추가
try:
    from PIL import Image
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

# 파일 내용 읽기 함수
def read_file_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        print(f"파일 읽기 오류 {file_path}: {e}")
        return ""

# 마크다운에 사용할 이미지 복사
# 더미 이미지 생성 함수 추가
def setup_dummy_images():
    """더미 이미지 파일을 생성하는 함수"""
    images_output_dir = os.path.join(output_dir, 'images')
    os.makedirs(images_output_dir, exist_ok=True)
    
    # 마크다운 파일에서 참조되는 모든 이미지 파일 목록 생성
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
    
    # 더 확실한 더미 이미지 파일 생성 (1x1 픽셀보다 더 큰 파일)
    try:
        # 외부 텍스트 파일 생성 (이미지 대체)
        for filename in image_filenames:
            filepath = os.path.join(images_output_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("DUMMY IMAGE FILE")  # 단순 텍스트 파일
            print(f"더미 이미지 생성: {filepath}")
        
        # 더미 PNG 이미지도 시도 (파일 크기 문제 해결)
        dummy_png_path = os.path.join(images_output_dir, "dummy.png")
        if PIL_AVAILABLE:
            img = Image.new('RGB', (100, 100), color='white')
            img.save(dummy_png_path, 'PNG')
        else:
            # 최소한의 유효한 PNG 헤더 (8 바이트)만 저장 (이전 방식, 권장하지 않음)
            with open(dummy_png_path, 'wb') as f:
                f.write(b'\x89PNG\r\n\x1a\n')
            print("[경고] Pillow(PIL)가 설치되어 있지 않아 더미 이미지를 올바르게 생성하지 못했습니다. 'pip install pillow'로 설치하세요.")
        
        # 각 이미지 파일 경로가 존재하는지 확인
        for filename in image_filenames:
            filepath = os.path.join(images_output_dir, filename)
            if os.path.exists(filepath):
                print(f"확인: {filepath} (크기: {os.path.getsize(filepath)} 바이트)")
            else:
                print(f"오류: {filepath} 파일이 생성되지 않았습니다.")
        
    except Exception as e:
        print(f"더미 이미지 생성 중 오류: {e}")
    
    return images_output_dir

# 논문 각 섹션 내용 수집
def collect_sections():
    sections = {}
    
    # 타이틀
    title_file = os.path.join(paper_dir, '0_overview', '0_0_title.md')
    if os.path.exists(title_file):
        sections['title'] = read_file_content(title_file)
    
    # 저자 정보
    author_file = os.path.join(paper_dir, '0_overview', '0_1_author.md')
    if os.path.exists(author_file):
        sections['author'] = read_file_content(author_file)
    
    # 목차
    toc_file = os.path.join(paper_dir, '0_overview', '0_2_contents.md')
    if os.path.exists(toc_file):
        sections['toc'] = read_file_content(toc_file)
    
    # 초록
    abstract_file = os.path.join(paper_dir, '0_overview', '0_3_abstract.md')
    if os.path.exists(abstract_file):
        sections['abstract'] = read_file_content(abstract_file)
    
    # 서론
    intro_file = os.path.join(paper_dir, '1_introduction', '1_introduction.md')
    if os.path.exists(intro_file):
        sections['introduction'] = read_file_content(intro_file)
    
    # 이론적 배경
    background_files = sorted(glob.glob(os.path.join(paper_dir, '2_background', '*.md')))
    sections['background'] = "\n\n".join([read_file_content(f) for f in background_files])
    
    # 연구 방법
    method_files = sorted(glob.glob(os.path.join(paper_dir, '3_method', '*.md')))
    sections['method'] = "\n\n".join([read_file_content(f) for f in method_files])
    
    # 실험 및 결과
    results_files = sorted(glob.glob(os.path.join(paper_dir, '4_experiments_and_results', '*.md')))
    sections['results'] = "\n\n".join([read_file_content(f) for f in results_files])
    
    # 결론
    conclusion_file = os.path.join(paper_dir, '5_conclusion', '5_conclusion.md')
    if os.path.exists(conclusion_file):
        sections['conclusion'] = read_file_content(conclusion_file)
    
    # 참고문헌
    reference_file = os.path.join(paper_dir, '6_reference', '6_reference.md')
    if os.path.exists(reference_file):
        sections['references'] = read_file_content(reference_file)
    
    return sections

# 이미지 경로 변환
def update_image_paths(content, image_dir):
    # 다양한 형식의 GitHub 이미지 링크를 로컬 이미지 링크로 변환
    patterns = [
        # 기존 패턴
        (r'!\[(.*?)\]\((https://github\.com/.*?/blob/.*?/research_results/analysis_plots/(.*?))\)', r'![\1](images/\3)'),
        
        # 추가 패턴 - 파일명만 추출
        (r'!\[(.*?)\]\(.*?/([^/]+\.png)\)', r'![\1](images/\2)'),
        
        # 직접 경로만 있는 경우 (![](경로))
        (r'!\[\]\(.*?/([^/]+\.png)\)', r'![](images/\1)')
    ]
    
    updated_content = content
    for pattern, replacement in patterns:
        updated_content = re.sub(pattern, replacement, updated_content)
    
    # 변환 결과 로그
    print(f"이미지 경로 변환 완료: {content != updated_content}")
    
    return updated_content

# 표 데이터 수집
def collect_table_data():
    table_data = {}
    csv_files = glob.glob(os.path.join(results_dir, '*.csv'))
    
    for csv_file in csv_files:
        table_name = os.path.basename(csv_file).replace('.csv', '')
        content = read_file_content(csv_file)
        table_data[table_name] = content
    
    return table_data

# 논문 생성
def generate_thesis():
    sections = collect_sections()
    images_dir = setup_dummy_images()  # 수정된 부분: 실제 이미지 대신 더미 이미지 생성
    table_data = collect_table_data()
    
    # 섹션 내용에서 이미지 경로 업데이트
    for key in sections:
        sections[key] = update_image_paths(sections[key], images_dir)
        
    # YAML 메타데이터 생성
    metadata = {
        'title': sections.get('title', '생성형 인공지능 기반 시계열 예측 자동화 연구'),
        'author': '이루오',
        'date': datetime.now().strftime('%Y-%m-%d'),
        'lang': 'ko',
        'papersize': 'a4',
        'fontsize': '12pt',
        'linestretch': 1.6,
        'mainfont': '바탕',
        'sansfont': '맑은고딕',
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
        'numbersections': True
    }
    
    # 마크다운 파일 생성
    with open(markdown_file, 'w', encoding='utf-8') as f:
        # YAML 메타데이터 작성
        f.write('---\n')
        yaml.dump(metadata, f, allow_unicode=True, default_flow_style=False)
        f.write('---\n\n')
        
        # 표지 작성
        f.write('\\begin{titlepage}\n')
        f.write('\\begin{center}\n')
        f.write('\\vspace*{2cm}\n\n')
        f.write(f'\\LARGE\\textbf{{{sections.get("title", "")}}}\n\n')
        f.write('\\vspace{1.5cm}\n\n')
        f.write('\\large 석사학위 논문\n\n')
        f.write('\\vspace{2cm}\n\n')
        
        # 저자 정보 처리
        author_info = sections.get('author', '').split('\n')
        for line in author_info:
            if line.strip():
                parts = line.split(':')
                if len(parts) > 1:
                    f.write(f'\\large {parts[0].strip()}: {parts[1].strip()}\\\\\n')
        
        f.write('\\vspace{3cm}\n\n')
        f.write('\\large\\today\n\n')
        f.write('\\vspace{2cm}\n\n')
        f.write('\\large aSSIST(서울과학종합대학원)\n')
        f.write('\\end{center}\n')
        f.write('\\end{titlepage}\n\n')
        
        # 초록
        f.write('## 초록\n\n')
        f.write(sections.get('abstract', '').replace('초록', '').strip())
        f.write('\n\n')
        
        # 목차는 자동 생성 (YAML 메타데이터의 toc 옵션)
        f.write('\\newpage\n\n')
        
        # 본문
        f.write('# 서론\n\n')
        f.write(sections.get('introduction', '').replace('1. 서론', ''))
        f.write('\n\n')
        
        f.write('# 이론적 배경\n\n')
        f.write(sections.get('background', '').replace('2. 이론적 배경', ''))
        f.write('\n\n')
        
        f.write('# 연구 방법\n\n')
        f.write(sections.get('method', '').replace('3. 연구 방법', ''))
        f.write('\n\n')
        
        f.write('# 실험 및 결과\n\n')
        f.write(sections.get('results', '').replace('4. 실험 및 결과', ''))
        f.write('\n\n')
        
        f.write('# 결론 및 향후 연구\n\n')
        f.write(sections.get('conclusion', '').replace('5. 결론 및 향후 연구', ''))
        f.write('\n\n')
        
        f.write('# 참고 문헌\n\n')
        f.write(sections.get('references', '').replace('6. 참고 문헌', ''))
    
    print(f"마크다운 파일이 생성되었습니다: {markdown_file}")
    return markdown_file

# PDF 변환
def convert_to_pdf(markdown_file, pdf_file):
    try:
        # 직접 xelatex 경로 사용 (사용자 시스템에 맞게 조정)
        xelatex_path = "/usr/local/texlive/2025/bin/x86_64-linux/xelatex"
        
        # xelatex 경로 검증
        if os.path.exists(xelatex_path):
            print(f"xelatex 경로 확인: {xelatex_path} (존재함)")
        else:
            print(f"경고: {xelatex_path} 경로에 xelatex이 존재하지 않습니다.")
            # 환경 변수 PATH에서 찾기 시도
            try:
                which_result = subprocess.run(['which', 'xelatex'], capture_output=True, text=True, check=True)
                xelatex_path = which_result.stdout.strip()
                print(f"which 명령으로 찾은 xelatex 경로: {xelatex_path}")
            except subprocess.CalledProcessError:
                print("which 명령으로 xelatex을 찾을 수 없습니다.")
        
        # 환경 변수 설정 (TeX Live 경로 추가)
        env = os.environ.copy()
        texlive_path = "/usr/local/texlive/2025/bin/x86_64-linux"
        if os.path.exists(texlive_path):
            if 'PATH' in env:
                env['PATH'] = f"{texlive_path}:{env['PATH']}"
            else:
                env['PATH'] = texlive_path
            print(f"PATH 환경 변수에 TeX Live 경로 추가: {texlive_path}")
        
        # pandoc 명령 실행 (xelatex 경로 명시)
        cmd = [
            'pandoc',
            markdown_file,
            '-o', pdf_file,
            f'--pdf-engine={xelatex_path}',
            '--listings',
            '-V', 'lang=ko',
            '-V', 'papersize=a4',
            '-V', 'fontsize=12pt',
            '-V', 'linestretch=1.6',
            '-V', 'mainfont=NanumMyeongjo',
            '-V', 'sansfont=NanumGothic',
            '-V', 'monofont=NanumGothicCoding',
            '-V', 'geometry:margin=3cm'
        ]
        
        print("실행할 명령어:")
        print(" ".join(cmd))
        
        # 수정된 환경 변수로 명령 실행
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        # 결과 출력 (성공/실패 여부와 관계없이)
        print("\n--- 실행 결과 ---")
        if result.stdout:
            print("표준 출력:")
            print(result.stdout)
        if result.stderr:
            print("표준 오류:")
            print(result.stderr)
        
        # 종료 코드 확인
        if result.returncode == 0:
            print(f"PDF 파일이 생성되었습니다: {pdf_file}")
            return True
        else:
            print(f"PDF 변환 실패: 종료 코드 {result.returncode}")
            
            # HTML로 대체 시도
            try_html = input("PDF 변환에 실패했습니다. HTML로 변환해볼까요? (y/n): ")
            if try_html.lower() == 'y':
                html_file = pdf_file.replace('.pdf', '.html')
                html_cmd = ['pandoc', markdown_file, '-o', html_file, '-s', '--embed-resources', '--standalone']
                try:
                    subprocess.run(html_cmd, check=True)
                    print(f"HTML 파일이 생성되었습니다: {html_file}")
                except Exception as html_error:
                    print(f"HTML 변환 중 오류 발생: {html_error}")
                    # 이전 방식 시도
                    html_cmd_old = ['pandoc', markdown_file, '-o', html_file, '-s', '--self-contained']
                    subprocess.run(html_cmd_old, check=True)
                    print(f"HTML 파일이 생성되었습니다: {html_file} (이전 옵션 사용)")
            
            return False
            
    except Exception as e:
        print(f"변환 프로세스 중 오류 발생: {e}")
        return False

# 메인 실행
def main():
    md_file = generate_thesis()
    pdf_file = md_file.replace('.md', '.pdf')
    html_file = md_file.replace('.md', '.html')
    
    print("\n논문 생성이 완료되었습니다!")
    print(f"마크다운 파일: {md_file}")
    
    # 변환 옵션 제공
    print("\n다음 단계:")
    print("1. HTML로 변환 (가장 간단하고 안정적)")
    print("2. PDF로 변환 (xelatex 필요)")
    print("3. 종료 (나중에 수동으로 변환)")
    
    choice = input("\n선택 (1-3): ")
    
    if choice == '1':
        # HTML로 변환
        html_cmd = ['pandoc', md_file, '-o', html_file, '-s', '--embed-resources', '--standalone']
        try:
            print("\nHTML로 변환 중...")
            subprocess.run(html_cmd, check=True)
            print(f"HTML 파일이 생성되었습니다: {html_file}")
            print("이 파일을 웹 브라우저에서 열어 내용을 확인할 수 있습니다.")
        except Exception as e:
            print(f"HTML 변환 중 오류 발생: {e}")
            # 이전 방식으로 시도
            try:
                html_cmd_old = ['pandoc', md_file, '-o', html_file, '-s', '--self-contained']
                subprocess.run(html_cmd_old, check=True)
                print(f"HTML 파일이 생성되었습니다: {html_file} (이전 옵션 사용)")
            except Exception as e2:
                print(f"이전 HTML 변환 옵션으로도 실패: {e2}")
    
    elif choice == '2':
        # PDF로 변환
        print("\nPDF로 변환 중...")
        convert_to_pdf(md_file, pdf_file)
    
    else:
        print("\n변환을 건너뛰었습니다. 나중에 다음 명령어로 변환할 수 있습니다:")
        print(f"HTML: pandoc {md_file} -o {html_file} -s --self-contained")
        print(f"PDF: pandoc {md_file} -o {pdf_file} --pdf-engine=/usr/local/texlive/2025/bin/x86_64-linux/xelatex")
    
    print("\n프로세스 완료!")

if __name__ == "__main__":
    main()
