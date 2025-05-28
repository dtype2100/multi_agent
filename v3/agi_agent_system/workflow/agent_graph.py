"""에이전트 실행 흐름 관리 모듈

이 모듈은 에이전트들의 실행 흐름을 관리합니다.
"""

from typing import Dict, Any, Callable, TypedDict, List
from langgraph.graph import Graph, StateGraph
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel

from ..agents import PlannerAgent, DeveloperAgent, CriticAgent
from ..core.llm import get_llm
from ..core.memory import MemoryManager
from ..core.config import config

class WorkflowState(TypedDict):
    """워크플로우 상태"""
    goal: str
    tasks: List[Any]
    current_task_index: int
    iterations: int
    results: List[Dict[str, Any]]
    evaluations: List[Dict[str, Any]]

def should_continue(state: WorkflowState) -> str:
    """다음 단계 결정
    
    Args:
        state: 현재 상태
        
    Returns:
        str: 다음 단계 ("developer" 또는 "end")
    """
    current_task = state["tasks"][state["current_task_index"]]
    current_evaluation = state["evaluations"][-1]
    
    # 성공했거나 최대 반복 횟수에 도달한 경우
    if current_evaluation["is_success"] or state["iterations"] >= config.max_iterations:
        # 다음 태스크로 이동
        state["current_task_index"] += 1
        state["iterations"] = 0
        
        # 모든 태스크가 완료되었는지 확인
        if state["current_task_index"] >= len(state["tasks"]):
            return "end"
        return "developer"
    
    # 실패한 경우 개발자에게 다시 요청
    return "developer"

def end_workflow(state: WorkflowState) -> WorkflowState:
    """워크플로우 종료
    
    Args:
        state: 현재 상태
        
    Returns:
        WorkflowState: 최종 상태
    """
    return state

def run_workflow(goal: str, memory: MemoryManager) -> Dict[str, Any]:
    """에이전트 실행 흐름 전체를 관리
    
    Args:
        goal: 목표
        memory: 메모리 관리자 인스턴스
        
    Returns:
        Dict[str, Any]: 최종 상태
    """
    # 에이전트 초기화
    planner = PlannerAgent(memory)
    developer = DeveloperAgent(memory)
    critic = CriticAgent(memory)
    
    # 그래프 노드 정의
    workflow = StateGraph(WorkflowState)
    
    # 노드 추가
    workflow.add_node("planner", planner.run)
    workflow.add_node("developer", developer.run)
    workflow.add_node("critic", critic.run)
    workflow.add_node("end", end_workflow)
    
    # 엣지 추가
    workflow.add_edge("planner", "developer")
    workflow.add_edge("developer", "critic")
    workflow.add_conditional_edges(
        "critic",
        should_continue,
        {
            "developer": "developer",
            "end": "end"
        }
    )
    
    # 시작 노드 설정
    workflow.set_entry_point("planner")
    
    # 그래프 컴파일
    app = workflow.compile()
    
    # 초기 상태 설정
    initial_state = {
        "goal": goal,
        "tasks": [],
        "current_task_index": 0,
        "iterations": 0,
        "results": [],
        "evaluations": []
    }
    
    # 워크플로우 실행
    final_state = app.invoke(initial_state)
    
    return final_state 