import os
from unittest.mock import AsyncMock, patch

os.environ.setdefault("OPENAI_API_KEY", "test-openai-key")

from agent.nodes.start_node import start_node
from models.agent import AgentState
from models.query import ParsedQuery


async def test_start_node_forces_audiobook_intent_for_explicit_download_prompt():
    state = AgentState(
        prompt="I want to download audiobook for Lord of the ring",
        user_id="u1",
        thread_id="u1_t1",
    )

    parsed_as_search = ParsedQuery(
        title="Lord of the Rings",
        author=None,
        intent="search",
    )

    mock_parse_query = AsyncMock()
    mock_parse_query.ainvoke.return_value = parsed_as_search

    with patch("agent.nodes.start_node.parse_query", mock_parse_query):
        updated = await start_node(state)

    assert updated.intent == "audiobook"
    assert updated.parsed_query is not None
    assert updated.parsed_query.intent == "audiobook"
