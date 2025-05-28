"""비평가 에이전트 모듈

이 모듈은 생성된 코드를 평가하는 CriticAgent 클래스를 정의합니다.
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field
from langchain.output_parsers import OutputParserException # Import for specific exception
import requests # Assuming LLM might use requests, for RequestException

from .base import BaseAgent
from ..core.memory import MemoryManager
from ..core.config import config

class CodeEvaluation(BaseModel):
    """코드 평가 결과를 정의하는 모델"""
    score: float = Field(description="평가 점수 (0-1)")
    feedback: str = Field(description="코드에 대한 피드백")
    improvements: List[str] = Field(description="개선 사항 목록")
    is_success: bool = Field(description="성공 여부")

CRITIC_PROMPT = """당신은 생성된 코드를 평가하고 피드백을 제공하는 비평가입니다.

현재 태스크: {task_description}

생성된 코드:
{code}

코드 설명:
{explanation}

테스트 케이스:
{test_cases}

이전 태스크들의 결과:
{previous_results}

위 코드를 평가하고 다음 정보를 제공해주세요:
- score: 코드의 품질 점수 (0-1)
- feedback: 코드에 대한 자세한 피드백
- improvements: 개선이 필요한 부분들의 목록
- is_success: 태스크 성공 여부 (score >= {success_threshold}일 때 True)

{format_instructions}

평가 결과:"""

class CriticAgent(BaseAgent):
    """생성된 코드를 평가하는 에이전트"""
    
    def __init__(self, memory: MemoryManager):
        """CriticAgent 초기화
        
        Args:
            memory: 메모리 관리자 인스턴스
        """
        super().__init__(
            memory=memory,
            prompt_template=CRITIC_PROMPT,
            output_model=CodeEvaluation
        )
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """생성된 코드 평가
        
        Args:
            state: 현재 상태
            
        Returns:
            Dict[str, Any]: 업데이트된 상태
        """
        # 현재 태스크와 결과 가져오기
        current_task = state["tasks"][state["current_task_index"]]
        current_result = state["results"][state["current_task_index"]]
        
        # 이전 태스크들의 결과 수집 (Refactored to BaseAgent)
        previous_results_str = self._compile_previous_results(state)
        
        evaluation_dict = {}
        try:
            # LLM 호출
            response_content = self.llm(self.prompt_template.format(
                task_description=current_task.description,
                code=current_result.get("code", "# CODE MISSING OR ERROR IN PREVIOUS STEP"), # Handle potential missing code
                explanation=current_result.get("explanation", "# EXPLANATION MISSING OR ERROR IN PREVIOUS STEP"),
                test_cases="\n".join(current_result.get("test_cases", [])),
                previous_results=previous_results_str,
                success_threshold=config.success_threshold
            ))
            
            # 응답 파싱
            evaluation = self.output_parser.parse(response_content)
            evaluation_dict = evaluation.dict()

        except OutputParserException as e:
            error_message = f"CriticAgent: Error parsing LLM response for task {current_task.task_id}. Details: {str(e)}"
            print(error_message)
            evaluation_dict = {
                "score": 0.0,
                "feedback": error_message,
                "improvements": ["Resolve the parsing error in Critic agent's LLM response."],
                "is_success": False
            }
        except requests.exceptions.RequestException as e: # More specific network error
            error_message = f"CriticAgent: Network error during LLM call for task {current_task.task_id}. Details: {str(e)}"
            print(error_message)
            evaluation_dict = {
                "score": 0.0,
                "feedback": error_message,
                "improvements": ["Resolve the network error in Critic agent."],
                "is_success": False
            }
        except Exception as e: # Catch any other unexpected errors
            error_message = f"CriticAgent: An unexpected error occurred for task {current_task.task_id}. Details: {str(e)}"
            print(error_message)
            evaluation_dict = {
                "score": 0.0,
                "feedback": error_message,
                "improvements": ["Resolve the unexpected error in Critic agent."],
                "is_success": False
            }

        # 메모리에 평가 결과 저장 (even if it's an error response)
        self.append_conversation("critic", {
            "task_id": current_task.task_id,
            "content": evaluation_dict
        })
        
        # 상태 업데이트
        if "evaluations" not in state:
            state["evaluations"] = []
        state["evaluations"].append(evaluation_dict)
        
        # 반복 횟수 업데이트 (always increment iterations as an attempt was made)
        state["iterations"] = state.get("iterations", 0) + 1
        
        return state 