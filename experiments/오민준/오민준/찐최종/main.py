import json
import os
import shutil
import zipfile
import tkinter as tk
from tkinter import filedialog
from parser import parse_markdown_to_structured_json
from section_editor import replace_text_in_section0
from owpml_packager import package_owpml
import win32com.client as win32
import time

def select_file(title, filetypes):
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename(title=title, filetypes=filetypes)

def convert_hwp_to_owpml(hwp_path, owpml_save_path):
    hwp = win32.gencache.EnsureDispatch("HWPFrame.HwpObject.1")
    hwp.Open(hwp_path, "HWP", "")
    time.sleep(0.5)  # 저장 직후 파일 시스템 안정화를 위해 대기
    success = hwp.SaveAs(owpml_save_path, "HWPML2X", "")

    hwp.Quit()
    if not success:
        raise RuntimeError(f"OWPML 저장 실패: {owpml_save_path}")

def is_zip_file(path):
    with open(path, 'rb') as f:
        sig = f.read(4)
        return sig == b'PK\x03\x04'

def main():
    print("변환할 .hwp 파일을 선택하세요")
    hwp_path = select_file("HWP 파일 선택", [("HWP files", "*.hwp")])

    print("변환할 .md 파일을 선택하세요")
    md_path = select_file("Markdown 파일 선택", [("Markdown files", "*.md")])

    owpml_template = os.path.abspath("template.owpml")

    # Step 1: HWP → OWPML 저장
    convert_hwp_to_owpml(hwp_path, owpml_template)
    print("Step1 done.")

    # Step 2: OWPML 압축 해제 (확장자만 zip으로 임시 변경)
    zip_path = "template.zip"
    if os.path.exists(zip_path):
        os.remove(zip_path)
    os.rename(owpml_template, zip_path)

    unzip_dir = "unpacked"
    if os.path.exists(unzip_dir):
        shutil.rmtree(unzip_dir)
    os.makedirs(unzip_dir)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(unzip_dir)
    print("Step2 done.")

    # Step 3: Markdown → JSON
    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()
    parsed = parse_markdown_to_structured_json(md_content)
    parsed_json_path = os.path.join(unzip_dir, "parsed_output.json")
    with open(parsed_json_path, "w", encoding="utf-8") as f:
        json.dump(parsed, f, ensure_ascii=False, indent=2)
    print("Step3 done.")

    # Step 4: section0.xml 텍스트 교체
    section0_path = os.path.join(unzip_dir, "Contents", "section0.xml")
    new_section0_path = os.path.join(unzip_dir, "new_section0.xml")
    replace_text_in_section0(section0_path, parsed_json_path, new_section0_path)
    shutil.copy(new_section0_path, section0_path)
    print("Step4 done.")

    # Step 5: 다시 압축하여 OWPML 생성
    output_final_owpml = "최종_변환본.owpml"
    shutil.make_archive("final_output", 'zip', unzip_dir)
    shutil.move("final_output.zip", output_final_owpml)

    print(f"변환 완료: {output_final_owpml}")

if __name__ == "__main__":
    main()
