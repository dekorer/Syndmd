import os
import zipfile

# HWPX 압축해제
def unzip_hwpx(hwpx_path: str, output_dir: str) -> None:
    with zipfile.ZipFile(hwpx_path, 'r') as zip_ref:
        zip_ref.extractall(output_dir)
    print("▶ HWPX 압축 해제 완료")

# HWPX로 압축
def zip_hwpx(folder_path: str, output_hwpx_path: str) -> None:
    with zipfile.ZipFile(output_hwpx_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)
    print("▶ 수정된 HWPX 파일 압축 완료")