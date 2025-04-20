import re

def parse_markdown_to_tagged_text(markdown: str) -> str:
    lines = markdown.splitlines()
    result = []
    heading_counter = [0] * 6  # 제목 계층용 번호 추적 (예: I, 1, 1.1 등)

    for line in lines:
        line = line.strip()
        if not line:
            continue  # 빈 줄은 생략

        # 제목 처리 (H1 ~ H6)
        heading_match = re.match(r'^(#{1,6}) (.+)', line)
        if heading_match:
            hashes, text = heading_match.groups()
            level = len(hashes)
            heading_counter[level - 1] += 1
            for i in range(level, 6):
                heading_counter[i] = 0  # 하위 제목 카운터 리셋

            if level == 1:
                tag = "[제목1][굴림][20][#000000][bold][왼쪽]"
                numbered = f"{text}"
            elif level == 2:
                # 로마자 번호 변환
                roman = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII']
                tag = "[제목2][굴림][18][#1A365D][bold][왼쪽][장식:라인]"
                numbered = f"[번호:{roman[heading_counter[1]-1]}] {text}"
            elif level == 3:
                tag = "[제목3][굴림][16][#333333][bold][왼쪽]"
                numbered = f"[번호:{heading_counter[2]}] {text}"
            else:
                tag = f"[제목{level}][굴림][14][#444444][bold][왼쪽]"
                numbered = text

            result.append(f"{tag}{numbered}")
            continue

        # 체크리스트 항목 (강조 포함)
        checklist_match = re.match(r'^-\s+\*\*(.+?)\*\*:\s*(.+)', line)
        if checklist_match:
            title, body = checklist_match.groups()
            tag = "[체크리스트][굴림][12][#000000][checkbox:true]"
            result.append(f"{tag}- [강조]{title}[/강조]: {body}")
            continue

        # 일반 리스트 항목
        if line.startswith('- '):
            content = line[2:].strip()
            tag = "[리스트][굴림][12][#000000][indent:1]"
            result.append(f"{tag}- {content}")
            continue

        # 본문
        tag = "[본문][굴림][12][#000000][정렬:양쪽]"
        result.append(f"{tag}{line}")

    return '\n'.join(result)

if __name__ == "__main__":
    input_md_path = "빈집문제.md"
    output_txt_path = "../parsed_output.txt"

    # 마크다운 파일 불러오기
    with open(input_md_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    # 파싱
    tagged_text = parse_markdown_to_tagged_text(md_content)

    # 출력 파일 저장
    with open(output_txt_path, "w", encoding="utf-8") as f:
        f.write(tagged_text)

    print("변환 완료 -> parsed_output.txt")
