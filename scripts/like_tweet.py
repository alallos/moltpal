#!/usr/bin/env python3
"""Like a tweet"""

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

def get_my_id():
    response = oauth.get("https://api.twitter.com/2/users/me")
    if response.status_code == 200:
        return response.json()['data']['id']
    return None

def like_tweet(user_id, tweet_id):
    response = oauth.post(
        f"https://api.twitter.com/2/users/{user_id}/likes",
        json={"tweet_id": tweet_id}
    )
    
    if response.status_code in [200, 201]:
        return True
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return False

my_id = get_my_id()
if my_id and len(sys.argv) > 1:
    tweet_id = sys.argv[1]
    if like_tweet(my_id, tweet_id):
        print(f"✅ Liked tweet {tweet_id}")
