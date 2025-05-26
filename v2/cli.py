import argparse
import json
from typing import Dict, Any
import uuid
from pathlib import Path

from app.agent_graph import run_graph
from app.memory import memory

def format_output(result: Dict[str, Any]) -> str:
    """
    결과를 보기 좋게 포맷팅합니다.
    
    Args:
        result: 에이전트 실행 결과
    
    Returns:
        str: 포맷팅된 출력
    """
    output = []
    
    # 목표
    output.append(f"🎯 목표: {result['goal']}\n")
    
    # 태스크 계획
    if "task_plan" in result:
        plan = result["task_plan"]
        output.append("📋 태스크 계획:")
        output.append(f"계획 수립 이유: {plan.get('reasoning', '')}\n")
        
        for task in plan.get("tasks", []):
            output.append(f"  • [Task {task['task_id']}] {task['description']}")
            output.append(f"    - 우선순위: {task['priority']}")
            if task["dependencies"]:
                output.append(f"    - 의존성: {task['dependencies']}")
            output.append("")
    
    # 실행 결과
    if "task_results" in result:
        output.append("✨ 실행 결과:")
        for task_result in result["task_results"]:
            status = "✅" if task_result["status"] == "success" else "❌"
            output.append(f"  {status} [Task {task_result['task_id']}]")
            output.append(f"    - 결과: {task_result['output']}")
            if task_result.get("error"):
                output.append(f"    - 에러: {task_result['error']}")
            output.append("")
    
    # 피드백
    if "feedback" in result:
        output.append("💭 피드백:")
        for feedback in result["feedback"]:
            output.append(f"  • [Task {feedback['task_id']}]")
            output.append(f"    - 점수: {feedback['score']}/5")
            output.append(f"    - 피드백: {feedback['feedback']}")
            if feedback["needs_improvement"]:
                output.append("    - 개선 제안:")
                for suggestion in feedback["improvement_suggestions"]:
                    output.append(f"      - {suggestion}")
            output.append("")
    
    # 에러
    if result.get("error"):
        output.append(f"❌ 에러: {result['error']}")
    
    return "\n".join(output)

def main():
    """CLI 메인 함수"""
    parser = argparse.ArgumentParser(description="LangGraph 기반 AGI-lite 시스템")
    parser.add_argument("--goal", required=True, help="실행할 목표")
    parser.add_argument("--session", help="세션 ID (선택사항)")
    parser.add_argument("--output", help="결과를 저장할 JSON 파일 경로 (선택사항)")
    
    args = parser.parse_args()
    
    try:
        # 세션 ID 생성 또는 사용
        session_id = args.session or str(uuid.uuid4())
        
        # 에이전트 실행
        result = run_graph(
            goal=args.goal,
            session_id=session_id
        )
        
        # 결과 출력
        print(format_output(result))
        
        # JSON 파일로 저장
        if args.output:
            output_path = Path(args.output)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"\n결과가 {output_path}에 저장되었습니다.")
        
        # 세션 ID 출력
        print(f"\n세션 ID: {session_id}")
        
    except Exception as e:
        print(f"에러: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main() 