from __future__ import annotations

import psycopg
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import END, START, StateGraph
from psycopg.rows import dict_row

from agents.orchestrator import fanout, orchestrator_node
from agents.reducer import build_reducer_subgraph
from agents.research import research_node
from agents.router import route_next, router_node
from agents.worker import worker_node
from core.config import settings
from schemas.models import State


def _build_graph() -> StateGraph:
    reducer_subgraph = build_reducer_subgraph()

    graph = StateGraph(State)
    graph.add_node("router", router_node)
    graph.add_node("research", research_node)
    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("worker", worker_node)
    graph.add_node("reducer", reducer_subgraph)

    graph.add_edge(START, "router")
    graph.add_conditional_edges(
        "router", route_next, {"research": "research", "orchestrator": "orchestrator"}
    )
    graph.add_edge("research", "orchestrator")

    graph.add_conditional_edges("orchestrator", fanout, ["worker"])
    graph.add_edge("worker", "reducer")
    graph.add_edge("reducer", END)

    return graph


def _build_checkpointer() -> PostgresSaver:
    conn = psycopg.connect(
        settings.database_url,
        autocommit=True,
        row_factory=dict_row,
    )
    checkpointer = PostgresSaver(conn)
    checkpointer.setup()
    return checkpointer


_graph = _build_graph()
_checkpointer = _build_checkpointer()
blog_graph = _graph.compile(checkpointer=_checkpointer)
