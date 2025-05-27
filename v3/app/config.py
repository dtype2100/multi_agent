from pathlib import Path
from pydantic import BaseModel, Field
from typing import Optional
import os

class Config(BaseModel):
    """시스템 설정값을 관리하는 클래스"""
    
    # 모델 설정
    model_path: Path = Field(
        default=Path("models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"),
        description="로컬 LLM 모델 파일 경로"
    )
    model_n_ctx: int = Field(
        default=4096,
        description="컨텍스트 윈도우 크기"
    )
    model_n_batch: int = Field(
        default=512,
        description="배치 크기"
    )
    model_temperature: float = Field(
        default=0.7,
        description="생성 온도"
    )
    
    # 메모리 설정
    memory_path: Path = Field(
        default=Path("memory.json"),
        description="메모리 파일 경로"
    )
    
    # API 설정
    api_host: str = Field(
        default="0.0.0.0",
        description="API 서버 호스트"
    )
    api_port: int = Field(
        default=8000,
        description="API 서버 포트"
    )
    
    # 에이전트 설정
    max_iterations: int = Field(
        default=5,
        description="최대 반복 횟수"
    )
    success_threshold: float = Field(
        default=0.8,
        description="성공 판단 임계값"
    )
    
    # Claude AI 설정
    claude_api_key: str = os.getenv("CLAUDE_API_KEY", "")
    claude_model: str = os.getenv("CLAUDE_MODEL", "claude-3-sonnet-20240229")
    claude_temperature: float = float(os.getenv("CLAUDE_TEMPERATURE", "0.7"))
    claude_max_tokens: int = int(os.getenv("CLAUDE_MAX_TOKENS", "4096"))
    
    class Config:
        arbitrary_types_allowed = True

# 전역 설정 인스턴스
config = Config() 