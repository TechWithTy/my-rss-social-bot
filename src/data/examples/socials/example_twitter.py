url = "https://api.twitter.com/2/tweets"


twitter_payload_example = {
    "card_uri": "<string>",
    "community_id": "1146654567674912769",
    "direct_message_deep_link": "<string>",
    "for_super_followers_only": False,
    "geo": {"place_id": "<string>"},
    "media": {"media_ids": ["1146654567674912769"], "tagged_user_ids": ["2244994945"]},
    "nullcast": False,
    "poll": {
        "duration_minutes": 5042,
        "options": ["<string>"],
        "reply_settings": "following",
    },
    "quote_tweet_id": "1346889436626259968",
    "reply": {
        "exclude_reply_user_ids": ["2244994945"],
        "in_reply_to_tweet_id": "1346889436626259968",
    },
    "reply_settings": "following",
    "text": "Learn how to use the user Tweet timeline and user mention timeline endpoints in the X API v2 to explore Tweet\u2026 https:\/\/t.co\/56a0vZUx7i",
}
headers = {"Authorization": "Bearer <token>", "Content-Type": "application/json"}

twitter_respone_example = {
    "data": {
        "id": "1346889436626259968",
        "text": "Learn how to use the user Tweet timeline and user mention timeline endpoints in the X API v2 to explore Tweet… https://t.co/56a0vZUx7i",
    }
}
