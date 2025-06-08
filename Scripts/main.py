import os
import shutil
import tempfile
import converter
import compressor
import parse_edit_section0
import re
from tkinter import filedialog, Tk
from typing import Literal


TextStyle = Literal["제목", "중제목", "본문", "리스트"]

def clean_md_line(line: str) -> str:
    """
    마크다운 서식을 제거한 텍스트 반환
    예: '# 제목' → '제목', '* 글머리표' → '글머리표'
    """
    line = line.strip()
    line = re.sub(r'^#{1,6}\s*', '', line)  # 제목 제거
    line = re.sub(r'^(\*|-|\+)\s+', '', line)  # 리스트 기호 제거
    line = re.sub(r'(\*\*|\*|__|_)', '', line)  # 인라인 스타일 제거
    return line

def classify_md_line(line: str) -> TextStyle:
    """
    마크다운 라인의 스타일 분류
    """
    if re.match(r'^#{1}\s+', line):
        return "제목"
    elif re.match(r'^#{2,6}\s+', line):
        return "중제목"
    elif re.match(r'^[-\*\+]\s+', line):
        return "리스트"
    else:
        return "본문"

def parse_md_file(md_path: str) -> list[dict]:
    """
    마크다운 파일을 분석하여 텍스트와 스타일 정보를 반환
    """
    results = []
    with open(md_path, "r", encoding="utf-8") as f:
        for line in f:
            cleaned = clean_md_line(line)
            if cleaned.strip():
                style = classify_md_line(line)
                results.append({"text": cleaned, "style": style})
    return results

def automate_hwp_roundtrip(input_hwp_path: str, output_hwp_path: str, styled_texts: list[dict]) -> None:
    """
    HWP 파일을 받아 -> HWPX로 변환 -> 압축 해제 -> section0 수정 -> 다시 HWP로 변환하는 전체 흐름
    """
    temp_dir = tempfile.mkdtemp()
    temp_hwpx = os.path.join(temp_dir, "converted.hwpx")
    temp_zip_dir = os.path.join(temp_dir, "unzipped")
    os.makedirs(temp_zip_dir, exist_ok=True)

    try:
        converter.convert_hwp_to_hwpx(input_hwp_path, temp_hwpx)
        compressor.unzip_hwpx(temp_hwpx, temp_zip_dir)
        parse_edit_section0.parse_and_edit_section0(temp_zip_dir, styled_texts)
        compressor.zip_hwpx(temp_zip_dir, temp_hwpx)
        converter.convert_hwpx_to_hwp(temp_hwpx, output_hwp_path)
    finally:
        shutil.rmtree(temp_dir)
        print("▶ 임시 폴더 정리 완료")

# 예시 실행
if __name__ == "__main__":
    # GUI로 파일 선택 (HWP 템플릿)
    root = Tk()
    root.withdraw()

    input_hwp = filedialog.askopenfilename(title="기반이 될 HWP 템플릿을 선택하세요", filetypes=[("HWP files", "*.hwp")])
    if not input_hwp:
        print("HWP 파일이 선택되지 않았습니다.")
        exit()

    md_path = filedialog.askopenfilename(title="삽입할 MD 파일을 선택하세요", filetypes=[("Markdown files", "*.md")])
    if not md_path:
        print("마크다운 파일이 선택되지 않았습니다.")
        exit()

    styled_texts = parse_md_file(md_path)

    output_hwp = os.path.abspath("final_output.hwp")
    automate_hwp_roundtrip(input_hwp, output_hwp, styled_texts)
