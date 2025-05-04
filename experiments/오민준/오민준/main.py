import json
from parser import parse_markdown_to_structured_json
from preset import preset_official
from owpml_generator import convert_json_to_owpml, save_owpml_to_file

def main():
    input_md_path = "빈집문제.md"
    output_json_path = "parsed_output.json"
    output_owpml_path = "output.owpml"

    with open(input_md_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    structured_data = parse_markdown_to_structured_json(md_content)

    for block in structured_data:
        style = preset_official.get(block.get("style_key", ""), {})
        block["style"] = style

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(structured_data, f, ensure_ascii=False, indent=2)

    print("✅ JSON 저장 완료 -> parsed_output.json")

    root = convert_json_to_owpml(structured_data)
    save_owpml_to_file(root, "빈집문제.owpml")

    print("✅ OWPML 파일 생성 완료 -> 빈집문제.owpml")

if __name__ == "__main__":
    main()
