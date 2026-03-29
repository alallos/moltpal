#!/usr/bin/env python3
"""
X/Twitter Engagement Bot for @MoltPal

Finds, follows, and interacts with relevant accounts in the AI/agent space.
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

def search_tweets(query, max_results=15):
    """Search for tweets"""
    response = oauth.get(
        "https://api.twitter.com/2/tweets/search/recent",
        params={
            "query": query,
            "max_results": max_results,
            "tweet.fields": "author_id,created_at,public_metrics",
            "expansions": "author_id",
            "user.fields": "username,name,description,public_metrics"
        }
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Search error: {response.status_code}")
        print(response.text)
        return None

def follow_user(user_id):
    """Follow a user"""
    # Get our own user ID first
    me = oauth.get("https://api.twitter.com/2/users/me").json()
    my_id = me['data']['id']
    
    response = oauth.post(
        f"https://api.twitter.com/2/users/{my_id}/following",
        json={"target_user_id": user_id}
    )
    
    return response.status_code == 200

def like_tweet(tweet_id):
    """Like a tweet"""
    me = oauth.get("https://api.twitter.com/2/users/me").json()
    my_id = me['data']['id']
    
    response = oauth.post(
        f"https://api.twitter.com/2/users/{my_id}/likes",
        json={"tweet_id": tweet_id}
    )
    
    return response.status_code == 200

def retweet(tweet_id):
    """Retweet a tweet"""
    me = oauth.get("https://api.twitter.com/2/users/me").json()
    my_id = me['data']['id']
    
    response = oauth.post(
        f"https://api.twitter.com/2/users/{my_id}/retweets",
        json={"tweet_id": tweet_id}
    )
    
    return response.status_code == 200

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

# Search queries for relevant content
SEARCH_QUERIES = [
    "AI agents -filter:retweets",
    "autonomous agents -filter:retweets",
    "LangChain -filter:retweets",
    "AutoGPT -filter:retweets",
    "AI automation -filter:retweets",
    "agent framework -filter:retweets",
    "Clawdbot -filter:retweets",
    "OpenAI agents -filter:retweets",
    "AI payments -filter:retweets",
    "agent infrastructure -filter:retweets"
]

# Key accounts to follow (usernames)
TARGET_ACCOUNTS = [
    "OpenAI",
    "LangChainAI",
    "AutoGPT_Official",
    "anthropicai",
    "GoogleAI",
    "huggingface",
    "Replit",
    "vercel",
    "stripe",
    "CrewAIInc",
    "togethercompute",
    "fixieai",
    "ai_agents",
    "AGI_txt"
]

def find_and_engage():
    """Find relevant content and engage"""
    print("🔍 Starting engagement bot...\n")
    
    engaged_count = 0
    
    for query in SEARCH_QUERIES:
        print(f"Searching: {query}")
        results = search_tweets(query, max_results=5)
        
        if not results or 'data' not in results:
            print("  No results\n")
            continue
        
        # Get users data
        users = {u['id']: u for u in results.get('includes', {}).get('users', [])}
        
        for tweet in results['data']:
            author_id = tweet['author_id']
            tweet_id = tweet['id']
            author = users.get(author_id, {})
            username = author.get('username', 'unknown')
            
            # Skip our own tweets
            if username == 'MoltPal':
                continue
            
            print(f"\n  📝 Tweet from @{username}")
            print(f"     {tweet.get('text', '')[:80]}...")
            
            # Check if relevant based on engagement
            metrics = tweet.get('public_metrics', {})
            likes = metrics.get('like_count', 0)
            retweets = metrics.get('retweet_count', 0)
            
            # Engage if it has some traction
            if likes > 5 or retweets > 2:
                # Like the tweet
                if like_tweet(tweet_id):
                    print(f"     ✅ Liked")
                    engaged_count += 1
                    time.sleep(1)
                
                # Follow the author if they're active
                author_metrics = author.get('public_metrics', {})
                if author_metrics.get('followers_count', 0) > 100:
                    if follow_user(author_id):
                        print(f"     ✅ Followed @{username}")
                        time.sleep(1)
            
            time.sleep(2)  # Rate limit protection
        
        print()
        time.sleep(3)  # Delay between searches
    
    print(f"\n✨ Engaged with {engaged_count} tweets")

if __name__ == "__main__":
    find_and_engage()
