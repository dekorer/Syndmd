def parse_markdown(md_text):
    lines = md_text.splitlines()
    parsed = []

    for line in lines:
        if not line.strip():
            continue
        if line.startswith("###") or line.startswith("##") or line.startswith("#"):
            parsed.append(("heading", line.lstrip("#").strip()))
        elif line.startswith("*"):
            parsed.append(("bullet", line.lstrip("*").strip()))
        elif line.startswith("---"):
            parsed.append(("hr", "──────────────────────"))
        else:
            parsed.append(("paragraph", line.strip()))

    return parsed
