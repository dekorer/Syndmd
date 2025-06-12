import os

def merge_paragraphs_with_header(paragraph_dir: str, output_path: str, templateNum: int):
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

    body = ""
    # 병합 대상 문단 파일 (오직 하나)
    paragraph_filename = f"template{templateNum}_title1.xml"
    paragraph_path = os.path.join(paragraph_dir, paragraph_filename)

    if not os.path.exists(paragraph_path):
        raise FileNotFoundError(f"{paragraph_filename}이 존재하지 않습니다.")

    with open(paragraph_path, encoding="utf-8") as f:
        content = f.read().strip()

    # 혹시라도 선언이 있다면 제거
    if content.startswith("<?xml"):
        content = content[content.find("?>") + 2:].strip()

    body += content + "\n"

    paragraph_filename = f"template{templateNum}_list1.xml"
    paragraph_path = os.path.join(paragraph_dir, paragraph_filename)

    if not os.path.exists(paragraph_path):
        raise FileNotFoundError(f"{paragraph_filename}이 존재하지 않습니다.")

    with open(paragraph_path, encoding="utf-8") as f:
        content = f.read().strip()

    # 혹시라도 선언이 있다면 제거
    if content.startswith("<?xml"):
        content = content[content.find("?>") + 2:].strip()

    body += content + "\n"


    # files = sorted(f for f in os.listdir(paragraph_dir)
    #                if f.startswith("paragraph_") and f.endswith(".xml"))

    # for file in files:
    #     with open(os.path.join(paragraph_dir, file), encoding="utf-8") as f:
    #         content = f.read().strip()
    #         # 혹시라도 숨겨진 xml 선언이 있으면 강제로 제거
    #         if content.startswith("<?xml"):
    #             content = content[content.find("?>")+2:].strip()
    #         # 중간 삽입 시 xml 선언이 들어가지 않도록 강제 필터링
    #         content = content.replace('<?xml version="1.0" encoding="utf-8"?>', '')
    #         content = content.replace("<?xml version='1.0' encoding='utf-8'?>", '')    
    #         body += content + "\n"

    # section0.xml 병합 저장
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(header)
        f.write(body)
        f.write("</hs:sec>\n")
        print(f"▶ 병합된 section0.xml 저장 완료: {output_path}")

