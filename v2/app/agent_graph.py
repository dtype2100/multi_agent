from typing import Dict, Any, Annotated, TypedDict
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
from langchain.tools import tool

from .agents.planner import planner_node
from .agents.developer import developer_node
from .agents.critic import critic_node
from .config import config

class AgentState(TypedDict):
    """에이전트 상태 타입"""
    goal: str
    session_id: str
    task_plan: Dict[str, Any]
    current_task_index: int
    task_results: List[Dict[str, Any]]
    feedback: List[Dict[str, Any]]
    needs_retry: bool
    retry_reason: str
    improvement_suggestions: List[str]
    error: str

def should_continue(state: AgentState) -> str:
    """
    다음 단계를 결정하는 조건 함수
    
    Args:
        state: 현재 상태
    
    Returns:
        str: 다음 노드 이름
    """
    if state.get("error"):
        return "end"
    
    if state.get("needs_retry"):
        return "developer"
    
    task_plan = state.get("task_plan", {})
    current_index = state.get("current_task_index", 0)
    tasks = task_plan.get("tasks", [])
    
    if current_index >= len(tasks):
        return "end"
    
    return "critic"

def create_agent_graph() -> StateGraph:
    """
    에이전트 그래프를 생성합니다.
    
    Returns:
        StateGraph: 구성된 그래프
    """
    # 그래프 생성
    workflow = StateGraph(AgentState)
    
    # 노드 추가
    workflow.add_node("planner", planner_node)
    workflow.add_node("developer", developer_node)
    workflow.add_node("critic", critic_node)
    
    # 엣지 추가
    workflow.add_edge("planner", "developer")
    workflow.add_edge("developer", "critic")
    workflow.add_conditional_edges(
        "critic",
        should_continue,
        {
            "developer": "developer",
            "end": END
        }
    )
    
    # 시작 노드 설정
    workflow.set_entry_point("planner")
    
    return workflow

def run_graph(goal: str, session_id: str = None) -> Dict[str, Any]:
    """
    에이전트 그래프를 실행합니다.
    
    Args:
        goal: 실행할 목표
        session_id: 세션 ID (선택사항)
    
    Returns:
        Dict[str, Any]: 최종 상태
    """
    # 초기 상태 설정
    initial_state = {
        "goal": goal,
        "session_id": session_id,
        "task_plan": {},
        "current_task_index": 0,
        "task_results": [],
        "feedback": [],
        "needs_retry": False,
        "retry_reason": "",
        "improvement_suggestions": [],
        "error": ""
    }
    
    # 그래프 생성 및 실행
    graph = create_agent_graph()
    app = graph.compile()
    
    # 실행
    final_state = app.invoke(initial_state)
    return final_state 