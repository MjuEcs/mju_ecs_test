# app/store/container_memory_store.py

from threading import Lock
from typing import Dict, List
from app.domain.container import Container

class ContainerMemoryStore:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(ContainerMemoryStore, cls).__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.containers: Dict[str, Container] = {}  # key: container.name, value: Container 객체

    def add_container(self, container: Container):
        """컨테이너 추가"""
        with self._lock:
            self.containers[container.name] = container

    def get_container(self, container_name: str) -> Container:
        """컨테이너 조회"""
        return self.containers.get(container_name)

    def remove_container(self, container_name: str):
        """컨테이너 제거"""
        with self._lock:
            self.containers.pop(container_name, None)

    def get_all_containers(self) -> List[Container]:
        """모든 컨테이너 조회"""
        return list(self.containers.values())