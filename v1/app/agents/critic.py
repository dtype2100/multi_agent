from typing import Dict, List, TypedDict, Literal
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage

from ..model import get_llm
from ..config import config
from ..memory import Memory

class CriticState(TypedDict):
    """Critic 노드의 상태 타입"""
    goal: str
    current_task: str
    solution: str
    feedback: str
    needs_reflexion: bool
    memory: Memory
    iteration: int

def create_critic_prompt() -> ChatPromptTemplate:
    """Critic 노드의 프롬프트 템플릿을 생성합니다."""
    return ChatPromptTemplate.from_messages([
        SystemMessage(content=config.CRITIC_PROMPT),
        HumanMessage(content="""목표: {goal}

현재 태스크: {current_task}

제시된 해결책:
{solution}

이전 피드백:
{previous_feedback}

위 해결책을 검토하고 다음 중 하나를 선택해주세요:
1. 해결책이 적절하다고 판단되면 "ACCEPT"라고 응답하고 그 이유를 설명해주세요.
2. 해결책이 부적절하다고 판단되면 "REFLEXION"이라고 응답하고 개선이 필요한 부분을 구체적으로 지적해주세요.

응답 형식:
판단: [ACCEPT/REFLEXION]
이유: [상세 설명]""")
    ])

def critic_node(state: Dict) -> Dict:
    """
    Developer의 해결책을 검토하고 피드백을 제공합니다.
    
    Args:
        state: 현재 상태 (goal, current_task, solution, feedback, memory, iteration 포함)
    
    Returns:
        업데이트된 상태
    """
    memory: Memory = state["memory"]
    goal: str = state["goal"]
    current_task: str = state["current_task"]
    solution: str = state.get("solution", "")
    iteration: int = state.get("iteration", 0)

    # DONE 상태이거나 해결책이 없는 경우
    if current_task == "DONE" or not solution:
        return state

    # 이전 피드백 가져오기
    previous_feedback = memory.get_state("feedback", [])
    previous_feedback_text = "\n".join(previous_feedback) if previous_feedback else "없음"

    # LLM을 사용하여 해결책 검토
    llm = get_llm(temperature=0.7)
    prompt = create_critic_prompt()
    
    response = llm.invoke(prompt.format_messages(
        goal=goal,
        current_task=current_task,
        solution=solution,
        previous_feedback=previous_feedback_text
    ))

    # 응답 파싱
    response_text = response.strip()
    lines = response_text.split("\n")
    judgment = ""
    reason = ""
    
    for line in lines:
        if line.startswith("판단:"):
            judgment = line.replace("판단:", "").strip()
        elif line.startswith("이유:"):
            reason = line.replace("이유:", "").strip()

    # 피드백 저장
    feedback = f"판단: {judgment}\n이유: {reason}"
    memory.add_to_history("critic", f"해결책에 대한 피드백을 제공했습니다:\n{feedback}")
    
    # 피드백 목록 업데이트
    previous_feedback.append(feedback)
    memory.update_state("feedback", previous_feedback)

    # Reflexion 필요 여부 결정
    needs_reflexion = judgment.upper() == "REFLEXION"
    
    if not needs_reflexion:
        # 해결책이 수락되면 완료된 태스크 목록에 추가
        completed_tasks = memory.get_state("completed_tasks", [])
        if current_task not in completed_tasks:
            completed_tasks.append(current_task)
            memory.update_state("completed_tasks", completed_tasks)

    return {
        **state,
        "feedback": feedback,
        "needs_reflexion": needs_reflexion,
        "iteration": iteration + 1
    } 