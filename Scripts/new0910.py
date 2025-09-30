from typing import Dict, Optional, List, Tuple
import xml.etree.ElementTree as ET
import re
import os

_TEXT_PATTERN = re.compile(r"[가-힣a-zA-Z0-9]")


NS = {
    "hh": "http://www.hancom.co.kr/hwpml/2011/head",
    "hc": "http://www.hancom.co.kr/hwpml/2011/core",
    "hp": "http://www.hancom.co.kr/hwpml/2011/paragraph",
    "hs": "http://www.hancom.co.kr/hwpml/2011/section",
}
for prefix, uri in NS.items():
    ET.register_namespace(prefix, uri)

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
def split_section0_and_extract_charids(unzipped_path: str, out_dir: str = "paragraphs") -> Dict[int, int]:

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

    # 3) 문단별 대표 charPrID 추출 + linesegarray 제거 + 분리 저장
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

if __name__ == "__main__":
    # hwp->hwpx

    # 압축해제

    # header.xml에서 charId_글자크기 쌍 추출
    charid_size = makeDict_charPr_height("template2_unzipped/Contents/header.xml")
    # section0.xml 읽어 문단별 대표 글자 charPrID,
    # 맨 앞 기호로 title감인지 list감인지 와 문단 전체 추출
    paragraph_charId, listable_map, bullet_map = split_section0_and_extract_charids(
        unzipped_path="template2_unzipped",
        out_dir="0930",
    )
    n, m = 4,4
    title_pids, list_pids = select_title_and_list_candidates_hybrid(
    paragraph_charId, charid_size, listable_map, bullet_map, n, m
    )
    print("Title candidates:", title_pids)
    print("List candidates:", list_pids)

    # # listable 예시 출력 (선두 특수문자로 시작한 문단만)
    # listable_pids = [pid for pid, ok in listable_map.items() if ok]
    # print("Listable paragraphs:", listable_pids)

    # 마크다운 입력 및 파싱

    # 압축
    # hwpx->hwp
