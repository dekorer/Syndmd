import os
import shutil
import tempfile
import converter
import compressor
from merge_section0 import merge_paragraphs_with_header

def build_hwp_from_template_folder(
    template_unzipped_dir: str,
    paragraph_dir: str,
    output_hwp_path: str,
    templateNum: int
) -> None:
    temp_dir = tempfile.mkdtemp()
    working_dir = os.path.join(temp_dir, "hwpx_build")
    os.makedirs(working_dir, exist_ok=True)

    try:
        # 1. 템플릿 디렉터리 복사
        shutil.copytree(template_unzipped_dir, working_dir, dirs_exist_ok=True)

        # 2. 병합된 section0.xml로 교체
        section0_path = os.path.join(working_dir, "Contents", "section0.xml")
        merge_paragraphs_with_header(paragraph_dir, section0_path, templateNum)

        # 3. hwpx로 압축
        temp_hwpx_path = os.path.join(temp_dir, "merged.hwpx")
        compressor.zip_hwpx(working_dir, temp_hwpx_path)

        # 4. hwpx → hwp 변환
        converter.convert_hwpx_to_hwp(temp_hwpx_path, output_hwp_path)

    finally:
        shutil.rmtree(temp_dir)
        print("▶ 임시 작업 폴더 정리 완료")

# 예시 실행
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    template_unzipped_dir = os.path.join(current_dir, "template1_unzipped")
    paragraph_dir = os.path.join(current_dir, "paragraphs")
    output_hwp_path = os.path.join(current_dir, "결과문서.hwp")
    templateNum = 1

    build_hwp_from_template_folder(template_unzipped_dir, paragraph_dir, output_hwp_path, templateNum)