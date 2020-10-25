# nextgen/api.py

from os import environ

from cached_property import cached_property


class Config:
    @cached_property
    def consumer_key(self):
        return environ.get("TWITTER_CONSUMER_KEY")

    @cached_property
    def consumer_secret(self):
        return environ.get("TWITTER_CONSUMER_SECRET")

    @cached_property
    def access_token_key(self):
        return environ.get("TWITTER_ACCESS_TOKEN_KEY")

    @cached_property
    def access_token_secret(self):
        return environ.get("TWITTER_ACCESS_TOKEN_SECRET")


config = Config()
