# templatekit.py
from __future__ import annotations
import os, re, json, csv, hashlib
from pathlib import Path
from collections import Counter, defaultdict
import xml.etree.ElementTree as ET
from xml.dom import minidom

# ====== 공통 NS ======
NS = {"hp": "http://www.hancom.co.kr/hwpml/2011/paragraph"}
ET.register_namespace("hp", NS["hp"])

# ====== features.py 통합 ======
def para_features(p: ET.Element) -> dict:
    feat = {}
    tbl = p.find(".//hp:tbl", NS)
    feat["is_table"] = int(tbl is not None)
    if tbl is not None:
        feat["tbl_colcnt"] = int(tbl.get("colCnt") or 0)
        feat["has_left_cell"] = int(tbl.find(".//hp:tc", NS) is not None)
    else:
        feat["tbl_colcnt"] = 0
        feat["has_left_cell"] = 0

    feat["paraPrIDRef"] = p.get("paraPrIDRef") or ""
    char_ids = sorted({ run.get("charPrIDRef") or "" for run in p.findall(".//hp:run", NS) })
    feat["charPrIDRefs"] = ",".join([c for c in char_ids if c])

    lead = ""
    for t in p.findall(".//hp:t", NS):
        txt = (t.text or "").strip()
        if txt:
            lead = txt[:2]
            break
    feat["lead"] = lead
    feat["has_colPr"] = int(p.find(".//hp:colPr", NS) is not None)
    return feat

def _remove_linesegarray(node: ET.Element) -> None:
    for child in list(node):
        tag = child.tag if isinstance(child.tag, str) else ""
        if tag.endswith("linesegarray"):
            node.remove(child)
        else:
            _remove_linesegarray(child)

def _normalize_ws(xml_bytes: bytes) -> bytes:
    return re.sub(rb">\s+<", b"><", xml_bytes)

def structure_hash(
    p: ET.Element,
    *,
    drop_text: bool = True,
    drop_lineseg: bool = True,
    normalize_prefix: bool = True,
    squeeze_ws: bool = True,
) -> str:
    p_copy = ET.fromstring(ET.tostring(p, encoding="utf-8"))
    if drop_text:
        for t in p_copy.findall(".//hp:t", NS):
            t.text = ""
    if drop_lineseg:
        _remove_linesegarray(p_copy)
    if normalize_prefix:
        ET.register_namespace("hp", NS["hp"])
    xml_bytes = ET.tostring(p_copy, encoding="utf-8")
    if squeeze_ws:
        xml_bytes = _normalize_ws(xml_bytes)
    return hashlib.sha1(xml_bytes).hexdigest()

# ====== template_safety.py 통합 ======
HP_NS = NS["hp"]
REQUIRED_ROLES = [
    "header",
    "title1", "title2", "title3",
    "list1", "list2", "list3", "list4",
    "default1", "none", "blank", "placeholder1"
]
DEFAULT_STUB_TEXT = {
    "title1": "제목",
    "title2": "I",
    "title3": "1",
    "list1": "▢",
    "list2": "❍",
    "list3": "•",
    "list4": "▷",
    "default1": "",
    "none": "",
    "blank": "",
    "placeholder1": "",
}
def _hp_p(text: str = "") -> ET.Element:
    p = ET.Element(f"{{{HP_NS}}}p")
    run = ET.SubElement(p, f"{{{HP_NS}}}run")
    t = ET.SubElement(run, f"{{{HP_NS}}}t")
    t.text = text
    return p

def _write_p(path: Path, p: ET.Element):
    xml = ET.tostring(p, encoding="utf-8", xml_declaration=False).decode("utf-8")
    path.write_text(xml, encoding="utf-8")

def ensure_complete_template_set(paragraph_dir: str, template_num: int = 1) -> None:
    d = Path(paragraph_dir)
    d.mkdir(parents=True, exist_ok=True)
    default_path = d / f"template{template_num}_default1.xml"
    default_src = None
    if default_path.exists():
        try:
            default_src = ET.fromstring(default_path.read_text(encoding="utf-8"))
        except Exception:
            default_src = None
    for role in REQUIRED_ROLES:
        outp = d / f"template{template_num}_{role}.xml"
        if outp.exists():
            continue
        if role == "header":
            _write_p(outp, _hp_p(""))
            continue
        if default_src is not None:
            p_copy = ET.fromstring(ET.tostring(default_src, encoding="utf-8"))
            t = p_copy.find(f".//{{{HP_NS}}}t")
            if t is None:
                run = ET.SubElement(p_copy, f"{{{HP_NS}}}run")
                t = ET.SubElement(run, f"{{{HP_NS}}}t")
            t.text = DEFAULT_STUB_TEXT.get(role, "")
            _write_p(outp, p_copy)
        else:
            _write_p(outp, _hp_p(DEFAULT_STUB_TEXT.get(role, "")))

# ====== role_classifier.py 통합 ======
def guess_role(feat: dict) -> str:
    lead = feat.get("lead", "")
    is_table = feat.get("is_table", 0)
    has_colPr = feat.get("has_colPr", 0)
    if is_table and has_colPr:
        if lead in ("I", "Ⅰ"): return "title2"
        if lead in ("1",):     return "title3"
        return "title1"
    if lead in ("▢",): return "list1"
    if lead in ("❍",): return "list2"
    if lead in ("•",): return "list3"
    if lead in ("▷",): return "list4"
    if not lead:       return "blank"
    return "default1"

# ====== template_extractor.py 통합 ======
def _serialize_hp_pretty(elem: ET.Element) -> str:
    ET.register_namespace("hp", NS["hp"])
    e = ET.fromstring(ET.tostring(elem, encoding="utf-8"))
    _remove_linesegarray(e)
    rough = ET.tostring(e, encoding="utf-8")
    pretty = minidom.parseString(rough).toprettyxml(indent="  ", encoding="utf-8")
    return pretty.decode("utf-8") if isinstance(pretty, (bytes, bytearray)) else pretty

def _template_signature(header_snippet: str, first_feats: list[dict]) -> str:
    key = (header_snippet or "")[:256]
    key += "|" + "|".join(f'{f.get("is_table")}:{f.get("paraPrIDRef")}:{f.get("charPrIDRefs")}:{f.get("lead")}' for f in first_feats[:5])
    return hashlib.sha1(key.encode("utf-8")).hexdigest()

def extract_templates(section0_path: str, out_dir: str, template_num: int = 1) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    xml_text = Path(section0_path).read_text(encoding="utf-8")
    idx = xml_text.find("<hp:p")
    header_xml = xml_text[:idx] if idx != -1 else ""
    Path(out_dir, f"template{template_num}_header.xml").write_text(header_xml, encoding="utf-8")

    root = ET.fromstring(xml_text)
    paras = root.findall("hp:p", NS)

    rows, feats_for_sig = [], []
    for i, p in enumerate(paras):
        feat = para_features(p)
        h = structure_hash(p)
        role = guess_role(feat)
        rows.append({"idx": i, "hash": h, "role": role, **feat})
        if i < 5: feats_for_sig.append(feat)

    # 대표 문단 저장
    written = set()
    for r in rows:
        role = r["role"]
        if role in written: continue
        para = paras[r["idx"]]
        Path(out_dir, f"template{template_num}_{role}.xml").write_text(_serialize_hp_pretty(para), encoding="utf-8")
        written.add(role)

    # 미리보기/프리셋
    if rows:
        with open(Path(out_dir, f"template{template_num}_preview.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader(); w.writerows(rows)

    sig = _template_signature(header_xml, feats_for_sig)
    preset = {"signature": sig, "generated_from": Path(section0_path).name, "roles_preview": rows[:20]}
    Path(out_dir, f"template{template_num}_map.json").write_text(json.dumps(preset, ensure_ascii=False, indent=2), encoding="utf-8")

    ensure_complete_template_set(out_dir, template_num)
    return {"out_dir": out_dir, "signature": sig, "roles_count": Counter([r["role"] for r in rows])}

# ====== test_runner.py 통합 ======
def _load_templates_by_hash(template_glob: str) -> dict:
    mapping = {}
    for path in Path().glob(template_glob):
        name = path.name
        if not re.match(r"template\d+_.+?\.xml$", name): continue
        try:
            root = ET.fromstring(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        h = structure_hash(root)
        m = re.match(r"(template\d+)_(.+?)\.xml$", name)
        role = m.group(2) if m else ""
        mapping[h] = {"path": str(path), "role": role}
    return mapping

def evaluate_templates(section0_path: str, template_dir: str, out_csv: str) -> dict:
    tmap = _load_templates_by_hash(os.path.join(template_dir, "template1_*.xml"))
    xml_text = Path(section0_path).read_text(encoding="utf-8")
    root = ET.fromstring(xml_text)
    paras = root.findall("hp:p", NS)

    rows = []
    for i, p in enumerate(paras):
        feat = para_features(p)
        h = structure_hash(p)
        guessed = guess_role(feat)
        matched = tmap.get(h)
        matched_role = matched["role"] if matched else ""
        rows.append({
            "idx": i, "hash": h, "lead": feat.get("lead",""),
            "is_table": feat.get("is_table",0), "has_colPr": feat.get("has_colPr",0),
            "paraPrIDRef": feat.get("paraPrIDRef",""), "charPrIDRefs": feat.get("charPrIDRefs",""),
            "guessed_role": guessed, "matched_template_role": matched_role,
            "exact_structure_match": 1 if matched else 0,
        })
    Path(os.path.dirname(out_csv)).mkdir(parents=True, exist_ok=True)
    if rows:
        with open(out_csv, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader(); w.writerows(rows)

    total = len(rows)
    exact = sum(r["exact_structure_match"] for r in rows)
    agree = sum(1 for r in rows if r["matched_template_role"] and r["matched_template_role"] == r["guessed_role"])
    summary = {"total_paragraphs": total, "exact_structure_hash_matches": exact, "role_agreements": agree}
    Path(out_csv.replace(".csv", "_summary.json")).write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    # 간단 리포트
    _make_report(out_csv, out_csv.replace(".csv", "_summary.json"), out_csv.replace(".csv", "_report.md"))
    return summary

def _make_report(csv_path: str, summary_json_path: str, out_md: str):
    rows = []
    if os.path.exists(csv_path):
        with open(csv_path, encoding="utf-8") as f:
            r = csv.DictReader(f)
            rows = list(r)
    summary = json.loads(Path(summary_json_path).read_text(encoding="utf-8"))

    roles = sorted(set([r["guessed_role"] for r in rows] + [r["matched_template_role"] for r in rows if r["matched_template_role"]]))
    if "(none)" not in roles:
        roles.append("(none)")
    mat = {g:{m:0 for m in roles} for g in roles}
    for r in rows:
        g = r["guessed_role"]
        m = r["matched_template_role"] if r["matched_template_role"] else "(none)"
        mat[g][m] = mat[g].get(m, 0) + 1

    per_role = defaultdict(lambda: {"total":0, "agree":0})
    for r in rows:
        key = r["matched_template_role"] if r["matched_template_role"] else "(none)"
        per_role[key]["total"] += 1
        if r["matched_template_role"] and r["matched_template_role"] == r["guessed_role"]:
            per_role[key]["agree"] += 1

    out = Path(out_md); out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(f"# Auto Template Evaluation Report\n\n")
        f.write(f"- Total paragraphs: **{summary['total_paragraphs']}**\n")
        f.write(f"- Role agreements: **{summary['role_agreements']}**\n")
        f.write(f"- Exact structure matches: **{summary['exact_structure_hash_matches']}**\n\n")
        f.write("## Confusion Matrix (guessed → matched)\n\n")
        header = "| guessed \\ matched | " + " | ".join(roles) + " |\n"
        sep = "|" + "---|"*(len(roles)+1) + "\n"
        f.write(header); f.write(sep)
        for g in roles:
            row = [str(mat.get(g, {}).get(m, 0)) for m in roles]
            f.write("| " + g + " | " + " | ".join(row) + " |\n")
        f.write("\n## Per-role Accuracy\n\n| role | total | agree | accuracy |\n|---|---:|---:|---:|\n")
        for role, stat in per_role.items():
            total, agree = stat["total"], stat["agree"]
            acc = f"{(agree/total*100):.1f}%" if total else "-"
            f.write(f"| {role} | {total} | {agree} | {acc} |\n")
