import asyncio
import google.generativeai as genai
from typing import Optional, AsyncGenerator, Generator

from .models import GeminiModel
from .types import (
    GenerateContentResponse,
    StreamingDelta,
    StreamingResponse,
    StreamingResponseState,
    StreamConfig,
    StreamingCallback,
    AsyncStreamingCallback
)
from .utils import get_gemini_api_key, get_gemini_logger, handle_api_error
from .exceptions import AuthenticationError

# Configure logging
logger = get_gemini_logger(__name__)

class GeminiClient:
    """Client for interacting with the Gemini API."""

    def __init__(self, api_key: Optional[str] = None):
        """Initializes the Gemini client and configures the API key."""
        try:
            self.api_key = api_key or get_gemini_api_key()
            genai.configure(api_key=self.api_key)
        except AuthenticationError as e:
            logger.error(f"Authentication failed: {e}")
            raise

    def generate_content(self, model: GeminiModel, prompt: str) -> GenerateContentResponse:
        """Generates content using the specified model and prompt."""
        try:
            model_instance = genai.GenerativeModel(model.value)
            response = model_instance.generate_content(prompt)
            return GenerateContentResponse.model_validate(response.to_dict())
        except Exception as e:
            # Catching a broad exception to handle various API errors
            # In a real-world scenario, you might want to catch more specific exceptions from the google-genai library
            logger.error(f"An API error occurred: {e}")
            handle_api_error(e)

    def generate_text(self, model: GeminiModel, prompt: str) -> Optional[str]:
        """A convenience method to generate text directly."""
        response = self.generate_content(model, prompt)
        return response.text

    def stream_content(
        self,
        model: GeminiModel,
        prompt: str,
        config: Optional[StreamConfig] = None,
        callback: Optional[StreamingCallback] = None,
    ) -> StreamingResponse:
        """
        Generates content with streaming support.

        Args:
            model: The Gemini model to use for generation
            prompt: The input prompt
            config: Configuration for the streaming request
            callback: Optional callback function to handle streaming deltas

        Returns:
            StreamingResponse: An iterable of StreamingDelta objects
        """
        config = config or StreamConfig()
        
        def generate() -> Generator[StreamingDelta, None, None]:
            try:
                model_instance = genai.GenerativeModel(model.value)
                response = model_instance.generate_content(
                    prompt,
                    stream=True
                )
                
                # Yield start of stream
                delta = StreamingDelta(
                    text=None,
                    state=StreamingResponseState.START,
                    raw={"model": model.value}
                )
                yield delta
                if callback:
                    callback(delta)

                # Stream chunks
                for chunk in response:
                    if not chunk.parts:
                        continue
                        
                    text = chunk.text
                    if text:
                        delta = StreamingDelta(
                            text=text,
                            state=StreamingResponseState.CONTENT,
                            raw=chunk.to_dict() if hasattr(chunk, 'to_dict') else str(chunk)
                        )
                        yield delta
                        if callback:
                            callback(delta)

                # Yield end of stream
                delta = StreamingDelta(
                    text=None,
                    state=StreamingResponseState.COMPLETE,
                    raw={"status": "complete"}
                )
                yield delta
                if callback:
                    callback(delta)
                    
            except Exception as e:
                logger.error(f"Error in streaming: {e}")
                delta = StreamingDelta(
                    text=str(e),
                    state=StreamingResponseState.ERROR,
                    raw={"error": str(e)}
                )
                if config.on_error:
                    config.on_error(e)
                yield delta
                if callback:
                    callback(delta)
                
                # Re-raise for error handling
                handle_api_error(e)

        return StreamingResponse(stream=generate(), is_async=False)

    async def astream_content(
        self,
        model: GeminiModel,
        prompt: str,
        config: Optional[StreamConfig] = None,
        callback: Optional[AsyncStreamingCallback] = None,
    ) -> StreamingResponse:
        """
        Asynchronously generates content with streaming support.

        Args:
            model: The Gemini model to use for generation
            prompt: The input prompt
            config: Configuration for the streaming request
            callback: Optional async callback function to handle streaming deltas

        Returns:
            StreamingResponse: An async iterable of StreamingDelta objects
        """
        config = config or StreamConfig()
        
        async def generate() -> AsyncGenerator[StreamingDelta, None]:
            try:
                model_instance = genai.GenerativeModel(model.value)
                response = await asyncio.to_thread(
                    model_instance.generate_content,
                    prompt,
                    stream=True
                )
                
                # Yield start of stream
                delta = StreamingDelta(
                    text=None,
                    state=StreamingResponseState.START,
                    raw={"model": model.value}
                )
                yield delta
                if callback:
                    await callback(delta)

                # Stream chunks
                for chunk in response:
                    if not hasattr(chunk, 'parts') or not chunk.parts:
                        continue
                        
                    text = chunk.text if hasattr(chunk, 'text') else ''
                    if text:
                        delta = StreamingDelta(
                            text=text,
                            state=StreamingResponseState.CONTENT,
                            raw=chunk.to_dict() if hasattr(chunk, 'to_dict') else str(chunk)
                        )
                        yield delta
                        if callback:
                            await callback(delta)
                    await asyncio.sleep(0)  # Yield control to the event loop

                # Yield end of stream
                delta = StreamingDelta(
                    text=None,
                    state=StreamingResponseState.COMPLETE,
                    raw={"status": "complete"}
                )
                yield delta
                if callback:
                    await callback(delta)
                    
            except Exception as e:
                logger.error(f"Error in async streaming: {e}")
                delta = StreamingDelta(
                    text=str(e),
                    state=StreamingResponseState.ERROR,
                    raw={"error": str(e)}
                )
                if config.on_error:
                    if asyncio.iscoroutinefunction(config.on_error):
                        await config.on_error(e)
                    else:
                        config.on_error(e)
                yield delta
                if callback:
                    await callback(delta)
                
                # Re-raise for error handling
                handle_api_error(e)

        return StreamingResponse(stream=generate(), is_async=True)

    async def agenerate_content(self, model: GeminiModel, prompt: str) -> GenerateContentResponse:
        """Asynchronously generates content using the specified model and prompt."""
        try:
            model_instance = genai.GenerativeModel(model.value)
            response = await asyncio.to_thread(model_instance.generate_content, prompt)
            return GenerateContentResponse.model_validate(response.to_dict())
        except Exception as e:
            logger.error(f"An API error occurred in async generation: {e}")
            handle_api_error(e)

    async def agenerate_text(self, model: GeminiModel, prompt: str) -> Optional[str]:
        """Asynchronously generates text directly."""
        response = await self.agenerate_content(model, prompt)
        return response.text
