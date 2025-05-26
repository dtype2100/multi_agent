from typing import Dict, List, TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from .agents.planner import planner_node
from .agents.developer import developer_node
from .agents.critic import critic_node
from .memory import Memory, get_memory
from .config import config

class AgentState(TypedDict):
    """에이전트 그래프의 상태 타입"""
    goal: str
    tasks: List[str]
    current_task: str
    solution: str
    feedback: str
    needs_reflexion: bool
    memory: Memory
    iteration: int

def should_continue(state: Dict) -> Literal["planner", "developer", "critic", "end"]:
    """
    다음 실행할 노드를 결정합니다.
    
    Args:
        state: 현재 상태
    
    Returns:
        다음 실행할 노드의 이름
    """
    current_task = state.get("current_task", "")
    needs_reflexion = state.get("needs_reflexion", False)
    iteration = state.get("iteration", 0)

    # 최대 반복 횟수 초과
    if iteration >= config.MAX_ITERATIONS:
        return "end"

    # DONE 상태
    if current_task == "DONE":
        return "end"

    # Reflexion이 필요한 경우 Developer로 돌아감
    if needs_reflexion:
        return "developer"

    # 기본 플로우: Planner -> Developer -> Critic
    if "solution" not in state:
        return "developer"
    if "feedback" not in state:
        return "critic"
    
    return "planner"

def create_agent_graph() -> StateGraph:
    """
    에이전트 그래프를 생성합니다.
    
    Returns:
        StateGraph: 구성된 에이전트 그래프
    """
    # 그래프 생성
    workflow = StateGraph(AgentState)

    # 노드 추가
    workflow.add_node("planner", planner_node)
    workflow.add_node("developer", developer_node)
    workflow.add_node("critic", critic_node)

    # 엣지 추가
    workflow.add_edge("planner", should_continue)
    workflow.add_edge("developer", should_continue)
    workflow.add_edge("critic", should_continue)

    # 종료 조건 설정
    workflow.set_entry_point("planner")
    workflow.add_terminal_node("end")

    return workflow

def run_graph(goal: str, session_id: str) -> Dict:
    """
    에이전트 그래프를 실행합니다.
    
    Args:
        goal: 달성할 목표
        session_id: 세션 ID
    
    Returns:
        Dict: 최종 상태
    """
    # 메모리 초기화
    memory = get_memory(session_id)
    memory.clear_state()
    memory.clear_history()

    # 초기 상태 설정
    initial_state = {
        "goal": goal,
        "tasks": [],
        "current_task": "",
        "solution": "",
        "feedback": "",
        "needs_reflexion": False,
        "memory": memory,
        "iteration": 0
    }

    # 그래프 생성 및 실행
    graph = create_agent_graph()
    final_state = graph.invoke(initial_state)

    return final_state 