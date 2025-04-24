import mistune

def extract_inline(node):
    """인라인 요소를 중첩된 튜플 구조로 추출하는 함수"""
    result = []
    node_type = node.get("type")

    if node_type == "text":
        result.append(("일반", node.get("text", "")))

    elif node_type == "strong":
        inner = []
        for child in node.get("children", []):
            inner.extend(extract_inline(child))
        result.append(("강조", inner))

    elif node_type == "emphasis":
        inner = []
        for child in node.get("children", []):
            inner.extend(extract_inline(child))
        result.append(("기울임", inner))
    elif node_type == "codespan":
        result.append(("코드", node.get("text", "")))

    elif node_type == "link":
        inner = []
        for child in node.get("children", []):
            inner.extend(extract_inline(child))
        href = node.get("link", "")
        result.append(("링크", (inner, href)))

    elif node_type == "image":
        alt = node.get("alt", "")
        src = node.get("src", "")
        result.append(("이미지", f"![{alt}]({src})"))

    elif "children" in node:
        for child in node["children"]:
            result.extend(extract_inline(child))

    return result

def parse_markdown(md_text):
    markdown = mistune.create_markdown(renderer=mistune.AstRenderer())
    ast = markdown(md_text)

    parsed = []

    for block in ast:
        t = block["type"]

        if t == "heading":
            level = block.get("level", 1)
            parsed.append(("제목", level, extract_inline(block)))

        elif t == "paragraph":
            parsed.append(("문장", extract_inline(block)))

        elif t == "list":
            level = block.get("level", 1)
            for item in block.get("children", []):
                contents = []
                sub_lists = []
                for child in item.get("children", []):
                    if child.get("type") == "list":
                        sub_lists.append(child)
                    else:
                        contents.extend(extract_inline(child))
                if contents:
                    parsed.append(("목록", level, contents))
                for sub in sub_lists:
                    sub_level = sub.get("level", level + 1)
                    for sub_item in sub.get("children", []):
                        parsed.append(("목록", sub_level, extract_inline(sub_item)))

        elif t == "thematic_break":
            parsed.append(("수평선", "────────────────────"))

        elif t == "block_quote":
            parsed.append(("인용문", extract_inline(block)))

        elif t == "code":
            lang = block.get("info", "")
            code_text = block.get("text", "")
            full = f"[{lang}]\n{code_text}" if lang else code_text
            parsed.append(("코드블럭", full))

        elif t == "image":
            alt = block.get("alt", "")
            src = block.get("src", "")
            parsed.append(("이미지", f"![{alt}]({src})"))

    return parsed