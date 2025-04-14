import win32com.client as win32
import re

def change_title():
    print("change_title() called")

def change_bullet():
    print("change_bullet() called")

def change_indent():
    print("change_indent() called")

def change(baseword):
    return f"[strong]{baseword}[strong]"

source_path = "C:/Users/pc/Desktop/텍스트변환.txt"

with open(source_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()



for line in lines:
    # 제목 처리
    line, num_title = re.subn(r'제목 h[12]:?', '', line)
    if num_title > 0:
        change_title()

    # 리스트 처리
    line, num_bullet = re.subn(r'불릿형', '', line)
    if num_bullet > 0:
        change_bullet()

    # 들여쓰기 처리
    if '들여쓰기 None' in line:
        line = line.replace('들여쓰기 None', '')
    else:
        line, num_indent = re.subn(r'들여쓰기 [0-2]', '', line)
        if num_indent > 0:
            change_indent()

    # 쓰레기 패턴 제거
    line = re.sub(r'리스트\s*\(\s*,\s*\)\s*:', '', line)

    # **강조 텍스트** 추출 및 변환
    def replace_strong(match):
        baseword = match.group(1).strip()
        if '(' in baseword:
            baseword = baseword.split('(')[0].strip()
        return change(baseword)

    line = re.sub(r'\*\*(.*?)\*\*', replace_strong, line)
 
    # 정제된 결과 출력
    print(line.strip())
