from typing import Dict, Any, List
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

from ..model import get_llm, format_prompt
from ..memory import memory

class SubTask(BaseModel):
    """하위 태스크 모델"""
    task_id: int = Field(description="태스크 ID")
    description: str = Field(description="태스크 설명")
    priority: int = Field(description="우선순위 (1-5, 5가 가장 높음)")
    dependencies: List[int] = Field(description="의존하는 태스크 ID 목록")

class TaskPlan(BaseModel):
    """태스크 계획 모델"""
    tasks: List[SubTask] = Field(description="하위 태스크 목록")
    reasoning: str = Field(description="계획 수립 이유")

PLANNER_PROMPT = """당신은 복잡한 목표를 작은 하위 태스크로 분해하는 플래너입니다.
주어진 목표를 달성하기 위해 필요한 모든 하위 태스크를 생성하고, 각 태스크의 우선순위와 의존성을 결정하세요.

목표: {goal}

이전 상태:
{previous_state}

다음 형식으로 응답하세요:
{format_instructions}

응답:"""

def planner_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    목표를 하위 태스크로 분해하는 플래너 노드
    
    Args:
        state: 현재 상태 (goal, session_id 등 포함)
    
    Returns:
        Dict[str, Any]: 업데이트된 상태
    """
    # 출력 파서 초기화
    parser = PydanticOutputParser(pydantic_object=TaskPlan)
    
    # 프롬프트 템플릿 생성
    prompt = PromptTemplate(
        template=PLANNER_PROMPT,
        input_variables=["goal", "previous_state"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    # 이전 상태 로드
    session_id = state.get("session_id")
    previous_state = memory.get_session(session_id) if session_id else {}
    
    # 프롬프트 생성
    formatted_prompt = prompt.format(
        goal=state["goal"],
        previous_state=str(previous_state)
    )
    
    # LLM 호출
    llm = get_llm(temperature=0.7)
    response = llm(formatted_prompt)
    
    # 응답 파싱
    try:
        task_plan = parser.parse(response)
        
        # 상태 업데이트
        state["task_plan"] = task_plan.dict()
        state["current_task_index"] = 0
        
        # 메모리에 저장
        if session_id:
            memory.update_session(session_id, {
                "task_plan": task_plan.dict(),
                "current_task_index": 0
            })
        
        return state
    except Exception as e:
        state["error"] = f"플래너 노드 오류: {str(e)}"
        return state 