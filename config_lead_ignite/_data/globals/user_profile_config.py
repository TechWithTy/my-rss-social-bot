from config._data.user.user import User

user_profile_config = User.model_dump()

__all__ = ["user_profile_config", "User"]
