# 영문·일문 전자책 ISBN 신청 패킷

작성 기준일: 2026-08-28 (KST)

이 문서는 국립중앙도서관 ISBN 신청에 필요한 확정 정보와 미결정 정보를 분리해 관리한다. 실제 ISBN이 발급되기 전에는 EPUB, PDF, 표지, 판권면에 임시 번호를 넣지 않는다. 한국어 종이책 ISBN 979-11-220895-8-5는 번역판에 재사용하지 않는다.

## 권장 발급 구성

Google Play Books에는 언어별 도서 항목을 하나씩 만든다. 각 항목 안에서 EPUB ISBN을 기본 ISBN으로, PDF ISBN을 관련 ISBN으로 연결한다.

| Google 도서 항목 | 기본 형식 | 기본 ISBN | 관련 형식 | 관련 ISBN |
|---|---|---|---|---|
| 영어판 | EPUB 3.0 리플로우 | 발급 대기 | PDF | 발급 대기 |
| 일본어판 | EPUB 3.0 리플로우 | 발급 대기 | PDF | 발급 대기 |

정식 ISBN을 사용하는 현재 발행 계획에는 총 4개가 필요하다. 언어 변경과 전자책 파일 형식 변경은 각각 별도 ISBN 사유다. PDF를 교정용 내부 파일로만 보관하고 공개·판매·배포하지 않기로 변경하면 PDF용 2개는 신청 대상에서 제외할 수 있다.

## 신청용 확정 메타데이터

| 항목 | 영어판 | 일본어판 |
|---|---|---|
| 현지어 제목 | Semiconductor Interviews: Answer the King’s Question | 半導体面接――王の問いに答えよ |
| 현지어 부제 | Data-Driven Debates on AI, Manufacturing, Design, and Supply Chains, Inspired by Korea's Royal Policy Examinations | 朝鮮王朝の策問で鍛える、AI・製造工程・設計・サプライチェーンのデータ討論 |
| 원서명 | 반도체 면접, 왕의 질문에 답하라 | 반도체 면접, 왕의 질문에 답하라 |
| 원서 부제 | 조선의 책문으로 훈련하는 AI·공정·설계·공급망 데이터 토론 | 조선의 책문으로 훈련하는 AI·공정·설계·공급망 데이터 토론 |
| 저자 | Nakcho Choi / 최낙초 | チェ・ナクチョ（Nakcho Choi） / 최낙초 |
| 발행처 표기 | Scholar Bridge / 스칼라브릿지 | スカラーブリッジ（Scholar Bridge） / 스칼라브릿지 |
| 본문 언어 | 영어 (en-US) | 일본어 (ja-JP) |
| 판형·구성 | EPUB 3.0 리플로우, 19장 | EPUB 3.0 리플로우, 19장 |
| 관련 PDF | A5 세로, 320쪽 | A5 세로, 281쪽 |
| EPUB 검증 | EPUBCheck 오류 0, 경고 0 | EPUBCheck 오류 0, 경고 0 |
| 판차 | 번역 초판 | 번역 초판 |
| 판매 형태 | 유료 전자책, 온라인 다운로드·열람 | 유료 전자책, 온라인 다운로드·열람 |

전자출판물 부가기호는 둘째 자리가 5인 체계를 적용하되, 나머지 분류 숫자는 국립중앙도서관 신청 화면과 출판 분야에 맞춰 확정한다.

## 발행자가 확정해야 할 정보

다음 항목이 확인되기 전에는 ISBN 신청서를 제출하거나 최종 파일을 재빌드하지 않는다.

- 출판사신고확인증에 적힌 정확한 발행처명
- 출판사 신고번호와 신고일
- 대표자명, 발행처 주소, ISBN 담당자 연락처
- 국립중앙도서관 통합 계정 및 발행자번호 보유 여부
- 신규 발행자라면 향후 1년간 출판예정목록과 ISBN 교육 이수 여부
- 영어판·일본어판의 발행예정일
- 각 언어판의 국내 정가와 해외 판매 기준 가격
- 역자 또는 번역 기여자 표기 방식
- 주제 분류, 키워드, 전자출판물 부가기호
- PDF도 Google Play 및 다른 유통망에 공개하는 별도 전자 형식인지 최종 확인

비밀번호, 인증번호, 계정 복구정보는 이 문서나 저장소에 기록하지 않는다.

## 발급 절차

1. 관할 시·구청의 출판사신고확인증을 확인한다.
2. 국립중앙도서관 ISBN·ISSN·UCI·납본 시스템 계정의 발행처명이 신고확인증과 일치하는지 확인한다.
3. 발행자번호가 없다면 신고확인증과 향후 1년 출판예정목록으로 발행자번호를 신청한다.
4. 발행자번호 배정 후 영어 EPUB, 영어 PDF, 일본어 EPUB, 일본어 PDF 순으로 ISBN 통보서를 신청한다.
5. 발급된 네 ISBN을 각 원고 설정, 판권면, EPUB 메타데이터, PDF 메타데이터에 반영한다.
6. EPUB과 PDF를 다시 빌드하고 EPUBCheck, 구조 검사, PDF 시각 검사를 재실행한다.
7. Google Play Books에 영어판과 일본어판을 각각 한 도서 항목으로 등록하고 형식별 ISBN을 연결한다.
8. 발행일 또는 제작일부터 30일 이내에 언어·형식별 전자책을 국립중앙도서관에 납본한다.

## 공식 근거

- 국립중앙도서관 ISBN·ISSN·UCI·납본 시스템: https://www.nl.go.kr/seoji/
- 발행자번호 신청 안내: https://www.nl.go.kr/seoji/contents/S30101000000.do
- ISBN 통보서 신청 안내: https://www.nl.go.kr/seoji/contents/S30201000000.do
- 한국문헌번호 편람: https://www.nl.go.kr/seoji/resource/manual/user_isbn_manual.pdf
- 전자책 입력 항목 안내: https://www.nl.go.kr/seoji/resource/form/user/isbn_1.pdf
- 전자책 납본 안내: https://www.nl.go.kr/seoji/contents/S50102010000.do
- 국제 ISBN 기구의 언어·형식별 배정 규정: https://www.isbn-international.org/content/isbn-assignment
- 국제 ISBN 기구의 전자책 배정 지침: https://www.isbn-international.org/content/guidelines-assignment-e-books/26
- Google Play Books ISBN 안내: https://support.google.com/books/partner/answer/3431108?hl=en
- Google Play Books 파일 지침: https://support.google.com/books/partner/answer/3424254?hl=en
