import os
import xml.etree.ElementTree as ET
import parse_markdown
from excludes import is_excluded

def merge_paragraphs_with_header(paragraph_dir: str, output_path: str, templateNum: int, markdown_text: str):
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

        # 텍스트 치환: 비어 있는 <hp:t>만 대상으로, 한 번 성공하면 중단
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

