import re
from preset import preset_official

def parse_markdown_to_structured_json(markdown: str) -> list:
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

            result.append({
                "type": "heading",
                "level": level,
                "text": text.strip(),
                "style_key": f"제목{level}"
            })
            continue

        # 체크리스트 항목 (강조 포함)
        checklist_match = re.match(r'^-\s+\*\*(.+?)\*\*:\s*(.+)', line)
        if checklist_match:
            title, body = checklist_match.groups()
            result.append({
                "type": "checklist",
                "title": title.strip(),
                "body": body.strip(),
                "style_key": "체크리스트"
            })
            continue

        # 일반 리스트 항목
        if line.startswith('- '):
            content = line[2:].strip()
            result.append({
                "type": "list_item",
                "content": content,
                "ordered": False,
                "style_key": "리스트"
            })
            continue

        # 본문 텍스트
        result.append({
            "type": "paragraph",
            "text": line,
            "style_key": "본문"
        })

    return result

if __name__ == "__main__":
    input_md_path = "빈집문제.md"
    output_json_path = "parsed_output.json"
    import json

    # 마크다운 파일 불러오기
    with open(input_md_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    # 파싱
    structured_data = parse_markdown_to_structured_json(md_content)

    # 스타일 프리셋 적용
    for item in structured_data:
        style = preset_official.get(item.get("style_key", ""), {})
        item["style"] = style

    # 출력 파일 저장
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(structured_data, f, ensure_ascii=False, indent=2)

    print("변환 완료 -> parsed_output.json")
