from contextlib import contextmanager

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.mongodb import MongoDBSaver

from config import MONGO_URI


@contextmanager
def get_checkpointer():
    """
    Sync context manager that yields a MongoDBSaver for use in the FastAPI lifespan.
    Falls back to InMemorySaver if the MongoDB connection fails — threads will not
    persist across restarts in degraded mode.

    Usage (in lifespan):
        with get_checkpointer() as checkpointer:
            app.state.graph = build_graph(checkpointer)
            yield
    """
    try:
        with MongoDBSaver.from_conn_string(MONGO_URI, db_name="book_ninja") as checkpointer:
            yield checkpointer
    except Exception:
        yield InMemorySaver()
