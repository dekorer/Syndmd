import os
import xml.etree.ElementTree as ET

ET.register_namespace("hp", "http://www.hancom.co.kr/hwpml/2011/paragraph")

def parse_and_edit_section0(unzipped_path: str) -> None:
    section_path = os.path.join(unzipped_path, "Contents", "section0.xml")
    output_dir = os.path.join("paragraphs")
    os.makedirs(output_dir, exist_ok=True)

    # step 1: 헤더 텍스트 추출
    with open(section_path, encoding="utf-8") as f:
        xml_text = f.read()

    first_p_index = xml_text.find("<hp:p")
    if first_p_index != -1:
        header_text = xml_text[:first_p_index]
        header_path = os.path.join(output_dir, "header.xml")
        with open(header_path, "w", encoding="utf-8") as f:
            f.write(header_text)
        print("▶ header.xml 저장 완료")

    # step 2: 문단 파싱 및 텍스트 수정    
    tree = ET.parse(section_path)
    root = tree.getroot()

    ns = {"hp": "http://www.hancom.co.kr/hwpml/2011/paragraph"}
    paragraphs = root.findall("hp:p", ns)

    for idx, p in enumerate(paragraphs):
        # linesegarray 제거
        for segarray in p.findall(".//hp:linesegarray", ns):
            if segarray in list(p):
                p.remove(segarray)

        # XML 선언 없이 문단 저장
        paragraph_str = ET.tostring(p, encoding="utf-8").decode("utf-8")
        filename = f"paragraph_{idx}.xml"
        with open(os.path.join(output_dir, filename), "w", encoding="utf-8") as f:
            f.write(paragraph_str)

    print("▶ section0.xml 수정 완료")
