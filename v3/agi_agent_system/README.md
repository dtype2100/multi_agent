# AGI 에이전트 시스템

이 프로젝트는 여러 에이전트가 협력하여 복잡한 목표를 달성하는 시스템입니다.

## 기능

- 목표를 하위 태스크로 분해
- 각 태스크에 대한 코드 생성
- 생성된 코드의 품질 평가 및 피드백
- 세션별 메모리 관리
- CLI 및 API 인터페이스 제공

## 설치

1. 저장소 클론:
```bash
git clone <repository-url>
cd agi_agent_system
```

2. 가상 환경 생성 및 활성화:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

3. 의존성 설치:
```bash
pip install -r requirements.txt
```

4. LLM 모델 다운로드:
- [Llama 2 7B Chat GGUF](https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF) 모델을 다운로드하여 `models` 디렉토리에 저장

## 사용 방법

### CLI 모드

```bash
python -m agi_agent_system.run_cli --goal "목표를 여기에 입력하세요"
```

옵션:
- `--session-id`: 세션 ID (기본값: 자동 생성)
- `--memory-dir`: 메모리 파일 디렉토리 (기본값: memory)

### API 모드

```bash
python -m agi_agent_system.main --mode api
```

옵션:
- `--host`: API 서버 호스트 (기본값: 0.0.0.0)
- `--port`: API 서버 포트 (기본값: 8000)
- `--session-id`: 세션 ID (기본값: 자동 생성)
- `--memory-dir`: 메모리 파일 디렉토리 (기본값: memory)

API 엔드포인트:
- `POST /run`: 워크플로우 실행
  - 요청 본문:
    ```json
    {
        "goal": "목표를 여기에 입력하세요",
        "session_id": "선택적 세션 ID",
        "memory_dir": "선택적 메모리 디렉토리"
    }
    ```

## 프로젝트 구조

```
agi_agent_system/
├── agents/              # 에이전트 구현
│   ├── base.py         # 기본 에이전트 클래스
│   ├── planner.py      # 플래너 에이전트
│   ├── developer.py    # 개발자 에이전트
│   └── critic.py       # 비평가 에이전트
├── core/               # 핵심 컴포넌트
│   ├── config.py       # 설정 관리
│   ├── llm.py         # LLM 모델 래퍼
│   └── memory.py      # 메모리 관리
├── workflow/           # 워크플로우 관리
│   └── agent_graph.py # 에이전트 실행 흐름
├── interface/          # 사용자 인터페이스
│   ├── cli.py         # 명령줄 인터페이스
│   └── api.py         # API 인터페이스
├── main.py            # 메인 모듈
├── run_cli.py         # CLI 실행 스크립트
└── README.md          # 프로젝트 문서
```

## 환경 변수

- `MODEL_PATH`: LLM 모델 파일 경로 (기본값: models/llama-2-7b-chat.gguf)
- `TEMPERATURE`: 생성 온도 (기본값: 0.7)
- `MAX_TOKENS`: 최대 토큰 수 (기본값: 2000)
- `SUCCESS_THRESHOLD`: 성공 기준 점수 (기본값: 0.8)
- `MEMORY_DIR`: 메모리 파일 디렉토리 (기본값: memory)

## 라이선스

MIT License 