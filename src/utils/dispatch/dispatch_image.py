from utils.prompt_builder import init_globals_for_test, get_prompt_globals
from utils.dispatch.image.image_pipeline_utils import (
    handle_pollinations_image,
    handle_pollinations_image_get,
    handle_openai_image,
    handle_huggingface_image,
    handle_giphy_image,
    fallback_error_image,
)
from utils.index import get_env_variable
from typing import Optional, Dict

# * Initialize state and test mode
TEST_MODE = get_env_variable("TEST_MODE").lower() == "true"
if TEST_MODE:
    init_globals_for_test()
state = get_prompt_globals()

# * Main async dispatch router for image providers
type Provider = str  # For future: consider Literal types for provider names

async def dispatch_image_pipeline(
    provider: Provider,
    creative_prompt_output: Optional[str] = None,
    gif_tags: Optional[Dict] = None,
) -> dict:
    """
    Main image dispatch router. Delegates provider logic to utility functions for maintainability.
    Args:
        provider: Name of the image provider to dispatch to.
        creative_prompt_output: The prompt for creative image generation (if required).
        gif_tags: Tags for GIF search (if required).
    Returns:
        dict: The result of the provider pipeline.
    """
    try:
        match provider:
            case "Pollinations_Image":
                return await handle_pollinations_image(creative_prompt_output)
            case "Pollinations_Image_Get":
                return await handle_pollinations_image_get(creative_prompt_output)
            case "OpenAI":
                return await handle_openai_image(creative_prompt_output)
            case "HuggingFace":
                return await handle_huggingface_image(creative_prompt_output)
            case "Giphy":
                return await handle_giphy_image(gif_tags)
            case _:
                raise ValueError(f"❌ Unsupported provider: {provider}")
    except Exception as e:
        print(f"❌ Error in dispatch_image_pipeline: {str(e)}")
        return fallback_error_image(e)
