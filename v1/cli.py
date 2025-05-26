import argparse
import json
from datetime import datetime
from pathlib import Path
import uuid

from app.agent_graph import run_graph
from app.config import config

def format_history(history: list) -> str:
    """대화 기록을 보기 좋게 포맷팅합니다."""
    formatted = []
    for entry in history:
        role = entry["role"]
        content = entry["content"]
        timestamp = datetime.fromisoformat(entry["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
        formatted.append(f"[{timestamp}] {role.upper()}:")
        formatted.append(content)
        formatted.append("")  # 빈 줄로 구분
    return "\n".join(formatted)

def save_result(session_id: str, final_state: dict, history: list) -> None:
    """실행 결과를 파일로 저장합니다."""
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / f"{session_id}.json"
    result = {
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "final_state": final_state,
        "history": history
    }
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n실행 결과가 저장되었습니다: {output_file}")

def main():
    """CLI 메인 함수"""
    parser = argparse.ArgumentParser(description="AGI-lite CLI")
    parser.add_argument("--goal", required=True, help="달성할 목표")
    parser.add_argument("--session-id", help="세션 ID (기본값: 자동 생성)")
    parser.add_argument("--save", action="store_true", help="실행 결과를 파일로 저장")
    
    args = parser.parse_args()
    
    # 세션 ID 생성 또는 사용
    session_id = args.session_id or str(uuid.uuid4())
    print(f"세션 ID: {session_id}")
    print(f"목표: {args.goal}")
    print("\n에이전트 시스템을 실행합니다...\n")
    
    try:
        # 에이전트 그래프 실행
        final_state = run_graph(args.goal, session_id)
        
        # 메모리에서 히스토리 가져오기
        memory = final_state["memory"]
        history = memory.get_history()
        
        # 대화 기록 출력
        print("\n=== 대화 기록 ===")
        print(format_history(history))
        
        # 결과 저장
        if args.save:
            save_result(session_id, final_state, history)
        
    except Exception as e:
        print(f"\n오류가 발생했습니다: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main() 