import xml.etree.ElementTree as ET
import json

def replace_text_in_section0(section0_path: str, parsed_json_path: str, output_path: str):
    ET.register_namespace("hp", "http://www.hancom.co.kr/hwpml/2010/paragraph")
    ns = {"hp": "http://www.hancom.co.kr/hwpml/2010/paragraph"}

    tree = ET.parse(section0_path)
    root = tree.getroot()

    with open(parsed_json_path, "r", encoding="utf-8") as f:
        parsed = json.load(f)

    text_nodes = root.findall(".//hp:t", ns)

    if len(text_nodes) != len(parsed):
        raise ValueError(f"❌ 텍스트 수 불일치: section0에 {len(text_nodes)}개, md에는 {len(parsed)}개 있음")

    for node, data in zip(text_nodes, parsed):
        if data["type"] == "heading":
            node.text = data["text"]
        elif data["type"] == "paragraph":
            node.text = data["text"]
        elif data["type"] == "list_item":
            node.text = "• " + data["content"]
        elif data["type"] == "checklist":
            node.text = "☑ " + data["title"] + ": " + data["body"]
        else:
            node.text = ""

    tree.write(output_path, encoding="utf-8", xml_declaration=True)
    return output_path