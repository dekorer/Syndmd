import os
import shutil
import tempfile
import converter
import compressor
from parser import parse_markdown
from parse_edit_section0 import parse_and_edit_section0


def automate_hwp_roundtrip(input_hwp_path: str, output_hwp_path: str, markdown_path: str) -> None:
    temp_dir = tempfile.mkdtemp()
    temp_hwpx = os.path.join(temp_dir, "converted.hwpx")
    temp_zip_dir = os.path.join(temp_dir, "unzipped")
    os.makedirs(temp_zip_dir, exist_ok=True)

    try:
        # 1. .hwp → .hwpx 변환
        converter.convert_hwp_to_hwpx(input_hwp_path, temp_hwpx)

        # 2. 압축 해제
        compressor.unzip_hwpx(temp_hwpx, temp_zip_dir)

        # 3. 마크다운 파싱
        with open(markdown_path, encoding="utf-8") as f:
            md_text = f.read()
        parsed = parse_markdown(md_text)

        # 4. 템플릿 추출 및 section0.xml 재생성
        parse_and_edit_section0(temp_zip_dir, parsed)

        # 5. 다시 압축
        compressor.zip_hwpx(temp_zip_dir, temp_hwpx)

        # 6. .hwpx → .hwp 복원
        converter.convert_hwpx_to_hwp(temp_hwpx, output_hwp_path)

    finally:
        shutil.rmtree(temp_dir)
        print("▶ 임시 폴더 정리 완료")


# 실행 예시
if __name__ == "__main__":
    input_hwp = os.path.abspath("한글-템플릿3.hwp")
    output_hwp = os.path.abspath("final_output.hwp")
    markdown_path = os.path.abspath("input.md")

    automate_hwp_roundtrip(input_hwp, output_hwp, markdown_path)
