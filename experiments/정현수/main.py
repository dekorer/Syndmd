import argparse
import os
from converter import convert_md_to_hwp


def main():
    parser = argparse.ArgumentParser(description="Markdown to HWP converter")
    parser.add_argument("input", help="Input markdown file path")
    parser.add_argument("output", help="Output HWP file path")
    args = parser.parse_args()
    
    print(f"입력 파일: {args.input}")
    print(f"출력 파일: {args.output}")

    if not os.path.exists(args.input):
        print("입력 파일이 존재하지 않습니다.")
        return

    with open(args.input, "r", encoding="utf-8") as f:
        md_text = f.read()

    print("마크다운 읽기 완료")

    convert_md_to_hwp(md_text, args.output)
    print("변환 완료");

if __name__ == "__main__":
    main()

