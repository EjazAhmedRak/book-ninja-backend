import logging

from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from langchain_core.tools import tool

from config import HARDCOVER_API_KEY
from models.book import BookResult
from models.query import ParsedQuery

logger = logging.getLogger(__name__)

_GRAPHQL_URL = "https://api.hardcover.app/v1/graphql"

_BOOKS_QUERY = gql("""
query Books($where: books_bool_exp, $limit: Int) {
  books(where: $where, order_by: {rating: desc_nulls_last}, limit: $limit) {
    title
    rating
    release_year
    description
    slug
    contributions {
      author {
        name
      }
    }
  }
}
""")


def _build_where(query: ParsedQuery) -> dict:
    """
    Builds a Hasura `books_bool_exp` filter from the parsed query.
    Each populated field becomes an `_eq` predicate on the matching column/relation.
    """
    where: dict = {}
    if query.title:
        where["title"] = {"_eq": query.title}
    if query.author:
        where["contributions"] = {"author": {"name": {"_eq": query.author}}}
    if query.year:
        try:
            where["release_year"] = {"_eq": int(query.year)}
        except ValueError:
            pass
    if query.genre:
        where["taggings"] = {"tag": {"tag": {"_eq": query.genre.title()}}}
    return where


@tool
async def search_books(query: ParsedQuery) -> list[BookResult]:
    """
    Searches HardCover GraphQL API for books matching the parsed query.
    Filters by title, author, year, and/or genre via a `books_bool_exp` where clause,
    sorted by rating descending. Returns up to 5 BookResult objects.
    """
    variables = {"where": _build_where(query), "limit": 5}
    logger.info("HardCover books — variables: %s", variables)

    transport = AIOHTTPTransport(
        url=_GRAPHQL_URL,
        headers={"Authorization": HARDCOVER_API_KEY},
    )
    async with Client(transport=transport, fetch_schema_from_transport=False) as session:
        result = await session.execute(_BOOKS_QUERY, variable_values=variables)

    books = []
    for doc in result.get("books", []):
        contributions = doc.get("contributions") or []
        author = contributions[0].get("author", {}).get("name", "Unknown") if contributions else "Unknown"
        books.append(BookResult(
            title=doc["title"],
            author=author,
            year=str(doc["release_year"]) if doc.get("release_year") else None,
            summary=doc.get("description") or "",
            hardcover_url=f"https://hardcover.app/books/{doc.get('slug', '')}",
            rating=doc.get("rating") or 0.0,
        ))

    return books
