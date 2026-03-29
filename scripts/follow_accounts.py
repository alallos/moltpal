#!/usr/bin/env python3
"""Follow key accounts in the AI agent ecosystem"""

import time
from requests_oauthlib import OAuth1Session

# Credentials
CONSUMER_KEY = "IZBatKrsySuHu97lNlqgne9EV"
CONSUMER_SECRET = "HPAFQ1Bk8ZeMPKX71haJ7MaZ4UTu7CDUhYradUbEdFCzY7e9L0"
ACCESS_TOKEN = "2038115305201745920-leGA1ouUYlOiJDHZUo5bUegR5ftZX6"
ACCESS_TOKEN_SECRET = "G4ythiWLEXGVh5XVAJhzvhO8UtkeKDxOJUSvOsv1AkBT1"

oauth = OAuth1Session(
    CONSUMER_KEY,
    client_secret=CONSUMER_SECRET,
    resource_owner_key=ACCESS_TOKEN,
    resource_owner_secret=ACCESS_TOKEN_SECRET,
)

# Key accounts to follow
TARGET_ACCOUNTS = [
    "OpenAI",
    "LangChainAI",
    "anthropicai",
    "GoogleAI",
    "huggingface",
    "Replit",
    "vercel",
    "stripe",
    "togethercompute",
    "buildinpublic",
    "ClawdBot",  # Clawdbot official
    "simonw",  # AI tools creator
    "levelsio",  # Indie hacker
    "aisolopreneur",
    "ai_for_success",
    "NickADobos",  # AI agent dev
    "swyx",  # AI engineer
    "gdb",  # Greg Brockman, OpenAI
    "sama",  # Sam Altman
    "karpathy",  # Andrej Karpathy
    "amasad",  # Replit CEO
    "rauchg",  # Vercel CEO
    "levie",  # Box CEO, AI enthusiast
    "ylecun",  # Yann LeCun
    "goodside",  # Riley Goodside, prompt eng
    "emollick",  # Ethan Mollick, AI research
    "mitchellh",  # HashiCorp, dev tools
]

def get_my_id():
    """Get our user ID"""
    response = oauth.get("https://api.twitter.com/2/users/me")
    if response.status_code == 200:
        return response.json()['data']['id']
    return None

def lookup_user(username):
    """Look up user by username"""
    response = oauth.get(
        f"https://api.twitter.com/2/users/by/username/{username}",
        params={"user.fields": "name,description,public_metrics"}
    )
    
    if response.status_code == 200:
        return response.json().get('data')
    return None

def follow_user(my_id, target_user_id):
    """Follow a user"""
    response = oauth.post(
        f"https://api.twitter.com/2/users/{my_id}/following",
        json={"target_user_id": target_user_id}
    )
    
    return response.status_code == 200

def main():
    print("🎯 Following key accounts in AI agent ecosystem...\n")
    
    my_id = get_my_id()
    if not my_id:
        print("❌ Failed to get user ID")
        return
    
    print(f"✅ Authenticated as ID: {my_id}\n")
    
    followed_count = 0
    
    for username in TARGET_ACCOUNTS:
        print(f"Looking up @{username}...", end=" ")
        
        user = lookup_user(username)
        
        if not user:
            print("❌ Not found")
            time.sleep(1)
            continue
        
        user_id = user['id']
        name = user.get('name', username)
        followers = user.get('public_metrics', {}).get('followers_count', 0)
        
        print(f"✅ Found ({followers:,} followers)")
        print(f"   Following...", end=" ")
        
        if follow_user(my_id, user_id):
            print("✅ Followed!")
            followed_count += 1
        else:
            print("⚠️  Already following or error")
        
        print()
        time.sleep(2)  # Rate limit protection
    
    print(f"\n🎉 Followed {followed_count} new accounts!")

if __name__ == "__main__":
    main()
