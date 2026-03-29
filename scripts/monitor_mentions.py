#!/usr/bin/env python3
"""Monitor and respond to mentions of @MoltPal"""

import time
import json
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

def get_my_id():
    """Get our user ID"""
    response = oauth.get("https://api.twitter.com/2/users/me")
    if response.status_code == 200:
        return response.json()['data']['id']
    return None

def get_mentions(user_id, since_id=None):
    """Get mentions"""
    params = {
        "tweet.fields": "author_id,created_at,conversation_id,in_reply_to_user_id",
        "expansions": "author_id",
        "user.fields": "username,name",
        "max_results": 10
    }
    
    if since_id:
        params["since_id"] = since_id
    
    response = oauth.get(
        f"https://api.twitter.com/2/users/{user_id}/mentions",
        params=params
    )
    
    if response.status_code == 200:
        return response.json()
    return None

def reply_to_tweet(tweet_id, text):
    """Reply to a tweet"""
    response = oauth.post(
        "https://api.twitter.com/2/tweets",
        json={
            "text": text,
            "reply": {"in_reply_to_tweet_id": tweet_id}
        }
    )
    
    return response.status_code == 201

def like_tweet(user_id, tweet_id):
    """Like a tweet"""
    response = oauth.post(
        f"https://api.twitter.com/2/users/{user_id}/likes",
        json={"tweet_id": tweet_id}
    )
    
    return response.status_code == 200

def monitor():
    """Monitor mentions and respond"""
    print("👀 Monitoring @MoltPal mentions...\n")
    
    my_id = get_my_id()
    if not my_id:
        print("❌ Failed to get user ID")
        return
    
    last_id = None
    
    while True:
        print(f"Checking mentions... (last_id: {last_id or 'None'})")
        
        result = get_mentions(my_id, since_id=last_id)
        
        if not result or 'data' not in result:
            print("  No new mentions\n")
            time.sleep(60)  # Check every minute
            continue
        
        users = {u['id']: u for u in result.get('includes', {}).get('users', [])}
        
        for mention in result['data']:
            tweet_id = mention['id']
            author_id = mention['author_id']
            text = mention.get('text', '')
            author = users.get(author_id, {})
            username = author.get('username', 'unknown')
            
            print(f"\n📨 Mention from @{username}")
            print(f"   {text[:100]}...")
            
            # Like the mention
            if like_tweet(my_id, tweet_id):
                print("   ✅ Liked")
            
            # Auto-reply based on content (keep it simple for now)
            # More sophisticated responses can be added later
            
            # Update last_id
            last_id = tweet_id
        
        print()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    try:
        monitor()
    except KeyboardInterrupt:
        print("\n\n👋 Stopped monitoring")
