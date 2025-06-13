import re

# 치환 제외 문자열 목록
EXCLUDE_EXACT = {"제목", "I", "1"}

# 특수기호만으로 구성된 문자열 판단
SPECIAL_CHAR_PATTERN = re.compile(r'^[^\w\s]+$')

def is_excluded(text: str) -> bool:
    if text is None:
        return True  # 비어 있으면 제외
    stripped = text.strip()
    if not stripped:
        return True  # 공백만 있으면 제외
    if stripped in EXCLUDE_EXACT:
        return True
    if SPECIAL_CHAR_PATTERN.fullmatch(stripped):
        print(text)
        return True
    return False