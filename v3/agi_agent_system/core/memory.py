"""메모리 관리 모듈

이 모듈은 세션별 메모리 관리를 담당하는 MemoryManager 클래스를 정의합니다.
"""

import json
from typing import Dict, Any, List, Optional
from pathlib import Path
import uuid
from datetime import datetime

class MemoryManager:
    """세션별 메모리를 관리하는 클래스
    
    Attributes:
        session_id: 세션 ID
        memory_file: 메모리 파일 경로
        memory: 메모리 데이터
    """
    
    def __init__(self, session_id: Optional[str] = None, memory_dir: str = "memory"):
        """MemoryManager 초기화
        
        Args:
            session_id: 세션 ID (기본값: None, 자동 생성)
            memory_dir: 메모리 파일 디렉토리 (기본값: "memory")
        """
        self.session_id = session_id or str(uuid.uuid4())
        self.memory_dir = Path(memory_dir)
        self.memory_file = self.memory_dir / f"{self.session_id}.json"
        self.memory = self._load_memory()
    
    def _load_memory(self) -> Dict[str, List[Dict[str, Any]]]:
        """메모리 파일에서 데이터 로드
        
        Returns:
            Dict[str, List[Dict[str, Any]]]: 메모리 데이터
        """
        if self.memory_file.exists():
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "conversations": [],
            "tasks": [],
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "session_id": self.session_id
            }
        }
    
    def _save_memory(self) -> None:
        """메모리 데이터를 파일에 저장"""
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=2)
    
    def append(self, key: str, value: Dict[str, Any]) -> None:
        """메모리에 데이터 추가
        
        Args:
            key: 데이터 키 (예: "conversations", "tasks")
            value: 추가할 데이터
        """
        if key not in self.memory:
            self.memory[key] = []
        self.memory[key].append(value)
        self._save_memory()
    
    def get(self, key: str) -> List[Dict[str, Any]]:
        """메모리에서 데이터 조회
        
        Args:
            key: 데이터 키
            
        Returns:
            List[Dict[str, Any]]: 조회된 데이터 목록
        """
        return self.memory.get(key, [])
    
    def clear(self) -> None:
        """메모리 초기화"""
        self.memory = {
            "conversations": [],
            "tasks": [],
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "session_id": self.session_id
            }
        }
        self._save_memory() 