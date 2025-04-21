def parse_markdown(md_text):
    #줄 바꿈을 기준으로 분할
    #chatGPT 복붙시 줄바꿈 포함해주므로 가능
    lines = md_text.splitlines()
    parsed = []

    for line in lines:
        if not line.strip():
            continue

        #헤더
        if line.startswith("###") or line.startswith("##") or line.startswith("#"):
            parsed.append(("heading", line.lstrip("#").strip()))
        #목록/리스트
        elif line.startswith("*"):
            parsed.append(("bullet", line.lstrip("*").strip()))
        #수평선
        elif line.startswith("---"):
            parsed.append(("hr", "──────────────────────"))
        #일반문장
        else:
            parsed.append(("paragraph", line.strip()))

    return parsed
