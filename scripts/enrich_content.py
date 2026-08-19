"""Replace outline chapters with data-backed discussion manuscripts.

Every number in EVIDENCE carries a year/unit/source note. The charts are SVG so
the same figure works in Quarto HTML, EPUB and PDF. Human fact-checking remains
mandatory before commercial release.
"""

from __future__ import annotations

import csv
import html
import math
from pathlib import Path

from chapter_blueprints import BLUEPRINTS

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = ROOT / "book" / "chapters"
FIGURES = ROOT / "book" / "figures"
DATA = ROOT / "data"

# chart values in a row always share one unit. facts may use other units.
EVIDENCE = {
    1: dict(unit="개발 시작 시점(연도)", chart=[("비행기", 1903), ("레이더", 1937), ("ARPANET", 1969), ("GPS", 1973)], facts=["비행기는 1차 세계대전 전에 존재했고 전쟁 중 임무·성능·생산이 빠르게 발전했다.", "레이더는 1937년 시연됐고 2차 세계대전에서 급속히 발전한 뒤 민간 항공과 기상관측으로 확산됐다.", "ARPANET은 1969년, 통합 NAVSTAR GPS 사업은 1973년 시작돼 두 세계대전의 직접 발명품이 아니다."], source="https://airandspace.si.edu/explore/stories/world-war-i-laboratory-air", source_name="Smithsonian National Air and Space Museum", extra_sources=[("U.S. Army 레이더 기술사", "https://www.army.mil/article/285662/radar_demonstration_transforms_the_army"), ("DARPA ARPANET", "https://www.darpa.mil/news/features/arpanet"), ("GPS.gov 기술사", "https://www.gps.gov/sites/default/files/2025-07/gps_finalreport618.pdf")]),
    2: dict(unit="ASML 시스템 매출 중 중국 출하 비중(%)", chart=[("2023", 29), ("2024", 41)], facts=["ASML의 시스템 매출에서 중국 출하 비중은 2023년 29%에서 2024년 41%로 상승했다.", "미국 BIS는 2024년 12월 24종 장비와 3종 소프트웨어 도구, HBM에 통제를 추가했다.", "네덜란드는 2024년 9월 일부 첨단 DUV 노광장비의 국가 허가 범위를 확대했으며, 전면 금지가 아닌 건별 심사라고 밝혔다."], source="https://ourbrand.asml.com/m/62a213cac2117ee6/original/2025_01_29-Presentation-Investor-Relations-Q4-FY-2024.pdf", source_name="ASML Q4 and FY 2024 Investor Presentation", extra_sources=[("U.S. BIS 2024년 12월 통제", "https://media.bis.gov/press-release/commerce-strengthens-export-controls-restrict-chinas-capability-produce-advanced-semiconductors-military"), ("네덜란드 정부 DUV 허가 확대", "https://www.government.nl/latest/news/2024/09/06/the-netherlands-expands-export-control-measure-advanced-semiconductor-manufacturing-equipment")]),
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
    26: dict(unit="데이터센터 전력소비(TWh)", chart=[("2024 소비", 415), ("2030 소비", 945), ("2035 소비", 1200)], facts=["IEA 기본 시나리오에서 데이터센터 전력소비는 2024년 약 415TWh에서 2030년 945TWh로 두 배 이상 늘어난다.", "2030년에는 세계 전력소비의 약 3%다.", "가속 서버 전력소비는 2030년까지 연 30% 증가해 순증분의 거의 절반을 차지한다."], source="https://www.iea.org/reports/energy-and-ai/energy-demand-from-ai", source_name="IEA Energy and AI"),
    27: dict(unit="산업계가 만든 주목할 AI 모델 비중(%)", chart=[("2023", 60), ("2024", 90), ("2025", 91.2)], facts=["산업계가 만든 주목할 AI 모델 비중은 2023년 60%에서 2024년 약 90%로 상승했다.", "2025년에는 산업 93개, 학계 2개로 산업 비중이 91.2%였다.", "2025년 미국은 59개, 중국은 35개의 주목할 모델을 배출했다."], source="https://hai.stanford.edu/assets/files/ai_index_report_2026_chapter_1_research_development.pdf", source_name="Stanford AI Index 2026"),
    28: dict(unit="상위 5개 디지털 다국적기업 매출 점유율(%)", chart=[("2017", 21), ("2025", 48)], facts=["UNCTAD는 상위 5개 디지털 다국적기업의 매출 점유율이 2017년 21%에서 2025년 48%로 두 배 이상 늘었다고 밝혔다.", "43개국 기업 전자상거래 매출은 2016~2022년 약 60% 증가했다.", "데이터 현지화는 통제권을 높일 수 있지만 중소기업의 클라우드 접근 비용도 키운다."], source="https://unctad.org/news/highly-concentrated-digital-markets-put-consumers-risk-heres-how-change-course", source_name="UNCTAD digital market concentration"),
    29: dict(unit="", chart=[], facts=["기억의 보존은 저장용량 문제가 아니라 접근권·삭제권·유족권의 충돌이다.", "완전삭제, 검색 비노출, 접근 제한, 기간 만료는 서로 다른 정책 수단이다.", "공익적 기록과 개인의 재출발 권리를 한 개의 보존기간으로 해결할 수 없다."], source="https://www.unesco.org/en/memory-world", source_name="UNESCO Memory of the World"),
    30: dict(unit="연간 노동시간(시간, 2022)", chart=[("한국", 1901), ("OECD 평균", 1752)], facts=["2022년 한국의 연간 노동시간은 1,901시간으로 OECD 평균 1,752시간보다 8.5% 길었다.", "한국의 시간당 생산성은 1995년 13.9달러에서 2024년 52.0달러(2020 PPP)로 약 네 배가 됐다.", "성능·매출과 함께 노동시간·건강·환경·삶의 만족을 보지 않으면 기술 진보와 인간 진보를 동일시하게 된다."], source="https://www.oecd.org/content/dam/oecd/en/publications/reports/2024/07/oecd-economic-surveys-korea-2024_9343c046/c243e16a-en.pdf", source_name="OECD Economic Surveys: Korea 2024"),
}


def svg_chart(week: int, title: str, unit: str, rows: list[tuple[str, float]]) -> str:
    """Render an evidence chart whose form follows the data rather than one template."""
    width, height = 920, 440
    palette = ["#A94E32", "#1F5A75", "#4D7C6F", "#C18A3D", "#725B8C"]
    max_value = max(value for _, value in rows) or 1

    def shown(value: float) -> str:
        return f"{value:,.2f}".rstrip("0").rstrip(".")

    common = f'''<title id="title">{html.escape(title)}</title>
<style>
  .bg{{fill:#F7F4ED}} .title{{font:700 28px "Noto Sans KR",sans-serif;fill:#10283F}}
  .unit{{font:21px "Noto Sans KR",sans-serif;fill:#6A625A}} .label{{font:21px "Noto Sans KR",sans-serif;fill:#253443}}
  .value{{font:700 21px "Noto Sans KR",sans-serif;fill:#10283F}} .grid{{stroke:#D9D1C5;stroke-width:1}}
  .axis{{stroke:#768594;stroke-width:1.4}} .note{{font:20px "Noto Sans KR",sans-serif;fill:#756C63}}
</style>
<rect class="bg" width="100%" height="100%" rx="18"/>
<text x="30" y="44" class="title">{html.escape(title)}</text>
<text x="30" y="72" class="unit">단위: {html.escape(unit)}</text>'''

    if week == 1:
        body = '''<desc id="desc">비행기와 레이더는 세계대전 전에, ARPANET과 GPS는 두 세계대전 뒤에 시작됐음을 보여주는 기술 연표</desc>
<rect x="218" y="103" width="38" height="238" fill="#A94E32" opacity="0.12"/><text x="237" y="126" text-anchor="middle" class="unit">1차대전</text>
<rect x="455" y="103" width="57" height="238" fill="#1F5A75" opacity="0.12"/><text x="484" y="126" text-anchor="middle" class="unit">2차대전</text>
<line x1="86" y1="260" x2="842" y2="260" class="axis"/>
<line x1="86" y1="251" x2="86" y2="269" class="axis"/><text x="86" y="300" text-anchor="middle" class="unit">1900</text>
<line x1="275" y1="251" x2="275" y2="269" class="axis"/><text x="275" y="300" text-anchor="middle" class="unit">1920</text>
<line x1="464" y1="251" x2="464" y2="269" class="axis"/><text x="464" y="300" text-anchor="middle" class="unit">1940</text>
<line x1="653" y1="251" x2="653" y2="269" class="axis"/><text x="653" y="300" text-anchor="middle" class="unit">1960</text>
<line x1="842" y1="251" x2="842" y2="269" class="axis"/><text x="842" y="300" text-anchor="middle" class="unit">1980</text>
<circle cx="114" cy="260" r="10" fill="#A94E32"/><line x1="114" y1="250" x2="114" y2="178" stroke="#A94E32" stroke-width="2"/>
<text x="114" y="151" text-anchor="middle" class="value">1903</text><text x="114" y="176" text-anchor="middle" class="label">비행기</text>
<rect x="425" y="250" width="20" height="20" fill="#1F5A75"/><line x1="435" y1="250" x2="435" y2="178" stroke="#1F5A75" stroke-width="2"/>
<text x="435" y="151" text-anchor="middle" class="value">1937</text><text x="435" y="176" text-anchor="middle" class="label">레이더</text>
<path d="M738 248L750 260L738 272L726 260Z" fill="#4D7C6F"/><line x1="738" y1="272" x2="738" y2="333" stroke="#4D7C6F" stroke-width="2"/>
<text x="704" y="360" text-anchor="middle" class="value">1969</text><text x="704" y="385" text-anchor="middle" class="label">ARPANET</text>
<path d="M776 248L789 272H763Z" fill="#C18A3D"/><line x1="776" y1="272" x2="776" y2="333" stroke="#C18A3D" stroke-width="2"/>
<text x="813" y="360" text-anchor="middle" class="value">1973</text><text x="813" y="385" text-anchor="middle" class="label">GPS</text>
<text x="86" y="424" class="note">발명·전시 가속·냉전기 국방 연구·민간 전환을 같은 말로 묶지 않습니다.</text>'''
        chart_name = "기술 연표"
    elif week == 2:
        body = '''<desc id="desc">ASML 시스템 매출의 중국 출하 비중과 주요 수출통제 일정을 함께 보여주는 막대 및 시간표</desc>
<text x="52" y="112" class="label" style="font-weight:700">ASML 시스템 매출 중 중국 출하 비중</text>
<rect x="73" y="225" width="118" height="116" rx="8" fill="#1F5A75"/>
<text x="132" y="208" text-anchor="middle" class="value" style="font-size:27px">29%</text>
<text x="132" y="370" text-anchor="middle" class="label">2023</text>
<rect x="240" y="177" width="118" height="164" rx="8" fill="#A94E32"/>
<text x="299" y="160" text-anchor="middle" class="value" style="font-size:27px">41%</text>
<text x="299" y="370" text-anchor="middle" class="label">2024</text>
<text x="54" y="420" class="note">고객 공장 소재지 기준 · EUV 확보와 다름</text>
<line x1="443" y1="136" x2="443" y2="345" stroke="#D9D1C5" stroke-width="2"/>
<text x="485" y="112" class="label" style="font-weight:700">통제 범위가 넓어진 과정</text>
<circle cx="488" cy="161" r="8" fill="#1F5A75"/><text x="512" y="166" class="value">2022.10</text>
<text x="617" y="166" class="label">미 첨단 칩·제조장비 통제</text>
<circle cx="488" cy="231" r="8" fill="#4D7C6F"/><text x="512" y="236" class="value">2024.09</text>
<text x="617" y="236" class="label">네덜란드 일부 DUV 허가 확대</text>
<circle cx="488" cy="301" r="8" fill="#A94E32"/><text x="512" y="306" class="value">2024.12</text>
<text x="617" y="306" class="label">미 24종 장비·3종 SW·HBM</text>
<text x="485" y="365" class="note">비중 상승만으로 통제 실패를 뜻하지 않음</text>
<text x="485" y="393" class="note">DUV 수요와 출하 시차를 함께 확인</text>'''
        chart_name = "규제 연표"
    elif week == 5:
        total = sum(value for _, value in rows)
        radius, circumference, offset = 98, 2 * math.pi * 98, 0.0
        segments = []
        legend = []
        for idx, (label, value) in enumerate(rows):
            length = circumference * value / total
            color = palette[idx % len(palette)]
            segments.append(
                f'<circle cx="230" cy="250" r="{radius}" fill="none" stroke="{color}" stroke-width="54" '
                f'stroke-dasharray="{length:.1f} {circumference - length:.1f}" stroke-dashoffset="{-offset:.1f}" '
                'transform="rotate(-90 230 250)"/>'
            )
            pct = value / total * 100
            y = 142 + idx * 55
            legend.append(f'<rect x="430" y="{y - 16}" width="18" height="18" rx="4" fill="{color}"/>')
            legend.append(f'<text x="462" y="{y}" class="label">{html.escape(label)}</text>')
            legend.append(f'<text x="790" y="{y}" text-anchor="end" class="value">{shown(value)} · {pct:.1f}%</text>')
            offset += length
        body = (
            '<desc id="desc">재원 구성 도넛 차트</desc>'
            + ''.join(segments)
            + f'<text x="230" y="242" text-anchor="middle" class="unit">총 재원</text>'
            + f'<text x="230" y="274" text-anchor="middle" class="title">{shown(total)}</text>'
            + ''.join(legend)
            + '<text x="430" y="385" class="note">구성비는 항목 합계 기준이며 반올림할 수 있음</text>'
        )
        chart_name = "도넛 차트"
    elif week == 4:
        body = '''<desc id="desc">2019·2021·2022년 일본산 불화수소 수입액을 실제 연도 간격으로 비교한 그림</desc>
<line x1="92" y1="338" x2="842" y2="338" class="axis"/>
<line x1="92" y1="118" x2="92" y2="338" class="axis"/>
<line x1="92" y1="118" x2="842" y2="118" class="grid"/><line x1="92" y1="228" x2="842" y2="228" class="grid"/>
<text x="78" y="344" text-anchor="end" class="unit">0</text><text x="78" y="234" text-anchor="end" class="unit">20</text><text x="78" y="124" text-anchor="end" class="unit">40</text>
<polyline points="92,138.4 592,269.3 842,292.4" fill="none" stroke="#1F5A75" stroke-width="5"/>
<circle cx="92" cy="138.4" r="8" fill="#A94E32"/><circle cx="592" cy="269.3" r="8" fill="#4D7C6F"/><circle cx="842" cy="292.4" r="8" fill="#C18A3D"/>
<text x="108" y="130" class="value">36.3</text><text x="592" y="254" text-anchor="middle" class="value">12.5</text><text x="842" y="277" text-anchor="middle" class="value">8.3</text>
<text x="92" y="374" text-anchor="middle" class="label">2019</text><text x="342" y="374" text-anchor="middle" class="unit">2020 자료 미표기</text><text x="592" y="374" text-anchor="middle" class="label">2021</text><text x="842" y="374" text-anchor="middle" class="label">2022</text>'''
        chart_name = "연도 비교"
    elif week == 26:
        body = '''<desc id="desc">2024년 데이터센터 전력소비 기준연도 추정과 2030·2035년 IEA 기본 시나리오 전망을 구분한 그림</desc>
<line x1="92" y1="338" x2="842" y2="338" class="axis"/><line x1="92" y1="108" x2="92" y2="338" class="axis"/>
<line x1="92" y1="108" x2="842" y2="108" class="grid"/><line x1="92" y1="223" x2="842" y2="223" class="grid"/>
<text x="78" y="344" text-anchor="end" class="unit">0</text><text x="78" y="229" text-anchor="end" class="unit">600</text><text x="78" y="114" text-anchor="end" class="unit">1,200</text>
<circle cx="92" cy="258.5" r="9" fill="#1F5A75"/><text x="112" y="250" class="value">415</text>
<line x1="92" y1="258.5" x2="842" y2="108" stroke="#A94E32" stroke-width="5" stroke-dasharray="13 9"/>
<circle cx="542" cy="156.9" r="9" fill="#F7F4ED" stroke="#A94E32" stroke-width="5"/><circle cx="842" cy="108" r="9" fill="#F7F4ED" stroke="#A94E32" stroke-width="5"/>
<text x="542" y="142" text-anchor="middle" class="value">945</text><text x="842" y="93" text-anchor="end" class="value">약 1,200</text>
<text x="92" y="374" text-anchor="middle" class="label">2024</text><text x="542" y="374" text-anchor="middle" class="label">2030</text><text x="842" y="374" text-anchor="middle" class="label">2035</text>
<rect x="300" y="78" width="20" height="20" rx="10" fill="#1F5A75"/><text x="330" y="95" class="unit">기준연도 추정</text>
<line x1="516" y1="88" x2="552" y2="88" stroke="#A94E32" stroke-width="5" stroke-dasharray="10 7"/><text x="565" y="95" class="unit">기본 시나리오 전망</text>
<text x="92" y="416" class="note">2030년 이후에는 수요·효율·정책에 따른 전망 불확실성이 더 커집니다.</text>'''
        chart_name = "추정·전망"
    elif week in {2, 8, 9, 12, 16, 25, 27, 28}:
        left, top, chart_width, chart_height = 82, 118, 760, 225
        step = chart_width / max(1, len(rows) - 1)
        points = []
        circles = []
        labels = []
        for idx, (label, value) in enumerate(rows):
            x = left + idx * step
            y = top + chart_height - (value / max_value) * chart_height
            points.append(f"{x:.1f},{y:.1f}")
            circles.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7" fill="#A94E32" stroke="#F7F4ED" stroke-width="3"/>')
            labels.append(f'<text x="{x:.1f}" y="{top + chart_height + 32}" text-anchor="middle" class="label">{html.escape(label)}</text>')
            labels.append(f'<text x="{x:.1f}" y="{max(104, y - 15):.1f}" text-anchor="middle" class="value">{shown(value)}</text>')
        grid = ''.join(
            f'<line x1="{left}" y1="{top + chart_height * i / 4:.1f}" x2="{left + chart_width}" y2="{top + chart_height * i / 4:.1f}" class="grid"/>'
            for i in range(5)
        )
        body = (
            '<desc id="desc">시간과 시나리오의 변화를 보여주는 추세선</desc>'
            + grid
            + f'<polyline points="{" ".join(points)}" fill="none" stroke="#1F5A75" stroke-width="5" stroke-linejoin="round"/>'
            + ''.join(circles + labels)
            + f'<text x="72" y="140" text-anchor="end" class="unit">{shown(max_value)}</text>'
            + '<text x="72" y="350" text-anchor="end" class="unit">0</text>'
            + f'<text x="82" y="410" class="note">첫 시점 대비 마지막 시점 변화: {((rows[-1][1] / rows[0][1]) - 1) * 100:+.1f}%</text>'
        )
        chart_name = "시점 비교"
    elif week in {1, 6, 11, 18, 19, 23, 30}:
        left, base, chart_height = 90, 350, 220
        slot = 740 / len(rows)
        bar_width = min(112, slot * 0.58)
        items = ['<line x1="78" y1="350" x2="850" y2="350" class="axis"/>']
        for idx, (label, value) in enumerate(rows):
            x = left + idx * slot + (slot - bar_width) / 2
            bar_height = chart_height * value / max_value
            y = base - bar_height
            color = palette[idx % len(palette)]
            items.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width:.1f}" height="{bar_height:.1f}" rx="7" fill="{color}"/>')
            items.append(f'<text x="{x + bar_width / 2:.1f}" y="{y - 13:.1f}" text-anchor="middle" class="value">{shown(value)}</text>')
            items.append(f'<text x="{x + bar_width / 2:.1f}" y="380" text-anchor="middle" class="label">{html.escape(label)}</text>')
        body = '<desc id="desc">범주별 세로 비교 차트</desc>' + ''.join(items)
        chart_name = "세로 비교"
    else:
        items = []
        for idx, (label, value) in enumerate(rows):
            y = 130 + idx * 70
            end = 275 + 545 * value / max_value
            color = palette[idx % len(palette)]
            items.append(f'<text x="32" y="{y + 5}" class="label">{html.escape(label)}</text>')
            items.append(f'<line x1="275" y1="{y}" x2="{end:.1f}" y2="{y}" stroke="{color}" stroke-width="5" stroke-linecap="round"/>')
            items.append(f'<circle cx="{end:.1f}" cy="{y}" r="11" fill="{color}"/>')
            items.append(f'<text x="{min(875, end + 22):.1f}" y="{y + 6}" class="value">{shown(value)}</text>')
        ratio = max_value / min(value for _, value in rows if value > 0)
        body = (
            '<desc id="desc">격차를 강조하는 롤리팝 차트</desc>'
            + ''.join(items)
            + f'<text x="32" y="410" class="note">최대값은 최소값의 {ratio:.1f}배 · 격차의 원인과 기준을 토론</text>'
        )
        chart_name = "격차 비교"

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
{common}{body}
<rect x="752" y="24" width="138" height="36" rx="18" fill="#10283F"/><text x="821" y="49" text-anchor="middle" style="font:700 20px 'Noto Sans KR',sans-serif;fill:#F7F4ED">{chart_name}</text>
</svg>'''


def svg_matrix(title: str) -> str:
    """Render a centered 2x2 decision matrix for qualitative evidence chapters."""
    cards = [
        (70, 118, "문제 정의", "어떤 결정을 내려야 하는가"),
        (520, 118, "영향받는 사람", "편익과 비용은 누구에게 가는가"),
        (70, 278, "측정 지표", "무엇으로 결과를 확인할 것인가"),
        (520, 278, "중단·수정 조건", "언제 판단을 바꿀 것인가"),
    ]
    items = []
    for index, (x, y, label, note) in enumerate(cards):
        color = "#A94E32" if index in {0, 3} else "#1F5A75"
        items.extend([
            f'<rect x="{x}" y="{y}" width="330" height="112" rx="14" fill="#FCFAF5" stroke="{color}" stroke-width="2"/>',
            f'<circle cx="{x + 32}" cy="{y + 34}" r="17" fill="{color}"/>',
            f'<text x="{x + 32}" y="{y + 40}" text-anchor="middle" class="num">{index + 1}</text>',
            f'<text x="{x + 62}" y="{y + 38}" class="label">{label}</text>',
            f'<text x="{x + 28}" y="{y + 80}" class="note">{note}</text>',
        ])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 430" role="img" aria-labelledby="title desc">
<title id="title">{html.escape(title)} 판단 매트릭스</title><desc id="desc">문제, 사람, 지표, 수정 조건을 중앙 대칭으로 배열한 표</desc>
<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#7C8994"/></marker></defs>
<style>.bg{{fill:#F7F4ED}}.title{{font:700 25px "Noto Sans KR",sans-serif;fill:#10283F}}.label{{font:700 18px "Noto Sans KR",sans-serif;fill:#10283F}}.note{{font:14px "Noto Sans KR",sans-serif;fill:#675F58}}.num{{font:700 15px "Noto Sans KR",sans-serif;fill:#FFF}}.badge{{font:700 12px "Noto Sans KR",sans-serif;fill:#F7F4ED}}</style>
<rect class="bg" width="100%" height="100%" rx="18"/><text x="30" y="46" class="title">{html.escape(title)}</text>
<rect x="772" y="28" width="118" height="28" rx="14" fill="#10283F"/><text x="831" y="47" text-anchor="middle" class="badge">판단 매트릭스</text>
<path d="M400 174H510M235 230V268M685 230V268M400 334H510" fill="none" stroke="#7C8994" stroke-width="2.5" marker-end="url(#arrow)"/>
{''.join(items)}</svg>'''


def svg_qualitative(week: int, title: str) -> str:
    """Render a chapter-specific framework when a numeric series is unsuitable."""
    common = f'''<title id="title">{html.escape(title)}</title>
<style>
  .bg{{fill:#F7F4ED}} .title{{font:700 25px "Noto Sans KR",sans-serif;fill:#10283F}}
  .label{{font:700 18px "Noto Sans KR",sans-serif;fill:#10283F}}
  .small{{font:14px "Noto Sans KR",sans-serif;fill:#675F58}}
  .big{{font:700 31px "Noto Sans KR",sans-serif;fill:#A94E32}}
  .badge{{font:700 12px "Noto Sans KR",sans-serif;fill:#F7F4ED}}
</style>
<rect class="bg" width="100%" height="100%" rx="18"/>
<text x="30" y="46" class="title">{html.escape(title)}</text>'''

    if week == 13:
        desc = "NIST AI 위험관리의 거버넌스와 세 실행 기능을 연결한 구조도"
        body = '''
<circle cx="460" cy="245" r="78" fill="#10283F"/><text x="460" y="251" text-anchor="middle" class="badge" style="font-size:18px">거버넌스</text>
<circle cx="215" cy="245" r="66" fill="#FCFAF5" stroke="#A94E32" stroke-width="3"/><text x="215" y="239" text-anchor="middle" class="label">맥락 파악</text><text x="215" y="267" text-anchor="middle" class="small">MAP</text>
<circle cx="705" cy="165" r="66" fill="#FCFAF5" stroke="#1F5A75" stroke-width="3"/><text x="705" y="159" text-anchor="middle" class="label">위험 측정</text><text x="705" y="187" text-anchor="middle" class="small">MEASURE</text>
<circle cx="705" cy="325" r="66" fill="#FCFAF5" stroke="#4D7C6F" stroke-width="3"/><text x="705" y="319" text-anchor="middle" class="label">위험 관리</text><text x="705" y="347" text-anchor="middle" class="small">MANAGE</text>
<path d="M284 245H374M535 221L639 184M535 269L639 306" stroke="#7C8994" stroke-width="3"/>
<text x="38" y="410" class="small">블랙박스 승인 여부는 정확도 하나가 아니라 관측·중단·책임 구조로 판단합니다.</text>'''
        badge = "AI RMF 구조"
    elif week == 17:
        desc = "직원 모니터링을 안전, 최소수집, 독립재심의 세 축으로 나눈 통제표"
        body = '''
<rect x="65" y="125" width="240" height="220" rx="18" fill="#FCFAF5" stroke="#1F5A75" stroke-width="3"/>
<text x="185" y="170" text-anchor="middle" class="label">가용성·안전</text><text x="185" y="215" text-anchor="middle" class="big">왜 수집합니까</text><text x="185" y="266" text-anchor="middle" class="small">사고 예방에 필요한 신호</text><text x="185" y="294" text-anchor="middle" class="small">보안 목적을 문서화</text>
<rect x="340" y="125" width="240" height="220" rx="18" fill="#FCFAF5" stroke="#A94E32" stroke-width="3"/>
<text x="460" y="170" text-anchor="middle" class="label">최소수집·목적제한</text><text x="460" y="215" text-anchor="middle" class="big">무엇을 뺍니까</text><text x="460" y="266" text-anchor="middle" class="small">직무와 무관한 개인신호</text><text x="460" y="294" text-anchor="middle" class="small">목적 밖 재사용 차단</text>
<rect x="615" y="125" width="240" height="220" rx="18" fill="#FCFAF5" stroke="#4D7C6F" stroke-width="3"/>
<text x="735" y="170" text-anchor="middle" class="label">보존기한·독립재심</text><text x="735" y="215" text-anchor="middle" class="big">누가 이의합니까</text><text x="735" y="266" text-anchor="middle" class="small">접근기록과 삭제시점</text><text x="735" y="294" text-anchor="middle" class="small">노동자 이의제기 절차</text>
<text x="65" y="399" class="small">탐지율이 높아도 목적·범위·구제 절차가 없으면 정당한 감시가 아닙니다.</text>'''
        badge = "통제 3축"
    elif week == 20:
        desc = "AI 제품 출시 전에 차례로 통과해야 할 네 개의 안전 게이트"
        body = '''
<path d="M126 238H792" stroke="#7C8994" stroke-width="5"/>
<circle cx="150" cy="238" r="47" fill="#A94E32"/><circle cx="355" cy="238" r="47" fill="#1F5A75"/><circle cx="560" cy="238" r="47" fill="#4D7C6F"/><circle cx="765" cy="238" r="47" fill="#10283F"/>
<text x="150" y="244" text-anchor="middle" class="badge" style="font-size:18px">1</text><text x="355" y="244" text-anchor="middle" class="badge" style="font-size:18px">2</text><text x="560" y="244" text-anchor="middle" class="badge" style="font-size:18px">3</text><text x="765" y="244" text-anchor="middle" class="badge" style="font-size:18px">4</text>
<text x="150" y="155" text-anchor="middle" class="label">영향평가</text><text x="355" y="155" text-anchor="middle" class="label">독립검토</text><text x="560" y="155" text-anchor="middle" class="label">제한출시</text><text x="765" y="155" text-anchor="middle" class="label">확대·중단</text>
<text x="150" y="315" text-anchor="middle" class="small">피해와 사용자</text><text x="355" y="315" text-anchor="middle" class="small">출하 전 반론</text><text x="560" y="315" text-anchor="middle" class="small">가역성 확인</text><text x="765" y="315" text-anchor="middle" class="small">증거로 전환</text>
<text x="46" y="405" class="small">검토 전에 제한출시부터 하지 않습니다. 게이트의 순서 자체가 책임 설계입니다.</text>'''
        badge = "출시 게이트"
    elif week == 21:
        desc = "신입사원이 이상 수율을 발견한 뒤 시간 제한을 두고 보고하는 절차"
        body = '''
<line x1="105" y1="234" x2="815" y2="234" stroke="#7C8994" stroke-width="4"/>
<circle cx="130" cy="234" r="34" fill="#A94E32"/><circle cx="350" cy="234" r="34" fill="#1F5A75"/><circle cx="570" cy="234" r="34" fill="#4D7C6F"/><circle cx="790" cy="234" r="34" fill="#10283F"/>
<text x="130" y="155" text-anchor="middle" class="label">이상 발견</text><text x="350" y="155" text-anchor="middle" class="label">원자료 재검증</text><text x="570" y="155" text-anchor="middle" class="label">동시 보고</text><text x="790" y="155" text-anchor="middle" class="label">수정·공시 판단</text>
<text x="130" y="240" text-anchor="middle" class="badge">발견</text><text x="350" y="240" text-anchor="middle" class="badge">시한</text><text x="570" y="240" text-anchor="middle" class="badge">기록</text><text x="790" y="240" text-anchor="middle" class="badge">책임</text>
<text x="130" y="314" text-anchor="middle" class="small">숨기지 않기</text><text x="350" y="314" text-anchor="middle" class="small">무기한 지연 금지</text><text x="570" y="314" text-anchor="middle" class="small">상사·독립채널</text><text x="790" y="314" text-anchor="middle" class="small">근거 보존</text>
<text x="68" y="402" class="small">즉시 보고와 선검증의 충돌은 ‘검증 시한’과 ‘독립 보고선’을 함께 두어 해결합니다.</text>'''
        badge = "보고 타임라인"
    elif week == 22:
        desc = "용인 반도체 클러스터에 필요한 전력과 용수를 나란히 보여주는 데이터 계기판"
        body = '''
<rect x="70" y="120" width="365" height="230" rx="24" fill="#FCFAF5" stroke="#1F5A75" stroke-width="3"/>
<text x="252" y="170" text-anchor="middle" class="label">신규 전력 수요</text><text x="252" y="242" text-anchor="middle" class="big" style="font-size:48px">10GW 이상</text><text x="252" y="294" text-anchor="middle" class="small">2053년까지 정부 전망</text>
<rect x="485" y="120" width="365" height="230" rx="24" fill="#FCFAF5" stroke="#4D7C6F" stroke-width="3"/>
<text x="667" y="170" text-anchor="middle" class="label">통합 용수 공급</text><text x="667" y="242" text-anchor="middle" class="big" style="font-size:43px">하루 107.2만㎥</text><text x="667" y="294" text-anchor="middle" class="small">약 300만 명 하루 사용량</text>
<text x="70" y="400" class="small">비용뿐 아니라 입지별 송전·취수 한계와 지역 편익협약을 함께 판단합니다.</text>'''
        badge = "지역 부담 계기판"
    elif week == 24:
        desc = "자동화 재교육에 필요한 시간과 비용을 원인과 편익에 따라 나누는 분담 구조"
        body = '''
<text x="72" y="128" class="label">재교육이 실제 직무전환이 되려면</text>
<rect x="72" y="162" width="188" height="160" rx="16" fill="#A94E32"/><text x="166" y="215" text-anchor="middle" class="badge" style="font-size:18px">유급 학습시간</text><text x="166" y="258" text-anchor="middle" class="badge">생계 장벽 제거</text>
<rect x="274" y="162" width="188" height="160" rx="16" fill="#1F5A75"/><text x="368" y="215" text-anchor="middle" class="badge" style="font-size:18px">교육비 지원</text><text x="368" y="258" text-anchor="middle" class="badge">고용주·공공 분담</text>
<rect x="476" y="162" width="188" height="160" rx="16" fill="#4D7C6F"/><text x="570" y="215" text-anchor="middle" class="badge" style="font-size:18px">전환 배치</text><text x="570" y="258" text-anchor="middle" class="badge">수료 뒤 일자리</text>
<rect x="678" y="162" width="170" height="160" rx="16" fill="#10283F"/><text x="763" y="215" text-anchor="middle" class="badge" style="font-size:18px">개인 선택</text><text x="763" y="258" text-anchor="middle" class="badge">경력 방향 참여</text>
<text x="72" y="388" class="small">수료율이 아니라 직무 이동률·임금 유지율·중도탈락의 원인을 봅니다.</text>'''
        badge = "전환 분담표"
    elif week == 29:
        desc = "퇴사자 업무기록을 필드별로 나누고 보존 기한 뒤 재심하는 생애주기"
        body = '''
<rect x="62" y="145" width="180" height="170" rx="18" fill="#FCFAF5" stroke="#A94E32" stroke-width="3"/><text x="152" y="195" text-anchor="middle" class="label">1. 수집</text><text x="152" y="240" text-anchor="middle" class="small">업무 목적 명시</text><text x="152" y="270" text-anchor="middle" class="small">불필요 항목 제외</text>
<rect x="267" y="145" width="180" height="170" rx="18" fill="#FCFAF5" stroke="#1F5A75" stroke-width="3"/><text x="357" y="195" text-anchor="middle" class="label">2. 필드 분리</text><text x="357" y="240" text-anchor="middle" class="small">품질·개인정보 분리</text><text x="357" y="270" text-anchor="middle" class="small">접근권 차등</text>
<rect x="472" y="145" width="180" height="170" rx="18" fill="#FCFAF5" stroke="#4D7C6F" stroke-width="3"/><text x="562" y="195" text-anchor="middle" class="label">3. 기간 만료</text><text x="562" y="240" text-anchor="middle" class="small">자동 비가시화</text><text x="562" y="270" text-anchor="middle" class="small">보존 사유 재심</text>
<rect x="677" y="145" width="180" height="170" rx="18" fill="#FCFAF5" stroke="#10283F" stroke-width="3"/><text x="767" y="195" text-anchor="middle" class="label">4. 삭제·보존</text><text x="767" y="240" text-anchor="middle" class="small">근거 있는 최소보존</text><text x="767" y="270" text-anchor="middle" class="small">감사 기록 남김</text>
<path d="M242 230H260M447 230H465M652 230H670" stroke="#7C8994" stroke-width="4"/>
<text x="62" y="395" class="small">‘전부 삭제’와 ‘영구 보존’ 사이를 필드·접근권·기한으로 나눕니다.</text>'''
        badge = "기록 생애주기"
    else:
        return svg_matrix(title)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 440" role="img" aria-labelledby="title desc">
{common}<desc id="desc">{desc}</desc>{body}
<rect x="752" y="28" width="138" height="28" rx="14" fill="#10283F"/><text x="821" y="47" text-anchor="middle" class="badge">{badge}</text>
</svg>'''


def render(topic) -> str:
    week, title, question, motif, source_name, source_url, data_lens, pro, con, condition = topic
    ev = EVIDENCE[week]
    facts = ev["facts"]
    figure = f"![{title} 핵심 데이터](../figures/week{week:02d}.png){{fig-alt=\"{title} 핵심 데이터와 판단 구조\"}}"
    fact_rows = "\n".join(f"| {i} | {fact} |" for i, fact in enumerate(facts, 1))
    memo = "첫 번째와 두 번째 핵심 수치"
    extra_sources = "\n".join(f"- [{name}]({url})" for name, url in ev.get("extra_sources", []))
    spoken_condition = condition.rstrip(".")
    return f'''---
title: "{title}"
description: "{question}"
categories: [반도체, 인문학, 집단토론, 데이터]
---

::: {{.book-question}}
[오늘의 책문]{{.book-question-label}}

[{question}?]{{.book-question-prompt}}
:::

조선의 모티브는 **{motif}**이다. 책문은 사실을 많이 아는 사람보다, 충돌하는 가치의 우선순위와 자기 답이 실패할 조건을 밝히는 사람을 가려냈다. 오늘의 응시자는 이 질문을 산업의 숫자와 인간의 비용을 함께 놓고 답해야 한다.

## 왜 지금 이 질문인가

{data_lens} 이 주제를 단순한 찬반으로 만들면 중요한 당사자가 사라진다. 공급망의 비용은 구매팀만, AI의 위험은 개발팀만, 노동의 전환은 개인만 책임지는 문제가 아니다. 결정권·편익·손실이 누구에게 배분되는지까지 보여야 토론이 산업 분석이 된다.

## 데이터 렌즈

{figure}

### 근거 데이터 표

| 근거 번호 | 토론에 쓸 수 있는 검증 문장 |
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

## AI 조사 설계

- **프롬프트:** 찬반 결론을 먼저 요구하지 말고 핵심 용어의 정의와 확인할 지표부터 질문한다.
- **데이터 취득:** 정부·국제기구·기업 공시의 직접 URL, 기준연도, 단위와 모집단을 함께 기록한다.
- **정보 판정:** 실측과 전망, 공식 발표와 독립 검증, 사실과 토론용 가정을 분리한다.
- **토론의 핵심:** 무엇을 측정해 어느 임계값에서 A·B·C 사이의 결정을 바꿀지 정한다.

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

## 출처

- [{ev['source_name']}]({ev['source']})
- [{source_name}]({source_url})
{extra_sources}
- [조선시대 책문 아카이브](https://waterfirst.github.io/Joseon-Dynasty-Civil-Service-Examination/)

> 데이터 기준일: 각 원출처의 표기 연도. 최신성이 중요한 수치는 상업 발행 직전에 다시 확인한다.
'''


def main() -> None:
    """Rebuild data figures without overwriting the edited chapter manuscripts."""
    FIGURES.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    titles = {
        1: "전쟁은 인류를 진보시키는가",
        2: "미·중 수출통제와 기술의 국적",
        **{week: item["title"] for week, item in BLUEPRINTS.items()},
    }
    records = []
    for week in range(1, 31):
        title = titles[week]
        ev = EVIDENCE[week]
        if ev["chart"]:
            (FIGURES / f"week{week:02d}.svg").write_text(svg_chart(week, title, ev["unit"], ev["chart"]), encoding="utf-8")
        else:
            (FIGURES / f"week{week:02d}.svg").write_text(svg_qualitative(week, title), encoding="utf-8")
        for label, value in ev["chart"]:
            records.append([week, title, label, value, ev["unit"], ev["source"]])
    with (DATA / "evidence.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["week", "topic", "label", "value", "unit", "source_url"])
        writer.writerows(records)
    print(f"preserved 30 edited chapters, rebuilt {len(list(FIGURES.glob('week*.svg')))} charts and {len(records)} evidence rows")


if __name__ == "__main__":
    main()
