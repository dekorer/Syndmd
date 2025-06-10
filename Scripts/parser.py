import mistune

def extract_inline(node):
    result = []
    node_type = node.get("type")

    if node_type == "text":
        result.append((node.get("text", "")))

    elif "children" in node:
        for child in node["children"]:
            result.extend(extract_inline(child))

    return "".join(result)

def parse_markdown(md_text):
    markdown = mistune.create_markdown(renderer=mistune.AstRenderer())
    ast = markdown(md_text)

    parsed = []

    for block in ast:
        t = block["type"]

        if t == "heading":
            level = block.get("level", 1)
            text = extract_inline(block)
            if level == 1:
                parsed.append(("heading1", text))
            elif level == 2:
                parsed.append(("heading2", text))
            elif level == 3:
                parsed.append(("heading3", text))
            elif level == 4:
                parsed.append(("heading4", text))

        elif t == "paragraph":
            parsed.append(("paragraph", extract_inline(block)))
        
        elif t == "list":
            def handle_list(block, level):
                for item in block.get("children", []):
                    for child in item.get("children", []):
                        if child["type"] == "list":
                            handle_list(child, level + 1)
                        else:
                            contents = extract_inline(child)
                            parsed.append((f"list{level}", contents))
    
            handle_list(block, block.get("level", 1))

    return parsed