Api Docs
https://github.com/pollinations/pollinations/blob/master/APIDOCS.md

Available Text Models In Polination : https://text.pollinations.ai/models

| Name                | Type   | Censored | Description                                     | Base Model | Vision | Reasoning | Provider    | Max Tokens | Audio | Voices                        |
|---------------------|--------|----------|-------------------------------------------------|------------|--------|-----------|-------------|-------------|--------|-------------------------------|
| openai              | chat   | true     | OpenAI GPT-4o-mini                              | true       | true   |           |             |             |        |                               |
| openai-large        | chat   | true     | OpenAI GPT-4o                                   | true       | true   |           |             |             |        |                               |
| openai-reasoning    | chat   | true     | OpenAI o3-mini                                  | true       |        | true      |             |             |        |                               |
| qwen-coder          | chat   | true     | Qwen 2.5 Coder 32B                              | true       |        |           |             |             |        |                               |
| llama               | chat   | false    | Llama 3.3 70B                                   | true       |        |           |             |             |        |                               |
| mistral             | chat   | false    | Mistral Small 3.1 2503                          | true       | true   |           |             |             |        |                               |
| unity               | chat   | false    | Unity with Mistral Large by Unity AI Lab        | false      |        |           |             |             |        |                               |
| midijourney         | chat   | true     | Midijourney musical transformer                 | false      |        |           |             |             |        |                               |
| rtist               | chat   | true     | Rtist image generator by @bqrio                 | false      |        |           |             |             |        |                               |
| searchgpt           | chat   | true     | SearchGPT with realtime news and web search     | false      |        |           |             |             |        |                               |
| evil                | chat   | false    | Evil Mode - Experimental                        | false      |        |           |             |             |        |                               |
| deepseek            | chat   | true     | DeepSeek-V3                                     | true       |        |           |             |             |        |                               |
| deepseek-r1         | chat   | true     | DeepSeek-R1 Distill Qwen 32B                    | true       |        | true      | cloudflare  |             |        |                               |
| deepseek-reasoner   | chat   | true     | DeepSeek R1 - Full                              | true       |        | true      | deepseek    |             |        |                               |
| deepseek-r1-llama   | chat   | true     | DeepSeek R1 - Llama 70B                         | true       |        | true      | scaleway    |             |        |                               |
| qwen-reasoning      | chat   | true     | Qwen QWQ 32B - Advanced Reasoning               | true       |        | true      | groq        |             |        |                               |
| llamalight          | chat   | false    | Llama 3.1 8B Instruct                           | true       |        |           |             | 7168        |        |                               |
| llamaguard          | safety | false    | Llamaguard 7B AWQ                               | false      |        |           | cloudflare  | 4000        |        |                               |
| phi                 | chat   | true     | Phi-4 Instruct                                  | true       |        |           | cloudflare  |             |        |                               |
| llama-vision        | chat   | false    | Llama 3.2 11B Vision                            | true       | true   |           | cloudflare  |             |        |                               |
| pixtral             | chat   | false    | Pixtral 12B                                     | true       | true   |           | scaleway    |             |        |                               |
| gemini              | chat   | true     | Gemini 2.0 Flash                                | true       |        |           | google      |             |        |                               |
| gemini-thinking     | chat   | true     | Gemini 2.0 Flash Thinking                       | true       |        |           | google      |             |        |                               |
| hormoz              | chat   | false    | Hormoz 8b by Muhammadreza Haghiri              | true       |        |           | modal       |             |        |                               |
| hypnosis-tracy      | chat   | false    | Hypnosis Tracy 7B - Self-help AI assistant     | false      |        |           | openai      |             |        |                               |
| sur                 | chat   | true     | Sur AI Assistant                                | false      |        |           |             |             |        |                               |
| sur-mistral         | chat   | true     | Sur AI Assistant (Mistral)                      | false      |        |           |             |             |        |                               |
| llama-scaleway      | chat   | false    | Llama (Scaleway)                                | true       |        |           |             |             |        |                               |
| openai-audio        | chat   | true     | OpenAI GPT-4o-audio-preview                     | true       |        |           |             |             | true   | alloy, echo, fable, onyx, nova, shimmer, coral, verse, ballad, ash, sage, amuch, dan |

Available Image Models in polination


| Model Name     | Best Use Case                                                                 |
|----------------|--------------------------------------------------------------------------------|
| `flux-realism` | High-quality realistic images – ideal for photorealistic scenes or people     |
| `flux`         | Balanced general-purpose model – good for most illustrations and concepts      |
| `any-dark`     | Dark-themed, moody visuals – great for atmospheric, cinematic-style art        |
| `flux-anime`   | Anime/manga-style art – perfect for characters, scenes, or posters in that style|
| `flux-3d`      | 3D render-style images – use for objects, environments, or isometric views     |
| `turbo`        | Fast image generation with decent quality – best for quick drafts or previews  |


Hey! 👋 To see what endpoints are available via an **OpenAI-compatible API** like `https://text.pollinations.ai/openai`, you can look for two things:

---

### ✅ 1. **OpenAI API Reference (Compatible Services Follow This)**
Pollinations' `/openai` endpoint is built to mimic OpenAI’s API, so it supports many of the same endpoints.

**Core OpenAI endpoints:**

| Endpoint | Description |
|----------|-------------|
| `POST /v1/chat/completions` | ChatGPT-style conversational completions |
| `POST /v1/completions` | Legacy GPT-3-style completions |
| `POST /v1/embeddings` | Generate vector embeddings |
| `POST /v1/moderations` | Run content moderation |
| `GET /v1/models` | List available models |
| `GET /v1/models/{model}` | Get model info |
| `POST /v1/images/generations` | Generate images from prompt (DALL·E style) |
| `POST /v1/audio/transcriptions` | Speech-to-text (Whisper) |
| `POST /v1/audio/translations` | Translate audio to English |
| `POST /v1/files` / `GET /v1/files` | For fine-tuning (GPT-3.5) |
| `POST /v1/fine_tuning/jobs` | Fine-tune jobs for GPT models |

If the service claims OpenAI compatibility, it likely supports at least:

- `POST /v1/chat/completions`
- `GET /v1/models`
- Possibly `POST /v1/completions` and `POST /v1/embeddings`

---

### ✅ 2. **Try This: Get Supported Models**
You can test what models are available by sending:

```bash
curl https://text.pollinations.ai/openai/v1/models
```

If it supports this endpoint, it’ll return a list of models and their metadata.

---

### ✅ 3. Use `POST /openai/v1/chat/completions` (like this)

```bash
curl https://text.pollinations.ai/openai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
        "model": "gpt-4",
        "messages": [
          {"role": "user", "content": "Write a viral LinkedIn post about AI."}
        ]
      }'
```



