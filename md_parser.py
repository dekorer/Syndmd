import re
from typing import List, Tuple

def parse_markdown(text: str) -> List[Tuple[str, str]]:
    """
    마크다운 텍스트를 (kind, content) 튜플 리스트로 파싱합니다.
    """
    results = []

    for line in text.splitlines():
        line = line.rstrip()
        if line == "":
            results.append(("blank", ""))
            continue

        # 헤더 처리: # ~ ######까지
        heading_match = re.match(r'^(#{1,6})\s*(.+)', line)
        if heading_match:
            level = len(heading_match.group(1))
            content = heading_match.group(2).strip()
            results.append((f"title{level}", content))
            continue

        # 리스트 처리: 들여쓰기 기준으로 list1, list2...
        list_match = re.match(r'^(\s*)([-*+])\s+(.+)', line)
        if list_match:
            indent_spaces = len(list_match.group(1))
            content = list_match.group(3).strip()
            level = indent_spaces // 2 + 1  # 들여쓰기 2칸당 한 단계
            results.append((f"list{level}", content))
            continue

         # 해당 없음: None 처리 + 내용 그대로
        results.append(("None", line.strip()))

    return results

def clean_title(title: str) -> str:
    """
    제목 앞의 넘버링 패턴(예: '1.', '2.1.1.', '(3)')을 제거합니다.
    """
    pattern = r'''
        ^                                           # 시작
        (?:
            \d+(?:\.\d+)*(?:\.)?                    # 1 / 1.1 / 1.1.1 / 1.1. (점 옵션)
          | \(\d+(?:\.\d+)*\)                       # (1) / (1.1)
          | \d+\)                                   # 1)
        )
        [\s\-–—]* # 뒤 공백/대시류
    '''
    return re.sub(pattern, '', title, flags=re.VERBOSE)

def clean_parsed_markdown(tokens: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    """
    파싱된 토큰 리스트에서 'title' 타입의 텍스트만 clean_title을 적용합니다.
    """
    cleaned: List[Tuple[str, str]] = []
    for kind, text in tokens:
        if kind.startswith("title"):
            cleaned.append((kind, clean_title(text)))
        else:
            cleaned.append((kind, text))
    return cleaned

def print_parsed_markdown(tokens: List[Tuple[str, str]]) -> None:
    """
    토큰들을 간단히 정리해서 콘솔에 출력합니다. (디버깅/확인용)
    """
    for kind, text in tokens:
        if kind == "blank":
            print("")  # 빈 줄 유지
            continue
        if kind.startswith("title"):
            print(f"[{kind.upper()}] {text}")
        elif kind.startswith("list"):
            print(f"[{kind.upper()}] {text}")
        elif kind == "None":
            print(f"[TEXT] {text}")
        else:
            # 혹시 모를 확장 토큰 대비
            print(f"[{kind}] {text}")

def parse_and_show_markdown(md_text: str) -> List[Tuple[str, str]]:
    """
    주어진 마크다운 문자열을 파싱 → 제목 번호 제거 → 콘솔 출력.
    반환값은 정리된 토큰 리스트(후속 처리용).
    """
    tokens = parse_markdown(md_text)
    cleaned = clean_parsed_markdown(tokens)
    print_parsed_markdown(cleaned)
    return cleaned