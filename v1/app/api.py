from typing import Dict, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid

from .agent_graph import run_graph
from .config import config

app = FastAPI(
    title="AGI-lite API",
    description="LangGraph 기반 멀티에이전트 시스템 API",
    version="1.0.0"
)

class AgentRequest(BaseModel):
    """에이전트 실행 요청 모델"""
    goal: str
    session_id: Optional[str] = None

class AgentResponse(BaseModel):
    """에이전트 실행 응답 모델"""
    session_id: str
    final_state: Dict
    history: list

@app.post("/run-agent", response_model=AgentResponse)
async def run_agent(request: AgentRequest) -> AgentResponse:
    """
    에이전트 시스템을 실행합니다.
    
    Args:
        request: 에이전트 실행 요청 (목표와 세션 ID)
    
    Returns:
        AgentResponse: 실행 결과
    """
    try:
        # 세션 ID 생성 또는 사용
        session_id = request.session_id or str(uuid.uuid4())
        
        # 에이전트 그래프 실행
        final_state = run_graph(request.goal, session_id)
        
        # 메모리에서 히스토리 가져오기
        memory = final_state["memory"]
        history = memory.get_history()
        
        return AgentResponse(
            session_id=session_id,
            final_state=final_state,
            history=history
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"에이전트 실행 중 오류가 발생했습니다: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """API 서버 상태 확인"""
    return {"status": "healthy"} 