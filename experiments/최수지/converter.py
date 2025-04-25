from parser import parse_markdown
from hwp_writer import HwpWriter

def convert_md_to_hwp(md_text, output_path):
    parsed_blocks = parse_markdown(md_text)
    writer = HwpWriter()

    for block in parsed_blocks:
        writer.write_block(*block)  # 튜플을 그대로 언팩해서 넘김
    
    writer.save(output_path)
