import os
import xml.etree.ElementTree as ET
import parse_markdown
from excludes import is_excluded

roman_counter = 0            # 로마숫자용 (title2)
sub_counter = 0              # 소제목 번호 (title3)
current_number = 0           # 로마숫자 → 숫자값 기억

def int_to_roman(n):
    vals = [
        (1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'),
        (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'),
        (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')
    ]
    res = ""
    for val, roman in vals:
        while n >= val:
            res += roman
            n -= val
    return res

def merge_paragraphs_with_header(paragraph_dir: str, output_path: str, templateNum: int, markdown_text: str):
    global roman_counter, sub_counter, current_number
    
    # templateN_header.xml 경로 지정
    header_filename = f"template{templateNum}_header.xml"
    header_path = os.path.join(paragraph_dir, header_filename)
    
    if not os.path.exists(header_path):
        raise FileNotFoundError("header.xml이 존재하지 않습니다. 먼저 parse_edit_section0()을 실행하세요.")

    # header.xml 읽기
    with open(header_path, encoding="utf-8") as f:
        header = f.read()
        
    if header.startswith("<?xml"):
        header = header[header.find("?>")+2:].strip()

#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
    # 2. 본문 (Markdown → (스타일, 내용))
    body = ""
    parsed = parse_markdown.parse_markdown(markdown_text)

    for style, content in parsed:
        if style is None:
            continue  # 스타일 없는 줄은 무시하거나 기본 문단으로 처리 가능

        template_file = f"template{templateNum}_{style}.xml"
        template_path = os.path.join(paragraph_dir, template_file)

        if not os.path.exists(template_path):
            raise FileNotFoundError(f"{template_file} 이 존재하지 않습니다.")

        # XML 파싱
        tree = ET.parse(template_path)
        root = tree.getroot()
        
        ns = {"hp": "http://www.hancom.co.kr/hwpml/2011/paragraph"}

        # --- title2: 큰 번호 증가 ---
        if style == "title2":
            roman_counter += 1
            sub_counter = 0
            current_number = roman_counter
            roman = int_to_roman(roman_counter)

            t_elements = root.findall(".//hp:t", ns)
            if len(t_elements) >= 2:
                t_elements[0].text = roman         # 왼쪽 셀
                t_elements[1].text = content       # 오른쪽 셀

        # --- title3: 하위 번호 붙이기 (1.1, 1.2 ...) ---
        elif style == "title3":
            sub_counter += 1
            numbering = f"{sub_counter}"

            # 글자가 있는 t 태그들만 따로 추림
            t_elements = [t for t in root.findall(".//hp:t", ns) if t.text and t.text.strip()]

            if len(t_elements) >= 2:
                t_elements[0].text = numbering   # 첫 번째: 번호
                t_elements[1].text = content     # 두 번째: 제목
            elif len(t_elements) == 1:
                t_elements[0].text = content


        # --- 기타 스타일: 일반 텍스트 치환 ---
        else:
            for t in root.findall(".//hp:t", ns):
                if not is_excluded(t.text):
                    t.text = content
                    break

        # 문자열로 변환
        paragraph_xml = ET.tostring(root, encoding="utf-8").decode("utf-8")
        body += paragraph_xml + "\n"
    # body = ""
    # # 병합 대상 문단 파일
    # paragraph_filename = f"template{templateNum}_title1.xml"
    # paragraph_path = os.path.join(paragraph_dir, paragraph_filename)

    # if not os.path.exists(paragraph_path):
    #     raise FileNotFoundError(f"{paragraph_filename}이 존재하지 않습니다.")

    # with open(paragraph_path, encoding="utf-8") as f:
    #     content = f.read().strip()

    # # 혹시라도 선언이 있다면 제거
    # if content.startswith("<?xml"):
    #     content = content[content.find("?>") + 2:].strip()

    # body += content + "\n"

    # paragraph_filename = f"template{templateNum}_list1.xml"
    # paragraph_path = os.path.join(paragraph_dir, paragraph_filename)

    # if not os.path.exists(paragraph_path):
    #     raise FileNotFoundError(f"{paragraph_filename}이 존재하지 않습니다.")

    # with open(paragraph_path, encoding="utf-8") as f:
    #     content = f.read().strip()

    # # 혹시라도 선언이 있다면 제거
    # if content.startswith("<?xml"):
    #     content = content[content.find("?>") + 2:].strip()

    # body += content + "\n"

#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ

    # section0.xml 병합 저장
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(header)
        f.write(body)
        f.write("</hs:sec>\n")
    print(f"▶ 병합된 section0.xml 저장 완료: {output_path}")

