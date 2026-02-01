"""LangChain and LangGraph streaming adapters for agent integration."""
import asyncio
import json
from typing import AsyncGenerator, Optional, Any, Callable
import logging

logger = logging.getLogger(__name__)

class LangChainAdapter:
    """Adapter for LangChain runnable chains to stream over WebSocket."""
    
    def __init__(self, on_chunk: Callable[[str], None]):
        """Initialize adapter with callback for each chunk.
        
        Args:
            on_chunk: Async callback that receives text chunks
        """
        self.on_chunk = on_chunk
    
    async def stream_chain(self, chain: Any, input_data: dict) -> str:
        """Stream a LangChain chain output.
        
        Args:
            chain: LangChain runnable chain
            input_data: Input dict for the chain
            
        Returns:
            Full accumulated output
        """
        accumulated = ""
        
        try:
            # Stream chunks from the chain
            async for chunk in chain.astream(input_data):
                if isinstance(chunk, str):
                    text = chunk
                elif isinstance(chunk, dict) and "content" in chunk:
                    text = chunk["content"]
                else:
                    text = str(chunk)
                
                accumulated += text
                await self.on_chunk(text)
            
            return accumulated
        except Exception as e:
            logger.error(f"Error streaming chain: {e}")
            raise

class LangGraphAdapter:
    """Adapter for LangGraph state graphs to stream over WebSocket."""
    
    def __init__(self, on_update: Callable[[dict], None]):
        """Initialize adapter with callback for graph updates.
        
        Args:
            on_update: Async callback that receives state updates
        """
        self.on_update = on_update
    
    async def stream_graph(self, graph: Any, input_state: dict) -> dict:
        """Stream a LangGraph computation.
        
        Args:
            graph: LangGraph StateGraph
            input_state: Initial state dict
            
        Returns:
            Final state dict
        """
        try:
            # Stream updates from the graph
            async for event in graph.astream_events(input_state, version="v1"):
                # Emit state updates
                if event.get("event") == "on_chain_end":
                    await self.on_update({
                        "type": "agent.event",
                        "node": event.get("name"),
                        "output": event.get("data", {}).get("output")
                    })
            
            return input_state  # Final state
        except Exception as e:
            logger.error(f"Error streaming graph: {e}")
            raise

class OpenAIStreamAdapter:
    """Direct OpenAI streaming adapter for text completion."""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """Initialize OpenAI adapter.
        
        Args:
            api_key: OpenAI API key
            model: Model name (gpt-4o-mini, gpt-4-turbo, etc.)
        """
        self.api_key = api_key
        self.model = model
    
    async def stream_completion(
        self, 
        messages: list[dict],
        on_chunk: Callable[[str], None],
        **kwargs
    ) -> str:
        """Stream a completion from OpenAI.
        
        Args:
            messages: Chat messages list
            on_chunk: Callback for text chunks
            **kwargs: Additional OpenAI parameters
            
        Returns:
            Full accumulated response
        """
        try:
            from openai import AsyncOpenAI
        except ImportError:
            raise ImportError("openai package required: pip install openai")
        
        client = AsyncOpenAI(api_key=self.api_key)
        accumulated = ""
        
        try:
            # Use completions API (text generation)
            stream = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                **kwargs
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    text = chunk.choices[0].delta.content
                    accumulated += text
                    await on_chunk(text)
            
            return accumulated
        finally:
            await client.close()
