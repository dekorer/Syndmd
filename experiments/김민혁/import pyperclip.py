import pyperclip
import time
import os
import pypandoc

# 저장 위치 및 파일 이름 설정
SAVE_DIR = os.path.join(os.path.expanduser("~"), "Desktop")
BASE_FILENAME = "MDtoHWP"

def convert_md_to_docx(md_text, docx_path):
    pypandoc.convert_text(md_text, 'docx', format='md', outputfile=docx_path)

def monitor_clipboard():
    prev_text = pyperclip.paste()
    while True:
        text = pyperclip.paste()

        if text != prev_text and "#" in text:
            print("[📋] 클립보드 감지.")
            docx_path = os.path.join(SAVE_DIR, f"{BASE_FILENAME}.docx")

            try:
                convert_md_to_docx(text, docx_path)
                print(f"[✅] Word 파일 저장 완료: {docx_path}")
            except Exception as e:
                print(f"[❌] 변환 실패: {e}")

            prev_text = text
        time.sleep(1)


if __name__ == "__main__":
    print("👀 클립보드를 감시 중... Markdown을 복사하면 Word로 저장됩니다.")
    monitor_clipboard()
