import os
import shutil
import tempfile
import converter
import compressor
from merge_section0 import merge_paragraphs_with_header

def build_hwp_from_template_folder(
    template_unzipped_dir: str,
    paragraph_dir: str,
    output_hwp_path: str,
    templateNum: int,
    markdownText: str
) -> None:
    temp_dir = tempfile.mkdtemp()
    working_dir = os.path.join(temp_dir, "hwpx_build")
    os.makedirs(working_dir, exist_ok=True)

    try:
        # 1. 템플릿 디렉터리 복사
        shutil.copytree(template_unzipped_dir, working_dir, dirs_exist_ok=True)

        # 2. 병합된 section0.xml로 교체
        section0_path = os.path.join(working_dir, "Contents", "section0.xml")
        merge_paragraphs_with_header(paragraph_dir, section0_path, templateNum, markdownText)

        # 3. hwpx로 압축
        temp_hwpx_path = os.path.join(temp_dir, "merged.hwpx")
        compressor.zip_hwpx(working_dir, temp_hwpx_path)

        # 4. hwpx → hwp 변환
        converter.convert_hwpx_to_hwp(temp_hwpx_path, output_hwp_path)

    finally:
        shutil.rmtree(temp_dir)
        print("▶ 임시 작업 폴더 정리 완료")

# 예시 실행
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    template_unzipped_dir = os.path.join(current_dir, "template1_unzipped")
    paragraph_dir = os.path.join(current_dir, "paragraphs")
    output_hwp_path = os.path.join(current_dir, "결과문서.hwp")
    templateNum = 1
    text = """# 빈집 문제 해결을 위한 방안

## 1. 빈집 문제의 개요 아ㅓ미ㅓ너나ㅓㅏㅓㅓㅏㅣ너미ㅏ러머러ㅣㅓ ㅓ리ㅑ러ㅑ러ㅑㅣ멀;ㅑㅣ머랴ㅓ리ㅑㄴ어ㅣㄹ눌우;ㄹ문ㅇ러ㅓㅏㅓ나ㅣ리미더ㅑㅣ러ㅑㅣㄴ어랴ㅣ머ㅑㅓ랴ㅓㅁ랴ㅣㅓㅣㄴ어리ㅓㅑㅁㄷ러ㅣ너이러ㅑㄴ더랴ㅣ널이러미널댜러이러ㅣㅏㅁㄴ러ㅣㅏ너ㅣ랴ㅓㅑㅣㄴ더미낭리
최근 도시 및 농촌 지역에서 빈집 증가가 사회적 문제로 대두되고 있다. 인구 감소, 도시화, 경제적 요인 등으로 인해 방치된 빈집이 늘어나면서 안전 문제, 범죄 발생 가능성, 도시 미관 저해 등의 부작용이 발생하고 있다. 이를 해결하기 위해 다양한 방안을 모색해야 한다.

## 2. 빈집 문제의 주요 원인
- 인구 감소: 저출산 및 고령화로 인해 주택 수요 감소ㅇ렁너랸머러ㅣ머리ㅓ러닝러ㅣ머ㅣ냐ㅓㅑㅓㅑㅓㅑ;ㅣ너랴ㅣ너랴니ㅓㅑㅣ리ㅑ러ㅑㅣ어ㅣㅑ너ㅑㅣ더ㅣㅑㅓㅣㅁ냐ㅣㅓ댜ㅣㅓㅑㅣ머야너랴ㅣㅓ먀ㅣㄴ더랴ㅣㅓ먀ㅣ너ㅑㅣ너ㅑㅣ러ㅣㅑ러이머;ㄹㅇ널너ㅣㄴ어랴ㅣㅓ너ㅑㅣㅓ랴ㅣㅓ냐ㅣ머냔
- 도시화: 지방의 인구가 대도시로 집중되면서 빈집 발생 증가
- 경제적 요인: 부동산 경기 침체 및 주택 유지보수 비용 증가
- 법적·행정적 문제: 소유주 부재, 상속 문제 등으로 인해 관리가 어려움

## 3. 빈집 문제 해결 방안
### 3.1. 정책적 지원 강화
- 빈집 실태 조사 및 데이터베이스 구축
  - 전국 단위의 빈집 데이터베이스를 구축하여 체계적으로 관리
  - 빈집 정보를 시민과 기업에 공개하여 활용 가능하도록 함
- 빈집 정비 및 철거 지원
  - 노후 빈집 철거 비용 지원
  - 철거 후 공공시설, 주차장, 공원 등으로 활용
- 세제 혜택 제공
  - 빈집 소유주가 개보수 후 임대·매매할 경우 세금 감면
  - 장기 방치된 빈집에 대한 과세 강화로 활용 유도

### 3.2. 빈집 활용 방안
- 청년 및 신혼부부 주거 지원
  - 리모델링을 통해 저렴한 임대주택으로 전환
  - 공공기관과 협력하여 사회적 주택으로 운영
- 지역 공동체 공간 조성
  - 빈집을 지역 커뮤니티 공간(카페, 도서관, 복지관 등)으로 변환
- 아무 리스트나 적어보기
  - 문화예술 공간, 스타트업 창업 공간으로 활용
- 스마트팜 및 도시 농업 시설로 활용
  - 도심 빈집을 활용하여 실내 농업 및 스마트팜 조성

### 3.3. 민관 협력 강화
- **기업 및 사회적 경제 조직과 협력**
  - 민간 기업이 빈집을 활용한 리모델링 사업에 참여하도록 장려
  - 사회적 기업 및 비영리 단체와 협력하여 공익적 활용
- **지방자치단체의 적극적 개입**
  - 지역 특성에 맞는 빈집 활용 모델 개발
  - 공공-민간 협력을 통한 재생 사업 추진
  - 아무 말이나 적어보기

## 4. 결론
빈집 문제는 단순히 개별 주택의 문제가 아니라 지역 사회 전반에 영향을 미치는 사회적 이슈이다. 따라서 정책적 지원, 빈집 활용 방안, 민관 협력 등의 다각적인 접근이 필요하다. 빈집을 단순한 방치된 공간이 아닌 새로운 기회로 전환하여 지역 활성화와 사회적 가치를 창출하는 방향으로 나아가야 한다.
### 정책적 지원 강화
- 빈집 실태 조사 및 데이터베이스 구축
  - 전국 단위의 빈집 데이터베이스를 구축하여 체계적으로 관리
  - 빈집 정보를 시민과 기업에 공개하여 활용 가능하도록 함
- 빈집 정비 및 철거 지원
  - 노후 빈집 철거 비용 지원
  - 철거 후 공공시설, 주차장, 공원 등으로 활용
- 세제 혜택 제공
  - 빈집 소유주가 개보수 후 임대·매매할 경우 세금 감면
  - 장기 방치된 빈집에 대한 과세 강화로 활용 유도
### 정책적 지원 강화
### 정책적 지원 강화

## 오번째 또 옴
### 오번째 원
- 가나다라
- 라럼니ㅏㄹ
  - 러아ㅓㅏ랑
  - ㄹ어ㅏ러ㅏㅇ
    - 러ㅏㅇ러ㅏㅇㄴ
      - rjkljafkla
### 오번째 둘
### 오번째 셋

## 아무 제목이나 적기

"""

    build_hwp_from_template_folder(template_unzipped_dir, paragraph_dir, output_hwp_path, templateNum, text)