"""명령줄 인터페이스 모듈

이 모듈은 시스템의 명령줄 인터페이스를 제공합니다.
"""

import argparse
from typing import Optional

from ..core.memory import MemoryManager
from ..workflow.agent_graph import run_workflow

def parse_args() -> argparse.Namespace:
    """명령줄 인자 파싱
    
    Returns:
        argparse.Namespace: 파싱된 인자
    """
    parser = argparse.ArgumentParser(description="AGI 에이전트 시스템")
    parser.add_argument(
        "--goal",
        type=str,
        required=True,
        help="달성할 목표"
    )
    parser.add_argument(
        "--session-id",
        type=str,
        help="세션 ID (기본값: 자동 생성)"
    )
    parser.add_argument(
        "--memory-dir",
        type=str,
        default="memory",
        help="메모리 파일 디렉토리 (기본값: memory)"
    )
    return parser.parse_args()

def run_cli(goal: Optional[str] = None, session_id: Optional[str] = None, memory_dir: str = "memory") -> None:
    """명령줄 인터페이스 실행
    
    Args:
        goal: 달성할 목표 (기본값: None)
        session_id: 세션 ID (기본값: None)
        memory_dir: 메모리 파일 디렉토리 (기본값: "memory")
    """
    # 인자가 제공되지 않은 경우 명령줄에서 파싱
    if goal is None:
        args = parse_args()
        goal = args.goal
        session_id = args.session_id
        memory_dir = args.memory_dir
    
    # 메모리 관리자 초기화
    memory = MemoryManager(session_id=session_id, memory_dir=memory_dir)
    
    # 워크플로우 실행
    final_state = run_workflow(goal, memory)
    
    # 결과 출력
    print("\n=== 최종 결과 ===")
    for i, (task, result, evaluation) in enumerate(zip(
        final_state["tasks"],
        final_state["results"],
        final_state["evaluations"]
    )):
        print(f"\n태스크 {i+1}: {task.description}")
        print(f"코드:\n{result['code']}")
        print(f"설명: {result['explanation']}")
        print(f"평가 점수: {evaluation['score']}")
        print(f"피드백: {evaluation['feedback']}")
        if evaluation['improvements']:
            print("개선 사항:")
            for improvement in evaluation['improvements']:
                print(f"- {improvement}")

if __name__ == "__main__":
    run_cli() 