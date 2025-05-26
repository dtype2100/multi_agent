import argparse
import json
from typing import Dict, Any

from app.agent_graph import run_graph
from app.memory import load_memory

def format_result(result: Dict[str, Any]) -> str:
    """실행 결과를 보기 좋게 포맷팅하는 함수
    
    Args:
        result (Dict[str, Any]): 실행 결과
        
    Returns:
        str: 포맷팅된 결과 문자열
    """
    output = []
    
    # 목표 출력
    output.append(f"🎯 목표: {result['goal']}\n")
    
    # 태스크 목록 출력
    output.append("📋 태스크 목록:")
    for i, task in enumerate(result['tasks'], 1):
        output.append(f"\n{i}. {task['description']}")
        output.append(f"   - 우선순위: {task['priority']}")
        if task['dependencies']:
            output.append(f"   - 의존성: {task['dependencies']}")
    
    # 실행 결과 출력
    output.append("\n✨ 실행 결과:")
    for i, (result, eval) in enumerate(zip(result['results'], result['evaluations']), 1):
        output.append(f"\n{i}. 코드:")
        output.append(f"```python\n{result['code']}\n```")
        output.append(f"\n   설명: {result['explanation']}")
        output.append(f"\n   평가:")
        output.append(f"   - 점수: {eval['score']:.2f}")
        output.append(f"   - 피드백: {eval['feedback']}")
        if eval['improvements']:
            output.append("   - 개선사항:")
            for imp in eval['improvements']:
                output.append(f"     * {imp}")
    
    return "\n".join(output)

def main():
    """CLI 메인 함수"""
    # 명령행 인자 파서 설정
    parser = argparse.ArgumentParser(description="AGI-lite 멀티에이전트 시스템")
    parser.add_argument("--goal", type=str, required=True, help="실행할 목표")
    parser.add_argument("--json", action="store_true", help="JSON 형식으로 출력")
    
    # 인자 파싱
    args = parser.parse_args()
    
    try:
        # 에이전트 실행
        result = run_graph(args.goal)
        
        # 메모리 로드
        memory = load_memory()
        
        # 결과 출력
        if args.json:
            print(json.dumps({
                "result": result,
                "memory": memory
            }, ensure_ascii=False, indent=2))
        else:
            print(format_result(result))
            
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main() 