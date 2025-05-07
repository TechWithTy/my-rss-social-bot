from config._data.user.blogs.plan import BlogPlan
from config._data.user.blogs.posted import PostedBlog

blog_plan = BlogPlan.model_construct()
posted_blog = PostedBlog.model_construct()

__all__ = ["blog_plan", "posted_blog", "BlogPlan", "PostedBlog"]
