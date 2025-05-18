# app/repositories/base_repository.py
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List

from cassandra import ConsistencyLevel
from cassandra.cluster import Session
from cassandra.query import SimpleStatement
from cassandra.cluster import Session

from app.db.cassandra import CassandraSessionManager
from app.models.schemas import Service

T = TypeVar('T')
K = TypeVar('K')


class BaseRepository(ABC):
    def __init__(self):
        self.session: Session = CassandraSessionManager.get_session()
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

    def list_paginated(self, session: Session, table_name: str, has_active_only: bool or False,
                       active_only: bool or False, limit: int, paging_state: bytes = None):
        """
        Fetch paginated services from Cassandra table.

        Args:
            active_only: Filter for active services.
            limit: Number of records to fetch.
            paging_state: Token for fetching the next page.

        Returns:
            A tuple: (list of services, next_page_token)
            :param table_name:
            :param has_active_only:
            :param paging_state:
            :param limit:
            :param active_only:
            :param session:
        """
        query = f"SELECT * FROM {table_name}"

        if has_active_only and active_only:
            query += " WHERE active = true ALLOW FILTERING"

        statement = SimpleStatement(query, fetch_size=limit, consistency_level=ConsistencyLevel.QUORUM
                                    )

        # Execute query with paging state
        result_set = session.execute(statement, paging_state=paging_state)
        rows = result_set.current_rows

        # Return the entities and next page token
        return rows, result_set.paging_state
