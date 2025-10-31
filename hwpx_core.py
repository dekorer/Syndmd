import shutil
from typing import Dict, Optional, List, Tuple
import xml.etree.ElementTree as ET
import re
import os
import zipfile

# 공통 상수 및 헬퍼 함수 임포트
from constants import NS, _TEXT_PATTERN, _NUMERIC_TOKEN_RE

# HWPX 압축해제
def unzip_hwpx(hwpx_path: str, output_dir: str) -> None:
    with zipfile.ZipFile(hwpx_path, 'r') as zip_ref:
        zip_ref.extractall(output_dir)
    print("▶ HWPX 압축 해제 완료")

# HWPX로 압축
def zip_hwpx(folder_path: str, output_hwpx_path: str) -> None:
    with zipfile.ZipFile(output_hwpx_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)
    print("▶ 수정된 HWPX 파일 압축 완료")

# --- XML 파싱 및 분석 ---

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

def split_section0_and_extract_charids(unzipped_path: str,
    out_dir: str = "paragraphs",
    start_page: int = 1,
    vert_tol: int = 20,
    min_reset: int = 5
) -> Tuple[Dict[int, int], Dict[int, bool], Dict[int, Optional[str]]]:

    section_path = os.path.join(unzipped_path, "Contents", "section0.xml")
    
    # ... (기존 함수의 나머지 코드 동일) ...
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
    paragraph_charId: Dict[int, int],
    charid_size: Dict[int, int],
    listable_map: Dict[int, bool],
    bullet_map: Dict[int, Optional[str]],
    n: int,
    m: int,
) -> Tuple[List[int], List[int]]:
    
    # ... (기존 함수의 코드 동일) ...
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


# --- XML 재조립 및 수정 ---

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
    s = (body or "").strip()
    if not s:
        return False
    if _NUMERIC_TOKEN_RE.match(s):
        return True
    if re.search(r"[가-힣a-zA-Z]", s):
        return False
    if all(not ch.isalnum() and not ch.isspace() for ch in s):
        return True
    return False

def replace_paragraph_text(p: ET.Element, new_text: str) -> bool:
    target_t = None
    target_prefix = ""
    runs = p.findall(".//{*}run")

    for run in runs:
        for t in run.findall("./{*}t"):
            raw = t.text or ""
            prefix, body = _split_prefix(raw)
            if not body.strip():
                continue
            if __is_symbol_or_numeric_only(body):
                continue
            if _TEXT_PATTERN.search(body):
                target_t = t
                target_prefix = prefix
                break
        if target_t is not None:
            break

    if target_t is None:
        return False

    target_t.text = f"{target_prefix}{new_text}"

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
    tree = ET.parse(template_para_path)
    p = tree.getroot()
    replace_paragraph_text(p, new_text)
    xml_str = ET.tostring(p, encoding="utf-8").decode("utf-8")
    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(xml_str)
    return xml_str

def get_section0_head_and_tail(section0_path: str) -> Tuple[str, str, str]:
    with open(section0_path, "r", encoding="utf-8") as f:
        xml_text = f.read()

    start_match = re.search(r"<(hp10|hp):p\b", xml_text)
    if not start_match:
        raise RuntimeError("section0.xml에서 단락 시작(<hp:p> 또는 <hp10:p>)을 찾지 못했습니다.")
    para_prefix = start_match.group(1)
    head = xml_text[:start_match.start()]

    end_tag_pattern = fr"</{para_prefix}:p>"
    last_end = xml_text.rfind(end_tag_pattern)
    if last_end == -1:
        raise RuntimeError(f"section0.xml에서 마지막 종료 태그 {end_tag_pattern}를 찾지 못했습니다.")
    tail = xml_text[last_end + len(end_tag_pattern):]

    return head, tail, para_prefix

def build_section0_from_tokens(
    head_xml_str: str,
    tail_xml_str: str,
    paragraphs_dir: str,
    title_pids: List[int],
    list_pids: List[int],
    tokens: List[Tuple[str, str]],
    output_section0_path: str,
) -> None:
    
    # ... (기존 함수의 코드 동일) ...
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
    
    # ... (기존 함수의 코드 동일) ...
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