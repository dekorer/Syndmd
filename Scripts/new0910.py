import shutil
from typing import Dict, Optional, List, Tuple
import xml.etree.ElementTree as ET
import re
import os
import zipfile
import win32com.client

_TEXT_PATTERN = re.compile(r"[가-힣a-zA-Z0-9]")

NS = {
    "hh": "http://www.hancom.co.kr/hwpml/2011/head",
    "hc": "http://www.hancom.co.kr/hwpml/2011/core",
    "hp": "http://www.hancom.co.kr/hwpml/2011/paragraph",
    "hs": "http://www.hancom.co.kr/hwpml/2011/section",
}
for prefix, uri in NS.items():
    ET.register_namespace(prefix, uri)
    
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

# HWP->HWPX
def convert_hwp_to_hwpx(hwp_path, hwpx_path):
    # HWP 경로가 유효한지 확인
    if not os.path.isfile(hwp_path):
        raise FileNotFoundError(f"HWP 파일을 찾을 수 없습니다: {hwp_path}")
    # 한/글 실행
    hwp = win32com.client.gencache.EnsureDispatch("HWPFrame.HwpObject")

    hwp.XHwpWindows.Item(0).Visible = True  # 옵션: 실행 창 보이기
    # 보안 모듈 비활성화 (비밀번호 있는 문서 등)
    hwp.RegisterModule("FilePathCheckDLL", "SecurityModule")
    # 파일 열기
    hwp.Open(hwp_path)
    # 다른 이름으로 저장 (포맷 코드 51 = HWPX)
    # HWPX 저장
    hwp.SaveAs(hwpx_path, "HWPX")
    # 한/글 종료
    hwp.Quit()
    print(f"변환 완료: {hwpx_path}")    
    print("▶ HWPX 압축 해제 완료")
# HWPX 압축해제
def unzip_hwpx(hwpx_path: str, output_dir: str) -> None:
    with zipfile.ZipFile(hwpx_path, 'r') as zip_ref:
        zip_ref.extractall(output_dir)

def makeDict_charPr_height(header_xml_path: str) -> Dict[int, int]:
    tree = ET.parse(header_xml_path)
    root = tree.getroot()
    result: Dict[int, int] = {}

    # 1) head 스키마: <hh:charPr id=".." height=".."/>
    for node in root.findall(".//hh:charPr", NS):
        id_attr = node.get("id")
        height_attr = node.get("height")
        if id_attr and height_attr:
            try:
                result[int(id_attr)] = int(height_attr)  # 1/100 pt
            except ValueError:
                pass

    # 2) core 스키마: <hc:charPr id=".." sz=".."/> (있다면 덮어씀)
    for node in root.findall(".//hc:charPr", NS):
        id_attr = node.get("id")
        sz_attr = node.get("sz")
        if id_attr and sz_attr:
            try:
                result[int(id_attr)] = int(sz_attr)  # 1/100 pt
            except ValueError:
                pass

    return result
def _get_representative_char_id(p: ET.Element, NS: Dict[str, str]) -> Optional[int]:
    """
    한 문단(<hp:p>) 엘리먼트에서 문서 흐름 순서대로 hp:run / hp:t를 훑어,
    실제 텍스트가 처음 나타난 시점의 charPrIDRef 값을 반환.
    """
    current_char_id: Optional[str] = None

    for run in p.findall(".//hp:run", NS):
        cid = run.get("charPrIDRef")
        if cid:
            current_char_id = cid

        for t in run.findall("./hp:t", NS):
            t_cid = t.get("charPrIDRef")
            if t_cid:
                current_char_id = t_cid

            text = t.text or ""
            if _TEXT_PATTERN.search(text):
                return int(current_char_id) if current_char_id is not None else None

    return None

def _get_first_visible_text(p: ET.Element, NS: Dict[str, str]) -> str:
    for run in p.findall(".//hp:run", NS):
        for t in run.findall("./hp:t", NS):
            text = t.text or ""
            if text.strip():
                return text
    return ""

def _leading_bullet_if_any(p: ET.Element, NS: Dict[str, str]) -> Optional[str]:
    first = _get_first_visible_text(p, NS)
    if not first:
        return None
    s = first.lstrip()
    if not s:
        return None
    c = s[0]
    return None if c.isalnum() else c

# -------- 통합 함수: head 분리 저장 + 문단 분리 저장 + 대표 charPrID 사전 생성 --------
def split_section0_and_extract_charids(unzipped_path: str,
    out_dir: str = "paragraphs",
    start_page: int = 1,   # ← 추가: 시작 페이지(1-based)
    vert_tol: int = 20,    # ← 추가: vertpos '큰 폭 감소' 허용오차
    min_reset: int = 5     # ← 추가: 0~작은값 리셋 판단 기준
) -> Tuple[Dict[int, int], Dict[int, bool], Dict[int, Optional[str]]]:

    section_path = os.path.join(unzipped_path, "Contents", "section0.xml")

    paragraph_charId: Dict[int, int] = {}
    listable_map: Dict[int, bool] = {}
    bullet_map: Dict[int, Optional[str]] = {}

    if not os.path.exists(section_path):
        raise FileNotFoundError(f"section0.xml not found: {section_path}")

    os.makedirs(out_dir, exist_ok=True)

    # 1) head.xml 저장 (원본 prefix/네임스페이스 유지)
    with open(section_path, "r", encoding="utf-8") as f:
        xml_text = f.read()

    first_p_idx = xml_text.find("<hp:p")
    if first_p_idx == -1:
        raise RuntimeError("section0.xml에서 <hp:p>를 찾지 못했습니다. 문단이 없거나 접두사가 다를 수 있습니다.")

    head_path = os.path.join(out_dir, "head.xml")
    with open(head_path, "w", encoding="utf-8") as f:
        f.write(xml_text[:first_p_idx])
    print(f"head.xml 저장: {head_path}")

    # 2) 최상위(직계) 문단들 파싱
    root = ET.parse(section_path).getroot()
    paras = root.findall("hp:p", NS)  # 전체 탐색이 필요하면 ".//hp:p"로

    HP_URI = NS["hp"]
    LINES_TAG = f"{{{HP_URI}}}linesegarray"
    LINE_TAG  = f"{{{HP_URI}}}lineseg"

    # 3) 지정한 페이지만큼 넘김
    def first_vertpos_top_level(p: ET.Element) -> Optional[int]:
        # p의 '직접 자식' linesegarray 아래 첫 lineSeg.vertPos만 확인
        for child in list(p):
            if child.tag == LINES_TAG:
                for seg in list(child):
                    if seg.tag == LINE_TAG:
                        vp = seg.attrib.get("vertpos") or seg.attrib.get("vertPos")
                        if vp is not None:
                            try:
                                return int(vp)
                            except ValueError:
                                return None
                return None
        return None

    page = 1
    prev_vp: Optional[int] = None
    start_idx: Optional[int] = None

    for i, p in enumerate(paras):
        vp = first_vertpos_top_level(p)
        if vp is not None:
            if prev_vp is None:
                prev_vp = vp
            else:
                # 0/작은값으로 리셋되었거나, 이전보다 크게 작아지면 페이지 전환
                if vp <= min_reset or (prev_vp - vp) > vert_tol:
                    page += 1
                prev_vp = vp

        if page >= start_page:
            start_idx = i
            break

    paras = paras[start_idx:] if start_idx is not None else []

    # 4) 문단별 대표 charPrID 추출 + linesegarray 제거 + 분리 저장
    HP_URI = NS["hp"]
    LINES_TAG = f"{{{HP_URI}}}linesegarray"

    paragraph_charId: Dict[int, int] = {}
    count = 0

    for i, p in enumerate(paras):
        rep_char_id = _get_representative_char_id(p, NS)
        if rep_char_id is not None:
            paragraph_charId[i] = rep_char_id

        bullet = _leading_bullet_if_any(p, NS)
        listable_map[i] = (bullet is not None)
        bullet_map[i] = bullet
        # linesegarray 제거 (부모 기준으로 안전 삭제)
        for parent in p.iter():
            for child in list(parent):
                if child.tag == LINES_TAG:
                    parent.remove(child)

        # 개별 문단 저장 (hp 접두사/xmlns 포함)
        para_xml = ET.tostring(p, encoding="utf-8").decode("utf-8")
        out_path = os.path.join(out_dir, f"paragraph_{i:03d}.xml")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(para_xml)
        count += 1

    print(f"✔ 문단 저장 완료: {count}개 -> {os.path.abspath(out_dir)}")
    return paragraph_charId, listable_map, bullet_map

def select_title_and_list_candidates_hybrid(
    paragraph_charId: Dict[int, int],      # pid -> cid
    charid_size: Dict[int, int],           # cid -> size
    listable_map: Dict[int, bool],         # pid -> is listable
    bullet_map: Dict[int, Optional[str]],  # pid -> bullet or None
    n: int,  # 제목 후보 개수
    m: int,  # 리스트 후보 개수
) -> Tuple[List[int], List[int]]:
    # ----- 1) 제목 후보: listable=False, size 내림차순, 같은 cid는 건너뜀 -----
    title_pool = []
    for pid, cid in paragraph_charId.items():
        if listable_map.get(pid):  # 리스트 문단은 제외
            continue
        size = charid_size.get(cid)
        if size is None:
            continue
        title_pool.append((pid, cid, size))
    # size desc, pid asc (안정성)
    title_pool.sort(key=lambda x: (-x[2], x[0]))

    title_candidates: List[int] = []
    seen_cids = set()
    for pid, cid, _size in title_pool:
        if cid in seen_cids:
            continue
        seen_cids.add(cid)
        title_candidates.append(pid)
        if len(title_candidates) >= max(n, 0):
            break
    # --- 2) 리스트 후보: listable=True, bullet 존재, bullet 중복 없이 선착순 Top-m ---
    # bullet 별로 "가장 먼저 등장한 문단(pid 최소)"을 대표로 선택
    bullet_representatives: Dict[str, Tuple[int, int, int]] = {}  # bullet -> (pid, cid, size)
    for pid in sorted(paragraph_charId.keys()):  # 등장 순서 보존용
        if not listable_map.get(pid, False):
            continue
        bullet = bullet_map.get(pid)
        if not bullet:  # None 또는 빈값 제외
            continue
        cid = paragraph_charId[pid]
        size = charid_size.get(cid)
        if size is None:
            continue
        # 첫 등장만 저장
        if bullet not in bullet_representatives:
            bullet_representatives[bullet] = (pid, cid, size)

    # 대표들을 "글자 크기 내림차순, 동률이면 pid 오름차순"으로 정렬
    rep_list = []
    for bullet, (pid, cid, size) in bullet_representatives.items():
        rep_list.append((pid, cid, bullet, size))
    rep_list.sort(key=lambda x: (-x[3], x[0]))

    list_candidates = [pid for pid, _cid, _bullet, _size in rep_list[:max(m, 0)]]

    return title_candidates, list_candidates

# HWPX로 압축
def zip_hwpx(folder_path: str, output_hwpx_path: str) -> None:

    with zipfile.ZipFile(output_hwpx_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)
    print("▶ 수정된 HWPX 파일 압축 완료")
# HWPX->HWP
def convert_hwpx_to_hwp(hwpx_path, hwp_path):
    if not os.path.isfile(hwpx_path):
        raise FileNotFoundError(f"HWPX 파일을 찾을 수 없습니다: {hwpx_path}")

    hwp = win32com.client.gencache.EnsureDispatch("HWPFrame.HwpObject")
    hwp.XHwpWindows.Item(0).Visible = False
    hwp.RegisterModule("FilePathCheckDLL", "SecurityModule")
    hwp.Open(hwpx_path)
    hwp.SaveAs(hwp_path, "HWP")
    hwp.Quit()

    print(f"변환 완료: {hwp_path}")
# 제목 앞의 넘버링 패턴 (1., 3.2., 2.1.1. 등) 제거

def parse_and_show_markdown(md_text: str) -> List[Tuple[str, str]]:
    """
    주어진 마크다운 문자열을 파싱 → 제목 번호 제거 → 콘솔 출력.
    반환값은 정리된 토큰 리스트(후속 처리용).
    """
    tokens = parse_markdown(md_text)
    cleaned = clean_parsed_markdown(tokens)
    print_parsed_markdown(cleaned)
    return cleaned
def parse_markdown(text: str):
    results = []

    for line in text.splitlines():
        line = line.rstrip()
        if line == "":
            results.append(("blank", ""))
            continue

        # 헤더 처리: # ~ ######까지
        heading_match = re.match(r'^(#{1,6})\s*(.+)', line)
        if heading_match:
            level = len(heading_match.group(1))
            content = heading_match.group(2).strip()
            results.append((f"title{level}", content))
            continue

        # 리스트 처리: 들여쓰기 기준으로 list1, list2...
        list_match = re.match(r'^(\s*)([-*+])\s+(.+)', line)
        if list_match:
            indent_spaces = len(list_match.group(1))
            content = list_match.group(3).strip()
            level = indent_spaces // 2 + 1  # 들여쓰기 2칸당 한 단계
            results.append((f"list{level}", content))
            continue

         # 해당 없음: None 처리 + 내용 그대로
        results.append(("None", line.strip()))

    return results
def clean_parsed_markdown(tokens: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    cleaned: List[Tuple[str, str]] = []
    for kind, text in tokens:
        if kind.startswith("title"):
            cleaned.append((kind, clean_title(text)))
        else:
            cleaned.append((kind, text))
    return cleaned
def clean_title(title: str) -> str:
    pattern = r'''
        ^                                           # 시작
        (?:
            \d+(?:\.\d+)*(?:\.)?                    # 1 / 1.1 / 1.1.1 / 1.1. (점 옵션)
          | \(\d+(?:\.\d+)*\)                       # (1) / (1.1)
          | \d+\)                                   # 1)
        )
        [\s\-–—]*                                   # 뒤 공백/대시류
    '''
    return re.sub(pattern, '', title, flags=re.VERBOSE)
def print_parsed_markdown(tokens: List[Tuple[str, str]]) -> None:
    """
    토큰들을 간단히 정리해서 콘솔에 출력.
    """
    for kind, text in tokens:
        if kind == "blank":
            print("")  # 빈 줄 유지
            continue
        if kind.startswith("title"):
            print(f"[{kind.upper()}] {text}")
        elif kind.startswith("list"):
            print(f"[{kind.upper()}] {text}")
        elif kind == "None":
            print(f"[TEXT] {text}")
        else:
            # 혹시 모를 확장 토큰 대비
            print(f"[{kind}] {text}")

# (이미 있다면 그대로 사용) 본문에서 선행공백/불릿 prefix 분리
def _split_prefix(text: str) -> Tuple[str, str]:
    if text is None:
        return "", ""
    s = text
    n = len(s)
    i = 0
    while i < n and s[i].isspace():
        i += 1
    prefix = s[:i]
    if i < n and not s[i].isalnum():
        prefix += s[i]
        i += 1
        if i < n and s[i].isspace():
            prefix += s[i]
            i += 1
    return prefix, s[i:]


def __is_symbol_or_numeric_only(body: str) -> bool:
    """
    body(불릿/선행공백 제외 후 텍스트)가
    - 숫자(번호표기), 혹은
    - 특수기호만
    으로 되어 있으면 True.
    즉, 글자가 하나도 없는 '시각적 기호' hp:t는 지우지 않는다.
    """
    s = (body or "").strip()
    if not s:
        return False  # 완전 공백은 무시

    # 1. 번호표기 (예: 1., 1.1, (2), Ⅱ, ② 등)
    if _NUMERIC_TOKEN_RE.match(s):
        return True

    # 2. 한글/영문자가 하나라도 포함되어 있으면 False
    if re.search(r"[가-힣a-zA-Z]", s):
        return False

    # 3. 한글/영문이 없고, 남은 게 전부 특수문자/숫자면 True
    #    예: "-", "•", "★", "※", "→", "→→", "◆"
    if all(not ch.isalnum() and not ch.isspace() for ch in s):
        return True

    return False

def replace_paragraph_text(p: ET.Element, new_text: str) -> bool:
    """
    문단(<hp:p>)에서 치환 대상 hp:t를 고를 때,
    - prefix(선행공백+불릿) 제거 후 body에 '한글/영문/숫자'가 처음 등장하되
    - body가 '숫자/기호만'으로 구성된 경우는 제외하고 선택.
    """
    target_t = None
    target_prefix = ""
    runs = p.findall(".//{*}run")

    # ✅ 대표 기준 + '숫자만' 제외
    for run in runs:
        for t in run.findall("./{*}t"):
            raw = t.text or ""
            prefix, body = _split_prefix(raw)
            if not body.strip():
                continue
            # 숫자/기호만인 경우는 건너뜀 (예: "1.", "1.1", "(2)", "Ⅱ", "②" 등)
            if __is_symbol_or_numeric_only(body):
                continue
            # 한/영/숫자 존재(=가시 본문)하는 첫 hp:t 선택
            if _TEXT_PATTERN.search(body):
                target_t = t
                target_prefix = prefix
                break
        if target_t is not None:
            break

    if target_t is None:
        return False

    # 선택된 hp:t에 치환 (불릿/선행공백 보존)
    target_t.text = f"{target_prefix}{new_text}"

    # 다른 hp:t 정리: 숫자/기호만(body)인 것은 보존, 그 외는 비움
    for run in runs:
        for t in run.findall("./{*}t"):
            if t is target_t:
                continue
            txt = t.text or ""
            if not txt.strip():
                continue
            _, body = _split_prefix(txt)
            if not __is_symbol_or_numeric_only(body):
                t.text = ""

    return True

def replace_text_in_template_paragraph(template_para_path: str, new_text: str, out_path: Optional[str] = None) -> str:
    """
    단일 문단 템플릿 파일을 읽어 불릿 보존 + 다른 텍스트 제거 후 new_text로 교체.
    """
    tree = ET.parse(template_para_path)
    p = tree.getroot()  # 루트는 <hp:p>

    replace_paragraph_text(p, new_text)

    xml_str = ET.tostring(p, encoding="utf-8").decode("utf-8")
    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(xml_str)
    return xml_str
def get_section0_head_and_tail(section0_path: str) -> Tuple[str, str, str]:
    """
    기존 section0.xml에서:
      - head: 첫 <hp:p> 또는 <hp10:p> '시작 태그 직전'까지
      - tail: '마지막 </hp:p> 또는 </hp10:p> 이후'부터 문서 끝까지
    를 문자열로 반환. 또한 실제 단락 태그 접두사('hp' 또는 'hp10')를 함께 돌려준다.
    """
    with open(section0_path, "r", encoding="utf-8") as f:
        xml_text = f.read()

    # 단락 시작/끝 태그 탐색 (hp/hp10 모두 대응)
    start_match = re.search(r"<(hp10|hp):p\b", xml_text)
    if not start_match:
        raise RuntimeError("section0.xml에서 단락 시작(<hp:p> 또는 <hp10:p>)을 찾지 못했습니다.")
    para_prefix = start_match.group(1)  # 'hp' 또는 'hp10'

    head = xml_text[:start_match.start()]

    # 마지막 종료 태그 탐색
    end_tag_pattern = fr"</{para_prefix}:p>"
    last_end = xml_text.rfind(end_tag_pattern)
    if last_end == -1:
        raise RuntimeError(f"section0.xml에서 마지막 종료 태그 {end_tag_pattern}를 찾지 못했습니다.")
    tail = xml_text[last_end + len(end_tag_pattern):]

    return head, tail, para_prefix


def build_section0_from_tokens(
    head_xml_str: str,
    tail_xml_str: str,
    paragraphs_dir: str,                  # paragraphs 저장 폴더 (paragraph_###.xml들)
    title_pids: List[int],
    list_pids: List[int],
    tokens: List[Tuple[str, str]],        # (kind, text) : parse_and_show_markdown 이후 cleaned 토큰
    output_section0_path: str,
) -> None:
    """
    head를 쓰고 → 각 토큰에 맞는 템플릿 문단을 복사/치환 → tail을 써서 새로운 section0.xml을 만든다.
    * 치환은 replace_text_in_template_paragraph()로 수행(불릿 보존 + 다른 텍스트 제거).
    * titleN -> title_pids[N-1], listN -> list_pids[N-1], 없으면 마지막으로 폴백.
    * 'blank'와 'None'은 스킵(원하면 나중에 일반 문단 템플릿을 확장).
    """
    def pick_template_pid(kind: str) -> Optional[int]:
        if kind.startswith("title"):
            try:
                lvl = int(kind.replace("title", ""))
            except ValueError:
                lvl = 1
            if not title_pids:
                return None
            idx = min(max(lvl - 1, 0), len(title_pids) - 1)
            return title_pids[idx]
        if kind.startswith("list"):
            try:
                lvl = int(kind.replace("list", ""))
            except ValueError:
                lvl = 1
            if not list_pids:
                return None
            idx = min(max(lvl - 1, 0), len(list_pids) - 1)
            return list_pids[idx]
        return None  # 그 외(plain/blank)는 현재 스킵

    with open(output_section0_path, "w", encoding="utf-8") as out:
        # 1) head
        out.write(head_xml_str)

        # 2) 본문 문단들
        for kind, text in tokens:
            if kind in ("blank", "None"):
                continue  # 필요 시 plain 템플릿로 확장 가능
            pid = pick_template_pid(kind)
            if pid is None:
                continue
            src_para = os.path.join(paragraphs_dir, f"paragraph_{pid:03d}.xml")
            if not os.path.isfile(src_para):
                continue
            # 텍스트 치환(불릿 보존 + 나머지 텍스트 제거)
            para_xml = replace_text_in_template_paragraph(src_para, text, out_path=None)
            out.write(para_xml)

        # 3) tail
        out.write(tail_xml_str)


def copy_unzipped_and_rebuild_section(
    src_unzipped_dir: str,
    dst_unzipped_dir: str,
    paragraphs_dir: str,
    title_pids: List[int],
    list_pids: List[int],
    tokens: List[Tuple[str, str]],
) -> str:
    """
    unzipped 전체를 dst로 복사한 뒤, dst의 section0.xml만 재생성한다.
    반환: 새로 만든 section0.xml 경로
    """
    # 복사본 준비(있으면 삭제 후 복사)
    if os.path.isdir(dst_unzipped_dir):
        shutil.rmtree(dst_unzipped_dir)
    shutil.copytree(src_unzipped_dir, dst_unzipped_dir)

    # 원본 section0.xml에서 head/tail 추출
    src_section0 = os.path.join(src_unzipped_dir, "Contents", "section0.xml")
    head, tail, _ = get_section0_head_and_tail(src_section0)

    # 복사본에 새 section0.xml 구성
    dst_section0 = os.path.join(dst_unzipped_dir, "Contents", "section0.xml")
    build_section0_from_tokens(
        head_xml_str=head,
        tail_xml_str=tail,
        paragraphs_dir=paragraphs_dir,
        title_pids=title_pids,
        list_pids=list_pids,
        tokens=tokens,
        output_section0_path=dst_section0,
    )
    return dst_section0
if __name__ == "__main__":
    # UI로 받는 부분ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
    hwp_Path    = r"C:\Users\User A\Desktop\MdToHwp\MdToHwp\한글-템플릿1.hwp"
    output_Path = r"C:\Users\User A\Desktop\mdtest"
    startPage = 1
    # ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ

    os.makedirs(output_Path, exist_ok=True)

    # 파일명 기반 파생 경로
    base_name   = os.path.splitext(os.path.basename(hwp_Path))[0]  # '한글-템플릿n'
    hwpx_Path   = os.path.join(output_Path, f"{base_name}.hwpx")
    unzipped_dir = os.path.join(output_Path, f"{base_name}_unzipped")

    # --- [STEP 1] HWP -> HWPX ---
    convert_hwp_to_hwpx(hwp_Path, hwpx_Path)

    # --- [STEP 2] HWPX 압축 해제(기존 폴더가 있으면 삭제 후 새로 생성) ---
    if os.path.isdir(unzipped_dir):
        shutil.rmtree(unzipped_dir)
    unzip_hwpx(hwpx_Path, unzipped_dir)

    # --- [STEP 3] header.xml에서 charId/height 맵 추출 ---
    header_xml_path = os.path.join(unzipped_dir, "Contents", "header.xml")
    charid_size = makeDict_charPr_height(header_xml_path)

    # --- [STEP 4] section0.xml에서 문단 분리 + 대표 charPrID/불릿 맵 추출 ---
    # out_dir은 분리된 문단 xml을 떨어뜨릴 작업 폴더
    out_dir = os.path.join(output_Path, "paragraphs")
    paragraph_charId, listable_map, bullet_map = split_section0_and_extract_charids(
        unzipped_path=unzipped_dir,
        out_dir=out_dir,
        start_page=startPage   # 필요 시 조정
    )

    # --- [STEP 5] 제목/리스트 후보 선정 ---
    n, m = 6, 6
    title_pids, list_pids = select_title_and_list_candidates_hybrid(
        paragraph_charId, charid_size, listable_map, bullet_map, n, m
    )
    print("Title candidates:", title_pids)
    print("List candidates:", list_pids)

    # --- [STEP 6] 마크다운 파싱/정리/출력 (원하면 비활성화 가능) ---
    md_path = os.path.join(output_Path, "input.md")
    if os.path.isfile(md_path):
        with open(md_path, "r", encoding="utf-8") as f:
            md_text = f.read()
    else:
        md_text = """# 1. 제목1
- 리스트1

## 1.1 제목2
- 리스트1
  - 리스트2
   - 리스트3
- 리스트1
### 2. 제목3
- 리스트1
"""

    _ = parse_and_show_markdown(md_text)
    # --- [STEP 7] 토큰 준비(앞서 만든 parse_and_show_markdown 사용) ---
    tokens_raw = parse_markdown(md_text)
    tokens = clean_parsed_markdown(tokens_raw)  # title 넘버링 제거 포함

    # --- [STEP 8] unzipped 작업본 생성 + section0.xml 재구성 ---
    paragraphs_dir = out_dir  # split_section0_and_extract_charids()에서 지정했던 폴더
    dst_unzipped_dir = os.path.join(output_Path, f"{base_name}_unzipped_built")

    new_section0_path = copy_unzipped_and_rebuild_section(
        src_unzipped_dir=unzipped_dir,
        dst_unzipped_dir=dst_unzipped_dir,
        paragraphs_dir=paragraphs_dir,
        title_pids=title_pids,
        list_pids=list_pids,
        tokens=tokens,
    )
    print("Rebuilt section0.xml:", new_section0_path)
    
    # --- [STEP 9] 수정된 언집 폴더 → HWPX로 재압축 ---
    built_hwpx_Path = os.path.join(output_Path, f"{base_name}_built.hwpx")
    zip_hwpx(dst_unzipped_dir, built_hwpx_Path)
    print("재압축 HWPX:", built_hwpx_Path)

    # --- [STEP 10] HWPX → HWP 변환 ---
    final_hwp_Path = os.path.join(output_Path, f"{base_name}_built.hwp")
    convert_hwpx_to_hwp(built_hwpx_Path, final_hwp_Path)
    print("최종 HWP:", final_hwp_Path)