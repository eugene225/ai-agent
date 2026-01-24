## Example Agent

`.env`에서 API 키를 불러오고, 간단한 프롬프트로 야구 관련 답변을 생성하는 예제입니다.

## 학습한 내용
- `python-dotenv`로 `.env` 자동 로드
- OpenAI Python SDK로 기본 호출 흐름 이해
- 시스템 프롬프트로 응답 톤/범위 제어

## 실행하기
```
cd example-agent
source .venv/bin/activate
python baseball_agent.py
```