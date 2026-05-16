import os
from unittest.mock import AsyncMock, patch

os.environ.setdefault("OPENAI_API_KEY", "test-openai-key")

from agent.nodes.validate_audiobook_node import validate_audiobook_node
from models.agent import AgentState
from models.audiobook import AudiobookLink
from models.query import ParsedQuery


async def test_validate_audiobook_node_parses_non_strict_llm_response():
    state = AgentState(
        prompt="I want to download audiobook for It by Stephen King",
        user_id="u1",
        thread_id="u1_t1",
        parsed_query=ParsedQuery(title="It", author="Stephen King", intent="audiobook"),
        audio_links=[
            AudiobookLink(source="AudiobookBay", title="It - Stephen King", url="https://a.example/it"),
            AudiobookLink(
                source="AudiobookBay",
                title="The End of the World As We Know It - Stephen King",
                url="https://a.example/not-it",
            ),
        ],
    )

    mock_llm_response = type("Resp", (), {"content": "Sure, keep these indices: ```json\n[0]\n```"})()

    mock_llm = AsyncMock()
    mock_llm.ainvoke.return_value = mock_llm_response

    with patch("agent.nodes.validate_audiobook_node._llm", mock_llm):
        updated = await validate_audiobook_node(state)

    assert len(updated.audio_links) == 1
    assert updated.audio_links[0].title == "It - Stephen King"
    assert "Here are audiobook download links:" in (updated.output or "")
