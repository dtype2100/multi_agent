"""설정 관리 모듈

이 모듈은 시스템의 설정을 관리합니다.
"""

from dataclasses import dataclass
from typing import Optional
import os
from pathlib import Path

@dataclass
class Config:
    """시스템 설정
    
    Attributes:
        model_path: LLM 모델 파일 경로
        temperature: 생성 온도
        max_tokens: 최대 토큰 수
        success_threshold: 성공 기준 점수
        memory_dir: 메모리 파일 디렉토리
        max_iterations: 최대 반복 횟수
    """
    model_path: str
    temperature: float = 0.7
    max_tokens: int = 2000
    success_threshold: float = 0.8
    memory_dir: str = "memory"
    max_iterations: int = 10

def load_config() -> Config:
    """환경 변수에서 설정을 로드
    
    Returns:
        Config: 로드된 설정
    """
    return Config(
        model_path=os.getenv("MODEL_PATH", "models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"),
        temperature=float(os.getenv("TEMPERATURE", "0.7")),
        max_tokens=int(os.getenv("MAX_TOKENS", "2000")),
        success_threshold=float(os.getenv("SUCCESS_THRESHOLD", "0.8")),
        memory_dir=os.getenv("MEMORY_DIR", "memory"),
        max_iterations=int(os.getenv("MAX_ITERATIONS", "10"))
    )

# 전역 설정 인스턴스
config = load_config() 