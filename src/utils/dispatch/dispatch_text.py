from utils.prompt_builder import init_globals_for_test, get_prompt_globals
from utils.dispatch.text.text_pipeline_utils import (
    handle_pollinations_text,
    handle_pollinations_text_advanced,
    handle_pollinations_text_completion,
    handle_openai_text,
    handle_huggingface_text,
    handle_deepseek_text,
    handle_claude_text,
    fallback_error_text,
)
from utils.index import get_env_variable

# * Initialize state and test mode
TEST_MODE = get_env_variable("TEST_MODE").lower() == "true"
if TEST_MODE:
    init_globals_for_test()
state = get_prompt_globals()

# * Main async dispatch router for text providers
type Provider = str  # For future: consider Literal types for provider names

async def dispatch_text_pipeline(provider: Provider) -> dict:
    """
    Main text dispatch router. Delegates provider logic to utility functions for maintainability.
    Args:
        provider: Name of the text provider to dispatch to.
    Returns:
        dict: The result of the provider pipeline.
    """
    try:
        match provider:
            case "Pollinations_Text":
                return await handle_pollinations_text(state)
            case "Pollinations_Text_Advanced":
                return await handle_pollinations_text_advanced(state)
            case "Pollinations_Text_Completion":
                return await handle_pollinations_text_completion(state)
            case "OpenAI":
                return await handle_openai_text(state)
            case "HuggingFace":
                return await handle_huggingface_text(state)
            case "DeepSeek":
                return await handle_deepseek_text(state)
            case "Claude":
                return await handle_claude_text(state)
            case _:
                raise ValueError(f"❌ Unsupported provider: {provider}")
    except Exception as e:
        print(f"❌ Error in dispatch_text_pipeline: {str(e)}")
        return fallback_error_text(e)
