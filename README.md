# My RSS Social Bot

A Python-based automation tool to fetch RSS feeds, generate social media posts from blog content, and post them to platforms like LinkedIn.

## Features
- Fetches and parses RSS feeds
- Generates social media posts using AI
- Posts to LinkedIn (and optionally other platforms)
- Configurable via YAML files and HTTP headers
- Flask API for workflow automation and integration

## Project Structure
```
my-rss-social-bot/
├── src/
│   ├── main.py           # Main entry point
│   ├── api/              # Flask API endpoints
│   ├── ...
├── _docs/                # Documentation
├── requirements.txt      # Python dependencies
```

## Setup
1. **Clone the repo:**
   ```bash
   git clone <repo-url>
   cd my-rss-social-bot
   ```
2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Bot
To run the main script (recommended):
```bash
python -m src.main
```
This ensures Python treats `src` as a package and resolves imports correctly.

If you try `python src/main.py` and see `ModuleNotFoundError: No module named 'src'`, use the `-m` method above or set your `PYTHONPATH` to the project root.

If using the Flask API (example):
```bash
python -m flask --app src/api/config_api run --reload
```

## Configuration
- Default configuration is loaded from YAML files.
- You can override config via HTTP headers using the format: `X-Config-Section-Subsection-Key: Value`.
- See `_docs/config_yaml.md` for details.

## API Endpoints
- `POST /api/generate-post` - Generate a post from blog content
- `POST /api/post-to-social` - Post content to social platforms
- `GET /api/status` - Check bot/API status
- `GET /api/test` - Run automated tests
- `POST /api/trigger-workflow` - Trigger the workflow manually

## Testing
To run tests (if available):
```bash
pytest
```

## Contributing
Pull requests and issues are welcome! See `_docs/_todo.md` for planned features.

## License
MIT License
