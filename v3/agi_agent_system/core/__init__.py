"""코어 패키지

이 패키지는 시스템의 핵심 컴포넌트들을 포함합니다:
- config: 시스템 설정 관리
- llm: LLM 모델 래퍼
- memory: 세션별 메모리 관리
"""

from .config import config
from .llm import get_llm
from .memory import MemoryManager

__all__ = ['config', 'get_llm', 'MemoryManager'] 