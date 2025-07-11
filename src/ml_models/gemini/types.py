from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union, Callable, AsyncGenerator, Generator, Awaitable
from enum import Enum

class Part(BaseModel):
    """A part of a content block, containing text."""
    text: str

class Content(BaseModel):
    """A content block, containing one or more parts."""
    parts: List[Part]

class GenerateContentRequest(BaseModel):
    """Request model for generating content."""
    contents: List[Content]

class Candidate(BaseModel):
    """A candidate response from the model."""
    content: Content

class GenerateContentResponse(BaseModel):
    """Response model for generated content."""
    candidates: List[Candidate]

    @property
    def text(self) -> Optional[str]:
        """Extracts the text from the first candidate's first part."""
        if self.candidates and self.candidates[0].content.parts:
            return self.candidates[0].content.parts[0].text
        return None


class StreamingResponseState(str, Enum):
    """State of a streaming response."""
    START = "start"
    CONTENT = "content"
    COMPLETE = "complete"
    ERROR = "error"


class StreamingDelta(BaseModel):
    """Represents a delta update in a streaming response."""
    text: Optional[str] = None
    state: StreamingResponseState = Field(..., description="Current state of the stream")
    raw: Optional[Dict[str, Any]] = Field(None, description="Raw response from the API")


class StreamConfig(BaseModel):
    """Configuration for streaming requests."""
    max_retries: int = 3
    timeout: float = 30.0
    chunk_timeout: float = 5.0
    on_error: Optional[Callable[[Exception], None]] = None
    on_complete: Optional[Callable[[], None]] = None


StreamingCallback = Callable[[StreamingDelta], None]
AsyncStreamingCallback = Callable[[StreamingDelta], Awaitable[None]]


class StreamingResponse(BaseModel):
    """Wrapper for streaming responses with helper methods."""
    model_config = {
        "arbitrary_types_allowed": True
    }
    
    stream: Union[Generator[StreamingDelta, None, None], AsyncGenerator[StreamingDelta, None]]
    is_async: bool = False

    def __iter__(self):
        if self.is_async:
            raise RuntimeError("Cannot iterate over async stream in sync context")
        return self.stream

    def __aiter__(self):
        if not self.is_async:
            raise RuntimeError("Cannot iterate over sync stream in async context")
        # An async generator is already an async iterator, so we can return it directly.
        return self.stream

    def collect(self) -> str:
        """Collect all text from the stream (synchronous)."""
        if self.is_async:
            raise RuntimeError("Cannot collect from async stream in sync context")
        return "".join(delta.text for delta in self.stream if delta.text)

    async def acollect(self) -> str:
        """Collect all text from the stream (asynchronous)."""
        if not self.is_async:
            raise RuntimeError("Cannot collect from sync stream in async context")
        return "".join([delta.text async for delta in self.stream if delta.text])
