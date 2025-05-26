import json
from typing import Dict, Any, Optional
from pathlib import Path

from .config import config

def load_memory() -> Dict[str, Any]:
    """메모리 파일에서 데이터를 로드하는 함수
    
    Returns:
        Dict[str, Any]: 메모리 데이터
    """
    try:
        if config.memory_path.exists():
            with open(config.memory_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"메모리 로드 중 오류 발생: {e}")
    
    # 기본 메모리 구조 반환
    return {
        "conversations": [],  # 대화 기록
        "tasks": [],         # 태스크 목록
        "reflections": [],   # 반성 기록
        "iterations": 0      # 현재 반복 횟수
    }

def save_memory(memory: Dict[str, Any]) -> None:
    """메모리 데이터를 파일에 저장하는 함수
    
    Args:
        memory (Dict[str, Any]): 저장할 메모리 데이터
    """
    try:
        # 메모리 디렉토리가 없으면 생성
        config.memory_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config.memory_path, 'w', encoding='utf-8') as f:
            json.dump(memory, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"메모리 저장 중 오류 발생: {e}")

def update_memory(key: str, value: Any) -> None:
    """메모리의 특정 키 값을 업데이트하는 함수
    
    Args:
        key (str): 업데이트할 키
        value (Any): 새로운 값
    """
    memory = load_memory()
    memory[key] = value
    save_memory(memory)

def append_to_memory(key: str, value: Any) -> None:
    """메모리의 특정 키에 값을 추가하는 함수
    
    Args:
        key (str): 추가할 키
        value (Any): 추가할 값
    """
    memory = load_memory()
    if key not in memory:
        memory[key] = []
    memory[key].append(value)
    save_memory(memory) 