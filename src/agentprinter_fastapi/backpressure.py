"""Backpressure controls and rate limiting for message processing."""
import time
import asyncio
from typing import Optional
from collections import deque
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """Token bucket rate limiter for messages per client."""
    
    def __init__(self, rate: int = 100, window_seconds: int = 1):
        """Initialize rate limiter.
        
        Args:
            rate: Max messages per window
            window_seconds: Time window in seconds
        """
        self.rate = rate
        self.window = window_seconds
        self.buckets: dict[str, deque] = {}
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if a client is within rate limit."""
        now = time.time()
        cutoff = now - self.window
        
        if client_id not in self.buckets:
            self.buckets[client_id] = deque()
        
        bucket = self.buckets[client_id]
        
        # Remove old timestamps outside window
        while bucket and bucket[0] < cutoff:
            bucket.popleft()
        
        # Check if under limit
        if len(bucket) < self.rate:
            bucket.append(now)
            return True
        
        return False
    
    def get_remaining(self, client_id: str) -> int:
        """Get remaining messages for client in current window."""
        now = time.time()
        cutoff = now - self.window
        
        if client_id not in self.buckets:
            return self.rate
        
        bucket = self.buckets[client_id]
        
        # Count messages still in window
        in_window = sum(1 for ts in bucket if ts > cutoff)
        return max(0, self.rate - in_window)

class BackpressureController:
    """Manages message queuing and backpressure for slow consumers."""
    
    def __init__(self, max_queue_size: int = 1000, drain_timeout: float = 5.0):
        """Initialize backpressure controller.
        
        Args:
            max_queue_size: Max messages queued per client
            drain_timeout: Timeout for queue drainage
        """
        self.max_queue_size = max_queue_size
        self.drain_timeout = drain_timeout
        self.queues: dict[str, asyncio.Queue] = {}
    
    async def enqueue(self, client_id: str, message: dict) -> bool:
        """Enqueue a message, return False if queue is full (backpressure).
        
        Args:
            client_id: Client identifier
            message: Message to enqueue
            
        Returns:
            True if enqueued, False if backpressure (queue full)
        """
        if client_id not in self.queues:
            self.queues[client_id] = asyncio.Queue(maxsize=self.max_queue_size)
        
        queue = self.queues[client_id]
        
        if queue.full():
            logger.warning(f"Backpressure: queue full for {client_id}")
            return False
        
        try:
            queue.put_nowait(message)
            return True
        except asyncio.QueueFull:
            return False
    
    async def dequeue(self, client_id: str, timeout: Optional[float] = None) -> Optional[dict]:
        """Dequeue a message for a client.
        
        Args:
            client_id: Client identifier
            timeout: Wait timeout in seconds
            
        Returns:
            Message or None if timeout
        """
        if client_id not in self.queues:
            self.queues[client_id] = asyncio.Queue(maxsize=self.max_queue_size)
        
        queue = self.queues[client_id]
        
        try:
            return await asyncio.wait_for(queue.get(), timeout=timeout or self.drain_timeout)
        except asyncio.TimeoutError:
            return None
    
    def queue_depth(self, client_id: str) -> int:
        """Get current queue depth for client."""
        if client_id not in self.queues:
            return 0
        return self.queues[client_id].qsize()

# Global instances
rate_limiter = RateLimiter(rate=1000, window_seconds=1)  # 1000 msg/sec per client
backpressure = BackpressureController(max_queue_size=5000)
connection_rate_limiter = RateLimiter(rate=100, window_seconds=1)  # 100 connections/sec per IP (high default, can be configured)
