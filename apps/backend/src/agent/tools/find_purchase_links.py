import asyncio

from langchain_core.tools import tool
from tavily import TavilyClient

from config import TAVILY_API_KEY
from models.purchase import PurchaseLink, PurchaseQuery

tavily = TavilyClient(api_key=TAVILY_API_KEY)


@tool
async def find_purchase_links(query: PurchaseQuery) -> list[PurchaseLink]:
    """
    Searches for ebook or audiobook purchase options on Amazon, Google Books, and Kobo.
    Returns a list of PurchaseLink objects with store name and URL.
    Formats supported: "ebook", "audiobook". If format is None, search for both.
    Example: buy ebook "The Great Gatsby" by F. Scott Fitzgerald site:amazon.com OR site:books.google.com OR site:kobo.com
    Example: buy audiobook "The Great Gatsby" by F. Scott Fitzgerald site:https://www.amazon.com/hz/audible/arya/mlp?ref_=null&_encoding=UTF8&purchaseType=STANDARD_MTRIAL&SHOPPING_PORTAL_MODE=AUGMENTED OR site:https://play.google.com/store/books/category/audiobooks?hl=en_GB OR site:https://librivox.org/

    NOTE: TavilyClient.search() is synchronous — wrapped in asyncio.to_thread().
    """
    audiobooks_sites = "site:https://www.amazon.com/hz/audible/arya/mlp?ref_=null&_encoding=UTF8&purchaseType=STANDARD_MTRIAL&SHOPPING_PORTAL_MODE=AUGMENTED OR site:https://play.google.com/store/books/category/audiobooks?hl=en_GB OR site:https://librivox.org/"
    ebooks_sites = "site:amazon.com OR site:books.google.com OR site:kobo.com"
    search_query = (
        f"buy {query.format} \"{query.title}\" by {query.author} "
        f"{audiobooks_sites if query.format == 'audiobook' else ebooks_sites}"
    )
    results = await asyncio.to_thread(tavily.search, query=search_query, max_results=6)
    return [PurchaseLink(store=r["title"], url=r["url"]) for r in results["results"]]
