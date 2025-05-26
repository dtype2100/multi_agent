import json
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from .config import config

class Memory:
    """JSON 파일 기반의 메모리 시스템"""
    
    def __init__(self, memory_file: Optional[str] = None):
        self.memory_file = Path(config.MEMORY_DIR) / (memory_file or config.MEMORY_FILE)
        self.memory: Dict[str, Any] = self._load()
    
    def _load(self) -> Dict[str, Any]:
        """메모리 파일에서 데이터를 로드합니다."""
        if not self.memory_file.exists():
            return {
                "sessions": {},
                "last_updated": datetime.now().isoformat()
            }
        
        try:
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {
                "sessions": {},
                "last_updated": datetime.now().isoformat()
            }
    
    def _save(self):
        """메모리 데이터를 파일에 저장합니다."""
        self.memory["last_updated"] = datetime.now().isoformat()
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=2)
    
    def get_session(self, session_id: str) -> Dict[str, Any]:
        """특정 세션의 메모리를 가져옵니다."""
        return self.memory["sessions"].get(session_id, {})
    
    def save_session(self, session_id: str, data: Dict[str, Any]):
        """세션 데이터를 저장합니다."""
        self.memory["sessions"][session_id] = data
        self._save()
    
    def update_session(self, session_id: str, data: Dict[str, Any]):
        """세션 데이터를 업데이트합니다."""
        current = self.get_session(session_id)
        current.update(data)
        self.save_session(session_id, current)
    
    def delete_session(self, session_id: str):
        """세션을 삭제합니다."""
        if session_id in self.memory["sessions"]:
            del self.memory["sessions"][session_id]
            self._save()
    
    def clear_all(self):
        """모든 세션을 삭제합니다."""
        self.memory["sessions"] = {}
        self._save()

# 전역 메모리 인스턴스
memory = Memory() 