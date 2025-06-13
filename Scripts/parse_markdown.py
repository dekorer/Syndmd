import re

def parse_markdown(text: str):
    results = []

    for line in text.splitlines():
        line = line.rstrip()

        # 헤더 처리: # ~ ######까지
        heading_match = re.match(r'^(#{1,6})\s*(.+)', line)
        if heading_match:
            level = len(heading_match.group(1))
            content = heading_match.group(2).strip()
            # 숫자 넘버링 제거
            content = re.sub(r'^\s*\d+(?:\.\d+)*\.?\s*', '', content)
            results.append((f"title{level}", f"{content}"))
            continue

        # 리스트 처리: 들여쓰기 기준으로 list1, list2...
        list_match = re.match(r'^(\s*)([-*+])\s+(.+)', line)
        if list_match:
            indent_spaces = len(list_match.group(1))
            content = list_match.group(3).strip()
            level = indent_spaces // 2 + 1  # 들여쓰기 2칸당 한 단계
            results.append((f"list{level}", f"{content}"))
            continue

         # 해당 없음: None 처리 + 내용 그대로
        results.append((None, f"{line.strip()}"))

    print(results)
    return results
