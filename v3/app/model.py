from langchain_community.llms import LlamaCpp
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from .config import config

def get_llm() -> LlamaCpp:
    """llama-cpp 모델을 LangChain에서 사용할 수 있도록 래핑하는 함수
    
    Returns:
        LlamaCpp: LangChain에서 사용 가능한 LLM 인스턴스
    """
    # 콜백 매니저 설정 (스트리밍 출력 지원)
    callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
    
    # LlamaCpp 모델 초기화
    llm = LlamaCpp(
        model_path=str(config.model_path),
        n_ctx=config.model_n_ctx,
        n_batch=config.model_n_batch,
        temperature=config.model_temperature,
        callback_manager=callback_manager,
        verbose=True,  # 디버깅을 위한 상세 로그 출력
    )
    
    return llm 