from typing import Dict, List, TypedDict
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage

from ..model import get_llm
from ..config import config
from ..memory import Memory

class DeveloperState(TypedDict):
    """Developer 노드의 상태 타입"""
    goal: str
    current_task: str
    solution: str
    memory: Memory
    iteration: int

def create_developer_prompt() -> ChatPromptTemplate:
    """Developer 노드의 프롬프트 템플릿을 생성합니다."""
    return ChatPromptTemplate.from_messages([
        SystemMessage(content=config.DEVELOPER_PROMPT),
        HumanMessage(content="""목표: {goal}

현재 태스크: {current_task}

이전 해결책:
{previous_solutions}

위 태스크를 해결하기 위한 구체적인 해결책을 제시해주세요.""")
    ])

def developer_node(state: Dict) -> Dict:
    """
    현재 태스크를 실행하고 해결책을 제시합니다.
    
    Args:
        state: 현재 상태 (goal, current_task, solution, memory, iteration 포함)
    
    Returns:
        업데이트된 상태
    """
    memory: Memory = state["memory"]
    goal: str = state["goal"]
    current_task: str = state["current_task"]
    iteration: int = state.get("iteration", 0)

    # DONE 상태이거나 태스크가 없는 경우
    if current_task == "DONE" or not current_task:
        return state

    # 이전 해결책 가져오기
    previous_solutions = memory.get_state("solutions", [])
    previous_solutions_text = "\n".join(previous_solutions) if previous_solutions else "없음"

    # LLM을 사용하여 해결책 생성
    llm = get_llm(temperature=0.7)
    prompt = create_developer_prompt()
    
    response = llm.invoke(prompt.format_messages(
        goal=goal,
        current_task=current_task,
        previous_solutions=previous_solutions_text
    ))

    # 해결책 저장
    solution = response.strip()
    memory.add_to_history("developer", f"태스크 '{current_task}'에 대한 해결책을 제시했습니다:\n{solution}")
    
    # 해결책 목록 업데이트
    previous_solutions.append(solution)
    memory.update_state("solutions", previous_solutions)

    return {
        **state,
        "solution": solution,
        "iteration": iteration + 1
    } 