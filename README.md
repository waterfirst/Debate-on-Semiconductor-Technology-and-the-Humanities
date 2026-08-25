# 반도체 면접, 왕의 질문에 답하라

> 조선의 책문으로 훈련하는 AI·공정·설계·공급망 데이터 토론

> **저작권 고지:** 책 원고·고유한 질문과 해설·편집 구성·도표·삽화·표지는 별도 표시가 없는 한 © 2026 최낙초. All rights reserved. 저장소 공개는 무단 복제·배포·번역·상업적 재사용이나 AI 학습용 데이터셋 편입을 허락한다는 뜻이 아닙니다. 제작 코드는 별도의 MIT 라이선스를 따릅니다. 자세한 범위는 [COPYRIGHT_NOTICE.md](COPYRIGHT_NOTICE.md)를 확인하세요.

조선시대 과거시험의 `책문(策問)`을 오늘의 반도체 산업 질문으로 다시 쓴 스칼라브릿지의 첫 단행본 프로젝트입니다. 30개 초고 가운데 반도체·디스플레이 지원자의 토론 훈련과 직접 연결되는 19개 핵심 질문을 선별하고, 데이터·대립 답안·AI 조사 설계·90초 발언·꼬리 질문으로 훈련하도록 설계했습니다.

이 책은 특정 기업의 공식 채용 자료가 아니며 기업의 후원·검수·승인을 받지 않았습니다.

## 현재 출간 상태

PDF·EPUB·인쇄용 날개 펼침표지까지 만든 **POD 제출 최종본**입니다. 종이책 ISBN `979-11-220895-8-5 (03500)`, 정가 15,000원과 발행예정일 2026년 8월 30일을 반영했습니다. 초판은 추천사·서평 없이 발행합니다.

- 교보 제출 절차와 체크리스트: [KYOBO_PUBLISHING_GUIDE.md](KYOBO_PUBLISHING_GUIDE.md)
- 개인정보를 제거한 POD 7일 출시·가격·홍보 템플릿: [POD_LAUNCH_SPRINT_TEMPLATE.md](POD_LAUNCH_SPRINT_TEMPLATE.md)
- 19개 출간 장 선별 기준과 정가 판단: [EDITORIAL_CURATION.md](EDITORIAL_CURATION.md)
- Claude 등 외부 감수자 전달용 점검표: [EXTERNAL_REVIEW_BRIEF.md](EXTERNAL_REVIEW_BRIEF.md)
- 이 프로젝트의 재현 가능한 편집·출판 절차: [SKILL.md](SKILL.md)
- 다른 Quarto 책에도 설치해 쓰는 재사용 스킬: [skills/quarto-korean-pod-book/SKILL.md](skills/quarto-korean-pod-book/SKILL.md)
- 개인정보를 제거한 교육기관 검토 요청 메일 템플릿: [EDUCATION_PARTNER_REVIEW_EMAIL_TEMPLATE.md](EDUCATION_PARTNER_REVIEW_EMAIL_TEMPLATE.md)
- 렛유인 검토용 서문·목차·대표 장 2편: `book/output/pdf/렛유인-검토용-서문-목차.pdf`

## 하루 만에 출판 교정쇄까지 만든 방식

짧은 시간에 출판 수준을 확보한 핵심은 글을 한 번에 길게 생성하는 것이 아니라, 원고·데이터·삽화·조판·검수를 서로 독립된 공정으로 나눈 것입니다.

1. 30개 책문 초고의 제목과 판단 구조를 만든 뒤, 산업 연관성·주제 중복·가격을 함께 검토해 19개 핵심 장만 본문에 남겼습니다.
2. 모든 장을 `오늘의 책문 → 맥락 → 데이터 렌즈 → 근거 표 → 대립 답안 A·B·C → AI 조사 설계 → 신입사원 사례 → 90초 모범 발언 → 장별 꼬리 질문`의 동일한 편집 규칙으로 만들었습니다.
3. 숫자에는 단위·기준 연도·출처를 붙이고, 비교할 수 없는 수치를 한 그래프에 억지로 합치지 않았습니다.
4. 막대그래프만 반복하지 않고 세로 막대, 추세선, 도넛, 롤리팝, 판단 매트릭스를 주제에 맞게 배치했습니다.
5. 장별 삽화는 단색 연필 데생과 옅은 수묵 번짐으로 통일하고, 본문 30mm 크기에서 알아볼 수 있는 상징만 남겼습니다.
6. 출간 장 가운데 실제 응시자 답안과 시험 등위가 함께 확인되는 12개 장에는 답안의 사고법을 90초 발언에 한 문장씩 연결하고, 인물·등위·현대어 의역·직접 출전을 각주로 밝혔습니다.
7. 장 범위를 나눈 집필 에이전트와 서로의 원고를 읽는 교차 레드팀을 운영해 수치 정의, 가정 표시, 직접 출처, 사례의 실제 선택을 다시 검증했습니다. 저자의 다른 글은 객관적 근거에서 제외했습니다.
8. A5 PDF를 실제 이미지로 다시 렌더링해 장 번호, 한자 글리프, 고아 글자, 글자·단어 간격, 표 폭, 도형 정렬, 존댓말, 반복 코너를 눈으로 검수했습니다.
9. 마지막에 앞표지·본문·뒷표지를 결합한 완성본과 POD 제출용 본문·펼침표지를 별도로 만들었습니다.

생성형 AI는 조사 보조, 초안, 반론 탐색과 삽화 생성에 활용했습니다. 최종 문장, 사실관계, 도표, 이미지 선택, 편집과 발행 책임은 저자에게 있습니다.

## 편집 디자인

- 판형: A5, 148 × 210mm
- 본문: Pretendard Regular 10.5pt, 줄 간격 1.36
- 책문: KoPub바탕 Medium, 한문 인용: Noto Serif KR
- 장 제목: Pretendard SemiBold, 남색과 구리색 편집선
- 책문 상자: 미색 바탕, 남색 외곽선, 구리색 표제
- 삽화: 출간 장별 19점, 단색 연필·수묵화 계열(제외 초고의 자산은 저장소에 보존)
- 표지: 밝은 한지와 낮의 수묵화 위에서 갓의 창을 실리콘 웨이퍼로 재해석한 전면 디자인
- 인쇄용 표지: 좌우 80mm 책날개, 본문 258쪽·미색모조 80g 기준 12.4mm 책등, 사방 3mm 도련과 접지 여유를 반영한 480.4 × 216mm 펼침표지
- 후면 왼쪽 하단에는 Scholar Bridge 로고를, 우측 하단에는 배정된 ISBN/EAN-13 바코드를 배치합니다.
- 제작 사양: 표지 컬러·무광 코팅, 내지 흑백, 미색모조 80g, 정가 15,000원. 표지 용지는 제작처가 지원하면 스노우 250g을 사용하고, 교보 POD에서는 선택 화면에 제공되는 250g 표지 용지를 확인합니다.
- 발행처: 스칼라브릿지. 표지 전면에는 미표기하고, 뒤표지 왼쪽 아래·책등 아래·판권면에 표기합니다.

## 사용한 도구와 패키지

- [Quarto](https://quarto.org/): 책의 목차, 장 번호, HTML·EPUB·PDF 렌더링
- Pandoc Lua filter: `오늘의 책문` 상자와 근거 표 열 너비 제어
- XeLaTeX/TinyTeX: A5 한글 조판, 글꼴 포함, 과부·고아줄 방지
- Python: 데이터 그림 생성, PDF 결합과 페이지 검증
- Node.js + Sharp: 표지 SVG 렌더링, 장별 삽화 분할과 크기 정규화
- pypdf, pypdfium2, ReportLab: PDF 병합, 메타데이터, 페이지 이미지 검수
- OpenAI GPT Image 2: 저자 기획·선정·편집 아래 장별 상징 삽화 생성 보조

## 저장소 구조

```text
book/
  _quarto.yml                 책 목차와 HTML·EPUB·PDF 설정
  print-style.tex             A5 한글 인쇄 조판
  book-question.lua           책문 상자 필터
  table-widths.lua            근거 표 열 폭 최적화 필터
  hanja-font.lua              한문 인용 전용 글꼴 라우팅
  chapters/week01.qmd ...     30개 초고(출간 목차에는 19개 선별)
  figures/                    장별 데이터 시각화 원본·인쇄본
  figures/symbols/            수묵 연필 삽화의 고해상도 원본·흑백 인쇄본
  cover/                      앞·뒤·책등·책날개·펼침표지 원본과 렌더링
  output/pdf/                 최종 PDF 산출물
scripts/
  audit_manuscript.py         출간 장 구조·출처·꼬리질문 자동 감사
  audit_hanja_fonts.py        원고 한자와 인쇄 글꼴의 전수 대조
  check_source_links.py       직접 출처 URL 상태 점검
  enrich_content.py           검수된 원고를 보존하며 데이터 도표 SVG 생성
  render_chapter_figures.mjs  장별 데이터 도표를 PNG로 렌더링
  prepare_print_images.py     삽화·도표를 흑백 인쇄본으로 최적화
  activate_print_images.py    원고 이미지 경로를 인쇄본으로 전환
  render_cover_assets.mjs     표지 SVG를 인쇄용 PNG로 렌더링
  verify_publish_artifacts.py PDF·EPUB 쪽수·판형·도련·발행처 검증
  build_recommendation_packets.py 과거 추천사 요청용 도구(초판에서는 사용하지 않음)
  build_letyuin_review_packet.py 렛유인 전달용 서문·목차 발췌본 생성
SKILL.md                      이 출판 공정을 재사용하는 작업 지침
skills/quarto-korean-pod-book/ 다른 Quarto 책에 설치해 쓰는 범용 출판 스킬
```

## 재현 방법

Quarto와 TinyTeX, Python 3, Node.js가 필요합니다. Python에는 `pypdf`, `pypdfium2`, `reportlab`을, Node.js에는 `sharp`를 준비합니다.

```powershell
# 1. 원고·출처·한자 구조 감사
python scripts/audit_manuscript.py
python scripts/check_source_links.py
python scripts/audit_hanja_fonts.py

# 2. 데이터 도표와 흑백 인쇄 이미지 준비
python scripts/enrich_content.py
node scripts/render_chapter_figures.mjs
python scripts/prepare_print_images.py
python scripts/activate_print_images.py

# 3. 최종 쪽수로 계산한 책등의 표지 자산 렌더링
node scripts/render_cover_assets.mjs

# 4. EPUB을 먼저 만들고 안정된 출력 폴더에 보존
cd book
quarto render . --to epub
Copy-Item "_book/*.epub" "output/epub/반도체-면접-왕의-질문에-답하라.epub" -Force

# 5. A5 본문 PDF와 POD 제출 파일
quarto render . --to pdf
python cover/build_cover_pdfs.py

# 6. 쪽수·판형·도련·발행처 메타데이터 검증
cd ..
python scripts/validate_book.py
python scripts/verify_publish_artifacts.py
```

최종 산출물은 다음처럼 분리합니다.

- `본문-A5.pdf`: POD 내지 업로드용
- `인쇄용-펼침표지.pdf`: 왼쪽 책날개+뒤표지+책등+앞표지+오른쪽 책날개 업로드용
- `최종본.pdf`: 앞뒤를 포함해 독자가 전체 책을 확인하는 교정용
- `.epub`: 전자책 업로드 후보

## 출판 전 최종 확인

- 개인정보를 제거한 단계별 실행 체크리스트: [PUBLISHING_EXECUTION_CHECKLIST.md](PUBLISHING_EXECUTION_CHECKLIST.md)

- 교보 POD에서 제공하는 실제 종이 종류와 책등 계산식으로 책등 폭을 다시 확정합니다.
- 현재 12.4mm는 교보 가격책정 화면이 258쪽·미색모조 80g 선택에 대해 제시한 예상 책등 두께입니다. 교보의 등록 사양을 바꾸면 `python book/cover/build_cover_pdfs.py --spine-mm 값`으로 다시 조립하고 표지 SVG의 책등 폭도 같은 값으로 조정합니다.
- 전자책 ISBN·발행일을 확정한 뒤 판권면을 갱신합니다.
- 초판은 추천사·서평 없이 확정했으므로 관련 빈 페이지나 유보 문구를 넣지 않습니다.
- 교보가 발급한 바코드를 뒷표지 흰색 영역에 넣습니다.
- 최신성이 중요한 수치의 기준일과 원출처를 다시 확인합니다.
- 전자책 미리보기에서 표, 수식, 이미지 대체텍스트와 목차 이동을 확인합니다.
- 생성형 AI 활용 여부는 유통사 입력 화면에서 사실대로 표시합니다.

다음 단행본으로 `waterfirst/insight-lab`을 옮겨 제작할 때의 작업 인계서는 [INSIGHT_LAB_BOOK_BATON.md](INSIGHT_LAB_BOOK_BATON.md)에 있습니다.

## 다음 책에서 재사용하는 방법

범용 스킬은 `skills/quarto-korean-pod-book`에 있습니다. 새 PC에서는 이 폴더를 `%USERPROFILE%\.codex\skills\quarto-korean-pod-book`으로 복사한 뒤 Codex에 `$quarto-korean-pod-book`을 명시해 호출합니다. 스킬은 목차 선별, 근거 검증, 90초 발언 균형, 장별 삽화, A5 조판, PDF·EPUB 검수, 책등·날개 표지 계산과 GitHub 인계까지 같은 순서로 안내합니다.

## 라이선스

- 책 콘텐츠 저작권 범위: [COPYRIGHT_NOTICE.md](COPYRIGHT_NOTICE.md)
- 원고·도표 설명·편집 구성: [LICENSE-CONTENT.md](LICENSE-CONTENT.md)
- 코드: `LICENSE-CODE` (MIT)
