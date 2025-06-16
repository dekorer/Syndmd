import re

# 제목 앞의 넘버링 패턴 (1., 3.2., 2.1.1. 등) 제거
def clean_title(title: str) -> str:
    return re.sub(r'^\d+(\.\d+)*\.\s*', '', title)

def parse_markdown(text: str):
    results = []

    for line in text.splitlines():
        line = line.rstrip()
        if line == "":
            results.append(("blank", ""))
            continue

        # 제목 처리
        heading_match = re.match(r'^(#{1,6})\s*(.+)', line)
        if heading_match:
            level = len(heading_match.group(1))
            content = clean_title(heading_match.group(2).strip())
            results.append((f"title{level}", content))
            continue

        # 리스트 항목 처리
        list_match = re.match(r'^(\s*)([-*+])\s+(.+)', line)
        if list_match:
            indent_spaces = len(list_match.group(1))
            content = list_match.group(3).strip()
            level = indent_spaces // 2 + 1
            results.append((f"list{level}", content))
            continue

        # 일반 문단 처리
        results.append(("None", line.strip()))
    
    return results
