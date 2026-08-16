# 반도체 면접, 왕의 질문에 답하라

> 조선의 책문으로 훈련하는 AI·전쟁·환율·공급망 데이터 토론 30

조선시대 과거시험의 `책문(策問)`을 오늘의 반도체 산업 질문으로 다시 쓴 스칼라브릿지의 첫 단행본 프로젝트입니다. AI, 전쟁, 환율, 공급망, 노동, 환경, 기술윤리를 30개의 질문으로 구성하고, 데이터·대립 답안·판정 조건·90초 발언·꼬리 질문으로 훈련하도록 설계했습니다.

이 책은 특정 기업의 공식 채용 자료가 아니며 SK하이닉스 또는 다른 기업의 후원·검수·승인을 받지 않았습니다.

## 하루 만에 출판 교정쇄까지 만든 방식

짧은 시간에 출판 수준을 확보한 핵심은 글을 한 번에 길게 생성하는 것이 아니라, 원고·데이터·삽화·조판·검수를 서로 독립된 공정으로 나눈 것입니다.

1. 30개 책문의 제목과 판단 구조를 먼저 고정했습니다.
2. 모든 장을 `오늘의 책문 → 맥락 → 데이터 렌즈 → 근거 표 → 대립 답안 → 판정 조건 → 90초 발언 → 꼬리 질문`의 동일한 편집 규칙으로 만들었습니다.
3. 숫자에는 단위·기준 연도·출처를 붙이고, 비교할 수 없는 수치를 한 그래프에 억지로 합치지 않았습니다.
4. 막대그래프만 반복하지 않고 세로 막대, 추세선, 도넛, 롤리팝, 판단 매트릭스를 주제에 맞게 배치했습니다.
5. 30개 장별 삽화는 단색 연필 데생과 옅은 수묵 번짐으로 통일하고, 본문 30mm 크기에서 알아볼 수 있는 상징만 남겼습니다.
6. A5 PDF를 실제 이미지로 다시 렌더링해 장 번호, 고아 글자, 글자·단어 간격, 표 폭, 도형 정렬, 존댓말, 반복 코너를 눈으로 검수했습니다.
7. 마지막에 앞표지·본문·뒷표지를 결합한 완성본과 POD 제출용 본문·펼침표지를 별도로 만들었습니다.

생성형 AI는 조사 보조, 초안, 반론 탐색과 삽화 생성에 활용했습니다. 최종 문장, 사실관계, 도표, 이미지 선택, 편집과 발행 책임은 저자에게 있습니다.

## 편집 디자인

- 판형: A5, 148 × 210mm
- 본문: Pretendard Regular 10.5pt, 줄 간격 1.32
- 책문: KoPub바탕 Medium
- 장 제목: Pretendard SemiBold, 남색과 구리색 편집선
- 책문 상자: 미색 바탕, 남색 외곽선, 구리색 표제
- 삽화: 장별 30점, 단색 연필·수묵화 계열
- 표지: 갓의 창을 실리콘 웨이퍼로 재해석한 단순한 전면 디자인
- 발행처: 스칼라브릿지(표지 전면에는 저자명·출판사명 미표기, 판권면에만 표기)

## 사용한 도구와 패키지

- [Quarto](https://quarto.org/): 책의 목차, 장 번호, HTML·EPUB·PDF 렌더링
- Pandoc Lua filter: `오늘의 책문` 상자와 근거 표 열 너비 제어
- XeLaTeX/TinyTeX: A5 한글 조판, 글꼴 포함, 과부·고아줄 방지
- Python: 데이터 그림 생성, PDF 결합과 페이지 검증
- Node.js + Sharp: 표지 SVG 렌더링, 30개 삽화 분할과 크기 정규화
- pypdf, pypdfium2, ReportLab: PDF 병합, 메타데이터, 페이지 이미지 검수
- OpenAI GPT Image 2: 저자 기획·선정·편집 아래 장별 상징 삽화 생성 보조

## 저장소 구조

```text
book/
  _quarto.yml                 책 목차와 HTML·EPUB·PDF 설정
  print-style.tex             A5 한글 인쇄 조판
  book-question.lua           책문 상자와 표 열 폭 필터
  chapters/week01.qmd ...     30개 장 원고
  figures/                    데이터 시각화 30점
  figures/symbols/            수묵 연필 삽화 30점과 원본 시트
  cover/                      앞·뒤·책등·펼침표지 원본과 렌더링
  output/pdf/                 최종 PDF 산출물
scripts/
  enrich_content.py           장별 데이터·문맥 생성 규칙
  render_figures.py           데이터 시각화 생성
  crop_symbol_sheets.mjs      삽화 시트 30점 분할
  update_book_layout.mjs      장 구조·중복 코너·조판 문법 정리
  formalize_korean.mjs        존댓말 종결 검수
  render_cover_assets.mjs     표지 SVG를 인쇄용 PNG로 렌더링
SKILL.md                      이 출판 공정을 재사용하는 작업 지침
```

## 재현 방법

Quarto와 TinyTeX, Python 3, Node.js가 필요합니다. Python에는 `pypdf`, `pypdfium2`, `reportlab`을, Node.js에는 `sharp`를 준비합니다.

```powershell
# 1. 데이터 시각화와 삽화 자르기
python scripts/render_figures.py
node scripts/crop_symbol_sheets.mjs

# 2. 장 구조, 존댓말, 표지 자산 정리
node scripts/update_book_layout.mjs
node scripts/formalize_korean.mjs
node scripts/render_cover_assets.mjs

# 3. A5 본문 PDF
cd book
quarto render . --to pdf

# 4. EPUB
quarto render . --to epub

# 5. 앞표지+본문+뒷표지 및 POD 제출 파일
python cover/build_cover_pdfs.py
```

최종 산출물은 다음처럼 분리합니다.

- `본문-A5.pdf`: POD 내지 업로드용
- `인쇄용-펼침표지.pdf`: 뒤표지+책등+앞표지 업로드용
- `최종본.pdf`: 앞뒤를 포함해 독자가 전체 책을 확인하는 교정용
- `.epub`: 전자책 업로드 후보

## 출판 전 최종 확인

- 교보 POD에서 제공하는 실제 종이 종류와 책등 계산식으로 책등 폭을 다시 확정합니다.
- ISBN·가격·발행일을 확정한 뒤 판권면을 갱신합니다.
- 교보가 발급한 바코드를 뒷표지 흰색 영역에 넣습니다.
- 최신성이 중요한 수치의 기준일과 원출처를 다시 확인합니다.
- 전자책 미리보기에서 표, 수식, 이미지 대체텍스트와 목차 이동을 확인합니다.
- 생성형 AI 활용 여부는 유통사 입력 화면에서 사실대로 표시합니다.

## 라이선스

- 원고·도표 설명·편집 구성: `LICENSE-CONTENT.md`
- 코드: `LICENSE-CODE` (MIT)

