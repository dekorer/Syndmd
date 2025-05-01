import argparse
import os
from converter import convert_md_to_hwp


def load_markdown(source):
    # 파일 경로면 파일 읽기, 아니면 직접 마크다운 문자열로 처리
    if os.path.exists(source):
        try:
            with open(source, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"❌ 파일 열기 실패: {e}")
            return None
    else:
        return source  # 직접 입력한 마크다운 문자열


def main():
    parser = argparse.ArgumentParser(description="Markdown → HWP 변환기")
    parser.add_argument("input", help="입력값: 파일 경로 또는 직접 마크다운 문자열")
    parser.add_argument("output", help="출력 HWP 파일 경로")
    args = parser.parse_args()

    print(f"입력: {args.input}")
    print(f"출력: {args.output}")

    md_text = load_markdown(args.input)
    if not md_text:
        print("⚠️ 입력값을 불러오지 못했습니다.")
        return

    print("🔄 변환 중...")
    convert_md_to_hwp(md_text, args.output)
    print("✅ 변환 완료!")


if __name__ == "__main__":
    main()
