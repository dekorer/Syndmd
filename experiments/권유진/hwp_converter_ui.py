import sys
import win32com.client
import pythoncom
import os
import time
import traceback

def convert_hwp_to_pdf(hwp_file_path):
    hwp = None
    try:
        pythoncom.CoInitialize()
        hwp = win32com.client.Dispatch("HWPFrame.HwpObject")
        hwp.RegisterModule("FilePathCheckDLL", "SecurityModule") ##보안모듈 팝업 안뜨게(2번째 인자는 레지스트리에 등록한 이름으로 변경할것)
        abs_hwp_path = os.path.abspath(hwp_file_path)
        base_path, _ = os.path.splitext(abs_hwp_path)
        abs_pdf_path = base_path + ".pdf"

        if os.path.exists(abs_pdf_path):
            os.remove(abs_pdf_path)

        hwp.Open(abs_hwp_path)
        time.sleep(0.3)
        
        hwp.SaveAs(abs_pdf_path, "PDF")
        hwp.Quit()
        hwp = None
        
        for _ in range(50):
            if os.path.exists(abs_pdf_path) and os.path.getsize(abs_pdf_path) > 0:
                print(f"[PDF 변환] 최종 확인: PDF 파일 생성 성공.")
                sys.exit(0)
            time.sleep(0.1)

        raise Exception("PDF 파일이 생성되지 않았습니다.")

    except Exception as e:
        print(f"[PDF 변환] 심각한 오류 발생:")
        print(traceback.format_exc())
        if hwp:
            try: hwp.Quit()
            except: pass
        sys.exit(1)
    finally:
        pythoncom.CoUninitialize()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        hwp_path_arg = sys.argv[1]
        convert_hwp_to_pdf(hwp_path_arg)
    else:
        print("[PDF 변환] 오류: HWP 파일 경로가 필요합니다.")
        sys.exit(1)