# Quarto Korean POD Book

한국어 Quarto 원고를 **교정 가능한 소스 → A5 POD 내지 → 펼침표지 → EPUB → 최종 검수 자료**로 완성하기 위한 Codex 스킬입니다.

단순히 PDF를 한 번 출력하는 도구가 아닙니다. 책의 내용과 근거를 먼저 검토하고, 인쇄 사양을 확정한 뒤, 조판·표지·전자책·검수·Git 인계까지 하나의 재현 가능한 작업 흐름으로 관리합니다.

## 주요 기능

- 한국어 장문 원고의 목차·장 구조·중복 논지 점검
- 수치와 주장에 대한 출처·단위·기준일·사실/추정/전망 구분
- A5 내지의 한글 글꼴, 행간, 표, 각주, 고아줄·과부줄 점검
- PDF와 EPUB의 동시 제작 및 산출물 분리
- 실제 쪽수와 종이 두께에 따른 책등·날개 펼침표지 계산
- 종이책/전자책 ISBN, 정가, 발행처, 바코드의 불일치 방지
- 차트의 흑백 인쇄 가독성과 삽화의 일관된 아트 디렉션 점검
- 독립 레드팀 검수와 GitHub 인계 기록 작성

## 설치

### 1. 저장소 전체를 받은 뒤 복사

```bash
git clone https://github.com/waterfirst/Debate-on-Semiconductor-Technology-and-the-Humanities.git
mkdir -p ~/.codex/skills
cp -R Debate-on-Semiconductor-Technology-and-the-Humanities/skills/quarto-korean-pod-book \
  ~/.codex/skills/
```

업데이트를 계속 받으려면 복사 대신 심볼릭 링크를 사용할 수 있습니다.

```bash
ln -s "$(pwd)/Debate-on-Semiconductor-Technology-and-the-Humanities/skills/quarto-korean-pod-book" \
  ~/.codex/skills/quarto-korean-pod-book
```

### 2. 필요한 실행 환경

- [Quarto](https://quarto.org/)
- Python 3
- PDF 조판용 TeX 배포판: [TinyTeX](https://quarto.org/docs/output-formats/pdf-engine.html#installing-tex) 또는 TeX Live
- 프로젝트가 지정한 한국어 글꼴

현재 개발 환경에서는 Quarto 1.9.38과 Python 3.12에서 점검했습니다. 실제 POD 제출 규격은 이용할 인쇄소나 유통 플랫폼의 최신 안내를 우선합니다.

## 빠른 시작

책 프로젝트 폴더에서 Codex를 실행하고 다음처럼 요청합니다.

```text
$quarto-korean-pod-book 스킬을 사용해 이 Quarto 원고를 점검해줘.
먼저 현재 목차, 출판 메타데이터, 미확정 항목과 위험 요소를 보고하고
내 승인 전에는 ISBN·정가·쪽수·책등을 추정해서 확정하지 마라.
```

기존 책을 출간 후보본으로 만드는 예시:

```text
$quarto-korean-pod-book 스킬로 한국어 A5 POD 출간 후보본을 만들어줘.
본문을 교정하고 근거를 검증한 뒤 PDF와 EPUB을 렌더해라.
최종 쪽수로 책등을 다시 계산하고, 대표 페이지를 이미지로 검수한 뒤
남은 인쇄소 의존 항목을 별도로 보고해라.
```

## 권장 작업 순서

1. **출판 계약 확정** — 판형, 종이, 제본, 날개, 도련, 가격, ISBN과 산출물을 기록합니다.
2. **내용 교정** — 목차와 장별 판단축을 먼저 고정하고 중복 장을 정리합니다.
3. **근거 검증** — 실제·추정·전망·가정을 구분하고 직접 출처를 연결합니다.
4. **차트·삽화 제작** — 본문이 확정된 뒤 최종 A5 크기와 흑백 인쇄를 기준으로 만듭니다.
5. **PDF·EPUB 렌더** — 같은 동결 소스에서 출력하고 대표 페이지와 의심 페이지를 직접 봅니다.
6. **표지 계산** — 내지 최종 쪽수가 확정된 뒤 책등과 펼침표지를 다시 계산합니다.
7. **레드팀 검수** — 내용, 데이터, 디자인, 산출물을 독립적으로 재검토합니다.
8. **Git 인계** — 소스와 생성물을 구분하고 테스트 결과·미확정 사항을 기록합니다.

세부 실행 규칙은 [`SKILL.md`](SKILL.md), 제작 수치는 [`references/publishing-specs.md`](references/publishing-specs.md), 최종 검수 항목은 [`references/red-team-checklist.md`](references/red-team-checklist.md)를 참고하세요.

## 포함된 검사 도구

### Quarto 책 구조 검사

```bash
python ~/.codex/skills/quarto-korean-pod-book/scripts/audit_quarto_book.py /path/to/book
```

필수 절 제목도 함께 검사할 수 있습니다.

```bash
python ~/.codex/skills/quarto-korean-pod-book/scripts/audit_quarto_book.py /path/to/book \
  --require-sections "출처" "90초 답변"
```

이 도구는 `_quarto.yml`에 등록된 장 파일, 중복 제목, 이미지 대체텍스트, 직접 URL이 없는 출처 절을 점검합니다.

### 책등·펼침표지 초기 계산

```bash
python ~/.codex/skills/quarto-korean-pod-book/scripts/calc_cover_geometry.py \
  --pages 262 \
  --paper-thickness-mm 0.12 \
  --wing-mm 80
```

계산값은 초기 설계용입니다. 최종 책등은 반드시 POD 플랫폼 또는 인쇄소의 종이별 계산값을 우선해야 합니다.

## 폴더 구성

```text
quarto-korean-pod-book/
├── README.md
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── publishing-specs.md
│   └── red-team-checklist.md
└── scripts/
    ├── audit_quarto_book.py
    └── calc_cover_geometry.py
```

## 중요한 안전 원칙

- ISBN, 정가, 발행일, 최종 쪽수와 인쇄 사양을 임의로 만들지 않습니다.
- 종이책 ISBN과 전자책 ISBN을 혼용하지 않습니다.
- 본문 수정 뒤에는 PDF·EPUB·표지를 함께 다시 생성합니다.
- 표지 책등은 내지 최종 쪽수가 확정되기 전에 고정하지 않습니다.
- 생성된 PDF만 보고 완료라 하지 않고 실제 페이지를 이미지로 렌더해 확인합니다.
- 다른 사람의 원고와 현재 Git 변경사항을 덮어쓰지 않습니다.
- 외부 이미지·글꼴·템플릿은 각각의 라이선스를 별도로 확인합니다.

## 감사와 오픈소스 고지

한국어 데이터 과학과 디지털 출판 생태계를 꾸준히 만들어 온 **[한국 알(R) 사용자회](https://github.com/bit2r)**에 감사드립니다. 특히 XeLaTeX 기반으로 한글 PDF 책을 조판하는 Quarto 확장인 **[bitPublish](https://github.com/bit2r/bitPublish)**와 공개된 사용 예시는 한국어 책을 코드로 재현 가능하게 출판하는 방법을 이해하는 데 큰 도움을 주었습니다.

이 `quarto-korean-pod-book` 스킬은 `bitPublish` 자체를 복제하거나 번들하지 않은 독립적인 출판·검수 워크플로입니다. 이 스킬의 코드에는 이 저장소의 [`LICENSE-CODE`](../../LICENSE-CODE)가 적용됩니다. `bitPublish`를 별도로 설치하거나 그 코드를 재사용할 때에는 원 프로젝트의 **GPL-2.0**을 따라야 하며, 원 프로젝트가 제공하는 예제 저작물에는 **CC BY-NC-SA** 조건이 적용됩니다.

Quarto와 Pandoc, TinyTeX 및 한국어 오픈 폰트 생태계의 개발자와 기여자에게도 감사드립니다.

## 라이선스와 책임 범위

- 이 스킬의 코드: 저장소 루트의 MIT [`LICENSE-CODE`](../../LICENSE-CODE)
- 책 원고와 고유 콘텐츠: 저장소 루트의 [`LICENSE-CONTENT.md`](../../LICENSE-CONTENT.md)
- 외부 프로젝트와 자산: 각 원출처의 라이선스 적용

이 스킬은 출판 준비를 돕지만, 특정 POD 플랫폼의 승인, 법률·세무 판단, 저작권 적법성 또는 인쇄 결과를 보증하지 않습니다.
