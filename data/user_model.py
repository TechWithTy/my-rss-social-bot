from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum


@dataclass
class PollinationsConfig:
    default_model: str = "openai"
    seed: int = 42
    temperature: float = 0.7
    jsonMode: bool = True
    private: bool = True

    # Nested configurations
    openai_compatible: Dict[str, Any] = field(default_factory=dict)
    native_post: Dict[str, Any] = field(default_factory=dict)
    native_get: Dict[str, Any] = field(default_factory=dict)
    pollinations_image_get: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OpenAIConfig:
    name: str = "gpt-4"
    text_model: str = "gpt-4o-mini"
    image_model: str = "dall-e-3"
    image_size: str = "1024x1024"
    temperature: float = 0.7
    top_p: float = 0.95
    response_format: str = "json"
    tool: Optional[str] = None
    available_models: List[str] = field(default_factory=list)


@dataclass
class DeepSeekConfig:
    text_model: str = "deepseek-chat"
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0
    response_format: str = "json_object"
    temperature: float = 0.7
    max_tokens: int = 500
    tools: str = "function"
    tool_choice: str = "auto"
    top_p: float = 0.95
    logprobs: bool = False
    top_logprobs: int = 5
    available_models: List[str] = field(default_factory=list)


@dataclass
class AnthropicConfig:
    text_model: str = "claude-3-sonnet-20240229"
    temperature: float = 0.7
    max_tokens: int = 500
    top_p: float = 0.9
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop_sequences: List[str] = field(default_factory=list)
    system: str = "You're a professional copywriter helping turn blog posts into viral LinkedIn content."
    available_models: List[str] = field(default_factory=list)
    message_format: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class HuggingFaceConfig:
    text_model: str = "mistralai/Mistral-7B-Instruct-v0.1"
    image_model: str = "runwayml/stable-diffusion-v1-5"
    video_model: str = "runwayml/stable-diffusion-v1-5"
    temperature: float = 0.7
    max_tokens: int = 500
    available_models: List[str] = field(default_factory=list)
    available_tools: List[str] = field(default_factory=list)


@dataclass
class CustomConfig:
    enabled: bool = False
    text_model: str = "your-custom-text_model"
    temperature: float = 0.7
    max_tokens: int = 500
    url: str = "https://your-custom-api.com/v1/completions"
    headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class LLMProviders:
    Pollinations: PollinationsConfig = field(default_factory=PollinationsConfig)
    OpenAI: OpenAIConfig = field(default_factory=OpenAIConfig)
    DeepSeek: DeepSeekConfig = field(default_factory=DeepSeekConfig)
    Anthropic: AnthropicConfig = field(default_factory=AnthropicConfig)
    HuggingFace: HuggingFaceConfig = field(default_factory=HuggingFaceConfig)
    Custom: CustomConfig = field(default_factory=CustomConfig)


@dataclass
class UserProfile:
    medium_username: str = "codingoni"
    wix_url: Optional[str] = None
    wordpress_url: Optional[str] = None
    target_audience: str = "Non Technical People Looking For Tech Thought Leadership"
    professional_summary: str = "I'm a Software Engineer with a passion for creating innovative solutions and sharing my knowledge with the world."
    resume_url: str = "https://www.linkedin.com/in/your-linkedin-url"
    llm: LLMProviders = field(default_factory=LLMProviders)
    cache: Dict[str, Optional[Dict[str, str]]] = field(default_factory=dict)
    storage: Dict[str, str] = field(default_factory=dict)


@dataclass
class LinkedInConfig:
    enabled: bool = True
    post_format: str = "Text"
    formatting_instructions: str = (
        "\n\nIMPORTANT: Format the post with proper line breaks for readability."
    )
    maximum_characters: int = 2000


@dataclass
class SocialMediaPlatforms:
    linkedin: LinkedInConfig = field(default_factory=LinkedInConfig)


@dataclass
class GenerateText:
    enabled: bool = True
    user_description: str = (
        "If true, generates a tailored AI Social Media Post and An Image Or Gif"
    )
    prompt: str = (
        "Create a high-quality AI-generated image relevant to the blog content."
    )
    LLM: str = "Pollinations_Text_Advanced"


@dataclass
class GenerateImage:
    enabled: bool = True
    user_description: str = (
        "If true, generates a fallback image if the prompt fails to create one"
    )
    width: int = 1024
    height: int = 1024
    prompt: str = (
        "Create a high-quality AI-generated image relevant to the blog content."
    )
    LLM: str = "Pollinations_Image_Get"


@dataclass
class FetchGif:
    enabled: bool = True
    user_description: str = "If true, ai suggests tags from giphy then pick the giph with the most relevant title"
    prompt: str = (
        "return atleast 3 giphy search terms in the returned object in an array"
    )


@dataclass
class GenerateVideo:
    enabled: bool = False
    user_description: str = (
        "If true, includes a video in the LinkedIn post to boost engagement."
    )
    prompt: str = "Generate a video that highlights the key points of the blog post."


@dataclass
class CreativeConfig:
    generate_image: GenerateImage = field(default_factory=GenerateImage)
    fetch_gif: FetchGif = field(default_factory=FetchGif)
    generate_video: GenerateVideo = field(default_factory=GenerateVideo)


@dataclass
class ViralFormattingOption:
    enabled: bool = True
    description: str = ""


@dataclass
class ViralPostingConfig:
    include_viral_formatting: ViralFormattingOption = field(
        default_factory=lambda: ViralFormattingOption(
            enabled=True,
            description="Ensures AI-generated posts follow viral structures.",
        )
    )

    attention_grabbing_intro: ViralFormattingOption = field(
        default_factory=lambda: ViralFormattingOption(
            enabled=True,
            description="First sentence must hook the reader to capture attention.",
        )
    )

    emotional_storytelling: ViralFormattingOption = field(
        default_factory=lambda: ViralFormattingOption(
            enabled=True,
            description="Includes personal/emotional elements to increase relatability.",
        )
    )

    extreme_statements: ViralFormattingOption = field(
        default_factory=lambda: ViralFormattingOption(
            enabled=False,
            description="Uses bold statements to spark engagement/debate (if enabled).",
        )
    )

    relatable_experiences: ViralFormattingOption = field(
        default_factory=lambda: ViralFormattingOption(
            enabled=True,
            description="Ensures the post connects with the audience's daily struggles.",
        )
    )

    actionable_takeaways: ViralFormattingOption = field(
        default_factory=lambda: ViralFormattingOption(
            enabled=True,
            description="Posts must offer practical insights or solutions for readers.",
        )
    )

    data_backed_claims: ViralFormattingOption = field(
        default_factory=lambda: ViralFormattingOption(
            enabled=True,
            description="Uses real data & examples to establish credibility and trust.",
        )
    )


@dataclass
class ViralPostExample:
    text: str
    engagement: str
    creative: str
    creative_asset: str
    reason: str


@dataclass
class TextConfig:
    generate_text: GenerateText = field(default_factory=GenerateText)


@dataclass
class AIConfig:
    default_response_instructions: str = "Return EITHER a generated JSON image (Creative and ImageAsset) if a creative prompt is provided OR GifSearchTags if not—never both."
    custom_system_instructions: str = "Return EITHER a generated JSON image (Creative and ImageAsset) if a creative prompt is provided OR GifSearchTags if not—never both."
    custom_user_instructions: str = 'Example response: { "Text": "Your message here.", "Creative": "[IMG] A relevant visual description."...'

    text: TextConfig = field(default_factory=TextConfig)
    creative: CreativeConfig = field(default_factory=CreativeConfig)
    viral_posting: ViralPostingConfig = field(default_factory=ViralPostingConfig)
    viral_posts_i_liked: List[ViralPostExample] = field(default_factory=list)


@dataclass
class HashtagConfig:
    default_tags: List[str] = field(
        default_factory=lambda: [
            "#AI",
            "#MachineLearning",
            "#DataScience",
            "#Automation",
            "#Technology",
        ]
    )
    custom_tags: List[str] = field(default_factory=list)


@dataclass
class UserPreferences:
    user_profile: UserProfile = field(default_factory=UserProfile)
    social_media_to_post_to: SocialMediaPlatforms = field(
        default_factory=SocialMediaPlatforms
    )
    ai: AIConfig = field(default_factory=AIConfig)
    hashtags: HashtagConfig = field(default_factory=HashtagConfig)


# Example of instantiating the model
def create_default_preferences() -> UserPreferences:
    """Create a default UserPreferences instance with all default values."""
    return UserPreferences()


def load_preferences_from_dict(data: Dict[str, Any]) -> UserPreferences:
    """Load preferences from a dictionary (e.g., parsed from YAML)."""
    # This would need a more complex implementation to properly map
    # the nested dictionary to our data classes
    # For demonstration purposes only
    return UserPreferences()


# Usage
if __name__ == "__main__":
    # Example of creating default preferences
    preferences = create_default_preferences()

    # Or loading from config
    # import yaml
    # with open('config.yaml', 'r') as f:
    #     config_data = yaml.safe_load(f)
    #     preferences = load_preferences_from_dict(config_data)

    print(f"User profile name: {preferences.user_profile.medium_username}")
    print(f"Selected OpenAI model: {preferences.user_profile.llm.OpenAI.text_model}")
