import sys
import os
import win32com.client as win32
import pythoncom
import traceback

def create_blank_hwp_with_dummy_args():
    if len(sys.argv) != 5:
        print("Error: This script requires exactly 4 arguments.")
        sys.exit(1)


    # 인자 1: 텍스트 내용이 담긴 임시 텍스트 파일의 경로
    # text_path = sys.argv[1]

    #인자 2: 생성될 HWP 파일의 전체 경로
    output_hwp_path = sys.argv[2]

    # 인자 3: 사용자가 선택한 템플릿 파일의 경로
    # template_path = sys.argv[3]
    
    # 인자 4: 사용자가 선택한 템플릿의 페이지 번호
    # template_page = sys.argv[4]


    hwp = None
    exit_code = 0  # 성공 시 0, 실패 시 1

    try:
        pythoncom.CoInitialize()
        hwp = win32.gencache.EnsureDispatch("HWPFrame.HwpObject")
        hwp.RegisterModule("FilePathCheckDLL", "SecurityModule") ##보안모듈 팝업 안뜨게(2번째 인자는 레지스트리에 등록한 이름으로 변경할것)
        hwp.Clear(1)
        hwp.SaveAs(output_hwp_path)
        
    except Exception as e:
        print(f"An error occurred in converter_test.py:")
        # 오류의 상세 내용을 터미널에 출력
        print(traceback.format_exc())
        exit_code = 1
    finally:
        if hwp:
            try:
                hwp.Quit()
            except Exception:
                # 종료 시 오류가 발생해도 무시
                pass
            hwp = None 
        
        pythoncom.CoUninitialize()
        print(f"converter_test.py finished with exit code {exit_code}.")
        sys.exit(exit_code)

if __name__ == "__main__":
    create_blank_hwp_with_dummy_args()