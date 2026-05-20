import os
import logging
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
from fastapi import FastAPI
from api.routes import chat, threads, health
from config import LANGCHAIN_TRACING_V2, LANGCHAIN_PROJECT
from db.checkpointer import get_checkpointer
from agent.graph import build_graph

os.environ["LANGCHAIN_TRACING_V2"] = LANGCHAIN_TRACING_V2
os.environ["LANGCHAIN_PROJECT"] = LANGCHAIN_PROJECT


@asynccontextmanager
async def lifespan(app: FastAPI):
    with get_checkpointer() as checkpointer:
        app.state.graph = build_graph(checkpointer)
        yield
    # MongoDBSaver connection closed automatically when the `with` block exits


app = FastAPI(
    title="Book Ninja API",
    version="2.0",
    description="AI-powered book discovery: search, purchase, ebook, and audiobook links.",
    lifespan=lifespan,
)

app.include_router(chat.router)
app.include_router(threads.router)
app.include_router(health.router)
