import os
import win32com.client

# HWP->HWPX
def convert_hwp_to_hwpx(hwp_path, hwpx_path):
    # HWP 경로가 유효한지 확인
    if not os.path.isfile(hwp_path):
        raise FileNotFoundError(f"HWP 파일을 찾을 수 없습니다: {hwp_path}")
    # 한/글 실행
    hwp = win32com.client.gencache.EnsureDispatch("HWPFrame.HwpObject")

    hwp.XHwpWindows.Item(0).Visible = True  # 옵션: 실행 창 보이기
    # 보안 모듈 비활성화 (비밀번호 있는 문서 등)
    hwp.RegisterModule("FilePathCheckDLL", "SecurityModule")
    # 파일 열기
    hwp.Open(hwp_path)
    # 다른 이름으로 저장 (포맷 코드 51 = HWPX)
    # HWPX 저장
    hwp.SaveAs(hwpx_path, "HWPX")
    # 한/글 종료
    hwp.Quit()
    print(f"변환 완료: {hwpx_path}")

# HWPX->HWP
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