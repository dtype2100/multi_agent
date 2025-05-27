"""LLM 모델 래퍼 모듈

이 모듈은 LLM 모델을 래핑하여 일관된 인터페이스를 제공합니다.
"""

from typing import Any, Optional
from langchain_community.llms import LlamaCpp
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from .config import config

def get_llm(
    model_path: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    streaming: bool = True
) -> Any:
    """LLM 모델 인스턴스를 생성하고 반환
    
    Args:
        model_path: 모델 파일 경로 (기본값: config.model_path)
        temperature: 생성 온도 (기본값: config.temperature)
        max_tokens: 최대 토큰 수 (기본값: config.max_tokens)
        streaming: 스트리밍 출력 사용 여부 (기본값: True)
        
    Returns:
        Any: LLM 모델 인스턴스
    """
    callback_manager = None
    if streaming:
        callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
    
    return LlamaCpp(
        model_path=model_path or config.model_path,
        temperature=temperature or config.temperature,
        max_tokens=max_tokens or config.max_tokens,
        n_ctx=4096,  # 컨텍스트 창 크기 증가
        n_batch=512,  # 배치 크기 설정
        callback_manager=callback_manager,
        verbose=True
    ) 