#!/usr/bin/env python3
"""Monitor mentions and auto-respond (works with free API tier)"""

import time
from requests_oauthlib import OAuth1Session

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

MY_ID = "2038115305201745920"
last_mention_id = None
engaged_tweets = set()

def get_mentions(since_id=None):
    params = {
        "tweet.fields": "author_id,created_at,conversation_id,text",
        "expansions": "author_id",
        "user.fields": "username,name",
        "max_results": 10
    }
    
    if since_id:
        params["since_id"] = since_id
    
    response = oauth.get(
        f"https://api.twitter.com/2/users/{MY_ID}/mentions",
        params=params
    )
    
    if response.status_code == 200:
        return response.json()
    return None

def like_tweet(tweet_id):
    if tweet_id in engaged_tweets:
        return True
    
    response = oauth.post(
        f"https://api.twitter.com/2/users/{MY_ID}/likes",
        json={"tweet_id": tweet_id}
    )
    
    if response.status_code in [200, 201]:
        engaged_tweets.add(tweet_id)
        return True
    return False

def reply_to_tweet(tweet_id, text):
    response = oauth.post(
        "https://api.twitter.com/2/tweets",
        json={
            "text": text,
            "reply": {"in_reply_to_tweet_id": tweet_id}
        }
    )
    
    return response.status_code == 201

print("👀 @MoltPal Mention Monitor Started")
print("=" * 50)
print("Checking every 2 minutes. Press Ctrl+C to stop.\n")

cycle = 0

try:
    while True:
        cycle += 1
        print(f"\n[{time.strftime('%H:%M:%S')}] Cycle #{cycle}")
        
        result = get_mentions(since_id=last_mention_id)
        
        if result and 'data' in result:
            users = {u['id']: u for u in result.get('includes', {}).get('users', [])}
            
            print(f"  📬 {len(result['data'])} new mention(s)")
            
            for mention in result['data']:
                tweet_id = mention['id']
                author_id = mention['author_id']
                text = mention.get('text', '').lower()
                full_text = mention.get('text', '')
                author = users.get(author_id, {})
                username = author.get('username', 'unknown')
                
                print(f"\n  📨 @{username}")
                print(f"     {full_text[:80]}...")
                
                # Like
                if like_tweet(tweet_id):
                    print(f"     ✅ Liked")
                
                # Smart reply
                replied = False
                
                if any(word in text for word in ['how', 'setup', 'start', 'install']):
                    reply_to_tweet(tweet_id, f"@{username} Quick start: https://github.com/alallos/moltpal#quick-start\n\nDocker: `docker-compose up -d`\nFull docs: https://github.com/alallos/moltpal/tree/main/docs")
                    print(f"     💬 Replied: setup guide")
                    replied = True
                    time.sleep(2)
                
                elif any(word in text for word in ['api', 'integrate', 'docs', 'documentation']):
                    reply_to_tweet(tweet_id, f"@{username} API docs: https://github.com/alallos/moltpal/blob/main/docs/API.md\n\nClient examples (JS/Python): https://github.com/alallos/moltpal/tree/main/examples")
                    print(f"     💬 Replied: API docs")
                    replied = True
                    time.sleep(2)
                
                elif any(word in text for word in ['thanks', 'awesome', 'great', 'cool', 'love', 'nice']):
                    reply_to_tweet(tweet_id, f"@{username} 🔥 Thanks! Let us know if you build something cool - we'd love to share it!")
                    print(f"     💬 Replied: appreciation")
                    replied = True
                    time.sleep(2)
                
                elif '?' in full_text:
                    print(f"     ❓ Question detected - needs manual review")
                
                if not replied and '?' not in full_text:
                    print(f"     ℹ️  No auto-reply pattern matched")
                
                last_mention_id = tweet_id
        else:
            print(f"  ✓ No new mentions")
        
        time.sleep(120)  # 2 minutes
        
except KeyboardInterrupt:
    print("\n\n👋 Stopped monitoring")
    print(f"Total engagement: {len(engaged_tweets)} tweets")
