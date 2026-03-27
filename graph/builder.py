from langgraph.graph import StateGraph, END
from graph.state import AppState
from graph.nodes import (
    router,
    generate_ideas,
    generate_titles,
    generate_script,
    generate_seo,
)


def build_graph():
    """Build and compile the LangGraph workflow."""
    builder = StateGraph(AppState)

    # Register nodes
    builder.add_node("router", router)
    builder.add_node("idea", generate_ideas)
    builder.add_node("title", generate_titles)
    builder.add_node("script", generate_script)
    builder.add_node("seo", generate_seo)

    # Entry point
    builder.set_entry_point("router")

    # Conditional routing based on feature
    builder.add_conditional_edges(
        "router",
        lambda state: state["feature"],
        {
            "idea": "idea",
            "title": "title",
            "script": "script",
            "seo": "seo",
        },
    )

    # All feature nodes → END
    builder.add_edge("idea", END)
    builder.add_edge("title", END)
    builder.add_edge("script", END)
    builder.add_edge("seo", END)

    return builder.compile()


# Compiled graph instance (singleton)
graph = build_graph()
