# AGI-lite 멀티에이전트 시스템

LangGraph 기반의 멀티에이전트 시스템으로, Planner, Developer, Critic 에이전트가 협력하여 사용자의 목표를 달성합니다.

## 기능

- CLI 인터페이스 (`python cli.py --goal "..."`)
- REST API (`POST /run-agent`)
- 로컬 LLM (Mistral-7B) 사용
- JSON 기반 메모리 시스템
- 자동 설치 스크립트

## 설치 방법

1. Windows 환경에서 `setup.bat` 실행:
```bash
setup.bat
```

2. 가상환경 활성화:
```bash
.venv\Scripts\activate.bat
```

## 사용 방법

### CLI 사용
```bash
python cli.py --goal "목표를 입력하세요"
```

### API 서버 실행
```bash
python main.py
```

API 엔드포인트: `POST http://localhost:8000/run-agent`
```json
{
    "goal": "목표를 입력하세요"
}
```

## 프로젝트 구조

```
agi_agent_system/
├── app/
│   ├── config.py          # 시스템 설정
│   ├── model.py           # LLM 래퍼
│   ├── memory.py          # 메모리 관리
│   ├── agent_graph.py     # LangGraph 구성
│   ├── api.py            # FastAPI 라우터
│   └── agents/           # 에이전트 구현
├── cli.py                # CLI 인터페이스
├── main.py              # API 서버 진입점
├── models/              # LLM 모델 파일
├── requirements.txt     # 의존성 목록
└── setup.bat           # 설치 스크립트
``` 