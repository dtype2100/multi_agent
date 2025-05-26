from typing import Dict, List, TypedDict, Annotated
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage

from ..model import get_llm
from ..config import config
from ..memory import Memory

class PlannerState(TypedDict):
    """Planner 노드의 상태 타입"""
    goal: str
    tasks: List[str]
    current_task: str
    memory: Memory
    iteration: int

def create_planner_prompt() -> ChatPromptTemplate:
    """Planner 노드의 프롬프트 템플릿을 생성합니다."""
    return ChatPromptTemplate.from_messages([
        SystemMessage(content=config.PLANNER_PROMPT),
        HumanMessage(content="""목표: {goal}

현재까지 완료된 태스크:
{completed_tasks}

남은 태스크:
{remaining_tasks}

다음 태스크를 선택하고 실행 계획을 세워주세요.""")
    ])

def planner_node(state: Dict) -> Dict:
    """
    목표를 하위 태스크로 분해하고 다음 실행할 태스크를 선택합니다.
    
    Args:
        state: 현재 상태 (goal, tasks, current_task, memory, iteration 포함)
    
    Returns:
        업데이트된 상태
    """
    memory: Memory = state["memory"]
    goal: str = state["goal"]
    tasks: List[str] = state.get("tasks", [])
    current_task: str = state.get("current_task", "")
    iteration: int = state.get("iteration", 0)

    # 첫 번째 반복에서는 태스크 분해
    if iteration == 0:
        llm = get_llm(temperature=0.7)
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=config.PLANNER_PROMPT),
            HumanMessage(content=f"다음 목표를 달성하기 위한 구체적인 단계들을 나열해주세요:\n\n{goal}")
        ])
        
        response = llm.invoke(prompt.format_messages())
        tasks = [task.strip() for task in response.split("\n") if task.strip()]
        
        # 메모리에 태스크 목록 저장
        memory.update_state("tasks", tasks)
        memory.add_to_history("planner", f"목표를 {len(tasks)}개의 태스크로 분해했습니다:\n" + "\n".join(tasks))
    
    # 다음 실행할 태스크 선택
    completed_tasks = memory.get_state("completed_tasks", [])
    remaining_tasks = [task for task in tasks if task not in completed_tasks]
    
    if remaining_tasks:
        current_task = remaining_tasks[0]
        memory.add_to_history("planner", f"다음 태스크를 선택했습니다: {current_task}")
    else:
        current_task = "DONE"
        memory.add_to_history("planner", "모든 태스크가 완료되었습니다.")

    return {
        **state,
        "tasks": tasks,
        "current_task": current_task,
        "iteration": iteration + 1
    } 