import os
import xml.etree.ElementTree as ET

def parse_and_edit_section0(unzipped_path: str, styled_texts: list[dict]) -> None:
    section_path = os.path.join(unzipped_path, "Contents", "section0.xml")
    tree = ET.parse(section_path)
    root = tree.getroot()

    ns = {"hp": "http://www.hancom.co.kr/hwpml/2011/paragraph"}
    paragraphs = root.findall(".//hp:p", ns)

    paragraph_dir = os.path.join(os.getcwd(), "paragraphs")
    os.makedirs(paragraph_dir, exist_ok=True)

    special_tokens = {"Ⅰ", "Ⅱ", "Ⅲ", "Ⅳ", "Ⅴ", "Ⅵ", "▢", "❍", "⦁", "●"}
    count = 0

    for i, p in enumerate(paragraphs):
        ts = p.findall(".//hp:t", ns)
        paragraph_modified = False

        for t in ts:
            if count >= len(styled_texts):
                break

            # 특문이거나 빈 텍스트인 경우 건너뜀
            original_text = t.text or ""
            stripped = original_text.strip()
            if not stripped or stripped in special_tokens:
                continue

            # 텍스트 대체 (스타일 유지)
            new_text = styled_texts[count]["text"]
            t.text = new_text
            count += 1
            paragraph_modified = True

        # 수정된 paragraph 저장
        xml_string = ET.tostring(p, encoding='unicode')
        with open(os.path.join(paragraph_dir, f"paragraph_{i}.xml"), "w", encoding="utf-8") as f:
            f.write(xml_string)
        if paragraph_modified:
            print(f"▶ paragraphs[{i}] 저장 완료")

    # section0.xml 저장
    tree.write(section_path, encoding="utf-8", xml_declaration=True)
    backup_path = os.path.join(os.getcwd(), "modified_section0.xml")
    tree.write(backup_path, encoding="utf-8", xml_declaration=True)
    print(f"▶ 수정된 section0.xml 백업 저장 완료 → {backup_path}")
