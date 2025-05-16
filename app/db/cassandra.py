from cassandra.cluster import Cluster
from cassandra.cqlengine import connection
from cassandra.auth import PlainTextAuthProvider
from app.config import settings

class CassandraSessionManager:
    _session = None

    @classmethod
    def get_session(cls):
        if cls._session is None:
            # auth_provider = PlainTextAuthProvider(
            #     username='your_username',
            #     password='your_password'
            # )
            cluster = Cluster(
                ['127.0.0.1'],
                # auth_provider=auth_provider,
                protocol_version=4
            )
            session = cluster.connect('experimentation')
            cls._session = session

            # Create keyspace if not exists
            session.execute(f"""
                CREATE KEYSPACE IF NOT EXISTS {settings.cassandra_keyspace}
                WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': 1}}
            """)

            # Set the keyspace
            session.set_keyspace(settings.cassandra_keyspace)

            # Register the connection
            connection.register_connection("fastapi_cluster", session=session)
        return cls._session

    @classmethod
    def shutdown(cls):
        if cls._session:
            cls._session.cluster.shutdown()
            cls._session = None
