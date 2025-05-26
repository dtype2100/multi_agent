from typing import Dict, Any, List
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field

from ..model import get_llm, format_prompt
from ..memory import memory

class TaskResult(BaseModel):
    """태스크 실행 결과 모델"""
    task_id: int = Field(description="태스크 ID")
    status: str = Field(description="실행 상태 (success/failure)")
    output: str = Field(description="실행 결과")
    error: str = Field(description="에러 메시지 (실패 시)")

DEVELOPER_PROMPT = """당신은 주어진 태스크를 실행하고 결과를 생성하는 개발자입니다.
태스크를 수행하고 상세한 결과를 생성하세요.

현재 태스크:
{current_task}

이전 태스크 결과:
{previous_results}

전체 목표:
{goal}

다음 형식으로 응답하세요:
{format_instructions}

응답:"""

def developer_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    하위 태스크를 실행하고 결과를 생성하는 개발자 노드
    
    Args:
        state: 현재 상태 (task_plan, current_task_index 등 포함)
    
    Returns:
        Dict[str, Any]: 업데이트된 상태
    """
    # 현재 태스크 가져오기
    task_plan = state.get("task_plan", {})
    current_index = state.get("current_task_index", 0)
    tasks = task_plan.get("tasks", [])
    
    if current_index >= len(tasks):
        state["error"] = "모든 태스크가 완료되었습니다."
        return state
    
    current_task = tasks[current_index]
    
    # 이전 결과 로드
    session_id = state.get("session_id")
    previous_results = []
    if session_id:
        session_data = memory.get_session(session_id)
        previous_results = session_data.get("task_results", [])
    
    # 프롬프트 생성
    prompt = PromptTemplate(
        template=DEVELOPER_PROMPT,
        input_variables=["current_task", "previous_results", "goal"],
        partial_variables={"format_instructions": TaskResult.schema_json()}
    )
    
    formatted_prompt = prompt.format(
        current_task=current_task,
        previous_results=str(previous_results),
        goal=state["goal"]
    )
    
    # LLM 호출
    llm = get_llm(temperature=0.7)
    response = llm(formatted_prompt)
    
    try:
        # 응답 파싱
        task_result = TaskResult.parse_raw(response)
        
        # 상태 업데이트
        if "task_results" not in state:
            state["task_results"] = []
        state["task_results"].append(task_result.dict())
        state["current_task_index"] = current_index + 1
        
        # 메모리에 저장
        if session_id:
            memory.update_session(session_id, {
                "task_results": state["task_results"],
                "current_task_index": state["current_task_index"]
            })
        
        return state
    except Exception as e:
        state["error"] = f"개발자 노드 오류: {str(e)}"
        return state 