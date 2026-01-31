# News Reader Agent

이 프로젝트는 CrewAI 기반 에이전트가 뉴스 검색/수집/요약/편집을 수행합니다.

## 사용된 툴 정리

`news-reader-agent/tools.py`에 정의된 커스텀 툴과 외부 도구를 정리했습니다.

### 1) `search_tool`

- **정의 위치**: `tools.py`
- **역할**: Serper 기반 웹 검색
- **내부 사용 도구**: `crewai_tools.SerperDevTool`
- **입력**: `search_query: str`
- **출력**: Serper 검색 결과 객체(또는 오류 문자열)
- **예외 처리**:
  - `site:` 같은 고급 검색 연산자가 Serper 정책에 의해 400을 반환할 수 있어, 실패 시 쿼리를 정제(sanitize)해 재시도함

### 2) `scrape_tool`

- **정의 위치**: `tools.py`
- **역할**: URL에서 기사 본문 수집
- **내부 사용 도구**:
  - `playwright.sync_api.sync_playwright` (페이지 렌더링)
  - `bs4.BeautifulSoup` (본문 추출)
- **입력**: `url: str`
- **출력**: 본문 텍스트 문자열 (없으면 `"No content"`)
- **동작 요약**:
  1. Playwright로 페이지 열기
  2. 렌더된 HTML 수집
  3. 불필요 태그 제거 후 텍스트 추출

## 어노테이션(Decorator) 정의/의미

CrewAI에서 툴/에이전트/태스크를 등록하는 데 사용하는 데코레이터입니다.

### `@tool`

- **정의 위치**: `crewai.tools.tool`
- **역할**: 파이썬 함수를 CrewAI 툴로 등록
- **예시**:
  - `@tool("search_tool")`로 툴 이름을 명시 가능
  - `@tool`만 쓰면 함수명 기반으로 등록

### `@CrewBase`, `@agent`, `@task`, `@crew`

- **정의 위치**: `crewai.project`
- **역할**: 클래스 기반으로 에이전트/태스크/크루 구성을 선언적으로 연결
- **현재 사용 위치**: `main.py`

## 실행 순서(파이프라인)

에이전트는 아래 순서로 동작합니다.

1. **콘텐츠 수집 (`content_harvesting_task`)**
   - 검색 → 기사 URL 선정 → 스크래핑 → 메타데이터 정리
   - 결과 파일: `output/content_harvest.md`
2. **요약 (`summarization_task`)**
   - 수집 결과를 읽어 다층 요약 생성
   - 결과 파일: `output/summary.md`
3. **최종 리포트 (`final_report_assembly_task`)**
   - 요약 결과를 편집해 최종 보고서 작성
   - 결과 파일: `output/final_report.md`

실제 작업 정의는 `config/tasks.yaml`, 에이전트 역할은 `config/agents.yaml`에 있습니다.

## 환경 변수

`.env`에 아래 값을 설정해야 정상 동작합니다.

- `SERPER_API_KEY`: Serper 검색 API 키
- (필요 시) LLM Provider 키: CrewAI 설정에 따라 추가

## 실행

```bash
uv run python main.py
```

> Playwright 설치가 필요하면 먼저 아래를 실행하세요:
>
> ```bash
> uv run playwright install
> ```