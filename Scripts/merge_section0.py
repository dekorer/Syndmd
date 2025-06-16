import os
import xml.etree.ElementTree as ET
import parse_markdown
from excludes import is_excluded


def merge_paragraphs_with_header(paragraph_dir: str, output_path: str, templateNum: int, markdown_text: str):
    # 로마자 변환 함수
    def to_roman(n):
        numerals = [
            (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
            (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
            (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")
        ]
        result = ""
        for value, numeral in numerals:
            while n >= value:
                result += numeral
                n -= value
        return result

    # templateN_header.xml 경로 지정
    header_filename = f"template{templateNum}_header.xml"
    header_path = os.path.join(paragraph_dir, header_filename)

    if not os.path.exists(header_path):
        raise FileNotFoundError("header.xml이 존재하지 않습니다. 먼저 parse_edit_section0()을 실행하세요.")

    # header.xml 읽기
    with open(header_path, encoding="utf-8") as f:
        header = f.read()

    if header.startswith("<?xml"):
        header = header[header.find("?>") + 2:].strip()

    # 2. 본문 (Markdown → (스타일, 내용))
    body = ""
    i = 1
    template_path = os.path.join(paragraph_dir, f"template{templateNum}_preplaceholder{i}.xml")
    while os.path.exists(template_path):
        paragraph_xml = ET.tostring(ET.parse(template_path).getroot(), encoding="utf-8").decode("utf-8")
        body += paragraph_xml + "\n"
        print(f"pre : {i}")
        i += 1
        template_path = os.path.join(paragraph_dir, f"template{templateNum}_preplaceholder{i}.xml")

    parsed = parse_markdown.parse_markdown(markdown_text)

    first_style, first_content = parsed[0]

    template_file = f"template{templateNum}_{first_style}.xml"
    template_path = os.path.join(paragraph_dir, template_file)

    if not os.path.exists(template_path):
        raise FileNotFoundError(f"{template_file} 이 존재하지 않습니다.")

    root = ET.parse(template_path).getroot()
    ns = {"hp": "http://www.hancom.co.kr/hwpml/2011/paragraph"}

    if first_style == "title1":
        # 텍스트 치환
        for t in root.findall(".//hp:t", ns):
            if not is_excluded(t.text):
                t.text = first_content
        # 첫 문단을 body에 추가
        body += ET.tostring(root, encoding="utf-8").decode("utf-8") + "\n"
        print("successfully added title1")
        # 나머지 문단만 for문에서 처리
        parsed_except_title1 = parsed[1:]
    else:
        # 텍스트 비움
        for t in root.findall(".//hp:t", ns):
            t.text = " "
        # 첫 문단도 그대로 추가
        body += ET.tostring(root, encoding="utf-8").decode("utf-8") + "\n"
        print("no title1 in this MD")
        # 이후 모든 문단 처리해야 하므로 parsed 전체 순회
        parsed_except_title1 = parsed

    i = 1
    template_path = os.path.join(paragraph_dir, f"template{templateNum}_placeholder{i}.xml")
    while os.path.exists(template_path):
        paragraph_xml = ET.tostring(ET.parse(template_path).getroot(), encoding="utf-8").decode("utf-8")
        body += paragraph_xml + "\n"
        print(i)
        i += 1
        template_path = os.path.join(paragraph_dir, f"template{templateNum}_placeholder{i}.xml")
    print("after add placeholder")

    title2_count = 0
    title3_count = 0

    for style, content in parsed_except_title1:
        if style is None:
            continue

        template_file = f"template{templateNum}_{style}.xml"
        template_path = os.path.join(paragraph_dir, template_file)

        if not os.path.exists(template_path):
            raise FileNotFoundError(f"{template_file} 이 존재하지 않습니다.")

        tree = ET.parse(template_path)
        root = tree.getroot()

        ns = {"hp": "http://www.hancom.co.kr/hwpml/2011/paragraph"}

        # 넘버링 로직
        numbering = None
        if style == "title2":
            title2_count += 1
            numbering = to_roman(title2_count)
            #print(f"[디버깅] style={style}, title1_count={title2_count}, numbering={numbering}")

        elif style == "title3":
            title3_count += 1
            numbering = str(title3_count)
            #print(f"[디버깅] style={style}, title1_count={title3_count}, numbering={numbering}")

        if style != "blank" :
            # 텍스트 치환 - 넘버링 먼저, 본문 텍스트 그다음
            for t in root.findall(".//hp:t", ns):
                if numbering and t.text and t.text.strip() in {"I", "1"}:
                    print(numbering)
                    t.text = numbering
                    continue
                elif not is_excluded(t.text):
                    t.text = content
                    break

        paragraph_xml = ET.tostring(root, encoding="utf-8").decode("utf-8")
        body += paragraph_xml + "\n"

    # section0.xml 저장
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(header)
        f.write(body)
        f.write("</hs:sec>\n")
    print(f"▶ 병합된 section0.xml 저장 완료: {output_path}")
