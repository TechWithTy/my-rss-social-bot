ai_img_example = {
  "Text": "Tired of messy culturing workflows? Our new tool makes it easy—label, organize, and share with a few clicks. Built for beginners & pros alike. 🧪✨ Join the #CyberOniCommunity and see the difference.",
  "Creative": "[IMG] A modern, organized lab workspace with digital tools, culture samples, and a Niimbot label printer in action.",
  "ImageAsset": "![Organized lab with digital tools and Niimbot printer](https://image.pollinations.ai/prompt=Organized%20lab%20with%20digital%20tools%20and%20Niimbot%20printer%20in%20use?width=1024&height=1024&seed=42&model=realistic_v4&nologo=true)",
  "Hashtags": ["#AI", "#MachineLearning", "#DataScience", "#Automation", "#Technology"]
}


ai_gif_example  = {
  "Text": "Tired of messy culturing workflows? We built a tool at Cyberoni that simplifies everything—from data management to label printing. Perfect for beginners & pros. No more chaos, just clarity. ✨ #CyberOniCommunity",
  "Hashtags": ["#AI", "#MachineLearning", "#DataScience", "#Automation", "#Technology"],
  "GifSearchTags": ["lab organization", "printing labels", "tech innovation"]
}


ai_completion_example =  {
    'choices': [{
        'content_filter_results': {},
        'finish_reason': 'tool_calls',
        'index': 0,
        'logprobs': None,
        'message': {
            'content': None,
            'refusal': None,
            'role': 'assistant',
            'tool_calls': [{
                'function': {
                    'arguments': '{"Text": "Embracing tech innovation can transform your career! As a software engineer, I\'ve seen the incredible impact of tech solutions. Let\'s learn together and push boundaries! 🚀 #AI #MachineLearning #DataScience #Automation #Technology", "Hashtags": ["#AI", "#MachineLearning", "#DataScience", "#Automation", "#Technology"]}',
                    'name': 'generate_post'
                },
                'id': 'call_GhnSBbNysIOnCn9DQ1yXKmUG',
                'type': 'function'
            }, {
                'function': {
                    'arguments': '{"description": "A software engineer embracing technology and innovation in a modern workspace", "width": 1024, "height": 1024, "model": "flux"}',
                    'name': 'generate_image'
                },
                'id': 'call_SluDWO1LU0OgIDziQD6mWBmT',
                'type': 'function'
            }]
        }
    }],
    'created': 1742705315,
    'id': 'pllns_c88db803b22b7b00a1691c4e2a8e37a7',
    'model': 'gpt-4o-mini-2024-07-18',
    'object': 'chat.completion',
    'prompt_filter_results': [{
        'prompt_index': 0,
        'content_filter_results': {
            'hate': {
                'filtered': False,
                'severity': 'safe'
            },
            'self_harm': {
                'filtered': False,
                'severity': 'safe'
            },
            'sexual': {
                'filtered': False,
                'severity': 'safe'
            },
            'violence': {
                'filtered': False,
                'severity': 'safe'
            }
        }
    }],
    'system_fingerprint': 'fp_ded0d14823',
    'usage': {
        'completion_tokens': 130,
        'completion_tokens_details': {
            'accepted_prediction_tokens': 0,
            'audio_tokens': 0,
            'reasoning_tokens': 0,
            'rejected_prediction_tokens': 0
        },
        'prompt_tokens': 764,
        'prompt_tokens_details': {
            'audio_tokens': 0,
            'cached_tokens': 0
        },
        'total_tokens': 894
    }
}