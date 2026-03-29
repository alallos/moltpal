#!/usr/bin/env python3
"""
Automatic X/Twitter engagement for @MoltPal

Monitors mentions, searches for relevant content, and engages
"""

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

MY_ID = "2038115305201745920"
MY_USERNAME = "MoltPal"

# Track what we've already engaged with
engaged_tweets = set()
last_mention_id = None

def search_tweets(query, max_results=15):
    """Search for recent tweets"""
    response = oauth.get(
        "https://api.twitter.com/2/tweets/search/recent",
        params={
            "query": query,
            "max_results": max_results,
            "tweet.fields": "author_id,created_at,public_metrics,conversation_id",
            "expansions": "author_id",
            "user.fields": "username,name,description,public_metrics"
        }
    )
    
    if response.status_code == 200:
        return response.json()
    return None

def get_mentions(since_id=None):
    """Get mentions"""
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
    """Like a tweet"""
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
    """Reply to a tweet"""
    response = oauth.post(
        "https://api.twitter.com/2/tweets",
        json={
            "text": text,
            "reply": {"in_reply_to_tweet_id": tweet_id}
        }
    )
    
    return response.status_code == 201

def monitor_mentions():
    """Check for new mentions"""
    global last_mention_id
    
    result = get_mentions(since_id=last_mention_id)
    
    if not result or 'data' not in result:
        return
    
    users = {u['id']: u for u in result.get('includes', {}).get('users', [])}
    
    for mention in result['data']:
        tweet_id = mention['id']
        author_id = mention['author_id']
        text = mention.get('text', '').lower()
        author = users.get(author_id, {})
        username = author.get('username', 'unknown')
        
        print(f"\n📨 Mention from @{username}")
        print(f"   {mention.get('text', '')[:100]}")
        
        # Like the mention
        if like_tweet(tweet_id):
            print(f"   ✅ Liked")
        
        # Smart auto-reply based on keywords
        replied = False
        
        if any(word in text for word in ['how', 'what', 'when', 'where', 'documentation', 'docs', 'guide']):
            if 'how' in text or 'start' in text or 'setup' in text:
                reply_to_tweet(tweet_id, f"@{username} Check out our setup guide! https://github.com/alallos/moltpal#quick-start\n\nDocker: `docker-compose up -d`\n\nFull docs: https://github.com/alallos/moltpal/tree/main/docs")
                print(f"   💬 Replied with setup info")
                replied = True
        
        elif any(word in text for word in ['api', 'integrate', 'use', 'implement']):
            reply_to_tweet(tweet_id, f"@{username} API docs here: https://github.com/alallos/moltpal/blob/main/docs/API.md\n\nWe have client examples in JS & Python: https://github.com/alallos/moltpal/tree/main/examples\n\nLet me know if you need help!")
            print(f"   💬 Replied with API docs")
            replied = True
        
        elif any(word in text for word in ['thanks', 'awesome', 'great', 'cool', 'nice', 'love']):
            reply_to_tweet(tweet_id, f"@{username} 🔥 Thanks! Let us know if you build something cool with it - we'd love to share!")
            print(f"   💬 Replied with thanks")
            replied = True
        
        if not replied:
            print(f"   ⏭️  No auto-reply pattern matched")
        
        last_mention_id = tweet_id
        time.sleep(2)

def search_and_engage():
    """Search for relevant content and engage"""
    
    queries = [
        "AI agents payment -filter:retweets lang:en",
        "autonomous agents spending -filter:retweets lang:en",
        "AI agent infrastructure -filter:retweets lang:en",
        "(LangChain OR AutoGPT) payment -filter:retweets lang:en",
        "agent budget -filter:retweets lang:en"
    ]
    
    for query in queries[:2]:  # Just do 2 searches per cycle to avoid rate limits
        print(f"\n🔍 Searching: {query}")
        results = search_tweets(query)
        
        if not results or 'data' not in results:
            continue
        
        users = {u['id']: u for u in results.get('includes', {}).get('users', [])}
        
        for tweet in results['data'][:3]:  # Only engage with top 3 per search
            author_id = tweet['author_id']
            tweet_id = tweet['id']
            author = users.get(author_id, {})
            username = author.get('username', 'unknown')
            
            # Skip our own tweets
            if username == MY_USERNAME:
                continue
            
            # Skip if already engaged
            if tweet_id in engaged_tweets:
                continue
            
            print(f"\n  📝 Tweet from @{username}")
            print(f"     {tweet.get('text', '')[:80]}...")
            
            # Check engagement metrics
            metrics = tweet.get('public_metrics', {})
            likes = metrics.get('like_count', 0)
            
            # Only engage if tweet has some traction
            if likes >= 3:
                if like_tweet(tweet_id):
                    print(f"     ✅ Liked")
                    time.sleep(2)
            else:
                print(f"     ⏭️  Low engagement, skipping")
        
        time.sleep(5)  # Delay between searches

def main():
    """Main engagement loop"""
    print("🤖 @MoltPal Auto-Engagement Bot Started")
    print("=" * 50)
    print("Monitoring mentions + searching for relevant content")
    print("Press Ctrl+C to stop\n")
    
    cycle = 0
    
    try:
        while True:
            cycle += 1
            print(f"\n{'='*50}")
            print(f"Cycle #{cycle} - {time.strftime('%H:%M:%S')}")
            print(f"{'='*50}")
            
            # Check mentions every cycle
            print("\n👀 Checking mentions...")
            monitor_mentions()
            
            # Search and engage every other cycle
            if cycle % 2 == 0:
                print("\n🔍 Searching for relevant content...")
                search_and_engage()
            
            # Wait before next cycle
            wait_time = 120  # 2 minutes
            print(f"\n⏰ Waiting {wait_time}s until next cycle...")
            time.sleep(wait_time)
            
    except KeyboardInterrupt:
        print("\n\n👋 Stopping auto-engagement")
        print(f"Total tweets engaged: {len(engaged_tweets)}")

if __name__ == "__main__":
    main()
