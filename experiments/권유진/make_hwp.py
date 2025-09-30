# make_hwp.py

import sys
import win32com.client
import pythoncom
import os
import time
import traceback
import pyperclip

def create_hwp_from_file(input_text_file_path, output_hwp_path):
    hwp = None
    try:
        with open(input_text_file_path, "r", encoding="utf-8") as f:
            text_content = f.read()
        pyperclip.copy(text_content)## 클립보드에 텍스트(textEdit) 복사 상태

        ##여 아래로 변환 코드 연결할 것(아래 다 지우삼)
        
        pythoncom.CoInitialize()
        # 1. hwp 객체 하나만 생성합니다.
        hwp = win32com.client.Dispatch("HWPFrame.HwpObject")
        hwp.RegisterModule("FilePathCheckDLL", "SecurityModule") ##보안모듈 팝업 안뜨게(2번째 인자는 레지스트리에 등록한 이름으로 변경할것)

        # 2. '새 문서' 매크로를 실행합니다.
        hwp.Run("FileNew")
        time.sleep(0.2)
        
        # 3. '붙여넣기' 매크로를 실행합니다.
        hwp.Run("Paste")
        time.sleep(0.2)

        # 4. '다른 이름으로 저장'은 SaveAs 메소드를 직접 호출합니다.
        #    Format="HWP"를 명시해주는 것이 더 안정적일 수 있습니다.
        hwp.SaveAs(os.path.abspath(output_hwp_path), "HWP")
        
        time.sleep(0.5)
        hwp.Quit()
        hwp = None
        
        if not os.path.exists(output_hwp_path):
            raise Exception("HWP 파일이 디스크에 생성되지 않았습니다.")
            
        print(f"[HWP 생성] 성공: {output_hwp_path}")
        
    except Exception as e:
        print(f"[HWP 생성] 심각한 오류 발생:")
        print(traceback.format_exc())
        if hwp:
            try: hwp.Quit()
            except: pass
        sys.exit(1)
    finally:
        pythoncom.CoUninitialize()

if __name__ == "__main__":
    if len(sys.argv) == 3:
        input_path = sys.argv[1]
        output_path = sys.argv[2]
        create_hwp_from_file(input_path, output_path)
    else:
        print(f"[HWP 생성] 오류: 입력 파일 경로와 출력 파일 경로가 모두 필요합니다.")
        sys.exit(1)

