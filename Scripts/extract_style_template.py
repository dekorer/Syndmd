import os
import xml.etree.ElementTree as ET
from collections import defaultdict

def extract_template_style(section_path: str, max_lines: int = 30):
    """
    section0.xml에서 상위 N개 문단을 분석하여 스타일 구조 추출
    """
    ns = {"hp": "http://www.hancom.co.kr/hwpml/2011/paragraph"}
    tree = ET.parse(section_path)
    root = tree.getroot()
    paragraphs = root.findall(".//hp:p", ns)

    style_summary = []

    for i, p in enumerate(paragraphs[:max_lines]):
        style_id = p.attrib.get("styleIDRef", "0")
        para_id = p.attrib.get("paraPrIDRef", "0")

        runs = p.findall(".//hp:run", ns)
        styles_in_run = []

        for r in runs:
            char_id = r.attrib.get("charPrIDRef", "0")
            text_node = r.find(".//hp:t", ns)
            text_preview = text_node.text.strip() if text_node is not None and text_node.text else ""

            styles_in_run.append({
                "charPrIDRef": char_id,
                "text": text_preview
            })

        style_summary.append({
            "paragraph_index": i,
            "paraPrIDRef": para_id,
            "styleIDRef": style_id,
            "runs": styles_in_run
        })

    return style_summary

# 예시 실행
if __name__ == "__main__":
    section_path = os.path.abspath("section0.xml")
    styles = extract_template_style(section_path)

    print("\n=== 스타일 구조 요약 ===\n")
    for block in styles:
        print(f"문단 {block['paragraph_index']} | paraPr: {block['paraPrIDRef']} | styleID: {block['styleIDRef']}")
        for r in block['runs']:
            print(f"  └ charPr: {r['charPrIDRef']} | 내용: {r['text']}")
        print("-" * 50)
