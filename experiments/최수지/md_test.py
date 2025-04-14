import mistune

with open("빈집문제.md", "r", encoding="utf-8") as f:
    md_text = f.read()

markdown = mistune.create_markdown(renderer=mistune.AstRenderer())
ast = markdown(md_text)

def extract_inline_text(children):
    result = ""
    for c in children:
        if c["type"] == "text":
            result += c["text"]
        elif c["type"] == "strong":
            result += f"**{extract_inline_text(c['children'])}**"
    return result

def parse_blocks(blocks):
    for block in blocks:
        t = block["type"]

        if t == "heading":
            level = block["level"]
            text = block["children"][0]["text"]
            print(f"[제목{level}] {text}")

        elif t == "paragraph":
            text = extract_inline_text(block["children"])
            print(f"[문단] {text}")

        elif t == "list":
            ordered = block.get("ordered", False)
            for item in block["children"]:
                text = extract_inline_text(item["children"][0]["children"])
                bullet = "1." if ordered else "•"
                print(f"[리스트] {bullet} {text}")

        elif t == "thematic_break":
            print("[수평선] ----------------------")

        else:
            print(f"[기타] {t}")

parse_blocks(ast)
