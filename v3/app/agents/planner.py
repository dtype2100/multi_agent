from typing import Dict, Any, List
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
import json
import re

from ..model import get_llm
from ..memory import append_to_memory

class SubTask(BaseModel):
    """하위 태스크를 정의하는 모델"""
    task_id: int = Field(description="태스크 ID")
    description: str = Field(description="태스크 설명")
    priority: int = Field(description="우선순위 (1-5, 5가 가장 높음)")
    dependencies: List[int] = Field(description="의존하는 태스크 ID 목록 (정수만 사용)")

class TaskPlan(BaseModel):
    """태스크 계획을 정의하는 모델"""
    tasks: List[SubTask] = Field(description="하위 태스크 목록")

PLANNER_PROMPT = """당신은 복잡한 목표를 작은 하위 태스크로 분해하는 플래너입니다.

목표: {goal}

이 목표를 달성하기 위해 필요한 하위 태스크들을 생성해주세요.
각 태스크는 다음 정보를 포함해야 합니다:
- task_id: 태스크의 고유 ID (정수)
- description: 태스크에 대한 자세한 설명
- priority: 우선순위 (1-5, 5가 가장 높음)
- dependencies: 이 태스크가 의존하는 다른 태스크의 ID 목록 (정수만 사용)

주의사항:
1. task_id는 1부터 시작하는 정수여야 합니다.
2. dependencies는 반드시 정수 배열이어야 합니다. 예: [1, 2, 3]
3. 각 태스크는 명확하고 구체적인 설명을 가져야 합니다.

{format_instructions}

태스크 계획:"""

def extract_json(text: str) -> str:
    """텍스트에서 JSON 부분만 추출
    
    Args:
        text (str): 원본 텍스트
        
    Returns:
        str: 추출된 JSON 문자열
    """
    # JSON 객체를 찾는 정규식 패턴
    pattern = r'\{[\s\S]*\}'
    match = re.search(pattern, text)
    if match:
        return match.group(0)
    return text

def parse_dependencies(deps: List[Any]) -> List[int]:
    """의존성 목록을 정수 배열로 변환
    
    Args:
        deps (List[Any]): 원본 의존성 목록
        
    Returns:
        List[int]: 정수로 변환된 의존성 목록
    """
    result = []
    for dep in deps:
        if isinstance(dep, int):
            result.append(dep)
        elif isinstance(dep, str):
            # "tasks.1" 형식의 문자열에서 숫자만 추출
            try:
                num = int(''.join(filter(str.isdigit, dep)))
                result.append(num)
            except ValueError:
                continue
    return result

def planner_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """목표를 하위 태스크로 분해하는 LangGraph 노드
    
    Args:
        state (Dict[str, Any]): 현재 상태
        
    Returns:
        Dict[str, Any]: 업데이트된 상태
    """
    # 출력 파서 설정
    parser = PydanticOutputParser(pydantic_object=TaskPlan)
    
    # 프롬프트 템플릿 설정
    prompt = PromptTemplate(
        template=PLANNER_PROMPT,
        input_variables=["goal"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    # LLM 호출
    llm = get_llm()
    response = llm(prompt.format(goal=state["goal"]))
    
    try:
        # JSON 추출 및 파싱
        json_str = extract_json(response)
        response_dict = json.loads(json_str)
        
        # 의존성 파싱 및 변환
        for task in response_dict["tasks"]:
            task["dependencies"] = parse_dependencies(task["dependencies"])
        
        # Pydantic 모델로 변환
        task_plan = TaskPlan(**response_dict)
        
        # 메모리에 태스크 저장
        for task in task_plan.tasks:
            append_to_memory("tasks", task.dict())
        
        # 상태 업데이트
        state["tasks"] = task_plan.tasks
        state["current_task_index"] = 0
        
        return state
        
    except Exception as e:
        print(f"파싱 오류: {str(e)}")
        print(f"원본 응답: {response}")
        raise 