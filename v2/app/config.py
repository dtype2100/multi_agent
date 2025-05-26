from pathlib import Path
from typing import Optional
from pydantic import BaseModel

class Config(BaseModel):
    """시스템 전반의 설정값을 관리하는 클래스"""
    
    # 기본 경로 설정
    BASE_DIR: Path = Path(__file__).parent.parent
    MODELS_DIR: Path = BASE_DIR / "models"
    MEMORY_DIR: Path = BASE_DIR / "memory"
    
    # LLM 모델 설정
    MODEL_NAME: str = "mistral-7b.Q4_K_M.gguf"
    MODEL_PATH: Path = MODELS_DIR / MODEL_NAME
    CONTEXT_SIZE: int = 4096
    TEMPERATURE: float = 0.7
    
    # API 설정
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    
    # Memory 설정
    MEMORY_FILE: str = "agent_memory.json"
    
    # Agent 설정
    MAX_ITERATIONS: int = 5
    REFLEXION_ENABLED: bool = True
    
    class Config:
        arbitrary_types_allowed = True

# 전역 설정 인스턴스
config = Config()

# 필요한 디렉토리 생성
config.MODELS_DIR.mkdir(exist_ok=True)
config.MEMORY_DIR.mkdir(exist_ok=True) 