import os
import shutil
import zipfile
import xml.etree.ElementTree as ET
import tempfile
import win32com.client


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
    # HWPX 저장: 51번 포맷 코드 사용
    hwp.SaveAs(hwpx_path, "HWPX")

    # 한/글 종료
    hwp.Quit()

    print(f"변환 완료: {hwpx_path}")


def unzip_hwpx(hwpx_path: str, output_dir: str) -> None:
    """HWPX 파일을 압축 해제"""
    with zipfile.ZipFile(hwpx_path, 'r') as zip_ref:
        zip_ref.extractall(output_dir)
    print("▶ HWPX 압축 해제 완료")


def parse_and_edit_section0(unzipped_path: str, new_texts: list[str]) -> None:
    """section0.xml을 파싱하고 텍스트 수정"""
    section_path = os.path.join(unzipped_path, "Contents", "section0.xml")
    tree = ET.parse(section_path)
    root = tree.getroot()

    ns = {"hp": "http://www.hancom.co.kr/hwpml/2011/paragraph"}

    paragraphs = root.findall("hp:p", ns)
    count = 0
    i = 0
    for p in paragraphs:
        ts = p.findall(".//hp:t", ns)

        # 텍스트 있는 문단인지 확인
        for t in ts:
            if t.text and t.text.strip():  # 공백이 아닌 실제 텍스트가 있는 경우
                if count < len(new_texts):
                    t.text = new_texts[count]
                    count += 1

        # paragraphs[0]을 XML 문자열로 변환
        xml_string = ET.tostring(paragraphs[i], encoding='unicode')

        # 파일로 저장
        
        filename = f"paragraph_{i}.xml"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(xml_string)

        print(f"▶ paragraphs[{i}] 저장 완료: {i}th paragraph.xml")
        i +=1   

    tree.write(section_path, encoding="utf-8", xml_declaration=True)
    print("▶ section0.xml 수정 완료")


def zip_hwpx(folder_path: str, output_hwpx_path: str) -> None:
    """수정된 내용을 다시 HWPX로 압축"""
    with zipfile.ZipFile(output_hwpx_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)
    print("▶ 수정된 HWPX 파일 압축 완료")



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


def automate_hwp_roundtrip(input_hwp_path: str, output_hwp_path: str, new_texts: list[str]) -> None:
    """HWP → HWPX → 수정 → 다시 HWP"""
    temp_dir = tempfile.mkdtemp()
    temp_hwpx = os.path.join(temp_dir, "converted.hwpx")
    temp_zip_dir = os.path.join(temp_dir, "unzipped")
    os.makedirs(temp_zip_dir, exist_ok=True)

    try:
        convert_hwp_to_hwpx(input_hwp_path, temp_hwpx)
        unzip_hwpx(temp_hwpx, temp_zip_dir)
        parse_and_edit_section0(temp_zip_dir, new_texts)
        zip_hwpx(temp_zip_dir, temp_hwpx)
        convert_hwpx_to_hwp(temp_hwpx, output_hwp_path)
    finally:
        shutil.rmtree(temp_dir)
        print("▶ 임시 폴더 정리 완료")


# 예시 실행
if __name__ == "__main__":
    input_hwp = os.path.abspath("한글-템플릿1.hwp")
    output_hwp = os.path.abspath("final_output.hwp")
    new_texts = ["새로운 문장1", "새로운 문장2", "세 번째 문단", "4번째 텍스트들", "5qjsWo xprtmxm"]

    automate_hwp_roundtrip(input_hwp, output_hwp, new_texts)

