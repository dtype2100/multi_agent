from typing import Dict, Any, List, Optional
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field

from ..model import get_llm, format_prompt
from ..memory import memory
from ..config import config

class Feedback(BaseModel):
    """피드백 모델"""
    task_id: int = Field(description="태스크 ID")
    score: int = Field(description="평가 점수 (1-5, 5가 가장 높음)")
    feedback: str = Field(description="상세 피드백")
    needs_improvement: bool = Field(description="개선 필요 여부")
    improvement_suggestions: List[str] = Field(description="개선 제안 목록")

CRITIC_PROMPT = """당신은 태스크 실행 결과를 검토하고 피드백을 제공하는 비평가입니다.
주어진 태스크와 결과를 분석하고, 필요한 경우 개선점을 제시하세요.

현재 태스크:
{current_task}

실행 결과:
{task_result}

전체 목표:
{goal}

이전 피드백:
{previous_feedback}

다음 형식으로 응답하세요:
{format_instructions}

응답:"""

def critic_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    태스크 결과를 검토하고 피드백을 제공하는 비평가 노드
    
    Args:
        state: 현재 상태 (task_plan, task_results 등 포함)
    
    Returns:
        Dict[str, Any]: 업데이트된 상태
    """
    # 현재 태스크와 결과 가져오기
    task_plan = state.get("task_plan", {})
    current_index = state.get("current_task_index", 0) - 1  # 마지막 실행된 태스크
    tasks = task_plan.get("tasks", [])
    task_results = state.get("task_results", [])
    
    if current_index < 0 or current_index >= len(tasks):
        state["error"] = "검토할 태스크가 없습니다."
        return state
    
    current_task = tasks[current_index]
    current_result = task_results[current_index] if task_results else None
    
    if not current_result:
        state["error"] = "태스크 결과가 없습니다."
        return state
    
    # 이전 피드백 로드
    session_id = state.get("session_id")
    previous_feedback = []
    if session_id:
        session_data = memory.get_session(session_id)
        previous_feedback = session_data.get("feedback", [])
    
    # 프롬프트 생성
    prompt = PromptTemplate(
        template=CRITIC_PROMPT,
        input_variables=["current_task", "task_result", "goal", "previous_feedback"],
        partial_variables={"format_instructions": Feedback.schema_json()}
    )
    
    formatted_prompt = prompt.format(
        current_task=current_task,
        task_result=current_result,
        goal=state["goal"],
        previous_feedback=str(previous_feedback)
    )
    
    # LLM 호출
    llm = get_llm(temperature=0.7)
    response = llm(formatted_prompt)
    
    try:
        # 응답 파싱
        feedback = Feedback.parse_raw(response)
        
        # 상태 업데이트
        if "feedback" not in state:
            state["feedback"] = []
        state["feedback"].append(feedback.dict())
        
        # Reflexion 루프 처리
        if feedback.needs_improvement and config.REFLEXION_ENABLED:
            state["needs_retry"] = True
            state["retry_reason"] = feedback.feedback
            state["improvement_suggestions"] = feedback.improvement_suggestions
            state["current_task_index"] = current_index  # 이전 태스크로 돌아가기
        
        # 메모리에 저장
        if session_id:
            memory.update_session(session_id, {
                "feedback": state["feedback"],
                "needs_retry": state.get("needs_retry", False),
                "retry_reason": state.get("retry_reason", ""),
                "improvement_suggestions": state.get("improvement_suggestions", [])
            })
        
        return state
    except Exception as e:
        state["error"] = f"비평가 노드 오류: {str(e)}"
        return state 