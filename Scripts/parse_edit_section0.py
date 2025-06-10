import os
import xml.etree.ElementTree as ET
import shutil

# parse_edit_section0.py 전체 흐름
# hp:p 문단 중 마크다운 문법에 맞는 템플릿.xml 파일저장(heading1.xml, heading2.xml, list1.xml, list2.xml, list3.xml, list4.xml)
# 파싱되서 넘어온 md 데이터를 기반으로 해당 템플릿.xml을 불러와 텍스트 대체
# md 내용 전체를 그런식으로 새로운 section0.xml로 조립

EXCLUDE_TEXTS = {"▢", "❍", "•", "▷", "□", "○", "-", "※", "Ⅰ", "Ⅱ", "Ⅲ", "Ⅳ", "Ⅴ", "Ⅵ", "Ⅶ", "Ⅷ", "Ⅸ", "Ⅹ", "제목", "1", "2", "3", "4", "5"}
ROMAN_NUMS = {"Ⅰ", "Ⅱ", "Ⅲ", "Ⅳ", "Ⅴ", "Ⅵ", "Ⅶ", "Ⅷ", "Ⅸ", "Ⅹ"}

# 공백 or 특정기호면 false 반환
def is_replacable(text):
    if not text:
        return False
    return text.strip() not in EXCLUDE_TEXTS

# 템플릿에 새 텍스트 넣는 함수
# 특정 xml 파일을 열어서 그 안에 텍스트 태그 중에 진짜 교체해도 되는 텍스트만 골라 새 텍스트로 교체
def inject_text(template_path: str, new_text: str) -> ET.Element:
    ns = {"hp": "http://www.hancom.co.kr/hwpml/2011/paragraph"}
    tree = ET.parse(template_path)
    root = tree.getroot()
    p = root if root.tag.endswith("p") else root.find(".//hp:p", ns)
    if p is None:
        raise ValueError(f"문단이 없음: {template_path}")

    for t in p.findall(".//hp:t", ns):
        if t.text and is_replacable(t.text):
            original = t.text.strip()

            # 앞쪽 기호 추출
            preserved_prefix = ""
            for ch in original:
                if ch in EXCLUDE_TEXTS:
                    preserved_prefix += ch
                else:
                    break

            # 기호 유지한 새 텍스트
            t.text = preserved_prefix + new_text
            break

    return p

# 전체 section0.xml을 새로 만드는 함수
# 파싱된 md 데이터('heading1', '빈집 문제 해결')를 보고
# 해당 템플릿.xml을 불러온 후 텍스트를 주입해서 section0.xml로 조립
def build_section0_from_parsed(parsed: list[tuple[str, str]], output_path: str):
    section = ET.Element("{http://www.hancom.co.kr/hwpml/2011/section}section")
    for role, text in parsed:
        template_path = os.path.join("paragraphs", f"{role}.xml") # 해당되는 템프릿 xml 불러오고
        paragraph = inject_text(template_path, text) # 텍스트 바꾼 후
        section.append(paragraph) # 문단에 붙임
    tree = ET.ElementTree(section)
    tree.write(output_path, encoding="utf-8", xml_declaration=True)
    print(f"✅ 최종 section0.xml 생성 완료: {output_path}")

# hp:p 문단을 순회하면서 템플릿 추출
def parse_and_edit_section0(unzipped_path: str, parsed: list[tuple[str, str]]) -> None:
    section_path = os.path.join(unzipped_path, "Contents", "section0.xml")
    tree = ET.parse(section_path)
    root = tree.getroot()

    ns = {"hp": "http://www.hancom.co.kr/hwpml/2011/paragraph"}
    paragraphs = root.findall("hp:p", ns)

    paragraph_dir = os.path.join(os.getcwd(), "paragraphs")
    os.makedirs(paragraph_dir, exist_ok=True)

    role_saved = {
        "heading1": False, "heading2": False,
        "list1": False, "list2": False,
        "list3": False, "list4": False
    } # 각 문법별 템플릿이 한번만 저장되도록 체크용

    for i, p in enumerate(paragraphs):
        ts = p.findall(".//hp:t", ns)
        texts = [t.text.strip() for t in ts if t.text and t.text.strip()]
        if not texts:
            continue

        first_text = texts[0]
        saved = False

        if not role_saved["heading1"]:
            role = "heading1"
            role_saved["heading1"] = True
            saved = True
        elif any(r in first_text for r in ROMAN_NUMS) and not role_saved["heading2"]:
            role = "heading2"
            role_saved["heading2"] = True
            saved = True
        elif (first_text.startswith("□") or first_text.startswith("▢")) and not role_saved["list1"]:
            role = "list1"
            role_saved["list1"] = True
            saved = True
        elif (first_text.startswith("○") or first_text.startswith("❍")) and not role_saved["list2"]:
            role = "list2"
            role_saved["list2"] = True
            saved = True
        elif (first_text.startswith("-") or first_text.startswith("•")) and not role_saved["list3"]:
            role = "list3"
            role_saved["list3"] = True
            saved = True
        elif (first_text.startswith("※") or first_text.startswith("▷")) and not role_saved["list4"]:
            role = "list4"
            role_saved["list4"] = True
            saved = True

        if saved:
            filename = os.path.join(paragraph_dir, f"{role}.xml")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(ET.tostring(p, encoding='unicode'))
            print(f"✅ {role}.xml 저장됨")

    output_path = os.path.join(unzipped_path, "Contents", "section0.xml")
    build_section0_from_parsed(parsed, output_path)
    shutil.copyfile(output_path, os.path.abspath("section0_modified.xml"))
    print("▶ section0.xml 수정 및 재생성 완료")
