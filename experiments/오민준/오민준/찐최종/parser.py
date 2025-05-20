import re

def parse_markdown_to_structured_json(md_text: str) -> list:
    lines = md_text.splitlines()
    result = []
    heading_counter = [0] * 6

    for line in lines:
        line = line.strip()
        if not line:
            continue

        heading_match = re.match(r'^(#{1,6}) (.+)', line)
        if heading_match:
            hashes, text = heading_match.groups()
            level = len(hashes)
            heading_counter[level - 1] += 1
            for i in range(level, 6):
                heading_counter[i] = 0
            result.append({"type": "heading", "level": level, "text": text.strip()})
            continue

        checklist_match = re.match(r'^-\s+\*\*(.+?)\*\*:\s*(.+)', line)
        if checklist_match:
            title, body = checklist_match.groups()
            result.append({"type": "checklist", "title": title.strip(), "body": body.strip()})
            continue

        if line.startswith("- "):
            result.append({"type": "list_item", "content": line[2:].strip()})
            continue

        result.append({"type": "paragraph", "text": line})
    return result