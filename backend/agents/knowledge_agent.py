import os
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from backend.rag.vectorstore import search_policies


KNOWLEDGE_SYSTEM_PROMPT = """
You are the Knowledge specialist for EnterpriseAssist. You answer questions
about company policies (leave, benefits, IT, finance policies) using the
search_policy tool. Base your answers strictly on retrieved text. If the
retrieved chunks don't contain the answer, say the policy isn't available
rather than guessing. Refer to the organization as "our company", never by
a name found in the retrieved text.

If the employee just greets you or asks what you can help with, respond
briefly and conversationally - mention you can help with HR, IT, Finance,
Travel, and company policy questions. Don't call search_policy for these.
"""


class KnowledgeState(TypedDict):
    messages: Annotated[list, add_messages]


def build_knowledge_tools():
    @tool
    def search_policy(query: str) -> str:
        """Search company policy documents for relevant information."""
        chunks = search_policies(query, k=3)
        if not chunks:
            return "No relevant policy information found."
        return "\n\n---\n\n".join(chunks)

    return [search_policy]


def build_knowledge_graph():
    tools = build_knowledge_tools()
    llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", api_key=os.getenv("GEMINI_API_KEY"))
    llm_with_tools = llm.bind_tools(tools)

    def knowledge_node(state: KnowledgeState):
        full_messages = [{"role": "system", "content": KNOWLEDGE_SYSTEM_PROMPT}] + state["messages"]
        response = llm_with_tools.invoke(full_messages)
        return {"messages": [response]}

    tool_node = ToolNode(tools)

    graph = StateGraph(KnowledgeState)
    graph.add_node("knowledge", knowledge_node)
    graph.add_node("tools", tool_node)
    graph.add_edge(START, "knowledge")
    graph.add_conditional_edges("knowledge", lambda s: "tools" if getattr(s["messages"][-1], "tool_calls", None) else END)
    graph.add_edge("tools", "knowledge")

    return graph.compile(), tools