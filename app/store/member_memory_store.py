# app/store/member_memory_store.py

from threading import Lock
from typing import Dict, List
from app.domain.member import Member

class MemberMemoryStore:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(MemberMemoryStore, cls).__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.members: Dict[int, Member] = {}  # key: member.id, value: Member 객체

    def add_member(self, member: Member):
        """멤버 추가"""
        with self._lock:
            self.members[member.id] = member

    def get_member(self, member_id: int) -> Member:
        """멤버 조회"""
        return self.members.get(member_id)

    def remove_member(self, member_id: int):
        """멤버 제거"""
        with self._lock:
            self.members.pop(member_id, None)

    def get_all_members(self) -> List[Member]:
        """모든 멤버 조회"""
        return list(self.members.values())