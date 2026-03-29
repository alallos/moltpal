#!/usr/bin/env python3
"""Run one cycle of engagement"""

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

def search_tweets(query, max_results=15):
    response = oauth.get(
        "https://api.twitter.com/2/tweets/search/recent",
        params={
            "query": query,
            "max_results": max_results,
            "tweet.fields": "author_id,created_at,public_metrics",
            "expansions": "author_id",
            "user.fields": "username,name,public_metrics"
        }
    )
    
    if response.status_code == 200:
        return response.json()
    return None

def like_tweet(tweet_id):
    response = oauth.post(
        f"https://api.twitter.com/2/users/{MY_ID}/likes",
        json={"tweet_id": tweet_id}
    )
    return response.status_code in [200, 201]

print("🔍 Searching for: AI agents -filter:retweets lang:en")
results = search_tweets("AI agents -filter:retweets lang:en", max_results=10)

if results and 'data' in results:
    users = {u['id']: u for u in results.get('includes', {}).get('users', [])}
    
    print(f"\n✅ Found {len(results['data'])} tweets\n")
    
    liked_count = 0
    for tweet in results['data'][:5]:
        author_id = tweet['author_id']
        tweet_id = tweet['id']
        author = users.get(author_id, {})
        username = author.get('username', 'unknown')
        text = tweet.get('text', '')
        
        if username == 'MoltPal':
            continue
        
        print(f"@{username}:")
        print(f"  {text[:100]}...")
        
        metrics = tweet.get('public_metrics', {})
        likes = metrics.get('like_count', 0)
        
        if likes >= 2:
            if like_tweet(tweet_id):
                print(f"  ✅ Liked")
                liked_count += 1
                time.sleep(1)
        else:
            print(f"  ⏭️  Low engagement ({likes} likes)")
        
        print()
    
    print(f"\n🎉 Liked {liked_count} tweets")
else:
    print("❌ No results")
