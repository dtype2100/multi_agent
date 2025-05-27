"""에이전트의 기본 클래스

이 모듈은 모든 에이전트의 기본이 되는 BaseAgent 클래스를 정의합니다.
각 에이전트는 이 클래스를 상속받아 구현됩니다.
"""

from typing import Dict, Any, Optional
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel

from ..core.llm import get_llm
from ..core.memory import MemoryManager

class BaseAgent:
    """에이전트의 공통 동작을 담당하는 베이스 클래스
    
    Attributes:
        llm: LLM 모델 인스턴스
        memory: 메모리 관리자 인스턴스
        prompt_template: 프롬프트 템플릿
        output_parser: 출력 파서
    """
    
    def __init__(
        self,
        memory: MemoryManager,
        prompt_template: str,
        output_model: type[BaseModel],
        llm: Optional[Any] = None
    ):
        """BaseAgent 초기화
        
        Args:
            memory: 메모리 관리자 인스턴스
            prompt_template: 프롬프트 템플릿 문자열
            output_model: 출력을 파싱할 Pydantic 모델
            llm: LLM 모델 인스턴스 (기본값: None)
        """
        self.memory = memory
        self.llm = llm or get_llm()
        self.prompt_template = PromptTemplate(
            template=prompt_template,
            input_variables=self._get_input_variables(prompt_template),
            partial_variables={"format_instructions": PydanticOutputParser(pydantic_object=output_model).get_format_instructions()}
        )
        self.output_parser = PydanticOutputParser(pydantic_object=output_model)
    
    def _get_input_variables(self, template: str) -> list[str]:
        """프롬프트 템플릿에서 입력 변수 목록을 추출
        
        Args:
            template: 프롬프트 템플릿 문자열
            
        Returns:
            list[str]: 입력 변수 목록
        """
        import re
        return re.findall(r'\{([^}]+)\}', template)
    
    def append_conversation(self, role: str, content: Dict[str, Any]) -> None:
        """대화 내용을 메모리에 기록
        
        Args:
            role: 대화 주체 (예: "planner", "developer", "critic")
            content: 기록할 내용
        """
        self.memory.append("conversations", {"role": role, "content": content})
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """에이전트 실행
        
        Args:
            state: 현재 상태
            
        Returns:
            Dict[str, Any]: 업데이트된 상태
            
        Raises:
            NotImplementedError: 하위 클래스에서 구현되지 않은 경우
        """
        raise NotImplementedError("하위 클래스에서 run 메서드를 구현하세요.") 