from typing import Optional
from langchain.llms import LlamaCpp
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from .config import config

def get_llm(
    temperature: Optional[float] = None,
    context_size: Optional[int] = None,
    streaming: bool = True
) -> LlamaCpp:
    """
    llama-cpp-python 기반 LLM 인스턴스를 생성합니다.
    
    Args:
        temperature: 생성 온도 (기본값: config.MODEL_TEMPERATURE)
        context_size: 컨텍스트 크기 (기본값: config.MODEL_CONTEXT_SIZE)
        streaming: 스트리밍 출력 사용 여부
    
    Returns:
        LlamaCpp: LLM 인스턴스
    """
    callback_manager = None
    if streaming:
        callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
    
    return LlamaCpp(
        model_path=str(config.MODEL_PATH),
        temperature=temperature or config.MODEL_TEMPERATURE,
        n_ctx=context_size or config.MODEL_CONTEXT_SIZE,
        callback_manager=callback_manager,
        verbose=True,
        n_gpu_layers=-1  # GPU 가속 활성화
    ) 