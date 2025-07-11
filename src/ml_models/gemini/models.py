from enum import Enum

class GeminiModel(str, Enum):
    """Enum for the available Gemini models."""

    GEMINI_2_5_PRO = "gemini-2.5-pro"
    GEMINI_2_5_FLASH = "gemini-2.5-flash"
    GEMINI_2_5_FLASH_LITE = "gemini-2.5-flash-lite"

    def __str__(self) -> str:
        return self.value
