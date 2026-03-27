from typing import TypedDict


class AppState(TypedDict):
    """LangGraph state shared across all nodes."""
    user_input: str
    feature: str      # idea | title | script | seo
    response: str
