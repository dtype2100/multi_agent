"""개발자 에이전트 모듈

이 모듈은 태스크에 맞는 코드를 생성하는 DeveloperAgent 클래스를 정의합니다.
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field
from langchain.output_parsers import OutputParserException # Import for specific exception
import requests # Assuming LLM might use requests, for RequestException

from .base import BaseAgent
from ..core.memory import MemoryManager

class CodeSolution(BaseModel):
    """코드 솔루션을 정의하는 모델"""
    code: str = Field(description="생성된 코드")
    explanation: str = Field(description="코드에 대한 설명")
    test_cases: List[str] = Field(description="테스트 케이스 목록")

DEVELOPER_PROMPT = """당신은 주어진 태스크를 해결하는 코드를 생성하는 개발자입니다.

현재 태스크: {task_description}

이전 태스크들의 결과:
{previous_results}

위 태스크를 해결하기 위한 코드를 생성해주세요.
코드는 다음 정보를 포함해야 합니다:
- code: 실제 구현 코드
- explanation: 코드에 대한 자세한 설명
- test_cases: 코드를 검증하기 위한 테스트 케이스 목록

{format_instructions}

코드 솔루션:"""

class DeveloperAgent(BaseAgent):
    """태스크에 맞는 코드를 생성하는 에이전트"""
    
    def __init__(self, memory: MemoryManager):
        """DeveloperAgent 초기화
        
        Args:
            memory: 메모리 관리자 인스턴스
        """
        super().__init__(
            memory=memory,
            prompt_template=DEVELOPER_PROMPT,
            output_model=CodeSolution
        )
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """태스크에 맞는 코드 생성
        
        Args:
            state: 현재 상태
            
        Returns:
            Dict[str, Any]: 업데이트된 상태
        """
        # 현재 태스크 가져오기
        current_task = state["tasks"][state["current_task_index"]]
        
        # 이전 태스크들의 결과 수집 (Refactored to BaseAgent)
        previous_results_str = self._compile_previous_results(state)
        
        current_solution_dict = {}
        try:
            # LLM 호출
            response_content = self.llm(self.prompt_template.format(
                task_description=current_task.description,
                previous_results=previous_results_str
            ))
            
            # 응답 파싱
            solution = self.output_parser.parse(response_content)
            current_solution_dict = solution.dict()

        except OutputParserException as e:
            error_message = f"DeveloperAgent: Error parsing LLM response for task {current_task.task_id}. Details: {str(e)}"
            print(error_message)
            current_solution_dict = {
                "code": "# ERROR: Could not parse LLM response.",
                "explanation": error_message,
                "test_cases": []
            }
        except requests.exceptions.RequestException as e: # More specific network error
            error_message = f"DeveloperAgent: Network error during LLM call for task {current_task.task_id}. Details: {str(e)}"
            print(error_message)
            current_solution_dict = {
                "code": "# ERROR: Network error during LLM call.",
                "explanation": error_message,
                "test_cases": []
            }
        except Exception as e: # Catch any other unexpected errors
            error_message = f"DeveloperAgent: An unexpected error occurred for task {current_task.task_id}. Details: {str(e)}"
            print(error_message)
            current_solution_dict = {
                "code": "# ERROR: An unexpected error occurred.",
                "explanation": error_message,
                "test_cases": []
            }
        
        # 메모리에 결과 저장 (even if it's an error response)
        self.append_conversation("developer", {
            "task_id": current_task.task_id,
            "content": current_solution_dict # Log the error or success
        })
        
        # 상태 업데이트
        if "results" not in state:
            state["results"] = []
        
        # Pad the list with None if it's shorter than current_task_index + 1
        while len(state["results"]) <= state["current_task_index"]:
            state["results"].append(None)
        
        # Overwrite or set the result for the current task index
        state["results"][state["current_task_index"]] = current_solution_dict
        
        return state 