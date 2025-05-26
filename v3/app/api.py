from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .agent_graph import run_graph
from .memory import load_memory

# 라우터 초기화
router = APIRouter(prefix="/api/v1")

class AgentRequest(BaseModel):
    """에이전트 실행 요청 모델"""
    goal: str

class AgentResponse(BaseModel):
    """에이전트 실행 응답 모델"""
    result: Dict[str, Any]
    memory: Dict[str, Any]

@router.post("/run-agent", response_model=AgentResponse)
async def run_agent(request: AgentRequest) -> AgentResponse:
    """에이전트를 실행하는 엔드포인트
    
    Args:
        request (AgentRequest): 실행 요청
        
    Returns:
        AgentResponse: 실행 결과
        
    Raises:
        HTTPException: 실행 중 오류 발생 시
    """
    try:
        # 에이전트 실행
        result = run_graph(request.goal)
        
        # 메모리 로드
        memory = load_memory()
        
        return AgentResponse(
            result=result,
            memory=memory
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"에이전트 실행 중 오류 발생: {str(e)}"
        ) 