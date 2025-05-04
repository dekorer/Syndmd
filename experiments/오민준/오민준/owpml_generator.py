import xml.etree.ElementTree as ET

def create_owpml_root():
    root = ET.Element("owpml", attrib={
        "xmlns": "http://www.hancom.co.kr/owpml",
        "version": "1.0"
    })
    body = ET.SubElement(root, "body")
    section = ET.SubElement(body, "section")
    return root, section

def apply_style(element, style):
    if not style:
        return
    # 간단한 스타일 속성 적용 예시
    if style.get("bold"):
        element.set("bold", "true")
    if style.get("font"):
        element.set("font", style["font"])
    if style.get("font_size"):
        element.set("fontSize", str(style["font_size"]))
    if style.get("color"):
        element.set("color", style["color"])
    if style.get("align"):
        element.set("align", style["align"])
    if style.get("indent"):
        element.set("indent", str(style["indent"]))

def convert_json_to_owpml(data: list) -> ET.Element:
    root, section = create_owpml_root()

    for block in data:
        if block["type"] == "heading":
            para = ET.SubElement(section, "p", attrib={"type": f"h{block['level']}"})
            apply_style(para, block.get("style"))
            para.text = block["text"]

        elif block["type"] == "paragraph":
            para = ET.SubElement(section, "p")
            apply_style(para, block.get("style"))
            para.text = block["text"]

        elif block["type"] == "list_item":
            para = ET.SubElement(section, "list")
            apply_style(para, block.get("style"))
            para.text = block["content"]

        elif block["type"] == "checklist":
            para = ET.SubElement(section, "check")
            apply_style(para, block.get("style"))
            para.set("title", block["title"])
            para.text = block["body"]

    return root

def save_owpml_to_file(root: ET.Element, output_path: str):
    tree = ET.ElementTree(root)
    tree.write(output_path, encoding="utf-8", xml_declaration=True)

if __name__ == "__main__":
    import json

    with open("parsed_output.json", "r", encoding="utf-8") as f:
        parsed = json.load(f)

    root = convert_json_to_owpml(parsed)
    save_owpml_to_file(root, "빈집문제.owpml")
    print("✅ OWPML 생성 완료 -> 빈집문제.owpml")
