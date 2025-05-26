from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import uuid

from .agent_graph import run_graph
from .memory import memory

router = APIRouter()

class AgentRequest(BaseModel):
    """에이전트 실행 요청 모델"""
    goal: str
    session_id: Optional[str] = None

class AgentResponse(BaseModel):
    """에이전트 실행 응답 모델"""
    session_id: str
    status: str
    result: Dict[str, Any]
    error: Optional[str] = None

@router.post("/run-agent", response_model=AgentResponse)
async def run_agent(request: AgentRequest) -> AgentResponse:
    """
    에이전트를 실행하는 API 엔드포인트
    
    Args:
        request: 에이전트 실행 요청
    
    Returns:
        AgentResponse: 실행 결과
    """
    try:
        # 세션 ID 생성 또는 사용
        session_id = request.session_id or str(uuid.uuid4())
        
        # 에이전트 실행
        result = run_graph(
            goal=request.goal,
            session_id=session_id
        )
        
        # 에러 처리
        if result.get("error"):
            raise HTTPException(
                status_code=500,
                detail=result["error"]
            )
        
        # 응답 생성
        return AgentResponse(
            session_id=session_id,
            status="success",
            result=result
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/session/{session_id}", response_model=AgentResponse)
async def get_session(session_id: str) -> AgentResponse:
    """
    세션 정보를 조회하는 API 엔드포인트
    
    Args:
        session_id: 세션 ID
    
    Returns:
        AgentResponse: 세션 정보
    """
    try:
        # 세션 데이터 조회
        session_data = memory.get_session(session_id)
        
        if not session_data:
            raise HTTPException(
                status_code=404,
                detail="세션을 찾을 수 없습니다."
            )
        
        # 응답 생성
        return AgentResponse(
            session_id=session_id,
            status="success",
            result=session_data
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """
    세션을 삭제하는 API 엔드포인트
    
    Args:
        session_id: 세션 ID
    """
    try:
        memory.delete_session(session_id)
        return {"status": "success", "message": "세션이 삭제되었습니다."}
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        ) 