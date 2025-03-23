
from utils.prompt_builder import build_prompt_payload,prompt,creative_prompt,system_instructions
from utils.config_loader import config
from models.pollinations_generator import (
  
    generate_image,
    generate_image_advanced,
   )
import urllib.parse
from models.openai_generator import run_openai_pipeline
from models.huggingface_generator import run_huggingface_pipeline
from models.deepseek_generator import send_message_to_deepseek
from models.claude_generator import send_message_to_claude
import asyncio
import json





def dispatch_image_pipeline(provider: str,):
    match provider:
        case "Pollinations_Image":
            print("🖼️ Pollinations_Image", creative_prompt)
            image_url = await generate_image(prompt=creative_prompt)
            return {"ImageAsset": image_url} if image_url else {"error": "Image generation failed"}

        case "Pollinations_Image_Get":
            print("🎨 Pollinations Image GET Setup")
            cfg = config['user_profile']['llm']['Pollinations']['pollinations_image_get']

            image_url = await generate_advanced_image(
                prompt=creative_prompt,
                model=cfg.get("model", "flux"),
                seed=cfg.get("seed", 42),
                width=cfg.get("width", 1024),
                height=cfg.get("height", 1024),
                nologo=cfg.get("nologo", True),
                private=cfg.get("private", True),
                enhance=cfg.get("enhance", False),
                safe=cfg.get("safe", True),
            )

            return {"ImageAsset": image_url} if image_url else {"error": "Image generation failed"}


        case "OpenAI":
            openai_cfg = config['user_profile']['llm']['OpenAI']
            payload = {
                "model": openai_cfg['text_model'],
                "messages": [{"role": "user", "content": prompt}],
                "temperature": openai_cfg['temperature'],
                "top_p": openai_cfg['top_p']
            }
            return asyncio.run(run_openai_pipeline())

        case "HuggingFace":
            print("🤗 Hugging Face")          
            result = run_huggingface_pipeline()
            print("🤗 Hugging Face Result", result.get('result'))          
            llm_response = result.get('response')  # corrected typo
            print("HF Response 🤗 " + str(type(llm_response).__name__) + " " + str(llm_response))            
            return llm_response 


        case "DeepSeek":
            ds_cfg = config['user_profile']['llm']['DeepSeek']
            payload = {
                "model": ds_cfg['text_model'],
                "prompt": prompt,
                "temperature": ds_cfg['temperature'],
                "top_p": ds_cfg['top_p'],
                "presence_penalty": ds_cfg['presence_penalty'],
                "frequency_penalty": ds_cfg['frequency_penalty'],
                "response_format": ds_cfg['response_format'],
                "max_tokens": ds_cfg['max_tokens']
            }
            llm_response = send_message_to_deepseek()
            print("🦈 Deep Seek Response",llm_response)
            return llm_response

        case "Claude":
            claude_cfg = config['user_profile']['llm']['Anthropic']
            payload = {
                "model": claude_cfg['text_model'],
                "max_tokens": claude_cfg['max_tokens'],
                "temperature": claude_cfg['temperature'],
                "top_p": claude_cfg['top_p'],
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "system": claude_cfg['system']
            }
            llm_response = send_message_to_claude()
            print("🎅 Claude Response",llm_response)
            return llm_response

        case _:
            raise ValueError(f"❌ Unsupported provider: {provider}")
