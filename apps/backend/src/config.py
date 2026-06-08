import os

from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY        = os.environ["OPENAI_API_KEY"]
TAVILY_API_KEY        = os.environ["TAVILY_API_KEY"]
HARDCOVER_API_KEY     = os.environ["HARDCOVER_API_KEY"]
MONGO_URI             = os.environ["MONGO_URI"]
LANGSMITH_API_KEY     = os.environ["LANGSMITH_API_KEY"]
GOOGLE_CLIENT_ID      = os.environ["GOOGLE_CLIENT_ID"]
LANGCHAIN_TRACING_V2  = os.environ.get("LANGCHAIN_TRACING_V2", "true")
LANGCHAIN_PROJECT     = os.environ.get("LANGCHAIN_PROJECT", "book-ninja")
APP_ENV                    = os.environ.get("APP_ENV", "dev")  # dev | qa | prod
AUDIOBOOKBAY_FALLBACK_URL  = os.environ.get("AUDIOBOOKBAY_FALLBACK_URL", "https://audiobookbay.lu")
FRONTEND_ORIGINS           = [
    origin.strip()
    for origin in os.environ.get("FRONTEND_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
    if origin.strip()
]
