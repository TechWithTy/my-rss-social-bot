# 🚀 **LinkedIn Auto-Post from Medium Blog**  

This project **automates** LinkedIn post creation from your **Medium blog RSS feed** using **OpenAI** for content generation and **LinkedIn API** for posting. It includes **AI-generated images**, GIF support, and viral engagement techniques.  

---

## **📌 Features**
✅ **Fetches Latest Medium Blog** – Uses RSS to track new posts  
✅ **AI-Generated LinkedIn Posts** – Customizable OpenAI prompts  
✅ **Image & GIF Support** – Dynamic AI-generated visuals or GIFs  
✅ **Viral Post Formatting** – Hooks, storytelling, and data-backed insights  
✅ **Hashtag Optimization** – Auto-includes relevant tags for engagement  

---

## **📂 Project Structure**
```
linkedin-action-auto-post/
│── .github/                     # GitHub Actions for automation
│── src/                         
│   ├── __init__.py              # Makes `src` a package
│   ├── main.py                  # 🚀 Main script to run
│   ├── linkedin_bot.py          # Handles LinkedIn API requests
│   ├── medium_bot.py            # Fetches latest blog post from Medium
│   ├── openai_generator.py      # AI-powered content generation
│   ├── config_loader.py         # Loads settings from `config.yaml`
│── venv/                        # Virtual environment (not committed)
│── .env                         # API keys (not committed)
│── .gitignore                   # Ignore sensitive files
│── config.yaml                  # 🔧 User-defined settings
│── pipfile                      # Project dependencies and Scripts
│── README.md                    # You’re here!
```

---

## **🛠️ Installation & Setup**
### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/your-username/linkedin-action-auto-post.git
cd linkedin-action-auto-post
```

### **3️⃣ Install Dependencies**
```bash
pipenv install

pipenv install <package-name>
```

### **🧪 Test APP Tests Medium | LinkedIn LLM Usability make sure to upload funds to required platforms**
```bash
pipenv test
```


### **4️⃣ Configure API Keys**
- **Create** a `.env` file in the root directory:
```ini
LINKEDIN_ACCESS_TOKEN="your_linkedin_access_token"
OPENAI_API_KEY="your_openai_api_key"
OPENAI_ASSISTANT_ID="your_openai_assistant_id"
```

- **Edit `config.yaml`** to match your preferences.

---

## **🚀 Running the Bot**
```bash
python -m src.main
```

- Fetches the latest Medium post  
- Sends content to OpenAI for optimization  
- Generates a viral LinkedIn post  
- Uploads an AI image or GIF (if enabled)  
- **Auto-posts** to LinkedIn 🎯  

---

## **🛠️ Configuration (`config.yaml`)**
Easily **customize** how your posts are generated:
```yaml
user_profile:
  medium_username: "codingoni"

creative:
  generate_image:
    enabled: true
    prompt: "Create a high-quality AI-generated image relevant to the blog content."

  post_gif:
    enabled: true
    gif_search_tags:
      - "motivation"
      - "career growth"
      - "AI revolution"

ai:
  custom_system_instructions: "Act as a LinkedIn content expert..."
  viral_posting:
    attention_grabbing_intro: true
    emotional_storytelling: true
```

---

## **📌 Automating with GitHub Actions**
1️⃣ **Enable GitHub Actions** in your repo  
2️⃣ **Commit & push your project**  
3️⃣ Add **GitHub Secrets** for API keys  
4️⃣ Edit `.github/workflows/rss-to-linkedin.yml` for **automatic posting**  

---

## **📝 Example LinkedIn Post Generated**
```txt
🚀 AI won’t replace you. But a person using AI will. 

Are you adapting? The tech landscape is evolving, and those who master AI tools will thrive.

🔥 Key insights:
✅ AI automates tasks, but creativity & strategy are irreplaceable
✅ Learning AI boosts career opportunities & productivity
✅ Adapt or risk being left behind

What’s your take on AI’s future? Drop a comment! 👇 #ArtificialIntelligence #FutureOfWork



---

## 🧠 AI Assistant Integration Guide

This project auto-generates social content from blog posts using multiple AI providers. It supports text generation, image generation, and video prompts — all controlled through a single YAML configuration file.

---

### 🔹 **OpenAI Assistants (v2) – Auto-Creation + Manual Setup**

OpenAI Assistants provide a memory-aware, instruction-driven experience. We use them to generate viral posts from long-form content (like Medium blogs).

#### ✅ How It Works:
- The system first looks for `OPENAI_ASSISTANT_ID` in your `.env` or GitHub Secrets.
- **If not found**, it **automatically creates a new assistant** using your creative and viral settings from the YAML file.
- Once created, the Assistant ID is printed to the console.

> 🔐 **Important:** You must **copy this Assistant ID** and add it to your `.env` or GitHub secrets:
```bash
OPENAI_ASSISTANT_ID=asst_abc123def456
```

All assistant behavior (style, tone, visuals, hashtags, etc.) is pulled from your YAML configuration — no coding required.

---

### 🤗 **Hugging Face AI (Text + Image + Video)**

You can use **any Hugging Face model** with the project. Configure your models in the YAML like this:

```yaml
HuggingFace:
  text_model: "meta-llama/Meta-Llama-3-8B"
  image_model: "runwayml/stable-diffusion-v1-5"
  video_model: "runwayml/stable-diffusion-v1-5"
  temperature: 0.7
  max_tokens: 500
```

- If `image_model` is set in any with any of the supported LLMS i.e `OPENAI > image_model: gpt-40`, your system will generate images based on creative prompts.
- `text_model` is used to generate post text.
- `video_model` will be used if you enable GIFs or videos in the config.

> No extra changes are needed — everything runs based on your YAML settings.

---

### 🦾 **DeepSeek Integration**

We support both:
- `deepseek-lite` (for basic summarization)
- `deepseek-chat` (for longer, conversation-aware generation)

DeepSeek models are useful for fast, lightweight text generation and can be swapped in via config.

---

### 💡 Claude 3.7 Sonnet (Anthropic)

Claude is used for direct, one-shot content transformation. No threads or assistants — just fast summarization and transformation using structured prompts.

Add your `ANTHROPIC_API_KEY` in your `.env` to get started.

---

### 🎨 Creative Settings (Unified YAML)

All user preferences — tone, image prompts, emotional storytelling, hashtags, media — are declared in your `config.yaml`.

No need to modify code. Just update your YAML, and the system adapts.



---

## **📌 Contributions**
Feel free to **fork, modify, and contribute!** 🎯 PRs are welcome!  

---

### **🔗 Stay Connected**
<!-- 📢 Follow me on **LinkedIn**: [Your Profile Link]  
📧 Contact: your.email@example.com   -->

🚀 **Let’s automate & go viral together!** 🚀