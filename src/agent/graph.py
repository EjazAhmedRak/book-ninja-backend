import uuid
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.base import BaseCheckpointSaver
from models.agent import AgentState
from agent.nodes.start_node import start_node
from agent.nodes.search_node import search_books_node
from agent.nodes.purchase_node import purchase_node
from agent.nodes.ebook_node import ebook_node
from agent.nodes.audiobook_node import audiobook_node
from agent.nodes.validate_audiobook_node import validate_audiobook_node


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


async def run_agent(graph, prompt: str, user_id: str, thread_id: str | None) -> AgentState:
    """Entry point called by the /chat route. Accepts the compiled graph from app state."""
    tid = build_thread_id(user_id, thread_id)
    initial_state = AgentState(prompt=prompt, user_id=user_id, thread_id=tid)
    config = {"configurable": {"thread_id": tid}}
    result = await graph.ainvoke(initial_state, config=config)
    if isinstance(result, dict):
        return AgentState(**result)
    return result
