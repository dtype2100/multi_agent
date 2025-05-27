"""메인 모듈

이 모듈은 시스템의 진입점을 제공합니다.
"""

import argparse
from typing import Optional

from .interface.cli import run_cli
from .interface.api import run_api

def parse_args():
    """명령줄 인자 파싱
    
    Returns:
        argparse.Namespace: 파싱된 인자
    """
    parser = argparse.ArgumentParser(description="AGI 에이전트 시스템")
    parser.add_argument(
        "--mode",
        type=str,
        choices=["cli", "api"],
        default="cli",
        help="실행 모드 (기본값: cli)"
    )
    parser.add_argument(
        "--goal",
        type=str,
        help="달성할 목표 (cli 모드에서만 사용)"
    )
    parser.add_argument(
        "--session-id",
        type=str,
        help="세션 ID"
    )
    parser.add_argument(
        "--memory-dir",
        type=str,
        default="memory",
        help="메모리 파일 디렉토리 (기본값: memory)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="API 서버 호스트 (api 모드에서만 사용, 기본값: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API 서버 포트 (api 모드에서만 사용, 기본값: 8000)"
    )
    return parser.parse_args()

def main():
    """메인 함수"""
    args = parse_args()
    
    if args.mode == "cli":
        if not args.goal:
            raise ValueError("cli 모드에서는 --goal 인자가 필요합니다.")
        run_cli(
            goal=args.goal,
            session_id=args.session_id,
            memory_dir=args.memory_dir
        )
    else:  # api 모드
        run_api(
            host=args.host,
            port=args.port
        )

if __name__ == "__main__":
    main() 