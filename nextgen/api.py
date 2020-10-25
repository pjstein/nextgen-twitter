# nexgen/api.py

import tweepy

from nextgen.config import config


def get_client():
    auth = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)
    auth.set_access_token(config.access_token_key, config.access_token_secret)
    return tweepy.API(auth)