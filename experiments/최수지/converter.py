from parser import parse_markdown
from hwp_writer import HwpWriter

def convert_md_to_hwp(md_text, output_path):
    parsed_blocks = parse_markdown(md_text)
    writer = HwpWriter()  # 템플릿 경로는 내부 고정
    writer.write_all(parsed_blocks)
    writer.save(output_path)
    writer.quit()
