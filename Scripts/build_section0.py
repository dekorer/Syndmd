from paragraphs import RUN_TEMPLATES
import xml.etree.ElementTree as ET
import os

def create_paragraph(run_keys: list[str]) -> ET.Element:
    p = ET.Element("{http://www.hancom.co.kr/hwpml/2011/paragraph}p")
    for key in run_keys:
        if key not in RUN_TEMPLATES:
            print(f"⚠️ 템플릿 '{key}' 없음")
            continue
        run_element = ET.fromstring(RUN_TEMPLATES[key])
        p.append(run_element)
    return p

def build_section0(unzipped_path: str, paragraph_run_lists: list[list[str]]) -> None:
    section_path = os.path.join(unzipped_path, "Contents", "section0.xml")
    root = ET.Element("section0")

    os.makedirs("paragraphs", exist_ok=True)

    for idx, run_keys in enumerate(paragraph_run_lists):
        p = create_paragraph(run_keys)
        root.append(p)

        # 개별 저장
        filename = f"paragraph_{idx}.xml"
        ET.ElementTree(p).write(os.path.join("paragraphs", filename), encoding="utf-8", xml_declaration=True)
        print(f"✅ 저장 완료: {filename}")

    ET.ElementTree(root).write(section_path, encoding="utf-8", xml_declaration=True)
    print("▶ section0.xml 생성 완료")
