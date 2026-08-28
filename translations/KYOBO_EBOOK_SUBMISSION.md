# 교보문고 영문·일문 전자책 납품 가이드

확인 기준일: 2026-08-28 (KST)

## 발행 구성

교보문고에는 텍스트 리플로우형 EPUB을 언어별 독립 상품으로 등록한다. PDF는 Google Play·검토용으로 유지하며 교보의 별도 판매상품으로 등록하지 않는다.

현재 산출물은 기술 사전검수본이다. OPF 식별자는 UUID이고 `dc:date`는 빌드 시각이므로, 실제 ISBN과 확정 발행일을 반영해 다시 빌드하기 전에는 교보에 업로드하지 않는다.

| 상품 | 주 납품 형식 | 전자책 ISBN | 발행일 | 정가 |
|---|---|---|---|---|
| 영어판 | EPUB 3.0 리플로우 | 발급 대기 | 결정 대기 | 결정 대기 |
| 일본어판 | EPUB 3.0 리플로우 | 발급 대기 | 결정 대기 | 결정 대기 |

따라서 교보 판매에 우선 필요한 ISBN은 영어 EPUB 1개와 일본어 EPUB 1개, 총 2개다. PDF까지 별도 판매하기로 바꾸면 형식별 ISBN을 추가한다. Google 전용 GGKEY는 교보 식별자로 사용할 수 없다.

## 직접 계약 조건

교보 eBook 파트너 등록은 법인사업자 또는 개인사업자만 가능하다. 개인저자 계정은 바로출판 POD 전용이다. 스칼라브릿지 명의의 직접 계약을 기본 경로로 삼는다.

계약 신청 전에 다음을 준비한다.

- 출판사 신고와 출판업이 포함된 사업자등록
- 국립중앙도서관에서 조회되는 전자책 ISBN 보유 디지털 콘텐츠 1종 이상
- 사업자명이 표시된 제1금융권 통장
- 사업자등록증 사본
- 스마일EDI 무료회원 가입, 로그인 확인, 신규계약 신청용 로그인 화면 첨부
- 정산용 전자세금계산서 승인에 사용할 인증서 준비
- 출판사명·임프린트명·대표자·정산 담당자 정보
- 대표자 1인 개인사업자는 약관 동의와 본인인증 준비
- 공동대표 개인사업자와 법인은 SignOK 전자계약용 범용 공동인증서 준비

전자세금계산서용·인터넷뱅킹용 인증서는 공동대표 개인사업자·법인의 전자계약 서명용 범용 공동인증서를 대신할 수 없다. 정산용 인증서와 서명용 인증서는 교보 안내에 따라 구분한다.

직접 계약 요건을 충족하지 못하면 교보 제휴사 e퍼플을 이용한다. e퍼플 공개 안내는 EPUB 제작 원고로 HWP·DOCX를 제시하므로, 완성 EPUB 수용 여부와 기존 디자인·구조 유지 가능성은 접수 전에 e퍼플에 확인한다.

## 기술 납품 기준

교보 공개 자료에서 EPUB·EPUB 3.0·PDF 지원은 확인된다. 다만 계약 후 적용되는 세부 제작 규격과 전체 수치 기준은 공개되어 있지 않다. 이번 교보 납품은 EPUB 3.0 리플로우형을 선택하고, 계약 승인 뒤 파트너시스템의 최신 제작 가이드가 다르면 그 값을 우선한다. PDF를 제출하지 않는 것은 이번 유통 계획이며 교보의 PDF 금지 규정이 아니다.

다음은 공개된 교보 강제 규격이 아니라 호환성과 검수 통과율을 높이기 위한 프로젝트 내부 사전검수 기준이다.

- EPUB 3.0 리플로우형, UTF-8
- 영어 en-US, 일본어 ja-JP 언어 메타데이터
- 제목, 부제, 저자, 발행처, 설명, 주제, 키워드, 권리정보 포함
- 발급된 ISBN을 OPF 고유 식별자와 판권면에 동일하게 기재
- 내장 표지와 별도 RGB JPG 표지 준비
- EPUB Navigation과 논리적 spine 순서 유지
- 본문 제목 구조와 목차 항목 일치
- 이미지 대체텍스트 포함
- JavaScript, 외부 멀티미디어, 사전 DRM, 암호화 제외
- 배포권이 불분명한 글꼴은 EPUB에 포함하지 않음
- 파일명은 영문·숫자·하이픈 중심
- EPUB과 별도 표지는 내부 목표로 각각 50MB 미만 유지. 이는 교보 공개 단권 상한이 아님
- EPUBCheck 오류 0건·경고 0건
- 교보 앱, PC e서재, 웹뷰어에서 목차·표·이미지·일본어 글꼴 대체·TTS 읽기 순서 확인

EPUB 2판은 계약 후 교보 검수팀이 요구할 경우에만 쓰는 호환용 파일이다. ISBN과 발행일을 반영한 EPUB 3.0판을 기본 제출한다.

## AI 활용 표시

두 번역판 모두 생성형 AI 활용 사실을 숨기지 않는다. 직접 eBook 파트너 등록 화면에 관련 선택 항목이 있으면 `Yes` 또는 `활용 있음`으로 등록하고, 항목이 없으면 상품정보 고지 방식은 담당자에게 확인한다. 적용 범위는 자료 조사, 한국어 원고의 영어·일본어 번역, 편집, 표지 및 본문 이미지 생성이다. 판권면에도 같은 취지의 고지를 넣고, 최종 선택·구성·수정·발행 책임은 저자에게 있음을 명시한다. 교보의 공개 AI 활용 등록 공지는 POD 기준이므로 eBook 화면의 필드명은 계약 후 다시 확인한다.

교보 상품정보에 사용할 한국어 안내문:

> 본 도서는 자료 조사, 번역, 편집 및 이미지 생성 과정에서 생성형 인공지능 기술을 보조적으로 활용했습니다. 저자가 최종 원고와 시각 자료를 검토하고 발행 책임을 집니다.

## 파일 구성

### 영어판

- 사전검수 EPUB 3.0(ISBN·발행일 반영 후 제출): translations/en/output/epub/semiconductor-interviews-answer-the-kings-question-en-EPUB3.epub
- 호환용 EPUB 2: translations/en/output/epub/semiconductor-interviews-answer-the-kings-question-en-EPUB2.epub
- 별도 표지 JPG: translations/en/output/cover/semiconductor-interviews-answer-the-kings-question-en-cover.jpg
- Google·보관용 PDF: translations/en/output/pdf/semiconductor-interviews-answer-the-kings-question-en.pdf

### 일본어판

- 사전검수 EPUB 3.0(ISBN·발행일 반영 후 제출): translations/ja/output/epub/semiconductor-interviews-answer-the-kings-question-ja-EPUB3.epub
- 호환용 EPUB 2: translations/ja/output/epub/semiconductor-interviews-answer-the-kings-question-ja-EPUB2.epub
- 별도 표지 JPG: translations/ja/output/cover/semiconductor-interviews-answer-the-kings-question-ja-cover.jpg
- Google·보관용 PDF: translations/ja/output/pdf/semiconductor-interviews-answer-the-kings-question-ja.pdf

실제 ISBN이 발급되면 교보가 요구하는 파일명 규칙에 맞춰 최종 이름을 다시 정한다. 발급 전 숫자 10자리·13자리 형태의 임시 파일명이나 가짜 ISBN을 사용하지 않는다.

## 상품등록 일치 규칙

항목마다 필요한 위치가 다르다. 서지정보는 같은 값을 사용하고, 가격·소개문처럼 OPF 표준 필드가 아닌 값은 파트너시스템에서 관리한다.

| 항목 | 파트너시스템 | EPUB OPF | 판권면 | 별도 표지 |
|---|---:|---:|---:|---:|
| 정식 제목·부제 | 필수 | 필수 | 필수 | 상품 식별이 가능하게 표시 |
| 저자·법적 발행처명 | 필수 | 필수 | 필수 | 저자 표기 권장 |
| 본문 언어 | 필수 | 필수 | 해당 언어로 작성 | 해당 언어로 작성 |
| EPUB ISBN·발행일 | 필수 | 필수 | 필수 | 필수 아님 |
| 정가 | 필수 | 표준 필드 아님 | 필수 아님 | 필수 아님 |
| AI 활용 고지 | 등록 항목·상품정보에서 처리 | 표준 필드 아님 | 수록 | 필수 아님 |
| 상품 소개·저자 소개 | 상품정보에서 처리 | 설명 메타데이터만 수록 | 별도 전문 불필요 | 불필요 |
| 목차 | 상품정보와 원고 기준 일치 | Navigation·spine에 수록 | 불필요 | 불필요 |

파트너시스템과 EPUB OPF에는 아래 정식 서명을 정확히 입력한다. 표지는 조판상 줄바꿈·부호·홍보 문구를 달리할 수 있지만 다른 책으로 오인될 표현은 쓰지 않는다.

- 영어: Semiconductor Interviews: Answer the King’s Question
- 일본어: 半導体面接――王の問いに答えよ

## 최종 제출 전 남은 확인

- [ ] 출판사신고확인증과 사업자등록증의 정확한 발행처명이 스칼라브릿지와 일치한다.
- [ ] 영어 EPUB ISBN과 일본어 EPUB ISBN이 국립중앙도서관에서 조회된다.
- [ ] 발행일과 정가가 확정됐다.
- [ ] 역자·현지화 기여자 표기 방식을 확정했다.
- [ ] 스칼라브릿지가 영문·일문 번역권과 전자적 복제·전송·유통 권한을 보유한다.
- [ ] 교보 eBook 사업자 파트너 계약이 승인됐다.
- [ ] 계약 후 제공되는 최신 제작 가이드와 파일을 대조했다.
- [ ] 두 EPUB에 실제 ISBN·발행일을 반영한 뒤 다시 빌드했다.
- [ ] 실제 발급값을 넣은 출시 메타데이터 JSON과 EPUBCheck 경로를 지정해 `python scripts/validate_translation_books.py --publication-ready --release-metadata <파일> --java <Java> --epubcheck-jar <JAR>`가 통과했다.
- [ ] EPUBCheck 오류·경고 0건을 확인했다.
- [ ] 교보 뷰어에서 영어·일본어판을 각각 확인했다.
- [ ] AI 생성·활용 도서로 표시했다.

## 공식 자료

- 교보 eBook 신규 거래 안내: https://www.kyobobook.co.kr/partners/ebook-new-guide
- 교보 디지털콘텐츠 파트너 가입: https://partner.kyobobook.co.kr/dpart/pcc/members
- 신규계약 필수 확인사항: https://partner.kyobobook.co.kr/dpart/pcc/members/downloadguide
- 교보 디지털콘텐츠 지원 포맷: https://company.kyobobook.co.kr/business/digital-contents
- 교보 eBook 이용안내: https://ebook.kyobobook.co.kr/dig/etc/ebookgdnc
- 교보 eBook 담당자 안내: https://www.kyobobook.co.kr/partners/chargeperson
- 교보 제휴 e퍼플 안내: https://store.kyobobook.co.kr/pod/introduce
- 교보 AI 활용 표시 공지(POD): https://store.kyobobook.co.kr/pod/notice/1007236
- 국제 ISBN 언어·형식별 배정 규정: https://www.isbn-international.org/content/isbn-assignment
