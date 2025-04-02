linkedin_payload_example = {
    "author": "urn:li:person:8675309",
    "lifecycleState": "PUBLISHED",
    "specificContent": {
        "com.linkedin.ugc.ShareContent": {
            "shareCommentary": {
                "text": "Feeling inspired after meeting so many talented individuals at this year's conference. #talentconnect"
            },
            "shareMediaCategory": "IMAGE",
            "media": [
                {
                    "status": "READY",
                    "description": {"text": "Center stage!"},
                    "media": "urn:li:digitalmediaAsset:C5422AQEbc381YmIuvg",
                    "title": {"text": "LinkedIn Talent Connect 2021"},
                }
            ],
        }
    },
    "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
}

linkedin_article_payload_example = {
    "author": "urn:li:person:8675309",
    "lifecycleState": "PUBLISHED",
    "specificContent": {
        "com.linkedin.ugc.ShareContent": {
            "shareCommentary": {
                "text": "Learning more about LinkedIn by reading the LinkedIn Blog!"
            },
            "shareMediaCategory": "ARTICLE",
            "media": [
                {
                    "status": "READY",
                    "description": {
                        "text": "Official LinkedIn Blog - Your source for insights and information about LinkedIn."
                    },
                    "originalUrl": "https://blog.linkedin.com/",
                    "title": {"text": "Official LinkedIn Blog"},
                }
            ],
        }
    },
    "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
}

linkedin_respone_example = {
    "status": "success",
    "message": "Post created successfully.",
    "data": {
        "id": "1346889436626259968",
        "text": "Here’s a new post created via the API. Excited to share it!",
    },
}
