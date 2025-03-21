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
│── requirements.txt             # Project dependencies
│── README.md                    # You’re here!
```

---

## **🛠️ Installation & Setup**
### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/your-username/linkedin-action-auto-post.git
cd linkedin-action-auto-post
```

### **2️⃣ Set Up Virtual Environment**
```bash
python -m venv venv
source venv/Scripts/activate  # (Windows)
source venv/bin/activate      # (Mac/Linux)
```

### **3️⃣ Install Dependencies**
```bash
pip install -r requirements.txt
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
```

---

## **📌 Contributions**
Feel free to **fork, modify, and contribute!** 🎯 PRs are welcome!  

---

### **🔗 Stay Connected**
<!-- 📢 Follow me on **LinkedIn**: [Your Profile Link]  
📧 Contact: your.email@example.com   -->

🚀 **Let’s automate & go viral together!** 🚀