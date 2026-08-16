"""Replace outline chapters with data-backed discussion manuscripts.

Every number in EVIDENCE carries a year/unit/source note. The charts are SVG so
the same figure works in Quarto HTML, EPUB and PDF. Human fact-checking remains
mandatory before commercial release.
"""

from __future__ import annotations

import csv
import html
from pathlib import Path

from scaffold_content import TOPICS

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = ROOT / "book" / "chapters"
FIGURES = ROOT / "book" / "figures"
DATA = ROOT / "data"

# chart values in a row always share one unit. facts may use other units.
EVIDENCE = {
    1: dict(unit="백만 명", chart=[("해외 피란민", 5.75), ("국내 실향민", 3.75), ("인도지원 필요", 10.8)], facts=["2025년 9월 기준 우크라이나 피란민은 세계 575만 명, 국내 실향민은 375만 명이었다(UNHCR).", "2026년 우크라이나 국내 인도지원 필요 인구는 1,080만 명으로 추산됐다(UNHCR).", "2014년 러시아·우크라이나 충격 때 반도체용 네온 가격은 600% 상승했다(USITC).", "우크라이나 정부는 2024년 AI·Palantir를 활용한 인도적 지뢰 제거를 추진하며 잠재 오염 면적을 15.6만km²로 제시했다.", "미 USGS에 따르면 2020년 미국은 세계 헬륨 생산의 약 44%를 담당했다. 우크라이나 직접 충격은 주로 네온이고 헬륨은 천연가스 생산국 집중 문제다."], source="https://www.unhcr.org/emergencies/ukraine-emergency", source_name="UNHCR Ukraine emergency", extra_sources=[("USITC 반도체 공급망 보고서", "https://www.usitc.gov/publications/332/working_papers/semiconductor_working_paper_corrected_103119.pdf"), ("우크라이나 경제부 AI 지뢰제거", "https://me.gov.ua/News/Detail?lang=en-GB&id=0669a1d8-8c2d-4d66-bb86-a579ed8e628a"), ("USGS helium statistics", "https://www.usgs.gov/centers/national-minerals-information-center/helium-statistics-and-information")]),
    2: dict(unit="누적 주요 통제 조치", chart=[("2022", 1), ("2023", 2), ("2024", 4), ("2025", 5)], facts=["미국 BIS는 2022년 10월 7일 첨단 컴퓨팅·반도체 제조 통제를 시작했다.", "2023년 10월, 2024년 4월·12월, 2025년 1월에 통제 보완과 우회 차단 조치가 이어졌다.", "2026년 1월에는 H200·MI325X급 제품을 일정 보안 요건 아래 건별 심사하는 정책이 발표됐다."], source="https://www.bis.gov/press-release/department-commerce-revises-license-review-policy-semiconductors-exported-china", source_name="U.S. BIS 2026 license policy"),
    3: dict(unit="첨단공정 매출 비중(%)", chart=[("2023", 58), ("2024", 69)], facts=["TSMC의 7nm 이하 첨단공정 매출 비중은 2023년 58%에서 2024년 69%로 늘었다.", "2024년 TSMC는 12인치 환산 웨이퍼 1,290만 장을 출하했다.", "같은 해 288개 공정기술로 522개 고객의 11,878개 제품을 생산했다."], source="https://investor.tsmc.com/static/annualReports/2024/english/index.html", source_name="TSMC 2024 Annual Report"),
    4: dict(unit="일본산 불화수소 수입액(백만 달러)", chart=[("2019", 36.3), ("2021", 12.5), ("2022", 8.3)], facts=["산업통상자원부는 일본산 불화수소 수입액이 2019년 3,630만 달러에서 2021년 1,250만 달러로 66% 감소했다고 밝혔다.", "무역통계 기반 보도에서 2022년 반도체용 불화수소 일본 수입액은 830만 달러로 집계됐다.", "규제 직전 고순도 불화수소의 일본 의존도는 43.9%로 제시됐다."], source="https://www.korea.kr/news/policyNewsView.do?newsId=148899420", source_name="산업통상자원부 소부장 정책자료"),
    5: dict(unit="미 CHIPS 재원(십억 달러)", chart=[("제조 인센티브", 39), ("R&D", 11), ("국방", 2), ("인력", 0.2)], facts=["미 CHIPS and Science Act는 5년간 527억 달러의 연방 재원을 배정했다.", "제조 인센티브 약 390억 달러와 연구개발 약 110억 달러가 핵심 축이다.", "국방부 Microelectronics Commons 20억 달러, NSF 인력·교육기금 2억 달러도 포함된다."], source="https://www.nist.gov/document/chips-america-fact-sheet-federal-incentives", source_name="NIST CHIPS for America fact sheet"),
    6: dict(unit="백만 명", chart=[("우크라이나 피란민", 5.75), ("우크라이나 실향민", 3.75), ("세계 난민", 41.6)], facts=["2025년 9월 우크라이나 피란민은 575만 명, 국내 실향민은 375만 명이었다.", "2025년 말 전 세계 난민은 4,160만 명이었다.", "제재의 산업 효과를 말할 때 물류·금융 차단이 민간 의약·통신에 미치는 영향을 별도 지표로 둬야 한다."], source="https://www.unhcr.org/about-unhcr/overview/figures-glance", source_name="UNHCR Figures at a Glance"),
    7: dict(unit="환율 가정별 10억 달러 매출 환산(조 원)", chart=[("1,200원/$", 1.2), ("1,350원/$", 1.35), ("1,500원/$", 1.5)], facts=["10억 달러 매출은 환율 1,200원일 때 1.2조 원, 1,500원일 때 1.5조 원으로 환산된다.", "같은 달러 매출이라도 원화 표시 매출은 이 가정에서 25% 차이 난다.", "따라서 상수환율 매출, 달러 원가, 헤지손익을 분리하지 않으면 제품 경쟁력과 환산효과가 섞인다."], source="https://ecos.bok.or.kr/", source_name="한국은행 ECOS 환율 통계"),
    8: dict(unit="분기 매출(조 원)", chart=[("24Q1", 12.43), ("24Q3", 17.57), ("25Q2", 22.23), ("25Q3", 24.45)], facts=["SK하이닉스 매출은 2024년 1분기 12.43조 원에서 2025년 3분기 24.45조 원으로 증가했다.", "2024년 3분기 HBM은 DRAM 매출의 30%였고 4분기 40%가 전망됐다.", "2025년 3분기 영업이익은 11.38조 원이었다. 호황 수요와 투자규율을 함께 봐야 한다."], source="https://news.skhynix.com/en/sk-hynix-announces-3q25-financial-results/", source_name="SK hynix 3Q25 results"),
    9: dict(unit="세계 반도체 매출(십억 달러)", chart=[("2024", 627), ("2025", 795.6), ("2026 전망", 1510)], facts=["WSTS는 2024년 시장을 6,270억 달러로 추정했다.", "2025년 실제 시장은 7,956억 달러로 전년보다 26.2% 성장했다.", "2026년 봄 전망은 AI·메모리 급증을 반영해 1.51조 달러를 제시했다. 전망치는 실제가 아니라 조건부 기대다."], source="https://www.wsts.org/76/Recent-News-Release", source_name="WSTS Spring 2026 forecast"),
    10: dict(unit="EU 세계 반도체 점유율(%)", chart=[("현재 약", 10), ("2030 목표", 20)], facts=["EU는 세계 반도체 점유율을 약 10%에서 20%로 두 배 높이는 목표를 세웠다.", "EU Chips Act는 2023년 9월 21일 발효됐다.", "2026년 EU는 기존 정책이 공공·민간 투자 520억 유로 이상과 일자리 4.6만 개를 동원했다고 설명했다."], source="https://digital-strategy.ec.europa.eu/en/policies/chips-act-2", source_name="European Commission Chips Act 2.0"),
    11: dict(unit="기업의 AI 사용률(%)", chart=[("소기업", 11.9), ("중기업", 20.4), ("대기업", 40.1)], facts=["OECD 집계에서 AI 사용률은 소기업 11.9%, 중기업 20.4%, 대기업 40.1%였다.", "대기업 사용률은 소기업의 약 3.4배다.", "공공 AI의 평가는 접속자 수보다 실제 과업 성과·지역·소득별 이용 품질 격차로 해야 한다."], source="https://www.oecd.org/en/publications/generative-ai-and-the-sme-workforce_2d08b99d-en/full-report/component-3.html", source_name="OECD Generative AI and the SME workforce"),
    12: dict(unit="2025 세계 반도체 시장 전망(십억 달러)", chart=[("봄 전망", 700.9), ("상반기 수정", 728), ("가을 전망", 772), ("실제", 795.6)], facts=["WSTS의 2025년 시장 전망은 봄 7,009억 달러에서 상반기 7,280억 달러, 가을 7,720억 달러로 상향됐다.", "2025년 실제 매출은 7,956억 달러였다.", "전망의 연속 수정은 시장가격이 미래를 완벽히 안다기보다 새로운 정보에 적응한다는 증거다."], source="https://www.wsts.org/76/PRESS-ARCHIVE", source_name="WSTS forecast archive"),
    13: dict(unit="", chart=[], facts=["NIST AI RMF의 핵심은 GOVERN·MAP·MEASURE·MANAGE 네 기능이다.", "GOVERN은 나머지 세 기능을 관통하는 거버넌스 층이다.", "NIST는 2026년 핵심 인프라용 신뢰 가능한 AI 프로파일 개념문서를 공개했다."], source="https://airc.nist.gov/airmf-resources/airmf/5-sec-core/", source_name="NIST AI RMF Core"),
    14: dict(unit="세계 고용 비중(%)", chart=[("일부 노출", 25), ("최고 노출", 3.3), ("그 외", 75)], facts=["ILO는 세계 노동자 4명 중 1명이 생성형 AI에 어느 정도 노출된 직업에 있다고 추정했다.", "최고 노출 범주는 세계 고용의 3.3%다.", "ILO의 결론은 대체보다 직무 변형 가능성이 더 크다는 것이다."], source="https://www.ilo.org/publications/generative-ai-and-jobs-refined-global-index-occupational-exposure", source_name="ILO Generative AI and Jobs 2025"),
    15: dict(unit="연간 인원(백만 명, 로그축 권장)", chart=[("업무 관련 사망", 2.93), ("비치명적 부상", 395)], facts=["ILO는 매년 업무 관련 요인으로 293만 명이 사망한다고 추정한다.", "비치명적 업무상 부상은 연 3억9,500만 건이다.", "전 세계 업무 관련 사망의 약 63%가 아시아·태평양에서 발생했다는 ILO 자료도 있다."], source="https://www.ilo.org/topics-and-sectors/safety-and-health-work", source_name="ILO Safety and Health at Work"),
    16: dict(unit="세계 특허출원(백만 건)", chart=[("2023", 3.55), ("2024", 3.7)], facts=["세계 특허출원은 2023년 355만 건에서 2024년 370만 건으로 증가했다.", "2024년 증가율은 4.9%로 2018년 이후 가장 빨랐다.", "2024년 세계 특허출원의 약 70%가 아시아 특허청에 접수됐다."], source="https://www.wipo.int/web-publications/world-intellectual-property-indicators-2025-highlights/en/patents-highlights.html", source_name="WIPO World IP Indicators 2025"),
    17: dict(unit="", chart=[], facts=["산업제어시스템 보안은 기밀성뿐 아니라 가용성과 안전을 함께 지켜야 한다.", "최소권한·망분리·다중인증이 있어도 내부자·공급망·원격정비 경로는 남는다.", "감시 데이터의 목적 제한·보존기간·이의제기권을 보안 KPI와 함께 설계해야 한다."], source="https://www.cisa.gov/topics/industrial-control-systems", source_name="CISA Industrial Control Systems"),
    18: dict(unit="2024 군사비(십억 달러)", chart=[("세계", 2718), ("상위 5개국", 1635), ("유럽", 693), ("우크라이나", 64.7)], facts=["2024년 세계 군사비는 2조7,180억 달러로 실질 9.4% 증가했다.", "상위 5개국이 1조6,350억 달러, 세계 총액의 60%를 차지했다.", "우크라이나 군사비는 647억 달러로 GDP의 34%였다."], source="https://www.sipri.org/publications/2025/sipri-fact-sheets/trends-world-military-expenditure-2024", source_name="SIPRI Military Expenditure 2024"),
    19: dict(unit="교육수준별 상대임금 지수", chart=[("중등 미만", 100), ("중등", 118), ("고등교육", 200)], facts=["OECD 평균에서 중등교육 이수자의 임금은 중등 미만보다 18% 높다.", "고등교육 이수자는 중등 미만의 거의 두 배를 번다.", "이 격차가 학위의 생산성 신호인지 선발 효과인지 구분해야 학벌 없는 채용을 설계할 수 있다."], source="https://www.oecd.org/en/topics/earnings-by-educational-attainment.html", source_name="OECD Earnings by educational attainment"),
    20: dict(unit="", chart=[], facts=["UNESCO AI 윤리 권고는 2021년 193개 회원국에 의해 채택됐다.", "윤리 원칙은 영향평가·감사·인권·환경·교육 같은 운영 장치로 내려와야 한다.", "엔지니어 개인의 양심에만 책임을 주면 조직의 일정·예산 권한과 책임이 분리된다."], source="https://www.unesco.org/en/artificial-intelligence/recommendation-ethics", source_name="UNESCO Recommendation on the Ethics of AI"),
    21: dict(unit="", chart=[], facts=["OECD 다국적기업 가이드라인은 인권·노동·환경·정보공개·기술을 기업책임의 범위에 둔다.", "언로는 익명제보 채널의 존재보다 보고 후 보복 여부, 조치 시차, 재발률로 측정해야 한다.", "반대 의견의 시간과 최종 결정의 시간을 분리하면 숙의와 속도를 동시에 설계할 수 있다."], source="https://mneguidelines.oecd.org/", source_name="OECD Guidelines for Multinational Enterprises"),
    22: dict(unit="", chart=[], facts=["정부는 용인 반도체 클러스터에 2053년까지 10GW 이상의 신규 전력이 필요하다고 봤다.", "통합 용수 공급 규모는 하루 약 107.2만 m³로 제시됐다.", "정부 설명상 이는 인구 약 300만 명의 하루 물 사용량과 맞먹는다."], source="https://www.korea.kr/common/docViewer.do?fileId=197961931&tblKey=GMN", source_name="대한민국 정책브리핑 용인 클러스터 전력·용수 협약"),
    23: dict(unit="여성 비중(%)", chart=[("연구자", 31.7), ("STEM 졸업", 35), ("G20 STEM 일자리", 22), ("STEM 리더", 10)], facts=["UNESCO는 여성 연구자 비중을 31.7%로 제시했다.", "세계 STEM 졸업자의 여성 비중은 35%, G20 STEM 일자리에서는 22%다.", "STEM 리더 중 여성은 10명 중 1명 수준이다."], source="https://www.unesco.org/en/science-technology-and-innovation/cta", source_name="UNESCO gender gap in science"),
    24: dict(unit="", chart=[], facts=["OECD 2023 성인역량조사에서 다수 국가의 성인학습 참여는 정체하거나 감소했다.", "고용주의 재정지원은 성인학습 참여율과 강하게 연관된다.", "교육 참여의 누적우위, 이른바 매튜 효과 때문에 가장 필요한 사람이 가장 적게 참여할 수 있다."], source="https://www.oecd.org/en/publications/trends-in-adult-learning_ec0624a6-en.html", source_name="OECD Trends in Adult Learning"),
    25: dict(unit="전자폐기물 발생량(백만 톤)", chart=[("2022", 62), ("2030 전망", 82)], facts=["2022년 세계 전자폐기물은 6,200만 톤으로 2010년보다 82% 늘었다.", "공식 수거·재활용률은 22.3%에 그쳤다.", "2030년 발생량은 8,200만 톤, 공식 재활용률은 20%로 낮아질 전망이다."], source="https://unitar.org/about/news-stories/press/global-e-waste-monitor-2024-electronic-waste-rising-five-times-faster-documented-e-waste-recycling", source_name="UNITAR Global E-waste Monitor 2024"),
    26: dict(unit="데이터센터 전력소비(TWh)", chart=[("2024", 460), ("2030", 945), ("2035", 1200)], facts=["IEA 기본 시나리오에서 데이터센터 전력소비는 2024년 약 460TWh에서 2030년 945TWh로 두 배가 된다.", "2030년에는 세계 전력소비의 약 3%다.", "가속 서버 전력소비는 2030년까지 연 30% 증가해 순증분의 거의 절반을 차지한다."], source="https://www.iea.org/reports/energy-and-ai/energy-demand-from-ai", source_name="IEA Energy and AI"),
    27: dict(unit="산업계가 만든 주목할 AI 모델 비중(%)", chart=[("2023", 60), ("2024", 90), ("2025", 91.2)], facts=["산업계가 만든 주목할 AI 모델 비중은 2023년 60%에서 2024년 약 90%로 상승했다.", "2025년에는 산업 93개, 학계 2개로 산업 비중이 91.2%였다.", "2025년 미국은 59개, 중국은 35개의 주목할 모델을 배출했다."], source="https://hai.stanford.edu/assets/files/ai_index_report_2026_chapter_1_research_development.pdf", source_name="Stanford AI Index 2026"),
    28: dict(unit="상위 5개 디지털 다국적기업 매출 점유율(%)", chart=[("2017", 21), ("2025", 48)], facts=["UNCTAD는 상위 5개 디지털 다국적기업의 매출 점유율이 2017년 21%에서 2025년 48%로 두 배 이상 늘었다고 밝혔다.", "43개국 기업 전자상거래 매출은 2016~2022년 약 60% 증가했다.", "데이터 현지화는 통제권을 높일 수 있지만 중소기업의 클라우드 접근 비용도 키운다."], source="https://unctad.org/news/highly-concentrated-digital-markets-put-consumers-risk-heres-how-change-course", source_name="UNCTAD digital market concentration"),
    29: dict(unit="", chart=[], facts=["기억의 보존은 저장용량 문제가 아니라 접근권·삭제권·유족권의 충돌이다.", "완전삭제, 검색 비노출, 접근 제한, 기간 만료는 서로 다른 정책 수단이다.", "공익적 기록과 개인의 재출발 권리를 한 개의 보존기간으로 해결할 수 없다."], source="https://www.unesco.org/en/memory-world", source_name="UNESCO Memory of the World"),
    30: dict(unit="연간 노동시간(시간, 2022)", chart=[("한국", 1901), ("OECD 평균", 1752)], facts=["2022년 한국의 연간 노동시간은 1,901시간으로 OECD 평균 1,752시간보다 8.5% 길었다.", "한국의 시간당 생산성은 1995년 13.9달러에서 2024년 52.0달러(2020 PPP)로 약 네 배가 됐다.", "성능·매출과 함께 노동시간·건강·환경·삶의 만족을 보지 않으면 기술 진보와 인간 진보를 동일시하게 된다."], source="https://www.oecd.org/content/dam/oecd/en/publications/reports/2024/07/oecd-economic-surveys-korea-2024_9343c046/c243e16a-en.pdf", source_name="OECD Economic Surveys: Korea 2024"),
}


def svg_chart(week: int, title: str, unit: str, rows: list[tuple[str, float]]) -> str:
    width, height = 920, 150 + 72 * len(rows)
    max_value = max(value for _, value in rows) or 1
    items = []
    for idx, (label, value) in enumerate(rows):
        y = 112 + idx * 72
        bar = 610 * value / max_value
        shown = f"{value:,.2f}".rstrip("0").rstrip(".")
        items.append(f'<text x="28" y="{y + 23}" class="label">{html.escape(label)}</text>')
        items.append(f'<rect x="230" y="{y}" width="{bar:.1f}" height="34" rx="6" class="bar"/>')
        items.append(f'<text x="{min(850, 246 + bar):.1f}" y="{y + 24}" class="value">{shown}</text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">{html.escape(title)}</title><desc id="desc">{html.escape(unit)} 막대그래프</desc>
<style>.bg{{fill:#fbf7ef}}.bar{{fill:#8b2f24}}.title{{font:700 27px sans-serif;fill:#18212b}}.unit{{font:16px sans-serif;fill:#655f58}}.label{{font:18px sans-serif;fill:#18212b}}.value{{font:700 17px sans-serif;fill:#18212b}}</style>
<rect class="bg" width="100%" height="100%" rx="18"/><text x="28" y="46" class="title">{html.escape(title)}</text><text x="28" y="76" class="unit">단위: {html.escape(unit)}</text>
{''.join(items)}</svg>'''


def render(topic) -> str:
    week, title, question, motif, source_name, source_url, data_lens, pro, con, condition = topic
    ev = EVIDENCE[week]
    facts = ev["facts"]
    figure = f"![{title} 핵심 데이터](../figures/week{week:02d}.svg){{fig-alt=\"{title} 핵심 데이터\"}}" if ev["chart"] else '''```{mermaid}
flowchart LR
  A[문제 정의] --> B[영향받는 사람]
  B --> C[측정 지표]
  C --> D[중단·수정 조건]
```'''
    fact_rows = "\n".join(f"| {i} | {fact} |" for i, fact in enumerate(facts, 1))
    memo = "첫 번째와 두 번째 핵심 수치"
    extra_sources = "\n".join(f"- [{name}]({url})" for name, url in ev.get("extra_sources", []))
    spoken_condition = condition.rstrip(".")
    return f'''---
title: "{week:02d}. {title}"
description: "{question}"
categories: [반도체, 인문학, 집단토론, 데이터]
---

## 오늘의 책문

> **{question}?**

조선의 모티브는 **{motif}**이다. 책문은 사실을 많이 아는 사람보다, 충돌하는 가치의 우선순위와 자기 답이 실패할 조건을 밝히는 사람을 가려냈다. 오늘의 응시자는 이 질문을 산업의 숫자와 인간의 비용을 함께 놓고 답해야 한다.

## 왜 지금 이 질문인가

{data_lens} 이 주제를 단순한 찬반으로 만들면 중요한 당사자가 사라진다. 공급망의 비용은 구매팀만, AI의 위험은 개발팀만, 노동의 전환은 개인만 책임지는 문제가 아니다. 결정권·편익·손실이 누구에게 배분되는지까지 보여야 토론이 산업 분석이 된다.

## 데이터 렌즈

{figure}

| 데이터 카드 | 발언에 쓸 수 있는 검증 문장 |
|---:|---|
{fact_rows}

첫 번째 숫자는 문제의 **규모**를, 두 번째는 **분배**를, 세 번째는 **시간축 또는 제약조건**을 보여준다. 다만 숫자는 결론이 아니다. 집계 범위가 다른 자료를 한 그래프에서 직접 비교하지 말고, 전망치는 사실값이 아니라 가정의 결과라고 밝혀야 한다. 기업·정부·군의 발표는 이해관계가 있는 1차 자료이므로 독립 통계와 대조한다.

### 숫자가 말하지 못하는 것

- 평균은 지역·직무·기업규모별 격차를 숨길 수 있다.
- 비용으로 계산되지 않은 안전, 존엄, 환경, 장기 역량은 의사결정표에서 쉽게 사라진다.
- 사건 뒤의 상관관계가 정책이나 기술의 인과효과를 자동으로 증명하지 않는다.

따라서 면접에서는 숫자를 많이 외우기보다 **숫자의 정의와 결론이 바뀌는 임계값**을 말하는 편이 강하다. 예를 들어 “공급선이 두 개”보다 “두 번째 공급선이 같은 원료·항만·인증 설비를 공유하는가”가 복원력을 더 잘 묻는다.

## 대립 답안

### 답안 A — 적극론

{pro}

이 답의 강점은 결정 지연의 비용을 본다는 데 있다. 위기가 실제이고 대체시간이 길다면, 평시의 최적비용보다 행동 속도가 중요하다. 약점은 정책이나 투자의 편익을 크게, 숨은 비용을 작게 추정하기 쉽다는 점이다.

### 답안 B — 경계론

{con}

이 답의 강점은 과잉대응과 권력 집중을 견제한다는 데 있다. 약점은 시장이나 기존 제도가 충분히 빠르게 조정될 것이라는 가정을 숨길 수 있다는 점이다. 아무것도 하지 않는 선택에도 피해자와 비용이 있다는 사실을 계산해야 한다.

### 답안 C — 조건부론

{condition}

## 판정 조건

조건부론은 가운데에 서는 타협이 아니다. 무엇을 측정해 어느 임계값에서 A에서 B로, 또는 B에서 A로 전환할지 정하는 답이다. 의사결정자는 효율·회복탄력성·분배·가역성·설명책임 가운데 최소 세 축을 공개해야 한다.

## 사례형 토론

당신은 반도체 기업의 전략 태스크포스에 참여했다. 이사회는 48시간 안에 투자·조달·운영 원칙을 정하라고 요구한다. 동시에 재무팀은 비용 증가를, 현장팀은 실행 가능성을, 노동자·지역사회는 안전과 부담을 문제 삼는다.

1. 첫 결정에서 보호할 최우선 가치를 하나만 고른다.
2. 그 선택으로 손해를 보는 집단을 명시한다.
3. 90일 안에 확인할 선행지표 두 개와 결과지표 한 개를 정한다.
4. 결정을 중단하거나 뒤집을 수치·사건을 사전에 약속한다.

## 90초 발언 예시

“제 결론은 **{spoken_condition}**라고 봅니다. 근거로 먼저 {facts[0]} 다음으로 {facts[1]} 이 두 수치는 문제의 규모와 편익이 자동으로 같은 곳에 가지 않는다는 점을 보여줍니다. 적극론의 장점은 행동 지연을 줄이는 것이지만, 비용과 권한이 고착될 위험이 있습니다. 반대로 경계론은 과잉대응을 막지만 아무것도 하지 않는 비용을 과소평가할 수 있습니다. 그래서 저는 90일 단위로 공개 지표를 점검하고, 사전에 정한 임계값을 넘으면 정책을 확대하되 넘지 못하면 축소하겠습니다. 확인하지 못한 숫자는 단정하지 않고 원출처와 정의부터 검증하겠습니다.”

이 문장을 외우지 말고 `결론 → 데이터 2개 → 강한 반론 → 전환 조건`의 순서를 익힌다. 집단토론에서는 상대방의 말을 요약한 뒤 빠진 지표를 보태야 점수를 얻는다.

## 꼬리 질문

**교차질문과 재반박**

- 적극론이 가정한 피해 규모가 절반이라도 같은 결론인가?
- 경계론이 말하는 시장 조정은 몇 개월 안에 일어나야 의미가 있는가?
- 비용을 가장 많이 부담하지만 데이터에 잡히지 않는 사람은 누구인가?
- 같은 원칙을 경쟁국·경쟁사에도 적용해도 받아들일 수 있는가?
- {memo} 가운데 어느 것이 바뀌면 결론을 수정할 것인가?
- 결정이 실패했을 때 책임자가 실제로 통제할 수 있었던 변수는 무엇인가?

## 면접장 직전 메모

- 숫자는 **출처·연도·단위**와 함께 말한다.
- 전망과 실제, 명목과 실질, 상관과 인과를 구분한다.
- 상대 주장의 가장 강한 버전을 먼저 인정한다.
- 자기 결론의 수혜자·비용부담자·중단조건을 밝힌다.
- 모르는 수치는 만들지 말고 확인할 데이터셋을 말한다.

## 출처

- [{ev['source_name']}]({ev['source']})
- [{source_name}]({source_url})
{extra_sources}
- [조선시대 책문 아카이브](https://waterfirst.github.io/Joseon-Dynasty-Civil-Service-Examination/)

> 데이터 기준일: 각 원출처의 표기 연도. 최신성이 중요한 수치는 상업 발행 직전에 다시 확인한다.
'''


def main() -> None:
    CHAPTERS.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    records = []
    for topic in TOPICS:
        week, title = topic[0], topic[1]
        ev = EVIDENCE[week]
        (CHAPTERS / f"week{week:02d}.qmd").write_text(render(topic), encoding="utf-8")
        if ev["chart"]:
            (FIGURES / f"week{week:02d}.svg").write_text(svg_chart(week, title, ev["unit"], ev["chart"]), encoding="utf-8")
        for label, value in ev["chart"]:
            records.append([week, title, label, value, ev["unit"], ev["source"]])
    with (DATA / "evidence.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["week", "topic", "label", "value", "unit", "source_url"])
        writer.writerows(records)
    print(f"wrote 30 chapters, {len(list(FIGURES.glob('week*.svg')))} charts, {len(records)} evidence rows")


if __name__ == "__main__":
    main()
