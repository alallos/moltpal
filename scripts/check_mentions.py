#!/usr/bin/env python3
"""Check mentions once"""

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
    response = oauth.get("https://api.twitter.com/2/users/me")
    if response.status_code == 200:
        return response.json()['data']['id']
    return None

def get_mentions(user_id):
    response = oauth.get(
        f"https://api.twitter.com/2/users/{user_id}/mentions",
        params={
            "tweet.fields": "author_id,created_at,text,conversation_id",
            "expansions": "author_id,referenced_tweets.id",
            "user.fields": "username,name,public_metrics",
            "max_results": 20
        }
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
    return None

my_id = get_my_id()
if my_id:
    print(f"Checking mentions for user ID: {my_id}\n")
    result = get_mentions(my_id)
    
    if result and 'data' in result:
        users = {u['id']: u for u in result.get('includes', {}).get('users', [])}
        
        print(f"📬 Found {len(result['data'])} mentions:\n")
        
        for mention in result['data']:
            author_id = mention['author_id']
            author = users.get(author_id, {})
            username = author.get('username', 'unknown')
            name = author.get('name', 'Unknown')
            text = mention.get('text', '')
            tweet_id = mention['id']
            
            print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"👤 @{username} ({name})")
            print(f"🆔 Tweet ID: {tweet_id}")
            print(f"💬 {text}")
            print()
    else:
        print("No mentions found")
