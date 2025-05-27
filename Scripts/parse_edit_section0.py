import os
import xml.etree.ElementTree as ET

def parse_and_edit_section0(unzipped_path: str, new_texts: list[str]) -> None:
    """section0.xml을 파싱하고 텍스트 수정"""
    section_path = os.path.join(unzipped_path, "Contents", "section0.xml")
    tree = ET.parse(section_path)
    root = tree.getroot()

    ns = {"hp": "http://www.hancom.co.kr/hwpml/2011/paragraph"}

    paragraphs = root.findall("hp:p", ns) # 맨 바깥쪽 문단 별로 나눔
    count = 0
    i = 0
    for p in paragraphs:
        ts = p.findall(".//hp:t", ns)

        # 텍스트 있는 문단인지 확인
        for t in ts:
            if t.text and t.text.strip():  # 공백이 아닌 실제 텍스트가 있는 경우
                if count < len(new_texts):
                    t.text = new_texts[count]
                    count += 1

        # paragraphs[0]을 XML 문자열로 변환
        xml_string = ET.tostring(paragraphs[i], encoding='unicode')

        # 파일로 저장
        filename = f"paragraph_{i}.xml"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(xml_string)

        print(f"▶ paragraphs[{i}] 저장 완료: {i}th paragraph.xml")
        i +=1   

    tree.write(section_path, encoding="utf-8", xml_declaration=True)
    print("▶ section0.xml 수정 완료")