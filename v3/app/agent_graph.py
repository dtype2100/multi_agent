from typing import Dict, Any, Annotated, TypedDict
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from .agents.planner import planner_node
from .agents.developer import developer_node
from .agents.critic import critic_node
from .config import config
from .memory import load_memory, save_memory

class AgentState(TypedDict):
    """에이전트 상태를 정의하는 타입"""
    goal: str
    tasks: list[Dict[str, Any]]
    current_task_index: int
    results: list[Dict[str, Any]]
    evaluations: list[Dict[str, Any]]
    iterations: int

def should_continue(state: AgentState) -> str:
    """다음 단계를 결정하는 조건 함수
    
    Args:
        state (AgentState): 현재 상태
        
    Returns:
        str: 다음 단계 ("developer", "critic", "end")
    """
    # 최대 반복 횟수 초과
    if state["iterations"] >= config.max_iterations:
        return "end"
    
    # 현재 태스크의 평가 결과
    current_eval = state["evaluations"][-1]
    
    # 성공한 경우
    if current_eval["is_success"]:
        # 다음 태스크가 있는지 확인
        if state["current_task_index"] + 1 < len(state["tasks"]):
            state["current_task_index"] += 1
            return "developer"
        return "end"
    
    # 실패한 경우 developer에게 피드백 전달
    return "developer"

def create_graph() -> StateGraph:
    """LangGraph 상태 흐름을 구성하는 함수
    
    Returns:
        StateGraph: 구성된 그래프
    """
    # 그래프 초기화
    workflow = StateGraph(AgentState)
    
    # 노드 추가
    workflow.add_node("planner", planner_node)
    workflow.add_node("developer", developer_node)
    workflow.add_node("critic", critic_node)
    
    # 엣지 추가
    workflow.add_edge("planner", "developer")
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

def run_graph(goal: str) -> Dict[str, Any]:
    """에이전트 그래프를 실행하는 함수
    
    Args:
        goal (str): 사용자 목표
        
    Returns:
        Dict[str, Any]: 최종 실행 결과
    """
    # 메모리 초기화
    memory = load_memory()
    memory["iterations"] = 0
    save_memory(memory)
    
    # 그래프 생성 및 컴파일
    graph = create_graph()
    executable = graph.compile()
    
    # 초기 상태 설정
    initial_state = {
        "goal": goal,
        "tasks": [],
        "current_task_index": 0,
        "results": [],
        "evaluations": [],
        "iterations": 0
    }
    
    # 그래프 실행
    result = executable.invoke(initial_state)
    
    return result 