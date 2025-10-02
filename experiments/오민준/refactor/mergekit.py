# mergekit.py — 텍스트 주입 포함 병합 모듈
from __future__ import annotations
from pathlib import Path
import os, re, xml.etree.ElementTree as ET

from templatekit import NS, ensure_complete_template_set
from hwpkit_io import zip_to_hwpx, convert_hwpx_to_hwp

# ====== MD → 역할 파싱 ======
H1 = re.compile(r"^#\s+")
H2 = re.compile(r"^##\s+")
H3 = re.compile(r"^###\s+")
LI = re.compile(r"^(\s*)-\s+")

def _strip_md_marker(line: str) -> tuple[str, str]:
    """한 줄을 역할과 텍스트로 분리해서 (role, text) 반환"""
    s = line.rstrip("\n")
    if not s.strip():
        return "blank", ""

    if H3.match(s):
        return "title3", H3.sub("", s, count=1).strip()
    if H2.match(s):
        return "title2", H2.sub("", s, count=1).strip()
    if H1.match(s):
        return "title1", H1.sub("", s, count=1).strip()

    m = LI.match(s)
    if m:
        indent = len(m.group(1) or "")
        text = LI.sub("", s, count=1).strip()
        if indent >= 6: return "list4", text
        if indent >= 4: return "list3", text
        if indent >= 2: return "list2", text
        return "list1", text

    return "default1", s.strip()

def items_from_markdown(md: str) -> list[dict]:
    """
    MD를 [{role, text}] 시퀀스로 변환.
    연속 blank는 1개로 압축, 마지막 blank 제거.
    """
    out = []
    for raw in md.splitlines():
        role, text = _strip_md_marker(raw)
        if role == "blank":
            if out and out[-1]["role"] == "blank":
                continue
            out.append({"role": "blank", "text": ""})
            continue
        out.append({"role": role, "text": text})
    if out and out[-1]["role"] == "blank":
        out.pop()
    return out

# ====== 템플릿 파일 해석/폴백 ======
FALLBACK_ORDER = {
    "title1": ["title1", "default1", "none", "blank"],
    "title2": ["title2", "default1", "none", "blank"],
    "title3": ["title3", "default1", "none", "blank"],
    "list1":  ["list1",  "default1", "none", "blank"],
    "list2":  ["list2",  "default1", "none", "blank"],
    "list3":  ["list3",  "default1", "none", "blank"],
    "list4":  ["list4",  "default1", "none", "blank"],
    "default1":["default1","none","blank"],
    "none":   ["none","default1","blank"],
    "blank":  ["blank","none","default1"],
    "placeholder1": ["placeholder1", "blank", "none", "default1"],
}

def _resolve_template_file(paragraph_dir: str, template_num: int, role: str) -> str:
    role_l = (role or "").strip().lower()
    if role_l in ("", "null", "none"):
        role_l = "none"
    base = Path(paragraph_dir)
    cand_roles = FALLBACK_ORDER.get(role_l, [role_l, "default1", "none", "blank"])
    for r in cand_roles:
        p = base / f"template{template_num}_{r}.xml"
        if p.exists():
            return str(p)
    ensure_complete_template_set(paragraph_dir, template_num)
    for r in cand_roles:
        p = base / f"template{template_num}_{r}.xml"
        if p.exists():
            return str(p)
    p = base / f"template{template_num}_default1.xml"
    if p.exists():
        return str(p)
    raise FileNotFoundError(f"{paragraph_dir}에서 {role} 대체 템플릿을 찾을 수 없습니다.")

# ====== 텍스트 주입 ======
GLYPH_BY_ROLE = {
    "list1": "▢",
    "list2": "❍",
    "list3": "•",
    "list4": "▷",
}

def _inject_text_into_template(xml_str: str, role: str, text: str) -> str:
    """
    template xml(단일 <hp:p>)의 첫 <hp:t>에 text를 주입하여 문자열로 반환.
    - list* : 글리프 유지 + ' ' + text
    - title*/default1 : 자리문자 교체 -> text
    - blank : 그대로 반환
    """
    if role == "blank" or not text:
        return xml_str

    ET.register_namespace("hp", NS["hp"])
    root = ET.fromstring(xml_str)
    t = root.find(".//hp:t", NS)
    if t is None:
        run = root.find(".//hp:run", NS)
        if run is None:
            run = ET.SubElement(root, f"{{{NS['hp']}}}run")
        t = ET.SubElement(run, f"{{{NS['hp']}}}t")
        t.text = ""

    if role.startswith("list"):
        glyph = GLYPH_BY_ROLE.get(role, "")
        base = glyph if glyph else ""
        t.text = (base + " " + text).strip()
    else:
        t.text = text

    return ET.tostring(root, encoding="utf-8").decode("utf-8")

# ====== section0.xml 병합 ======
def merge_paragraphs_with_header(paragraph_dir: str,
                                 section0_path: str,
                                 templateNum: int,
                                 markdownText: str) -> None:
    """
    paragraph_dir(템플릿 폴더)의 templateN_header.xml + 역할별 templateN_*.xml을 사용해
    markdownText를 순서대로 section0.xml로 병합.
    템플릿 누락 시 자동 보정/폴백 처리 + MD 텍스트 주입.
    """
    paragraph_dir = os.path.abspath(paragraph_dir)
    ensure_complete_template_set(paragraph_dir, templateNum)

    # header
    header_file = _resolve_template_file(paragraph_dir, templateNum, "header")
    header_xml = Path(header_file).read_text(encoding="utf-8")

    # MD → [{role, text}]
    items = items_from_markdown(markdownText)

    # 역할별 템플릿 로드 + 텍스트 주입
    parts = [header_xml]
    for it in items:
        role, text = it["role"], it["text"]
        tpl_path = _resolve_template_file(paragraph_dir, templateNum, role)
        tpl_xml = Path(tpl_path).read_text(encoding="utf-8")
        injected = _inject_text_into_template(tpl_xml, role, text)
        parts.append(injected)

    # section0.xml 저장
    Path(section0_path).write_text("\n".join(parts), encoding="utf-8")

# ====== 전체 빌드 ======
def build_hwp_from_template_folder(template_unzipped_dir: str,
                                   paragraph_dir: str,
                                   output_hwp_path: str,
                                   templateNum: int,
                                   markdownText: str) -> str:
    """
    template_unzipped_dir/Contents/section0.xml 을 paragraph_dir의 템플릿으로 교체 후
    HWPX 재압축 → HWP 변환.
    """
    tud = Path(template_unzipped_dir)
    contents = tud / "Contents"
    if not contents.exists():
        raise FileNotFoundError(f"Contents 폴더가 없습니다: {contents}")

    section0_path = contents / "section0.xml"
    merge_paragraphs_with_header(paragraph_dir, str(section0_path), templateNum, markdownText)

    # HWPX로 압축uyt
    hwpx_out = tud.parent / "_merged.hwpx"
    zip_to_hwpx(str(tud), str(hwpx_out))

    # HWP로 변환
    out_hwp = Path(output_hwp_path)
    convert_hwpx_to_hwp(str(hwpx_out), str(out_hwp))

    try:
        hwpx_out.unlink()
    except Exception:
        pass
    return str(out_hwp)
