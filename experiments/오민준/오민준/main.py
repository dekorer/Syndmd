import json
from parser import parse_markdown_to_structured_json
from preset import preset_official

def main():
    input_md_path = "빈집문제.md"
    output_json_path = "parsed_output.json"

    # 마크다운 파일 불러오기
    with open(input_md_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    # 파싱
    structured_data = parse_markdown_to_structured_json(md_content)

    # 프리셋 스타일 적용
    for block in structured_data:
        style = preset_official.get(block.get("style_key", ""), {})
        block["style"] = style

    # 결과 저장
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(structured_data, f, ensure_ascii=False, indent=2)

    print("✅ 변환 완료 -> parsed_output.json")

if __name__ == "__main__":
    main()
