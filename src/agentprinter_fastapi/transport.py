"""Enhanced WebSocket transport with backoff, resume, and ordering."""
import time
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class MessageSequence:
    """Track message ordering and acknowledgment."""
    sequence_number: int
    timestamp: float
    message_id: str
    payload: dict
    acked: bool = False

class ResumableTransport:
    """WebSocket transport with session resumption capability."""
    
    def __init__(self, resume_timeout: int = 60):
        """Initialize resumable transport.
        
        Args:
            resume_timeout: Seconds to keep session for resumption
        """
        self.resume_timeout = resume_timeout
        self.sessions: Dict[str, dict] = {}
        self.message_history: Dict[str, list[MessageSequence]] = {}
    
    def create_session(self, client_id: str) -> str:
        """Create a resumable session."""
        session_id = f"{client_id}:{time.time()}"
        self.sessions[session_id] = {
            "created": time.time(),
            "last_ack": 0,
            "sequence": 0
        }
        self.message_history[session_id] = []
        logger.info(f"Created session: {session_id}")
        return session_id
    
    def can_resume_session(self, session_id: str) -> bool:
        """Check if session can be resumed."""
        if session_id not in self.sessions:
            return False
        
        created = self.sessions[session_id]["created"]
        age = time.time() - created
        return age < self.resume_timeout
    
    def resume_session(self, session_id: str, last_ack: int) -> list[MessageSequence]:
        """Resume session and get unacked messages since last ack.
        
        Args:
            session_id: Session to resume
            last_ack: Last acknowledged sequence number
            
        Returns:
            List of unacked messages to retransmit
        """
        if not self.can_resume_session(session_id):
            raise ValueError(f"Cannot resume session: {session_id}")
        
        history = self.message_history[session_id]
        # Return messages after last_ack
        return [msg for msg in history if msg.sequence_number > last_ack]
    
    def track_message(self, session_id: str, message_id: str, payload: dict) -> int:
        """Track outgoing message with sequence number.
        
        Args:
            session_id: Session ID
            message_id: Message identifier
            payload: Message payload
            
        Returns:
            Sequence number
        """
        session = self.sessions[session_id]
        seq = session["sequence"]
        session["sequence"] += 1
        
        msg = MessageSequence(
            sequence_number=seq,
            timestamp=time.time(),
            message_id=message_id,
            payload=payload
        )
        
        self.message_history[session_id].append(msg)
        return seq
    
    def ack_message(self, session_id: str, sequence_number: int):
        """Mark message as acknowledged."""
        history = self.message_history.get(session_id, [])
        for msg in history:
            if msg.sequence_number <= sequence_number:
                msg.acked = True
        
        self.sessions[session_id]["last_ack"] = sequence_number

class ExponentialBackoff:
    """Exponential backoff strategy for reconnection."""
    
    def __init__(self, initial: float = 1.0, max_delay: float = 60.0, factor: float = 2.0):
        """Initialize backoff strategy.
        
        Args:
            initial: Initial backoff in seconds
            max_delay: Maximum backoff delay
            factor: Multiplier for each attempt
        """
        self.initial = initial
        self.max_delay = max_delay
        self.factor = factor
        self.attempt = 0
    
    def next_delay(self) -> float:
        """Get next backoff delay."""
        delay = min(self.initial * (self.factor ** self.attempt), self.max_delay)
        self.attempt += 1
        return delay
    
    def reset(self):
        """Reset backoff on successful connection."""
        self.attempt = 0

class OrderedMessageBuffer:
    """Buffer and order messages in sequence number order."""
    
    def __init__(self):
        self.buffer: Dict[int, Any] = {}
        self.next_expected = 0
    
    def add_message(self, sequence: int, message: Any) -> list[Any]:
        """Add message to buffer, return ordered messages if in sequence.
        
        Args:
            sequence: Message sequence number
            message: Message payload
            
        Returns:
            List of ordered messages that can now be processed
        """
        self.buffer[sequence] = message
        
        # Collect consecutive ordered messages
        ordered = []
        while self.next_expected in self.buffer:
            ordered.append(self.buffer.pop(self.next_expected))
            self.next_expected += 1
        
        return ordered
    
    def get_pending_sequences(self) -> list[int]:
        """Get list of missing sequence numbers."""
        if not self.buffer:
            return []
        
        pending = []
        for i in range(self.next_expected, max(self.buffer.keys()) + 1):
            if i not in self.buffer:
                pending.append(i)
        
        return pending

# Global instances
resumable_transport = ResumableTransport()
backoff_strategy = ExponentialBackoff()
message_buffer = OrderedMessageBuffer()
