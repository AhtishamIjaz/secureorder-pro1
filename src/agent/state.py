from typing import Annotated, List
import operator
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    # This ensures messages stack so the AI remembers the conversation
    messages: Annotated[List[BaseMessage], operator.add]