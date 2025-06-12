import os
import xml.etree.ElementTree as ET
import shutil

EXCLUDE_TEXTS = {"▢", "❍", "•", "▷", "□", "○", "-", "※", "Ⅰ", "Ⅱ", "Ⅲ", "Ⅳ", "Ⅴ", "Ⅵ", "Ⅶ", "Ⅷ", "Ⅸ", "Ⅹ", "제목", "1", "2", "3", "4", "5"}
ROMAN_NUMS = {"Ⅰ", "Ⅱ", "Ⅲ", "Ⅳ", "Ⅴ", "Ⅵ", "Ⅶ", "Ⅷ", "Ⅸ", "Ⅹ"}
NUMS = {str(i) for i in range(1, 101)}

ROMAN_MAP = {
    1: "Ⅰ", 2: "Ⅱ", 3: "Ⅲ", 4: "Ⅳ", 5: "Ⅴ",
    6: "Ⅵ", 7: "Ⅶ", 8: "Ⅷ", 9: "Ⅸ", 10: "Ⅹ"
}

def is_replacable(text):
    if not text:
        return False
    return text.strip() not in EXCLUDE_TEXTS

def inject_text(template_path: str, new_text: str, heading2_number: int = None) -> ET.Element:
    ns = {"hp": "http://www.hancom.co.kr/hwpml/2011/paragraph"}
    tree = ET.parse(template_path)
    root = tree.getroot()
    p = root if root.tag.endswith("p") else root.find(".//hp:p", ns)
    if p is None:
        raise ValueError(f"문단이 없음: {template_path}")

    t_list = p.findall(".//hp:t", ns)

    if template_path.endswith("heading2.xml") and heading2_number is not None and len(t_list) >= 2:
        roman = ROMAN_MAP.get(heading2_number, str(heading2_number))
        t_list[0].text = roman
        t_list[1].text = new_text
    else:
        for t in t_list:
            if t.text and is_replacable(t.text):
                original = t.text.strip()
                preserved_prefix = ""
                for ch in original:
                    if ch in EXCLUDE_TEXTS:
                        preserved_prefix += ch
                    else:
                        break
                t.text = preserved_prefix + " " + new_text
                break

    return p

def build_section0_from_parsed(parsed: list[tuple[str, str]], output_path: str):
    section = ET.Element("{http://www.hancom.co.kr/hwpml/2011/section}section")
    heading2_counter = 1

    for role, text in parsed:
        template_path = os.path.join("paragraphs", f"{role}.xml")
        if not os.path.exists(template_path):
            print(f"템플릿 없음: {role}.xml → 건너뜀")
            continue

        if role == "heading2":
            paragraph = inject_text(template_path, text, heading2_counter)
            heading2_counter += 1
        else:
            paragraph = inject_text(template_path, text)

        section.append(paragraph)

    tree = ET.ElementTree(section)
    tree.write(output_path, encoding="utf-8", xml_declaration=True)
    print(f"최종 section0.xml 생성 완료: {output_path}")

def parse_and_edit_section0(unzipped_path: str, parsed: list[tuple[str, str]]) -> None:
    section_path = os.path.join(unzipped_path, "Contents", "section0.xml")
    tree = ET.parse(section_path)
    root = tree.getroot()

    ns = {"hp": "http://www.hancom.co.kr/hwpml/2011/paragraph"}
    paragraphs = root.findall("hp:p", ns)

    paragraph_dir = os.path.join(os.getcwd(), "paragraphs")
    os.makedirs(paragraph_dir, exist_ok=True)

    role_saved = {
        "heading1": False, "heading2": False, "heading3": False,
        "list1": False, "list2": False, "list3": False, "list4": False
    }

    seen_bullet_chars = []
    list_counter = 1
    max_lists = 4

    for i, p in enumerate(paragraphs):
        ts = p.findall(".//hp:t", ns)
        texts = [t.text.strip() for t in ts if t.text and t.text.strip()]
        if not texts:
            continue

        first_text = texts[0]
        cleaned = first_text.lstrip()
        saved = False

        if not role_saved["heading1"]:
            role = "heading1"
            role_saved["heading1"] = True
            saved = True

        elif any(r in cleaned for r in ROMAN_NUMS) and not role_saved["heading2"]:
            role = "heading2"
            role_saved["heading2"] = True
            saved = True

        elif any(r in cleaned for r in NUMS) and not role_saved["heading3"]:
            role = "heading3"
            role_saved["heading3"] = True
            saved = True

        else:
            for ch in cleaned:
                if ch.isalnum():
                    continue
                if ch not in seen_bullet_chars:
                    if list_counter <= max_lists:
                        role = f"list{list_counter}"
                        seen_bullet_chars.append(ch)
                        role_saved[role] = True
                        saved = True
                        list_counter += 1
                    break

        if saved:
            filename = os.path.join(paragraph_dir, f"{role}.xml")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(ET.tostring(p, encoding='unicode'))
            print(f"{role}.xml 저장됨")

    output_path = os.path.join(unzipped_path, "Contents", "section0.xml")
    build_section0_from_parsed(parsed, output_path)
    shutil.copyfile(output_path, os.path.abspath("section0_modified.xml"))
    print("▶ section0.xml 수정 및 재생성 완료")
