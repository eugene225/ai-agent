## Job-Hunter-Agent
이 프로젝트는 **CrewAI 기반 채용 정보 탐색/매칭 에이전트**를 만들고, LLM 출력/스키마 검증/툴 연동 이슈를 해결하면서 학습한 내용을 정리한 문서입니다.

### 만든 것
- 웹 검색 → 공고 추출 → 매칭 → 최종 선택 → 이력서 최적화 → 기업 리서치 → 면접 준비 문서 생성 파이프라인
- 이력서 텍스트(`knowledge/resume.txt`)를 지식 소스로 활용해 개인화
- 결과물은 `output/`에 마크다운 파일로 저장

### 흐름 (Task 연결)
1. `job_extraction_task`: 웹 검색으로 공고 리스트 추출
2. `job_matching_task`: 이력서 기반 점수/이유 부여
3. `job_selection_task`: 최적 공고 1개 선택 (ChosenJob)
4. `resume_rewriting_task`: 선택 공고 기준 이력서 리라이팅
5. `company_research_task`: 회사 조사 리포트 생성
6. `interview_prep_task`: 면접 대비 문서 통합 생성

## 오류 정리 (원인/해결)
### 1) `ImportError: cannot import name 'ScrapeOptions'`
- **원인**: `firecrawl` v4에서 `ScrapeOptions`가 v2 타입으로 정리되며 위치/사용 방식 변경
- **해결**: `ScrapeOptions` import 제거 후 `search()`의 `scrape_options`를 dict로 전달

### 2) `SearchRequest scrape_options validation error`
- **원인**: `V1ScrapeOptions` 인스턴스를 v2 `search()`에 전달해 타입 불일치
- **해결**: `{"formats": ["markdown"]}` 같은 **dict** 형태로 전달

### 3) `'SearchData' object has no attribute 'success'`
- **원인**: `search()`는 `SearchData`를 반환하며 `success/data`가 없음
- **해결**: 결과를 `response.web`/`news`/`images`에서 읽고 `Document`/`SearchResult` 타입을 분기 처리

### 4) `ChosenJob validation error (job/selected/reason missing)`
- **원인**: LLM 출력이 `ChosenJob` 스키마와 불일치하거나 JSON 외 텍스트 포함
- **해결**: `tasks.yaml`에 **JSON만 출력**하도록 명시하고, `RankedJobList`/`ChosenJob` 스키마 형태를 명확히 안내

## 중요 Context 개념 (CrewAI)
- **Task context**: 이전 Task의 출력을 다음 Task에 전달하는 메커니즘.
- `resume_rewriting_task`, `company_research_task`, `interview_prep_task`가 `job_selection_task` 출력에 의존하도록 `context`에 지정됨.
- 에이전트별로 `knowledge_sources`를 지정해 이력서 파일을 참고하도록 구성됨.

## Model 객체 선언 (Pydantic)
- `models.py`에 `BaseModel` 기반 스키마 정의.
- Task에서 `output_pydantic`으로 스키마를 지정하면 **LLM 출력이 해당 구조를 반드시 충족**해야 함.
- `ChosenJob`는 `job`, `selected`, `reason` 필드가 **필수**라 누락 시 검증 오류 발생.

## 참고 코드
```python
# models.py
class ChosenJob(BaseModel):
    job: Job
    selected: bool
    reason: str
```

```python
# main.py (Task 스키마 지정 예시)
Task(config=..., output_pydantic=ChosenJob)
```
