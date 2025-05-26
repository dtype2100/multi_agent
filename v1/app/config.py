from pathlib import Path
from typing import Optional
from pydantic import BaseModel

class Config(BaseModel):
    # 기본 경로 설정
    BASE_DIR: Path = Path(__file__).parent.parent
    MODELS_DIR: Path = BASE_DIR / "models"
    MEMORY_DIR: Path = BASE_DIR / "memory"
    
    # 모델 설정
    MODEL_PATH: Path = MODELS_DIR / "mistral-7b.Q4_K_M.gguf"
    MODEL_CONTEXT_SIZE: int = 4096
    MODEL_TEMPERATURE: float = 0.7
    
    # 에이전트 설정
    MAX_ITERATIONS: int = 5
    REFLEXION_ENABLED: bool = True
    
    # API 설정
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # 시스템 프롬프트
    PLANNER_PROMPT: str = """당신은 목표를 분석하고 하위 태스크로 분해하는 플래너입니다.
주어진 목표를 달성하기 위해 필요한 단계들을 순차적으로 나열해주세요.
각 단계는 명확하고 실행 가능해야 합니다."""

    DEVELOPER_PROMPT: str = """당신은 주어진 태스크를 실행하는 개발자입니다.
태스크를 완료하기 위해 필요한 코드나 해결책을 제시해주세요.
코드는 실행 가능하고 효율적이어야 합니다."""

    CRITIC_PROMPT: str = """당신은 개발자의 결과를 검토하고 피드백을 제공하는 비평가입니다.
결과의 정확성, 효율성, 완성도를 평가하고 개선점을 제시해주세요."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 필요한 디렉토리 생성
        self.MODELS_DIR.mkdir(exist_ok=True)
        self.MEMORY_DIR.mkdir(exist_ok=True)

# 전역 설정 인스턴스
config = Config() 