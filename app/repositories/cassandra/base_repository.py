# app/repositories/base_repository.py
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List

T = TypeVar('T')
K = TypeVar('K')


class BaseRepository(ABC):
    def __init__(self):
        self._sync_table()

    @abstractmethod
    def _sync_table(self):
        """Initialize the Cassandra table"""
        pass

    @abstractmethod
    def create(self, entity: T) -> T:
        """Create a new entity"""
        pass

    @abstractmethod
    def find_by_id(self, id: K) -> Optional[T]:
        """Find entity by primary key"""
        pass

    @abstractmethod
    def update(self, entity: T) -> T:
        """Update existing entity"""
        pass

    @abstractmethod
    def delete(self, id: K) -> bool:
        """Delete entity by primary key"""
        pass