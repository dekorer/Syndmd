import os
import shutil

# 모듈화된 함수들 임포트
from hwp_converter import convert_hwp_to_hwpx, convert_hwpx_to_hwp
from hwpx_core import (
    unzip_hwpx,
    makeDict_charPr_height,
    split_section0_and_extract_charids,
    select_title_and_list_candidates_hybrid,
    copy_unzipped_and_rebuild_section,
    zip_hwpx
)
from md_parser import parse_markdown, clean_parsed_markdown, parse_and_show_markdown
from constants import register_namespaces # ET 등록을 위해 임포트 (필수는 아님)

def create_blank_hwp_with_dummy_args():
    if len(sys.argv) != 5:
        print("Error: This script requires exactly 4 arguments.")
        sys.exit(1)


    # 인자 1: 텍스트 내용이 담긴 임시 텍스트 파일의 경로
    text_path = sys.argv[1]

    #인자 2: 생성될 HWP 파일의 전체 경로
    output_hwp_path = sys.argv[2]

    # 인자 3: 사용자가 선택한 템플릿 파일의 경로
    template_path = sys.argv[3]
    
    # 인자 4: 사용자가 선택한 템플릿의 페이지 번호
    template_page = sys.argv[4]

    return text_path, output_hwp_path, template_path, template_page

if __name__ == "__main__":
        # --- ▼▼▼ 디버깅 코드 추가 1 ▼▼▼ ---
    print("\n--- [new0910.py] 스크립트 시작 ---")
    import sys
    print("전달받은 인자:", sys.argv)
    print("-----------------------------------")
    # --- ▲▲▲ 디버깅 코드 추가 1 ▲▲▲ ---
    # 1. UI로부터 인자 4개를 올바르게 받습니다.
    text_path, final_hwp_path, template_path, template_page_str = create_blank_hwp_with_dummy_args()

    # 2. 작업 디렉토리를 'final_hwp_path'가 위치할 폴더로 설정합니다.
    #    예: "C:\경로\결과물.hwp" -> "C:\경로"
    work_dir = os.path.dirname(final_hwp_path)
    os.makedirs(work_dir, exist_ok=True) # 작업 디렉토리 생성

    # 3. 페이지 번호를 정수로 변환합니다.
    try:
        startPage = int(template_page_str)
    except ValueError:
        print("오류: 페이지 번호 인자는 숫자여야 합니다.")
        sys.exit(1)

    # 4. 파일명 기반으로 파생 경로들을 생성합니다. (기준: template_path)
    base_name   = os.path.splitext(os.path.basename(template_path))[0]
    hwpx_Path   = os.path.join(work_dir, f"{base_name}.hwpx")
    unzipped_dir = os.path.join(work_dir, f"{base_name}_unzipped")

    # --- [STEP 1] HWP -> HWPX ---
    print(f"STEP 1: HWP -> HWPX 변환 ({template_path})")
    convert_hwp_to_hwpx(template_path, hwpx_Path)

    # --- [STEP 2] HWPX 압축 해제 ---
    print("STEP 2: HWPX 압축 해제")
    if os.path.isdir(unzipped_dir):
        shutil.rmtree(unzipped_dir)
    unzip_hwpx(hwpx_Path, unzipped_dir)

    # --- [STEP 3] header.xml에서 charId/height 맵 추출 ---
    print("STEP 3: 스타일(charId/height) 맵 추출")
    header_xml_path = os.path.join(unzipped_dir, "Contents", "header.xml")
    charid_size = makeDict_charPr_height(header_xml_path)

    # --- [STEP 4] section0.xml 문단 분리 및 정보 추출 ---
    print(f"STEP 4: 문단 분리 시작 (시작 페이지: {startPage})")
    paragraphs_dir = os.path.join(work_dir, "paragraphs")
    paragraph_charId, listable_map, bullet_map = split_section0_and_extract_charids(
        unzipped_path=unzipped_dir,
        out_dir=paragraphs_dir,
        start_page=startPage
    )

    # --- [STEP 5] 제목/리스트 후보 선정 ---
    print("STEP 5: 제목/리스트 후보 선정")
    n, m = 6, 6
    title_pids, list_pids = select_title_and_list_candidates_hybrid(
        paragraph_charId, charid_size, listable_map, bullet_map, n, m
    )
    print("선정된 제목 후보(pid):", title_pids)
    print("선정된 리스트 후보(pid):", list_pids)

    # --- [STEP 6] & [STEP 7] 마크다운 텍스트 파싱 및 정리 ---
    print("STEP 6 & 7: 입력 텍스트 파싱")
    # 이제 text_path (인자 1)를 직접 읽어옵니다.
    if os.path.isfile(text_path):
        with open(text_path, "r", encoding="utf-8") as f:
            md_text = f.read()

                        
            # --- ▼▼▼ 디버깅 코드 추가 2 ▼▼▼ ---
            print("\n--- 임시 텍스트 파일 내용 ---")
            print(md_text)
            print("---------------------------\n")
            # --- ▲▲▲ 디버깅 코드 추가 2 ▲▲▲ ---
            
    else:
        # 비상용 기본 텍스트
        md_text = "# 오류\n입력 텍스트 파일을 찾을 수 없습니다."
    
    tokens_raw = parse_markdown(md_text)
    tokens = clean_parsed_markdown(tokens_raw)

       # --- ▼▼▼ 디버깅 코드 추가 3 ▼▼▼ ---
    print("\n--- 파싱 후 토큰 결과 ---")
    print(tokens)
    print("-------------------------\n")
    # --- ▲▲▲ 디버깅 코드 추가 3 ▲▲▲ ---
    
    # --- [STEP 8] unzipped 작업본 생성 + section0.xml 재구성 ---
    print("STEP 8: 새 HWPX 컨텐츠 재구성")
    dst_unzipped_dir = os.path.join(work_dir, f"{base_name}_unzipped_built")

    new_section0_path = copy_unzipped_and_rebuild_section(
        src_unzipped_dir=unzipped_dir,
        dst_unzipped_dir=dst_unzipped_dir,
        paragraphs_dir=paragraphs_dir,
        title_pids=title_pids,
        list_pids=list_pids,
        tokens=tokens,
    )
    print("재구성된 section0.xml:", new_section0_path)
    
    # --- [STEP 9] 수정된 폴더 -> HWPX로 재압축 ---
    print("STEP 9: HWPX로 재압축")
    built_hwpx_Path = os.path.join(work_dir, f"{base_name}_built.hwpx")
    zip_hwpx(dst_unzipped_dir, built_hwpx_Path)
    print("재압축된 HWPX:", built_hwpx_Path)

    # --- [STEP 10] HWPX -> HWP 변환 (최종 경로 사용) ---
    print("STEP 10: 최종 HWP 파일로 변환")
    convert_hwpx_to_hwp(built_hwpx_Path, final_hwp_path)
    print("✔ 최종 HWP 생성 완료:", final_hwp_path)