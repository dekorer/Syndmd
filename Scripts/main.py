import os
import shutil
import tempfile
import converter
import compressor
import parse_edit_section0

def automate_hwp_roundtrip(input_hwp_path: str, output_hwp_path: str) -> None:
    temp_dir = tempfile.mkdtemp()
    temp_hwpx = os.path.join(temp_dir, "converted.hwpx")
    temp_zip_dir = os.path.join(temp_dir, "unzipped")
    os.makedirs(temp_zip_dir, exist_ok=True)

    try:
        converter.convert_hwp_to_hwpx(input_hwp_path, temp_hwpx)
        compressor.unzip_hwpx(temp_hwpx, temp_zip_dir)
        parse_edit_section0.parse_and_edit_section0(temp_zip_dir)
        compressor.zip_hwpx(temp_zip_dir, temp_hwpx)
        converter.convert_hwpx_to_hwp(temp_hwpx, output_hwp_path)

    finally:
        shutil.rmtree(temp_dir)
        print("▶ 임시 폴더 정리 완료")

# 실행 예시
if __name__ == "__main__":
    input_hwp = os.path.abspath("한글-템플릿1.hwp")
    output_hwp = os.path.abspath("결과물.hwp")

    automate_hwp_roundtrip(input_hwp, output_hwp)