from parser import parse_markdown
from hwp_writer import HwpWriter

def convert_md_to_hwp(md_text, output_path):
    parsed_blocks = parse_markdown(md_text)
    writer = HwpWriter()

    for kind, content in parsed_blocks:
        if kind == "heading":
            writer.insert_paragraph(content, bold=True)
        elif kind == "bullet":
            writer.insert_paragraph("• " + content)
        elif kind == "hr":
            writer.insert_paragraph(content)
        else:
            writer.insert_paragraph(content)
    
    writer.save(output_path)    
