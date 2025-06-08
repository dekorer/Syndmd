import os
import win32com.client

# HWP → HWPX 변환 함수
def convert_hwp_to_hwpx(hwp_path, hwpx_path):
    if not os.path.isfile(hwp_path):
        raise FileNotFoundError(f"HWP 파일을 찾을 수 없습니다: {hwp_path}")
    hwp = win32com.client.gencache.EnsureDispatch("HWPFrame.HwpObject")
    hwp.XHwpWindows.Item(0).Visible = True
    hwp.RegisterModule("FilePathCheckDLL", "SecurityModule")
    hwp.Open(hwp_path)
    hwp.SaveAs(hwpx_path, "HWPX")
    hwp.Quit()
    print(f"변환 완료: {hwpx_path}")

# HWPX → HWP 변환 함수
def convert_hwpx_to_hwp(hwpx_path, hwp_path):
    if not os.path.isfile(hwpx_path):
        raise FileNotFoundError(f"HWPX 파일을 찾을 수 없습니다: {hwpx_path}")
    hwp = win32com.client.gencache.EnsureDispatch("HWPFrame.HwpObject")
    hwp.XHwpWindows.Item(0).Visible = False
    hwp.RegisterModule("FilePathCheckDLL", "SecurityModule")
    hwp.Open(hwpx_path)
    hwp.SaveAs(hwp_path, "HWP")
    hwp.Quit()
    print(f"변환 완료: {hwp_path}")