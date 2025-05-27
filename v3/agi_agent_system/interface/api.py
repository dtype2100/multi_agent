"""API 인터페이스 모듈

이 모듈은 시스템의 API 인터페이스를 제공합니다.
"""

from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from ..core.memory import MemoryManager
from ..workflow.agent_graph import run_workflow

app = FastAPI(title="AGI 에이전트 시스템 API")

class GoalRequest(BaseModel):
    """목표 요청 모델"""
    goal: str
    session_id: Optional[str] = None
    memory_dir: str = "memory"

class TaskResult(BaseModel):
    """태스크 결과 모델"""
    task_id: int
    description: str
    code: str
    explanation: str
    score: float
    feedback: str
    improvements: list[str]

class WorkflowResponse(BaseModel):
    """워크플로우 응답 모델"""
    session_id: str
    results: list[TaskResult]

@app.post("/run", response_model=WorkflowResponse)
async def run_workflow_api(request: GoalRequest) -> Dict[str, Any]:
    """워크플로우 실행 API
    
    Args:
        request: 목표 요청
        
    Returns:
        Dict[str, Any]: 워크플로우 실행 결과
        
    Raises:
        HTTPException: 실행 중 오류 발생 시
    """
    try:
        # 메모리 관리자 초기화
        memory = MemoryManager(
            session_id=request.session_id,
            memory_dir=request.memory_dir
        )
        
        # 워크플로우 실행
        final_state = run_workflow(request.goal, memory)
        
        # 결과 변환
        results = []
        for task, result, evaluation in zip(
            final_state["tasks"],
            final_state["results"],
            final_state["evaluations"]
        ):
            results.append(TaskResult(
                task_id=task.task_id,
                description=task.description,
                code=result["code"],
                explanation=result["explanation"],
                score=evaluation["score"],
                feedback=evaluation["feedback"],
                improvements=evaluation["improvements"]
            ))
        
        return WorkflowResponse(
            session_id=memory.session_id,
            results=results
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def run_api(host: str = "0.0.0.0", port: int = 8000) -> None:
    """API 서버 실행
    
    Args:
        host: 호스트 주소 (기본값: "0.0.0.0")
        port: 포트 번호 (기본값: 8000)
    """
    import uvicorn
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    run_api() 