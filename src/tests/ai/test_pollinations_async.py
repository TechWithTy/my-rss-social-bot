import sys
import os
import pytest
import asyncio
from utils.prompt_builder import init_globals_for_test

from models.pollinations_generator import (
    generate_image,
    list_image_models,
    generate_text,
    generate_text_advanced,
    generate_audio,
    list_text_models,

    call_openai_compatible_endpoint
)


# Initialize the state
init_globals_for_test()

# Add src path for module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))



# Constants for tests
TEST_PROMPT = "hello world"
TEST_IMAGE_PROMPT = "a futuristic city skyline at sunset"
TEST_PAYLOAD = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is artificial intelligence?"}
        ],
        "model": "openai",
        "seed": 42,
        "jsonMode": True,  
        "private": True,  
        "reasoning_effort": "high" 
    }



@pytest.mark.asyncio
async def test_generate_image():
    url = await generate_image(TEST_IMAGE_PROMPT)
    assert url is not None and url.startswith("http"), "❌ generate_image should return a valid image URL"
    print(f"✅ generate_image passed:\n{url}")


@pytest.mark.asyncio
async def test_list_image_models():
    models = await list_image_models()
    assert models, "❌ No models returned by list_image_models"
    assert isinstance(models, list), "❌ Expected a list of image models"
    assert all(isinstance(m, str) for m in models), "❌ Each image model should be a string"
    print(f"✅ list_image_models returned {len(models)} models")




@pytest.mark.asyncio
async def test_generate_text_advanced():
    result = await generate_text_advanced(TEST_PAYLOAD)

    print("🧪 generate_text_advanced result:", result)

    assert result is not None, "❌ Expected a non-null string response"
    assert isinstance(result, str), "❌ Expected result to be a string"
    assert result.strip(), "❌ Response string should not be empty"

    print("✅ generate_text_advanced passed.")



@pytest.mark.asyncio
async def test_generate_text():
    prompt = "What is the capital of France?"
    result = await generate_text(prompt)

    print("🧪 generate_text result:", result)

    assert result is not None, "❌ Expected a non-null response"
    assert isinstance(result, str), "❌ Expected result to be a string"
    assert result.strip(), "❌ Response string should not be empty"

    print("✅ generate_text passed.")


@pytest.mark.asyncio
async def test_generate_audio():
    audio_url = await generate_audio(TEST_PROMPT, voice="nova")
    assert isinstance(audio_url, str) and audio_url.startswith("http"), "❌ generate_audio should return a valid audio URL"
    print(f"✅ generate_audio passed:\n{audio_url}")


@pytest.mark.asyncio
async def test_list_text_models():
    models = await list_text_models()
    assert models, "❌ No text models returned"
    assert isinstance(models, list), "❌ Expected a list of text model dictionaries"
    assert all(isinstance(m, dict) for m in models), "❌ Each text model should be a dictionary"
    assert all("name" in m and "description" in m for m in models), "❌ Each model should have 'name' and 'description'"
    print(f"✅ list_text_models returned {len(models)} models")

@pytest.mark.asyncio
async def test_openai_chat_completions():
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": "What’s the capital of Japan?"}
        ],
        "temperature": 0.5
    }

    result = await call_openai_compatible_endpoint("/v1/chat/completions", payload=payload)

    assert result is not None, "❌ Response should not be None"
    assert isinstance(result, dict), "❌ Expected a dictionary response"
    assert "choices" in result, "❌ 'choices' key not in response"
    assert isinstance(result["choices"], list) and result["choices"], "❌ 'choices' should be a non-empty list"
    assert "message" in result["choices"][0], "❌ 'message' key missing in first choice"

    print("✅ test_openai_chat_completions passed.")


# @pytest.mark.asyncio
# async def test_completions():
#     payload = {
#         "model": "text-davinci-003",
#         "prompt": TEST_PROMPT,
#         "max_tokens": 30
#     }
#     result = await call_openai_compatible_endpoint("/v1/completions", payload=payload)
#     assert result and "choices" in result, "❌ completions failed"

# # Endpoint Functions
# @pytest.mark.asyncio
# async def test_embeddings():
#     payload = {
#         "model": "text-embedding-ada-002",
#         "input": TEST_PROMPT
#     }
#     result = await call_openai_compatible_endpoint("/v1/embeddings", payload=payload)
#     assert result and "data" in result, "❌ embeddings failed"

# @pytest.mark.asyncio
# async def test_moderations():
#     payload = {
#         "input": "You are so stupid!"
#     }
#     result = await call_openai_compatible_endpoint("/v1/moderations", payload=payload)
#     assert result and "results" in result, "❌ moderations failed"

# @pytest.mark.asyncio
# async def test_list_models():
#     result = await call_openai_compatible_endpoint("/v1/models", method="GET")
#     assert result and "data" in result, "❌ models list failed"

# @pytest.mark.asyncio
# async def test_model_info():
#     result = await call_openai_compatible_endpoint("/v1/models/gpt-3.5-turbo", method="GET")
#     assert result and "id" in result, "❌ model info failed"

# @pytest.mark.asyncio
# async def test_image_generation():
#     payload = {
#         "prompt": TEST_IMAGE_PROMPT,
#         "n": 1,
#         "size": "512x512"
#     }
#     result = await call_openai_compatible_endpoint("/v1/images/generations", payload=payload)
#     assert result and "data" in result, "❌ image generation failed"

# @pytest.mark.asyncio
# async def test_audio_transcriptions():
#     pytest.skip("🔇 Pollinations may not support audio uploads for transcriptions. Manual test or mock required.")

# @pytest.mark.asyncio
# async def test_audio_translations():
#     pytest.skip("🔇 Pollinations may not support audio translations. Manual test or mock required.")

# @pytest.mark.asyncio
# async def test_file_upload_list():
#     pytest.skip("📂 Pollinations likely doesn’t support file endpoints. Skip or mock for now.")

# @pytest.mark.asyncio
# async def test_fine_tuning_jobs():
#     pytest.skip("🧠 Fine-tuning jobs likely unsupported on Pollinations API.")
# @pytest.mark.asyncio
# async def test_fetch_image_feed():
#     feed = await fetch_image_feed()
#     assert feed is not None and isinstance(feed, dict)
#     print("✅ fetch_image_feed passed.")


# @pytest.mark.asyncio
# async def test_fetch_text_feed():
#     feed = await fetch_text_feed()
#     assert feed is not None and isinstance(feed, dict)
#     print("✅ fetch_text_feed passed.")
