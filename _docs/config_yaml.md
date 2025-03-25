Here's the documentation for your `config.yaml` configuration, explaining each section with comments on how to customize it for optimal use:

---

### **🛠️ Configure (`config.yaml`)**

This configuration file allows you to customize how your posts are generated, including social media settings, creative content preferences, and integration with different AI models.

---

### **User Profile Settings**
Customize your **user profile** to align with your content and professional background. This section defines your Rss Source Only one source is allowed , target audience, professional summary, and more.

```yaml
user_profile:
  medium_username: "codingoni"  # Your Medium username, used to fetch your posts.
  wix_url: Null  # Optional: Add your website URL if using Wix.
  wordpress_url: Null  # Optional: Add your blog's WordPress URL.
  target_audience: "Non Technical People Looking For Tech Thought Leadership"  # Define your audience.
  professional_summary: "I'm a Software Engineer with a passion for creating innovative solutions..."  # Brief about your professional journey.
  resume_url: "https://www.linkedin.com/in/your-linkedin-url"  # Link to your LinkedIn or resume.
  brand_guidlines: ""  # Add your brand guidelines here.
  llm:  # Defines the settings for the language model used for text generation.
    Pollinations:
      # Common default settings for the Pollinations language model.
      default_model: "openai"
      seed: 42
      temperature: 0.7
      jsonMode: true
      private: true

      # OpenAI-Compatible Completion Settings
      openai_compatible:
        endpoint: "/v1/chat/completions"
        model: "text-davinci-003"
        prompt: "Your custom prompt"  # Customize the prompt for content generation.
        temperature: 0.7  # Controls the creativity of the generated content (higher = more creative).
        max_tokens: 256  # Maximum number of tokens to generate per request.
        n: 1
        stop: null  # Stop sequence (can be a string or array of strings).
        messages:
          - role: "system"
            content: "You are a helpful assistant."
          - role: "user"
            content: "What is artificial intelligence?"
      # Native Pollinations Completion
      native_post:
        endpoint: "https://text.pollinations.ai/"
        model: "mistral"
        messages:
          - role: "system"
            content: "You're a helpful assistant."
          - role: "user"
            content: "Your User Prompt"
```

### **Creative Preferences (Visuals & Storytelling)**
Define how your posts should be created, including whether to generate images, GIFs, and the type of creative content if both generate_image and post_gif are enabled. Then the ai will choose randomly which asset to use

```yaml
creative:
  generate_image:
    enabled: true  # Set to true to enable AI image generation.
    prompt: "Create a high-quality AI-generated image relevant to the blog content."  # Customize the image description.
  post_gif:
    enabled: true  # Set to true to fetch GIFs for posts.
    gif_search_tags:
      - "motivation"
      - "career growth"
      - "AI revolution"  # Define search tags for GIFs from Giphy.
  viral_posting:
    include_viral_formatting:
      enabled: true  # Use viral formatting for posts.
      description: "Ensure the post follows viral structures." # Your take on viral formatting
    attention_grabbing_intro:
      enabled: true  # Ensure the post starts with an attention-grabbing hook.
      description: "Ensure the post follows viral structures." # Your take on an attention-grabbing intro
    emotional_storytelling:
      enabled: true  # Include emotional elements to increase relatability.
      description: "Ensure the post follows viral structures." # Your take on emotional storytelling
    extreme_statements:
      enabled: false  # Option to use bold or controversial statements.
      description: "Ensure the post follows viral structures." # Your take on extreme statements
    relatable_experiences:
      enabled: true  # Ensure the post resonates with the audience's daily experiences.
      description: "Ensure the post follows viral structures." # Your take on relatable experiences
    actionable_takeaways:
      enabled: true  # Posts should offer practical insights or takeaways.
      description: "Ensure the post follows viral structures." # Your take on actionable takeaways
    data-backed_claims:
      enabled: true  # Include real data and examples to support claims.
      description: "Ensure the post follows viral structures." # Your take on data-backed claims
```

### **Social Media Platforms**
Configure which platforms to post to and customize post formatting. In this example, LinkedIn is enabled for text-based posts. We will be adding more platforms soon

```yaml
social_media_to_post_to:
  linkedin:
    enabled: true  # Set to true to enable posting to LinkedIn.
    post_format: "Text"  # Format of the post (Markdown, HTML, or None).
    maximum_characters: 260  # Maximum character length for LinkedIn posts.
```

### **AI Configuration & Content Generation**
This section specifies how the AI models should behave when generating content, including the behavior for generating text, images, or videos. You can specify which models to use (e.g., OpenAI, HuggingFace, etc.).

```yaml
ai:
  custom_system_instructions: "Return either a generated JSON image or GifSearchTags based on user input."  # Custom instructions to guide AI behavior.
  custom_user_instructions: "Example response: { \"Text\": \"Message\", \"Creative\": \"[IMG] Image Description\", \"Hashtags\": [\"#tag\"] }"  # Edit  this message the initial string is needed to return the correct json
  
  text:
    generate_text:
      enabled: true  # Set to true to generate text posts.
      prompt: "Create a high-quality AI-generated image relevant to the blog content."  # Customize the text prompt.
      LLM: "Pollinations_Text_Advanced"  # Specify which LLM (language model) to use for text generation.
  
  creative:
    generate_image:
      enabled: true  # Set to true to enable image generation.
      prompt: "Create a high-quality AI-generated image relevant to the blog content."  # Customize the image prompt.
      LLM: "Pollinations_Image_Get"  # Model used for image generation (e.g., HuggingFace, OpenAI).
  
    fetch_gif:
      enabled: true  # Set to true to fetch relevant GIFs.
      prompt: "return at least 3 giphy search terms in the returned object: choose terms that best describe blog content in emotion" # custom prompt for gif search
```

### **Hashtags for Engagement**
Define default and custom hashtags to use in your posts to increase visibility and engagement.

```yaml
hashtags:
  default_tags:
    - "#AI"
    - "#MachineLearning"
    - "#DataScience"
    - "#Automation"
    - "#Technology"  # Default set of hashtags for AI and tech-related posts.
  custom_tags: []  # Add any custom hashtags here.
```

