from typing import Optional, List, Dict, Any
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
        temperature: 생성 온도 (기본값: config.TEMPERATURE)
        context_size: 컨텍스트 크기 (기본값: config.CONTEXT_SIZE)
        streaming: 스트리밍 출력 사용 여부
    
    Returns:
        LlamaCpp: 초기화된 LLM 인스턴스
    """
    callback_manager = None
    if streaming:
        callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
    
    return LlamaCpp(
        model_path=str(config.MODEL_PATH),
        temperature=temperature or config.TEMPERATURE,
        n_ctx=context_size or config.CONTEXT_SIZE,
        callback_manager=callback_manager,
        verbose=True,
    )

def format_prompt(
    system_prompt: str,
    user_prompt: str,
    history: Optional[List[Dict[str, str]]] = None
) -> str:
    """
    시스템 프롬프트와 사용자 프롬프트를 포맷팅합니다.
    
    Args:
        system_prompt: 시스템 프롬프트
        user_prompt: 사용자 프롬프트
        history: 대화 기록 (선택사항)
    
    Returns:
        str: 포맷팅된 프롬프트
    """
    formatted_prompt = f"<s>[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n"
    
    if history:
        for msg in history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            formatted_prompt += f"{content} [/INST] "
            if role == "assistant":
                formatted_prompt += f"{msg.get('response', '')} </s><s>[INST] "
    
    formatted_prompt += f"{user_prompt} [/INST]"
    return formatted_prompt 