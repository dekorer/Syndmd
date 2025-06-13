import re

def parse_markdown(text: str):
    results = []

    for line in text.splitlines():
        line = line.rstrip()

        # 헤더 처리: # ~ ######까지
        heading_match = re.match(r'^(#{1,6})\s*(.+)', line)
        if heading_match:
            level = len(heading_match.group(1))
            content = heading_match.group(2).strip()
            results.append((f"title{level}", f"{{{content}}}"))
            continue

        # 리스트 처리: 들여쓰기 기준으로 list1, list2...
        list_match = re.match(r'^(\s*)([-*+])\s+(.+)', line)
        if list_match:
            indent_spaces = len(list_match.group(1))
            content = list_match.group(3).strip()
            level = indent_spaces // 2 + 1  # 들여쓰기 2칸당 한 단계
            results.append((f"list{level}", f"{{{content}}}"))
            continue

         # 해당 없음: None 처리 + 내용 그대로
        results.append((None, f"{{{line.strip()}}}"))

    return results

if __name__ == "__main__":
    md_text = """
### 1. 개요
본 보고서는 2025년 6월 9일 기준, 특이사항 없이 평온하게 진행된 하루의 분위기 및 무작위적 사색을 기록한 자료이다. 보고서는 실질적인 정보 전달보다는 형식적 정제와 관찰자의 임의적 사고 전개를 목적으로 한다.
### 2. 관찰 내용
#### 2.1 시간의 흐름
오전 9시, 하루는 비교적 조용하게 시작되었으며, 커피의 향과 함께 컴퓨터의 팬이 가볍게 돌아가는 소리가 실내를 채웠다. 바깥은 흐린 하늘이 무언가를 예고하는 듯하였으나, 비는 내리지 않았다.
#### 2.2 무작위 사유
"문장은 어디까지 의미를 지녀야 하는가?"라는 질문이 떠올랐다. 의미가 없는 문장은 문장이 아닌가, 혹은 의미란 독자의 마음속에서만 태어나는 것인가. 예를 들어, 다음 문장을 보자:
이 문장이 말하는 바는 없다. 그러나 읽은 이는 어쩌면 이야기를 상상할 것이다. 의미란, 말보다 늦게 오는 것인지도 모른다.
#### 2.3 의도되지 않은 패턴
보고서 형식을 빌린 이 텍스트는 사실 보고할 대상을 갖고 있지 않다. 그러나 형식만으로도 무언가 체계가 있는 것처럼 보인다. 사람은 구조를 보면 내용을 상상한다. 글쓰기의 절반은 착각을 유도하는 기술이다.

### 3. 결론 및 제언
보고할 내용이 없음에도 불구하고 보고서를 작성하는 행위는 언어적 틀에 기대어 무(無)로부터 유(有)를 생성하는 일종의 마술과 같다. 앞으로도 이러한 무의미한 형식을 유지함으로써 사고의 실험을 지속할 수 있기를 바란다.

"""

    
parsed = parse_markdown(md_text)
for style, content in parsed:
    print(style, content)