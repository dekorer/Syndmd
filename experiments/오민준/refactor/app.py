# app.py
from __future__ import annotations
from pathlib import Path
from hwpkit_io import ensure_unzipped_template
from templatekit import extract_templates, evaluate_templates
from mergekit import build_hwp_from_template_folder


def build_report_with_auto_template(
        base_hwp: str | None,  # 입력 HWP (없으면 unzipped_dir가 있어야 함)
        template_unzipped_dir: str,  # HWPX 압축해제 폴더(없으면 base_hwp에서 생성)
        auto_template_dir: str,  # auto 템플릿 출력 폴더
        markdown_path: str,  # 입력 MD 파일
        output_hwp: str,  # 결과 HWP 파일
        templateNum: int = 1,
        run_extractor: bool = True,
        run_tester: bool = False,
) -> str:
    # 1) 템플릿 폴더 준비
    tud = ensure_unzipped_template(template_unzipped_dir, base_hwp)

    # 2) auto 템플릿 추출(테스트 가능)
    if run_extractor:
        section0 = str(Path(tud) / "Contents" / "section0.xml")
        extract_templates(section0, auto_template_dir, templateNum)

    # 3) MD 읽기
    markdownText = Path(markdown_path).read_text(encoding="utf-8")

    # 4) 빌드
    out = build_hwp_from_template_folder(
        template_unzipped_dir=tud,
        paragraph_dir=auto_template_dir,
        output_hwp_path=output_hwp,
        templateNum=templateNum,
        markdownText=markdownText,
    )

    # 5) (옵션) 평가
    if run_tester:
        section0 = str(Path(tud) / "Contents" / "section0.xml")
        evaluate_templates(section0, auto_template_dir, str(Path("test_results") / "eval.csv"))

    return out


if __name__ == "__main__":
    build_report_with_auto_template(
        base_hwp="base.hwp",  # 없으면 None 주고 template_unzipped_dir를 준비
        template_unzipped_dir="template1_unzipped",
        auto_template_dir="auto_template1",
        markdown_path="input.md",
        output_hwp="결과문서_auto.hwp",
        templateNum=1,
        run_extractor=True,  # auto 템플릿 생성 유지(테스트 가능)
        run_tester=False  # 필요 시 True
    )
