import os
import xml.etree.ElementTree as ET

# 특수 기호나 장식 글자 등 대체하지 않을 텍스트 정의
EXCLUDED_TEXTS = {'▢', '❍', 'Ⅰ', 'Ⅱ', 'Ⅲ', 'Ⅳ', 'Ⅴ', 'Ⅵ', 'Ⅶ'}

def parse_and_edit_section0(unzipped_path: str, new_texts: list[str]) -> None:
    section_path = os.path.join(unzipped_path, "Contents", "section0.xml")
    tree = ET.parse(section_path)
    root = tree.getroot()
    ns = {"hp": "http://www.hancom.co.kr/hwpml/2011/paragraph"}
    paragraphs = root.findall("hp:p", ns)

    paragraph_dir = os.path.join(os.getcwd(), "paragraphs")
    os.makedirs(paragraph_dir, exist_ok=True)

    count = 0
    for i, p in enumerate(paragraphs):
        ts = p.findall(".//hp:t", ns)
        for t in ts:
            if t.text and t.text.strip() and t.text.strip() not in EXCLUDED_TEXTS:
                if count < len(new_texts):
                    t.text = new_texts[count]["text"]
                    count += 1

        xml_string = ET.tostring(p, encoding='unicode')
        filename = os.path.join(paragraph_dir, f"paragraph_{i}.xml")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(xml_string)
        print(f"▶ paragraphs[{i}] 저장 완료: {filename}")

    tree.write(section_path, encoding="utf-8", xml_declaration=True)
    print("▶ section0.xml 수정 완료")

    modified_output_path = os.path.join(os.getcwd(), "modified_section0.xml")
    tree.write(modified_output_path, encoding="utf-8", xml_declaration=True)
    print(f"▶ 수정된 section0.xml 백업 저장 완료 → {modified_output_path}")
