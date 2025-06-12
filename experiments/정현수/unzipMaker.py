import os
import zipfile
import win32com.client

def convert_hwp_to_hwpx(hwp_path, hwpx_path):
    hwp = win32com.client.gencache.EnsureDispatch("HWPFrame.HwpObject")
    hwp.XHwpWindows.Item(0).Visible = True
    hwp.RegisterModule("FilePathCheckDLL", "SecurityModule")
    hwp.Open(hwp_path)
    hwp.SaveAs(hwpx_path, "HWPX")
    hwp.Quit()
    print(f"변환 완료: {hwpx_path}")

def unzip_hwpx(hwpx_path: str, output_dir: str) -> None:
    with zipfile.ZipFile(hwpx_path, 'r') as zip_ref:
        zip_ref.extractall(output_dir)
    print("▶ HWPX 압축 해제 완료:", output_dir)

def process_hwp_file(filename: str):
    # 현재 작업 디렉토리 기준으로 경로 구성
    base_dir = os.getcwd()
    hwp_path = os.path.join(base_dir, filename)

    if not os.path.isfile(hwp_path):
        raise FileNotFoundError(f"HWP 파일이 현재 폴더에 없습니다: {filename}")

    base_name = os.path.splitext(filename)[0]
    hwpx_path = os.path.join(base_dir, f"{base_name}.hwpx")
    extract_dir = os.path.join(base_dir, f"{base_name}_unzipped")

    convert_hwp_to_hwpx(hwp_path, hwpx_path)
    unzip_hwpx(hwpx_path, extract_dir)

    return extract_dir

if __name__ == "__main__":
    # 현재 폴더에 있는 HWP 파일 이름만 입력
    hwp_filename = "한글-템플릿1.hwp"
    output_folder = process_hwp_file(hwp_filename)
    print("압축 해제된 폴더 경로:", output_folder)
