import ast
import textwrap
import mistune

source_path = "C:/Users/pc/Desktop/빈집마크다운.txt"
target_path = "C:/Users/pc/Desktop/빈집마크다운.py"
output_path = "C:/Users/pc/Desktop/텍스트변환.txt"

# txt 파일을 함수로 감싸기
with open(source_path, 'r', encoding='utf-8') as f:
    content = f.read()

indented = '\n'.join('    ' + line for line in content.splitlines())
wrapped = f'def doc():\n    """\n{indented}\n    """'

with open(target_path, 'w', encoding='utf-8') as f:
    f.write(wrapped)

print("변환 완료: .txt → .py")

# AST로 docstring 추출
with open(target_path, 'r', encoding='utf-8') as f:
    data = f.read()

tree = ast.parse(data)
docstrings = [ast.get_docstring(n) for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]

# 공백 정리
processed = []
for doc in docstrings:
    cleaned = textwrap.dedent(doc).strip()
    processed.append(cleaned)

# Markdown AST 파서
markdown_parser = mistune.create_markdown(renderer='ast')

# 텍스트 추출
def get_text_from_node(node):
    if node['type'] == 'text':
        return node.get('raw', '')
    elif node['type'] == 'strong':
        inner = ''.join(get_text_from_node(c) for c in node.get('children', []))
        return f"**{inner}**"
    elif node['type'] == 'emphasis':
        inner = ''.join(get_text_from_node(c) for c in node.get('children', []))
        return f"*{inner}*"
    elif 'children' in node:
        return ''.join(get_text_from_node(c) for c in node['children'])
    return ''

# 결과 저장 리스트
output_lines = []

# AST 순회하며 정보 수집
def traverse_ast(nodes, lines, indent=0):
    for node in nodes:
        ntype = node.get('type')

        if ntype == 'heading':
            level = node['attrs']['level']
            text = get_text_from_node(node)
            output_lines.append(f"{'  ' * indent}제목 h{level}: {text}")

        elif ntype == 'list':
            ordered = node.get('ordered', False)
            for item in node['children']:
                item_text = get_text_from_node(item)
                indent_level = None
                for line in lines:
                    if item_text.strip() and item_text.strip() in line:
                        indent_level = len(line) - len(line.lstrip())
                        break
                output_lines.append(f"{'  ' * indent}리스트 ({'번호형' if ordered else '불릿형'}, 들여쓰기 {indent_level}): {item_text}")
                traverse_ast(item.get('children', []), lines, indent + 1)

        if 'children' in node:
            traverse_ast(node['children'], lines, indent)

# 실행 및 결과 저장
for doc in processed:
    ast_tree = markdown_parser(doc)
    lines = doc.splitlines()
    output_lines.append("\n 분석 결과:")
    traverse_ast(ast_tree, lines)

# 결과 파일로 저장
with open(output_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output_lines))

print(f"마크다운 분석 결과가 '{output_path}'에 저장되었습니다.")
