from cassandra.cluster import Cluster
from cassandra.cqlengine import connection
from app.config import settings

cluster = None
session = None

def init_cassandra():
    global cluster, session
    cluster = Cluster(
        [settings.cassandra_host],
        port=settings.cassandra_port,
    )
    session = cluster.connect()

    # Create keyspace if not exists
    session.execute(f"""
        CREATE KEYSPACE IF NOT EXISTS {settings.cassandra_keyspace}
        WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': 1}}
    """)

    # Set the keyspace
    session.set_keyspace(settings.cassandra_keyspace)

    # Register the connection
    connection.register_connection("fastapi_cluster", session=session)

def close_cassandra():
    global cluster
    if cluster is not None:
        cluster.shutdown()