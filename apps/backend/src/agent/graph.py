import uuid
from collections.abc import AsyncIterator

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, StateGraph

from agent.nodes.audiobook_node import audiobook_node
from agent.nodes.ebook_node import ebook_node
from agent.nodes.purchase_node import purchase_node
from agent.nodes.search_node import search_books_node
from agent.nodes.start_node import start_node
from agent.nodes.validate_audiobook_node import validate_audiobook_node
from models.agent import AgentState


def build_thread_id(user_id: str, incoming_thread_id: str | None) -> str:
    """
    Returns existing thread_id (continuing a conversation) or generates a new one.
    Format: '{user_id}_{uuid4}' — the underscore separator matches the spec.
    """
    if incoming_thread_id:
        return incoming_thread_id
    return f"{user_id}_{uuid.uuid4()}"


def _route(state: AgentState) -> str:
    """Conditional edge: routes from start node based on state.intent."""
    if state.intent == "search":
        return "search_books"
    if state.intent == "purchase":
        return "purchase"
    if state.intent == "ebook":
        return "download_ebook"
    if state.intent == "audiobook":
        return "download_audiobook"
    return END


def build_graph(checkpointer: BaseCheckpointSaver):
    """Compile the LangGraph StateGraph with the provided checkpointer."""
    g = StateGraph(AgentState)
    g.add_node("start", start_node)
    g.add_node("search_books", search_books_node)
    g.add_node("purchase", purchase_node)
    g.add_node("download_ebook", ebook_node)
    g.add_node("download_audiobook", audiobook_node)
    g.add_node("validate_audiobook", validate_audiobook_node)
    g.set_entry_point("start")
    g.add_conditional_edges("start", _route)
    g.add_edge("search_books", END)
    g.add_edge("purchase", END)
    g.add_edge("download_ebook", END)
    g.add_edge("download_audiobook", "validate_audiobook")
    g.add_edge("validate_audiobook", END)
    return g.compile(checkpointer=checkpointer)


def _apply_stream_update(state: AgentState, update: object) -> AgentState:
    """Merges a node update chunk into an AgentState instance."""
    if isinstance(update, AgentState):
        return update
    if isinstance(update, dict):
        return state.model_copy(update=update)
    return state


async def stream_agent(
    graph, prompt: str, user_id: str, thread_id: str | None
) -> AsyncIterator[tuple[str, AgentState]]:
    """
    Streams node-by-node graph progress.

    Yields:
        (node_name, latest_state_after_node)
    """
    tid = build_thread_id(user_id, thread_id)
    initial_state = AgentState(prompt=prompt, user_id=user_id, thread_id=tid)
    config = {"configurable": {"thread_id": tid}}
    latest_state = initial_state

    async for chunk in graph.astream(initial_state, config=config, stream_mode="updates"):
        chunk_data = chunk[-1] if isinstance(chunk, tuple) else chunk
        if not isinstance(chunk_data, dict):
            continue
        for node_name, node_update in chunk_data.items():
            latest_state = _apply_stream_update(latest_state, node_update)
            yield node_name, latest_state


async def run_agent(graph, prompt: str, user_id: str, thread_id: str | None) -> AgentState:
    """Entry point called by the /chat route. Accepts the compiled graph from app state."""
    latest_state: AgentState | None = None
    async for _, state in stream_agent(
        graph=graph, prompt=prompt, user_id=user_id, thread_id=thread_id
    ):
        latest_state = state

    if latest_state is not None:
        return latest_state

    tid = build_thread_id(user_id, thread_id)
    return AgentState(prompt=prompt, user_id=user_id, thread_id=tid)
