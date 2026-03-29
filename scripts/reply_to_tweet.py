#!/usr/bin/env python3
"""Reply to a specific tweet"""

import sys
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

def reply_to_tweet(tweet_id, text):
    response = oauth.post(
        "https://api.twitter.com/2/tweets",
        json={
            "text": text,
            "reply": {"in_reply_to_tweet_id": tweet_id}
        }
    )
    
    if response.status_code == 201:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

if __name__ == "__main__":
    tweet_id = sys.argv[1]
    text = sys.argv[2]
    
    result = reply_to_tweet(tweet_id, text)
    if result:
        print(f"✅ Replied to {tweet_id}")
        print(f"New tweet ID: {result['data']['id']}")
