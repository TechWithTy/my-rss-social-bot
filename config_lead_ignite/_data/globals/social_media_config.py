from config._data.user.post_settings.main import SocialMediaConfig

social_media_config = SocialMediaConfig().model_dump()

__all__ = ["social_media_config", "SocialMediaConfig"]
