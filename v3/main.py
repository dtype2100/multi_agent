from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router
from app.config import config

# FastAPI 앱 초기화
app = FastAPI(
    title="AGI-lite 멀티에이전트 시스템",
    description="LangGraph 기반의 멀티에이전트 시스템 API",
    version="1.0.0"
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(router)

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "AGI-lite 멀티에이전트 시스템 API",
        "version": "1.0.0",
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    
    # 서버 실행
    uvicorn.run(
        "main:app",
        host=config.api_host,
        port=config.api_port,
        reload=True
    ) 