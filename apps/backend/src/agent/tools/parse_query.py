from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from models.query import ParsedQuery
from utils.llm_stream import collect_stream

_llm = ChatOpenAI(model="gpt-4o-mini").with_structured_output(ParsedQuery)


@tool
async def parse_query(prompt: str) -> ParsedQuery:
    """
    Parses a natural language book query into structured fields.
    Returns a ParsedQuery with title, genre, year, author, and intent.
    Intent is one of: search, purchase, ebook, audiobook.
    """
    response = await collect_stream(_llm.astream(
        "Extract structured fields from a book-related query.\n\n"
        "Fields:\n"
        "- title: ONLY set this when the user names a specific book (e.g. 'The Shining', 'Atomic Habits'). "
        "Leave null if the user is browsing by genre, theme, or topic without naming a book.\n"
        "- genre: ONLY set this when an actual genre, theme, or topic word is present "
        "(e.g. 'horror', 'sci-fi', 'fantasy', 'romance', 'thriller', 'mystery', 'self-help', 'biography'). "
        "Leave null if only generic descriptors like 'best', 'popular', 'classic', 'top' appear with no genre word — "
        "these descriptors are NOT genres on their own.\n"
        "- year: publication year or range mentioned by the user.\n"
        "- author: author name if mentioned.\n"
        "- intent: one of 'search', 'purchase', 'ebook', 'audiobook'. Default to 'search' for discovery queries.\n"
        "- format: one of 'ebook', 'audiobook'. Set based on the user's request.\n\n"
        "Example: 'find me best horror books of 2022' → title=null, genre='horror', year='2022', intent='search'\n"
        "Example: 'Find me the best books by Stephen King' → title=null, genre=null, author='Stephen King', intent='search'\n"
        "Example: 'download ebook of Dune by Frank Herbert' → title='Dune', author='Frank Herbert', intent='ebook'\n\n"
        "Example:'Find me purchase options for King of Pigs By J. H. Archer audiobook' → title='King of Pigs', author='J. H. Archer', intent='purchase', format='audiobook'\n\n"
        f"Query: {prompt}"
    ))
    if isinstance(response, ParsedQuery):
        return response
    if isinstance(response, dict):
        return ParsedQuery(**response)
    raise ValueError("parse_query streaming response could not be parsed into ParsedQuery")
