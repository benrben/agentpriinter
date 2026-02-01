"""Example LangChain and LangGraph agents for AgentPrinter."""
from typing import Any, Optional

class ExampleLangChainAgent:
    """Example: Simple LangChain agent setup."""
    
    @staticmethod
    def create_simple_math_agent():
        """Create a simple math agent using LangChain.
        
        Example usage:
        ```python
        agent_executor = ExampleLangChainAgent.create_simple_math_agent()
        adapter = LangChainAgentAdapter(on_event=my_event_handler)
        result = await adapter.run_agent(agent_executor, {"input": "What is 25 * 4?"})
        ```
        """
        try:
            from langchain.agents import initialize_agent, Tool
            from langchain.llm import OpenAI
            from langchain.tools import tool
            
            @tool
            def multiply(a: int, b: int) -> int:
                """Multiply two numbers."""
                return a * b
            
            @tool
            def add(a: int, b: int) -> int:
                """Add two numbers."""
                return a + b
            
            @tool
            def subtract(a: int, b: int) -> int:
                """Subtract two numbers."""
                return a - b
            
            tools = [multiply, add, subtract]
            
            # You can use your OpenAI key from environment
            llm = OpenAI(temperature=0)
            
            agent_executor = initialize_agent(
                tools,
                llm,
                agent="zero-shot-react-description",
                verbose=True
            )
            
            return agent_executor
        except ImportError:
            raise ImportError("Install langchain: pip install langchain openai")

class ExampleLangGraphAgent:
    """Example: LangGraph state graph setup."""
    
    @staticmethod
    def create_simple_research_graph():
        """Create a simple research workflow using LangGraph.
        
        Nodes:
        1. generate_query - Generate a search query
        2. search - Simulate search results
        3. analyze - Analyze results
        4. summarize - Create summary
        
        Example usage:
        ```python
        graph = ExampleLangGraphAgent.create_simple_research_graph()
        adapter = LangGraphAgentAdapter(on_event=my_event_handler)
        result = await adapter.run_graph(graph, {"topic": "Python async/await"})
        ```
        """
        try:
            from langgraph.graph import StateGraph
            from pydantic import BaseModel, Field
            from typing import List
            
            class ResearchState(BaseModel):
                """State for research workflow."""
                topic: str
                query: Optional[str] = None
                search_results: Optional[List[str]] = None
                analysis: Optional[str] = None
                summary: Optional[str] = None
            
            def generate_query(state: ResearchState) -> ResearchState:
                """Generate search query from topic."""
                query = f"Recent research on: {state.topic}"
                state.query = query
                return state
            
            def search(state: ResearchState) -> ResearchState:
                """Simulate search (in real app, call actual search)."""
                results = [
                    f"Result 1: Overview of {state.topic}",
                    f"Result 2: Advanced concepts in {state.topic}",
                    f"Result 3: Best practices for {state.topic}",
                ]
                state.search_results = results
                return state
            
            def analyze(state: ResearchState) -> ResearchState:
                """Analyze search results."""
                if state.search_results:
                    analysis = f"Analysis: {len(state.search_results)} results found. " \
                               f"Key areas: fundamentals, advanced concepts, best practices."
                    state.analysis = analysis
                return state
            
            def summarize(state: ResearchState) -> ResearchState:
                """Create final summary."""
                summary = f"Research Summary on {state.topic}: " \
                         f"Found {len(state.search_results or [])} relevant resources. " \
                         f"Key findings: {state.analysis}"
                state.summary = summary
                return state
            
            # Build graph
            graph = StateGraph(ResearchState)
            graph.add_node("generate_query", generate_query)
            graph.add_node("search", search)
            graph.add_node("analyze", analyze)
            graph.add_node("summarize", summarize)
            
            # Connect nodes
            graph.add_edge("generate_query", "search")
            graph.add_edge("search", "analyze")
            graph.add_edge("analyze", "summarize")
            
            # Set entry and exit
            graph.set_entry_point("generate_query")
            graph.set_finish_point("summarize")
            
            return graph.compile()
        
        except ImportError:
            raise ImportError("Install langgraph: pip install langgraph")

# Example: Quick integration code
"""
# In your WebSocket action handler:
from agentprinter_fastapi.agent_adapters import (
    LangChainAgentAdapter, 
    LangGraphAgentAdapter,
    AgentWebSocketBridge
)
from agentprinter_fastapi.agents.examples import (
    ExampleLangChainAgent,
    ExampleLangGraphAgent
)

@action_router.action("run_math_agent")
async def handle_math_agent(message, websocket):
    # Setup bridge to convert agent events to UI updates
    bridge = AgentWebSocketBridge(websocket.send_json)
    
    # Create agent
    agent_executor = ExampleLangChainAgent.create_simple_math_agent()
    adapter = LangChainAgentAdapter(on_event=bridge.on_agent_event)
    
    # Run agent
    user_input = message.payload.get("input", "What is 25 * 4?")
    result = await adapter.run_agent(agent_executor, {"input": user_input})
    
    # Send final result
    await websocket.send_json(Message(
        type="ui.patch",
        header=MessageHeader(trace_id=message.header.trace_id),
        payload={"target": "result", "text": str(result)}
    ).model_dump(mode='json'))

@action_router.action("run_research_agent")
async def handle_research_agent(message, websocket):
    # Setup bridge
    bridge = AgentWebSocketBridge(websocket.send_json)
    
    # Create graph
    graph = ExampleLangGraphAgent.create_simple_research_graph()
    adapter = LangGraphAgentAdapter(on_event=bridge.on_agent_event)
    
    # Run graph
    topic = message.payload.get("topic", "Python")
    result = await adapter.run_graph(graph, {"topic": topic})
    
    # Send final result
    await websocket.send_json(Message(
        type="ui.patch",
        header=MessageHeader(trace_id=message.header.trace_id),
        payload={"target": "summary", "text": result.get("summary", "")}
    ).model_dump(mode='json'))
"""
