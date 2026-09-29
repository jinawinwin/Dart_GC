# GC녹십자 DART Financial Agent

[![GC Dashboard](assets/gc-dashboard.jpg)](https://jinawinwin.github.io/Dart_GC/)

OpenDART를 이용하여 GC녹십자(006280, corp_code 00129679)의 사업보고서·반기보고서·분기보고서 재무데이터를 수집하고 주요 재무비율을 계산하여 GitHub Pages dashboard로 보여주는 자동화 프로젝트입니다.

## Scope
- Target: GC녹십자
- Period target: 2010–present
- Structured OpenDART financial API: 2015–present
- Reports: Annual 11011 / Half-year 11012 / Q1 11013 / Q3 11014
- CFS 연결재무제표 우선, 없으면 OFS 별도재무제표
- 2010–2014는 OpenDART 구조화 재무 API 제공범위 밖이므로 추정값을 넣지 않습니다.
- Raw API JSON은 data/raw/YYYY/ 아래에 저장합니다.

## Dashboard
https://jinawinwin.github.io/Dart_GC/

상단 KPI와 그래프, Annual / Half-year / Quarterly 3개 표, 국내 peer firms 표를 제공합니다. 오른쪽 floating panel에서 브라우저 화면을 PDF로 출력하고 기간을 선택해 .xlsx Excel 파일을 다운로드할 수 있습니다.

## 주요 지표
Revenue, Gross Profit, Operating Profit, Net Income, Total Assets, Total Liabilities, Total Equity, Current Assets, Current Liabilities, Cash, Operating Cash Flow, R&D Expense, EPS와 Operating Margin, Net Margin, ROA, ROE, Debt Ratio, Current Ratio, Cash Ratio, R&D Ratio를 계산합니다.

첨부 재무지표 파일이 현재 대화의 파일 저장소에서 확인되지 않아 표준 지표 세트를 기본값으로 구성했습니다. 이후 config/metrics.json의 계정명 alias를 추가하면 지표를 확장할 수 있습니다.

## 국내 Peer Firms
| Company | Ticker | Reference |
|---|---:|---|
| 유한양행 | 000100 | 국내 대형 제약사 peer |
| 종근당 | 185750 | 국내 대형 제약사 peer |
| 한미약품 | 128940 | 국내 대형 제약사 peer |
| 대웅제약 | 069620 | 국내 대형 제약사 peer |

## API Key 설정
GitHub → Settings → Secrets and variables → Actions → New repository secret

- Name: DART_API_KEY
- Value: 발급받은 OpenDART 40자리 인증키

Workflow는 secrets.DART_API_KEY를 읽습니다. API key는 소스 코드에 넣지 않습니다.

## 자동 업데이트
workflow_dispatch + 매월 1일 자동 실행입니다. GitHub Actions cron은 UTC 기준이므로 00:15 KST 실행을 목표로 15 15 1 * * 를 사용합니다.

## GitHub Pages
Repository → Settings → Pages → Build and deployment → Source를 GitHub Actions로 한 번 설정하면 pages.yml이 dashboard를 배포합니다.

Repository About의 Website에는 다음 주소를 입력하세요.
https://jinawinwin.github.io/Dart_GC/

## Source
Financial data: Financial Supervisory Service OpenDART. 중요한 수치는 원문 DART 공시와 대조하세요.
