import re
import xml.etree.ElementTree as ET
from typing import Dict

# HWPML XML 네임스페이스
NS: Dict[str, str] = {
    "hh": "http://www.hancom.co.kr/hwpml/2011/head",
    "hc": "http://www.hancom.co.kr/hwpml/2011/core",
    "hp": "http://www.hancom.co.kr/hwpml/2011/paragraph",
    "hs": "http://www.hancom.co.kr/hwpml/2011/section",
}

# 텍스트 존재 여부 판별용
_TEXT_PATTERN = re.compile(r"[가-힣a-zA-Z0-9]")

# 숫자/기호만으로 이뤄진 토큰(번호표기 포함) 판정
_NUMERIC_TOKEN_RE = re.compile(
    r"""^\s*
        (?:                         # 대표적인 '번호' 패턴들
            \(?\d+(?:\.\d+)*\)?\.?  # 1, 1.1, (1), (1.2), 1), 1.1. 등
          | [\u2160-\u2188]+\.?     # Ⅰ,Ⅱ,Ⅲ … (유니코드 로마숫자)
          | [\u2460-\u2473\u24EA\u278A-\u2793]  # ①~⑳, ⓪, ➊~➓ 등
        )
        \s*$""",
    re.VERBOSE
)

def register_namespaces():
    """
    ElementTree가 HWPML 네임스페이스를 인식하도록 등록합니다.
    """
    for prefix, uri in NS.items():
        ET.register_namespace(prefix, uri)

# 모듈 로드 시 네임스페이스 등록
register_namespaces()