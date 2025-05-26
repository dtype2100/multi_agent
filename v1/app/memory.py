import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from .config import config

class Memory:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.memory_file = config.MEMORY_DIR / f"{session_id}.json"
        self.data: Dict[str, Any] = self._load()

    def _load(self) -> Dict[str, Any]:
        """메모리 파일에서 데이터를 로드합니다."""
        if not self.memory_file.exists():
            return {
                "session_id": self.session_id,
                "created_at": datetime.now().isoformat(),
                "history": [],
                "current_state": {}
            }
        
        with open(self.memory_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self) -> None:
        """현재 상태를 메모리 파일에 저장합니다."""
        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def add_to_history(self, role: str, content: str) -> None:
        """대화 기록에 새로운 메시지를 추가합니다."""
        self.data["history"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self.save()

    def update_state(self, key: str, value: Any) -> None:
        """현재 상태를 업데이트합니다."""
        self.data["current_state"][key] = value
        self.save()

    def get_state(self, key: str, default: Any = None) -> Any:
        """현재 상태에서 값을 가져옵니다."""
        return self.data["current_state"].get(key, default)

    def get_history(self) -> List[Dict[str, str]]:
        """전체 대화 기록을 반환합니다."""
        return self.data["history"]

    def clear_history(self) -> None:
        """대화 기록을 초기화합니다."""
        self.data["history"] = []
        self.save()

    def clear_state(self) -> None:
        """현재 상태를 초기화합니다."""
        self.data["current_state"] = {}
        self.save()

def get_memory(session_id: str) -> Memory:
    """세션 ID에 해당하는 메모리 인스턴스를 반환합니다."""
    return Memory(session_id) 