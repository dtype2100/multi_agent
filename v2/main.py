import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router
from app.config import config

# FastAPI 앱 생성
app = FastAPI(
    title="AGI-lite API",
    description="LangGraph 기반 멀티에이전트 시스템 API",
    version="1.0.0"
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 운영 환경에서는 특정 도메인만 허용하도록 수정
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    """API 루트 엔드포인트"""
    return {
        "message": "AGI-lite API 서버가 실행 중입니다.",
        "version": "1.0.0",
        "docs_url": "/docs"
    }

def main():
    """FastAPI 서버 실행"""
    uvicorn.run(
        "main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=True  # 개발 환경에서 코드 변경 시 자동 재시작
    )

if __name__ == "__main__":
    main() 