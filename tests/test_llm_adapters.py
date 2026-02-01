"""Tests for LLM adapters (OpenAI integration + streaming)."""
import pytest
import asyncio
from agentprinter_fastapi.adapters import LangChainAdapter, OpenAIStreamAdapter


@pytest.mark.asyncio
async def test_langchain_adapter_streams_chunks():
    """Test LangChainAdapter collects chunks."""
    chunks = []
    
    async def on_chunk(text: str):
        chunks.append(text)
    
    adapter = LangChainAdapter(on_chunk)
    
    # Mock chain
    class MockChain:
        async def astream(self, input_data):
            for chunk in ["Hello", " ", "World"]:
                yield chunk
    
    result = await adapter.stream_chain(MockChain(), {})
    
    assert len(chunks) == 3
    assert result == "Hello World"


@pytest.mark.asyncio
async def test_langchain_adapter_handles_dict_chunks():
    """Test LangChainAdapter handles dict chunks with content."""
    chunks = []
    
    async def on_chunk(text: str):
        chunks.append(text)
    
    adapter = LangChainAdapter(on_chunk)
    
    # Mock chain returning dicts
    class MockChain:
        async def astream(self, input_data):
            yield {"content": "Chunk1"}
            yield {"content": "Chunk2"}
    
    result = await adapter.stream_chain(MockChain(), {})
    
    assert len(chunks) == 2
    assert result == "Chunk1Chunk2"


@pytest.mark.asyncio
async def test_openai_adapter_real_stream(openai_key, openai_model):
    """Real test: Stream completion from OpenAI."""
    adapter = OpenAIStreamAdapter(openai_key, openai_model)
    
    chunks = []
    
    async def on_chunk(text: str):
        chunks.append(text)
    
    messages = [
        {"role": "user", "content": "Say 'Hello from OpenAI' in exactly 5 words."}
    ]
    
    result = await adapter.stream_completion(messages, on_chunk, max_tokens=50)
    
    # Verify streaming worked
    assert len(chunks) > 0
    assert len(result) > 0
    assert "Hello" in result.lower() or "hello" in result.lower()
    
    print(f"OpenAI response: {result}")
    print(f"Chunks: {len(chunks)}")


@pytest.mark.asyncio
async def test_openai_adapter_error_handling(openai_key):
    """Test that OpenAI adapter handles errors gracefully."""
    adapter = OpenAIStreamAdapter("invalid-key", "gpt-4o-mini")
    
    async def on_chunk(text: str):
        pass
    
    messages = [{"role": "user", "content": "test"}]
    
    with pytest.raises(Exception):  # Should raise auth error
        await adapter.stream_completion(messages, on_chunk)
