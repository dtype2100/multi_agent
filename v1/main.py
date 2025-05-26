import uvicorn
from app.api import app
from app.config import config

def main():
    """FastAPI 서버를 실행합니다."""
    print(f"AGI-lite API 서버를 시작합니다...")
    print(f"호스트: {config.API_HOST}")
    print(f"포트: {config.API_PORT}")
    print(f"API 문서: http://{config.API_HOST}:{config.API_PORT}/docs")
    
    uvicorn.run(
        "app.api:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=True  # 개발 모드에서 코드 변경 시 자동 재시작
    )

if __name__ == "__main__":
    main() 