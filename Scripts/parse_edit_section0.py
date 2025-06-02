import os
import xml.etree.ElementTree as ET

# 제외할 특문 목록
EXCLUDE_TEXTS = {"▢", "❍", "Ⅰ", "Ⅱ", "Ⅲ", "Ⅳ", "Ⅴ", "Ⅵ", "Ⅶ", "Ⅷ", "Ⅸ", "Ⅹ"}

def is_replacable(text):
    if not text:
        return False
    return text.strip() not in EXCLUDE_TEXTS

def parse_and_edit_section0(unzipped_path: str, new_texts: list[str]) -> None:
    """section0.xml을 파싱하고 텍스트 수정"""
    section_path = os.path.join(unzipped_path, "Contents", "section0.xml")
    tree = ET.parse(section_path)
    root = tree.getroot()

    ns = {"hp": "http://www.hancom.co.kr/hwpml/2011/paragraph"}
    paragraphs = root.findall("hp:p", ns)  # 문단 기준으로 나눔

    # paragraph 파일 저장 폴더 생성하고 이 폴더에 paragraphs저장
    paragraph_dir = os.path.join(os.getcwd(), "paragraphs")
    os.makedirs(paragraph_dir, exist_ok=True)

    count = 0
    for i, p in enumerate(paragraphs):
        ts = p.findall(".//hp:t", ns)

        # 텍스트 있는 문단인지 확인 후 대체
        for t in ts:
            if t.text and t.text.strip() and is_replacable(t.text):
                if count < len(new_texts):
                    t.text = new_texts[count]
                    count += 1

        # paragraphs[i]를 XML 문자열로 변환해서 파일로 저장
        xml_string = ET.tostring(p, encoding='unicode')
        filename = os.path.join(paragraph_dir, f"paragraph_{i}.xml")

        with open(filename, "w", encoding="utf-8") as f:
            f.write(xml_string)
        print(f"▶ paragraphs[{i}] 저장 완료: {filename}")

    tree.write(section_path, encoding="utf-8", xml_declaration=True)
    print("▶ section0.xml 수정 완료")

    # section0 수정본을 별도로 저장
    modified_output_path = os.path.join(os.getcwd(), "modified_section0.xml")
    tree.write(modified_output_path, encoding="utf-8", xml_declaration=True)
    print(f"▶ 수정된 section0.xml 백업 저장 완료 → {modified_output_path}")
