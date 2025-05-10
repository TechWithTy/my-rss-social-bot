"""
text_utils.py
Utility functions for text dispatch pipeline.
"""
from typing import Dict, Any
import json

# * Helper: Extract tool call data from LLM response
def extract_tool_call(llm_response: Dict[str, Any], function_name: str) -> Dict[str, Any]:
    tool_calls = llm_response["choices"][0]["message"]["tool_calls"]
    call = next((call for call in tool_calls if call["function"]["name"] == function_name), None)
    if call:
        return json.loads(call["function"]["arguments"])
    return {}

# * Helper: Clean post text for readability
def clean_post_text(text: str) -> str:
    """
    Clean and format the post text for better readability.
    """
    return text.strip().replace("\n\n", "\n").replace("  ", " ")
