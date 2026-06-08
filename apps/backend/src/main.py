import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agent.graph import build_graph
from api.routes import auth, chat, health, threads
from config import FRONTEND_ORIGINS, LANGCHAIN_PROJECT, LANGCHAIN_TRACING_V2
from db.checkpointer import get_checkpointer

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(threads.router)
app.include_router(health.router)
