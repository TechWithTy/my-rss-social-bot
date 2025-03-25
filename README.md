

# 🚀 **Social Media Auto-Post from Medium, WordPress, or Wix Blog**

This project **automates** Social Media post creation from your **Medium**, **WordPress**, or **Wix** blog RSS feed using **OpenAI** for content generation and **Social Media API** for posting. It integrates **AI-generated text**, and **Pollinations** for image creation, alongside **Hugging Face** and **Claude** for advanced text generation and semantic understanding. 

The tool utilizes free APIs and deep-learning models to enhance your posting strategy with **AI-generated visuals** and **GIF support**, including viral engagement techniques.

---

## **📌 Features**
 
```
View More about pollinations _docs\api\pollination.md
```
✅ **Fetches Latest Blog Posts** – Automatically pulls from **Medium**, **WordPress**, or **Wix** using RSS feed  
✅ **AI-Generated Social Media Posts** – Customizable OpenAI prompts for content generation  
✅ **AI-Generated Images** – Dynamic visuals via **Pollinations** **OpenAI** or **Hugging Face** for enhanced engagement  
✅ **Text Generation with Hugging Face and Claude** – Deep-seek insights and advanced writing for meaningful posts  
✅ **Image & GIF Support** – Auto-generates images or GIFs for added visual appeal  
✅ **Viral Post Formatting** – Hooks, storytelling, and data-backed insights  
✅ **Hashtag Optimization** – Auto-includes relevant tags for enhanced reach  
✅ **API Use** – Leverages **Pollinations**,**DeepSeek** , **OpenAI**, **Hugging Face**and **Claude** for cost-effective and powerful automation




---

## **📂 Project Structure**


```
my-rss-social-bot/
│── .github/                     # GitHub Actions for automation
│── _docs/                       # Documentation files
│── _temp/                       # Temporary files
│── .github/workflows            # GitHub Actions workflows
│── src/
│   ├── __init__.py              # Makes `src` a package
│   ├── main.py                  # 🚀 Main script to run
│   ├── data/                    # Data handling and storage
│   ├── models/                  # AI models including HuggingFace generator
│   ├── rss_feed/                # RSS feed processing
│   ├── socials/                 # Social media integration
│   ├── tests/                   # Test files including HuggingFace tests
│   ├── utils/                   # Utility functions and helpers
│── venv/                        # Virtual environment (not committed)
│── .env                         # API keys (not committed)
│── .gitignore                   # Ignore sensitive files
│── config.yaml                  # 🔧 User-defined settings
│── Pipfile                      # Project dependencies
│── Pipfile.lock                 # Locked dependencies
│── blog_cache.json              # Cache for blog posts
│── README.md                    # Project documentation

```
---

## **🛠️ Installation & Setup**

Here’s the updated version with the changes you requested:

### **1️⃣ Fork and Clone the Repository**

1. **Fork the repository** from GitHub:  
   Go to [my-rss-social-bot](https://github.com/TechWithTy/my-rss-social-bot) and click the **Fork** button in the top right corner.

2. **Clone the repository** to your local machine:  
   Run the following commands in your terminal:
   
```bash
git clone https://github.com/TechWithTy/my-rss-social-bot/
cd my-rss-social-bot
```

### **2️⃣ Enable GitHub Actions**

Ensure **GitHub Actions** are enablead for your forked repository:

- Go to the **Actions** tab in your forked repository.
- If it's the first time using actions, you'll need to enable it by clicking **I understand my workflows, go ahead and enable them**.

### **3️⃣ Set Required Action Permissions**

- In your repository, go to **Settings** > **Actions** > **General**.
- Under **Workflow permissions**, select **Read and write permissions**.
- Enable **Require approval for first-time contributors** and **Allow all actions and reusable workflows**.

### **4️⃣ Customize the YAML Workflow**

- Customize the workflow YAML file for your specific needs.
- Declare necessary environment variables in your repository.  
   You can check the `.env.example` and the github actions file for the required environment variables.
   

Here’s the updated version with setup and running instructions locally:

### **1️⃣ Setting Up the Environment Locally**

- First, install the necessary dependencies using **Pipenv**:

```bash
pipenv install
```

- To install an additional package, run:

```bash
pipenv install <package-name>
```

### **2️⃣ Running Tests Locally**

To run the app tests (for Medium, Social Media, and LLM usability), ensure you've uploaded the necessary funds to the required platforms. Then, run the tests:

```bash
pipenv run test
```

- Check the test reports in the `/tests/reports/html` directory for details.

### **3️⃣ Configure API Keys**

- **Create a `.env` file** in the root directory of your project:

```ini
OPENAI_API_KEY="your_openai_api_key"
OPENAI_ASSISTANT_ID="your_openai_assistant_id"
ANTHROPIC_API_KEY="your_anthropic_api_key"
DEEPSEEK_API_KEY="your_deepseek_api_key"
HUGGINGFACE_API_KEY="your_huggingface_api_key"
LINKEDIN_ACCESS_TOKEN="your_linkedin_access_token"
GIPHY_ASSET_TOKEN="your_giphy_asset_token"
TEST_MODE=true  # Set to true to run tests prior to deploying [ This may use up your funds ]



## **🛠️ Configure (`config.yaml`)**
```Check _docs\config_yaml.md for more details.```

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
  custom_system_instructions: "Act as a Social Media content expert..."
  viral_posting:
    attention_grabbing_intro: true
    emotional_storytelling: true
```



## **📝 Example Social Media Post Generated**

````txt
🚀 AI won’t replace you. But a person using AI will.

Are you adapting? The tech landscape is evolving, and those who master AI tools will thrive.

🔥 Key insights:
✅ AI automates tasks, but creativity & strategy are irreplaceable
✅ Learning AI boosts career opportunities & productivity
✅ Adapt or risk being left behind

What’s your take on AI’s future? Drop a comment! 👇 #ArtificialIntelligence #FutureOfWork

![GIF](https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdjR1NGM5a3N1bzNyanVkY3plNG45aWdtd3FqM3kwbmJpcnNrazc3bSZlcD12MV9naWZzX3RyZW5kaW5nJnRpZD03MzAxNzNhMjFmZTQzYjU1ZjUxNGQ2NWUzNTIwZDJkMmI1MmVjZjUxNzg2NGRhNTBiY2ViZTBmNmNkODM2MWQwJmN0PWcmYXA9MA/aaMRmblWuKEdbFJQlq/giphy.gif)

or 

![Image](https://image.pollinations.ai/prompt/A%20sleek,%20modern%20interface%20of%20a%20culturing%20tool%20with%20data%20charts,%20customizable%20file%20names,%20and%20a%20Niimbot%20printer%20in%20action?width=1024&height=1024&seed=42&model=flux&nologo=true)


# RSS to Social Media Workflow

This project includes two workflows that work together to ensure smooth deployment and posting to Social Media: **RSS to Social Media** and **Auto Test (CI)**.

## Workflows Overview

### **RSS to Social Media Workflow**
- **Triggered**: Every hour (or manually).
- **Purpose**: Runs the app script to post content to Social Media.
- **Pre-checks**: Verifies that tests passed by checking the status from the **Auto Test (CI)** workflow.
- **Steps**:
  1. Checkout code
  2. Setup Python environment
  3. Install dependencies
  4. Check test status
  5. Run app script to post to Social Media if tests pass

### **Auto Test (CI) Workflow**
- **Triggered**: On push to `master` or manually.
- **Purpose**: Runs tests to ensure app quality before deployment.
- **Steps**:
  1. Checkout code
  2. Setup Python environment
  3. Install dependencies
  4. Run tests
  5. Cache test status (pass/fail)

## How They Work Together

- The **Auto Test (CI)** workflow ensures only passing tests trigger the **RSS to Social Media** workflow.
- **RSS to Social Media** posts content to Social Media only if the test status is "pass."
- This ensures reliable and tested content is posted to Social Media, preventing broken or unstable posts.

By combining these workflows, the app ensures content is only posted when the code is fully tested and stable.


## **📌 Contributions**

Feel free to **fork, modify, and contribute!** 🎯 PRs are welcome!

---

### **🔗 Stay Connected**

<!-- 📢 Follow me on **Social Media**: [Your Profile Link]
📧 Contact: your.email@example.com   -->

🚀 **Let’s automate & go viral together!** 🚀
