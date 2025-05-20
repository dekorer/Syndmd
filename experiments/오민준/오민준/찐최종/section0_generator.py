import xml.etree.ElementTree as ET

def generate_section0(structured_data, template_pr_id="1", char_pr_map=None):
    ET.register_namespace("hp", "http://www.hancom.co.kr/hwpml/2010/paragraph")
    hp = "http://www.hancom.co.kr/hwpml/2010/paragraph"

    root = ET.Element(f"{{{hp}}}section")

    for block in structured_data:
        p = ET.SubElement(root, f"{{{hp}}}p")
        p.set("paraPrIDRef", template_pr_id)
        char_id = char_pr_map.get(f"제목{block['level']}", "1") if block["type"] == "heading" else "2"
        charPr = ET.SubElement(p, f"{{{hp}}}charPr")
        charPr.set("charPrIDRef", char_id)

        t = ET.SubElement(p, f"{{{hp}}}t")
        if block["type"] == "heading":
            t.text = block["text"]
        elif block["type"] == "paragraph":
            t.text = block["text"]
        elif block["type"] == "list_item":
            t.text = "• " + block["content"]
        elif block["type"] == "checklist":
            t.text = "☑ " + block["title"] + ": " + block["body"]

    tree = ET.ElementTree(root)
    output_path = "new_section0.xml"
    tree.write(output_path, encoding="utf-8", xml_declaration=True)
    return output_path

if __name__ == "__main__":
    import json
    with open("parsed_output.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    tree = generate_section0(data, char_pr_map={"제목1": "11", "제목2": "12"})
    tree.write("new_section0.xml", encoding="utf-8", xml_declaration=True)
