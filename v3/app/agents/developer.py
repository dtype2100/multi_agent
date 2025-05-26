from typing import Dict, Any
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

from ..model import get_llm
from ..memory import append_to_memory

class CodeSolution(BaseModel):
    """코드 솔루션을 정의하는 모델"""
    code: str = Field(description="생성된 코드")
    explanation: str = Field(description="코드에 대한 설명")
    test_cases: list[str] = Field(description="테스트 케이스 목록")

DEVELOPER_PROMPT = """당신은 주어진 태스크를 해결하는 코드를 생성하는 개발자입니다.

현재 태스크: {task_description}

이전 태스크들의 결과:
{previous_results}

위 태스크를 해결하기 위한 코드를 생성해주세요.
코드는 다음 정보를 포함해야 합니다:
- code: 실제 구현 코드
- explanation: 코드에 대한 자세한 설명
- test_cases: 코드를 검증하기 위한 테스트 케이스 목록

{format_instructions}

코드 솔루션:"""

def developer_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """태스크에 맞는 코드를 생성하는 LangGraph 노드
    
    Args:
        state (Dict[str, Any]): 현재 상태
        
    Returns:
        Dict[str, Any]: 업데이트된 상태
    """
    # 현재 태스크 가져오기
    current_task = state["tasks"][state["current_task_index"]]
    
    # 이전 태스크들의 결과 수집
    previous_results = []
    for i in range(state["current_task_index"]):
        if "results" in state and i < len(state["results"]):
            previous_results.append(f"태스크 {i+1}: {state['results'][i]}")
    
    # 출력 파서 설정
    parser = PydanticOutputParser(pydantic_object=CodeSolution)
    
    # 프롬프트 템플릿 설정
    prompt = PromptTemplate(
        template=DEVELOPER_PROMPT,
        input_variables=["task_description", "previous_results"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    # LLM 호출
    llm = get_llm()
    response = llm(prompt.format(
        task_description=current_task.description,
        previous_results="\n".join(previous_results) if previous_results else "없음"
    ))
    
    # 응답 파싱
    solution = parser.parse(response)
    
    # 메모리에 결과 저장
    append_to_memory("conversations", {
        "role": "developer",
        "task_id": current_task.task_id,
        "content": solution.dict()
    })
    
    # 상태 업데이트
    if "results" not in state:
        state["results"] = []
    state["results"].append(solution.dict())
    
    return state 