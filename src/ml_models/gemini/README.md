# Gemini API SDK

This SDK provides a client for interacting with the Google Gemini API.

## Installation

Ensure you have the required dependencies installed:

```bash
poetry install
```

## Configuration

Set your Gemini API key as an environment variable:

```
export GEMINI_API_KEY="your-api-key-here"
```

## Usage

Here's a basic example of how to use the `GeminiClient` to generate text:

```python
from src.ml_models.gemini import GeminiClient, GeminiModel

# Initialize the client
client = GeminiClient()

# Define the model and prompt
model = GeminiModel.GEMINI_2_5_FLASH
prompt = "What is the meaning of life?"

# Generate text
response_text = client.generate_text(model, prompt)

if response_text:
    print(response_text)
```

### Multimodal Usage (Text and Image)

To send a multimodal prompt with both text and an image, you can use the `generate_content` method with helper utilities:

```python
from pathlib import Path
from src.ml_models.gemini import GeminiClient, GeminiModel
from src.ml_models.gemini.utils import create_text_part, create_image_part, load_image_as_base64

client = GeminiClient()

# Prepare the prompt parts
text_part = create_text_part("What is in this image?")

image_path = Path("path/to/your/image.jpg")
image_data = load_image_as_base64(image_path)
image_part = create_image_part("image/jpeg", image_data)

# Combine parts into a content request
prompt_parts = [text_part, image_part]

# Generate content
response = client.generate_content(GeminiModel.GEMINI_2_5_FLASH, prompt_parts)

if response and response.text:
    print(response.text)

### Streaming Usage

The SDK supports streaming responses for both synchronous and asynchronous operations, allowing you to process content as it's being generated.

#### Synchronous Streaming

Use the `stream_content` method to receive a stream of `StreamingDelta` objects. You can iterate over the response to process chunks in real-time.

```python
from src.ml_models.gemini import GeminiClient, GeminiModel

client = GeminiClient()
model = GeminiModel.GEMINI_2_5_FLASH
prompt = "Write a short story about a robot who discovers music."

# Start the stream
streaming_response = client.stream_content(model, prompt)

# Iterate over the streaming deltas
full_text = ""
for delta in streaming_response:
    if delta.text:
        print(delta.text, end="", flush=True)
        full_text += delta.text

print("\n\n--- Final Text ---")
print(full_text)
```

You can also use the `collect()` helper method to get the full text after the stream is complete:

```python
streaming_response = client.stream_content(model, prompt)
full_text = streaming_response.collect()
print(full_text)
```

#### Synchronous Streaming with a Callback

You can provide a `callback` function to `stream_content` to process each delta as it arrives.

```python
from src.ml_models.gemini import StreamingDelta

def my_callback(delta: StreamingDelta):
    if delta.text:
        print(f"Callback received: {delta.text}")

streaming_response = client.stream_content(model, prompt, callback=my_callback)

# You still need to consume the iterator for the callbacks to fire
list(streaming_response)
```

#### Asynchronous Streaming

For asynchronous applications, use `astream_content`.

```python
import asyncio
from src.ml_models.gemini import GeminiClient, GeminiModel

async def main():
    client = GeminiClient()
    model = GeminiModel.GEMINI_2_5_FLASH
    prompt = "Write a short async story."

    # Start the async stream
    streaming_response = await client.astream_content(model, prompt)

    # Asynchronously iterate over the deltas
    full_text = ""
    async for delta in streaming_response:
        if delta.text:
            print(delta.text, end="", flush=True)
            full_text += delta.text
    
    print(f"\n\n--- Final Async Text ---\n{full_text}")

    # Or collect the full text asynchronously
    streaming_response = await client.astream_content(model, prompt)
    full_text = await streaming_response.acollect()
    print(f"\n--- Collected Async Text ---\n{full_text}")

if __name__ == "__main__":
    asyncio.run(main())
```
```
