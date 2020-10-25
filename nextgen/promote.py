# nextgen/promote.py

import logging
import random

import tweepy

from nextgen.events import EventLog
from nextgen.api import get_client
from nextgen import data


class PromotionListener(tweepy.StreamListener):
    __country_code = "US"

    def __init__(self, client, events, states):
        self.api = client
        self.me = self.api.me()
        self.events = events
        self.states = states
        self.log = logging.getLogger(self.__class__.__name__)

    def generate_promotion_tweet(self):
        return random.choice(data.PROMOTION_TWEETS)

    def normalize_tweet_data(self, tweet):
        return {
            "tweet_id": tweet.id,
            "user_id": tweet.user.id,
            "user_name": tweet.user.screen_name,
            "tweet_content": tweet.text,
        }

    def is_in_right_location(self, tweet):
        if tweet.user.location:
            location = tweet.user.location.lower()

            for state in self.states:
                if state.name in location or location.endswith(f" {state.code}"):
                    return True

        if not tweet.place:
            return False

        if not tweet.place.country_code == self.__country_code:
            return False

        if tweet.place.full_name[-2:] in [state.code for state in self.states]:
            return True

        if tweet.place.full_name.endswith(f", {self.__country_code}"):
            for state in self.states:
                if tweet.place.full_name.lower().startswith(state):
                    return True

        return False

    def should_skip_tweet_on_content(self, tweet):
        return bool(data.SKIP_RE.search(tweet.text))

    def already_following_author(self, tweet):
        source, _ = self.api.show_friendship(
            source_screen_name=self.me.screen_name,
            target_screen_name=tweet.user.screen_name,
        )
        return source.following

    def friend(self, tweet):
        try:
            self.api.create_friendship(tweet.user.id)
        except:
            self.log.exception(
                f"Failed to create a friendship with user (id: {tweet.id}, user_id: {tweet.user.id})"
            )
            self.events.log(
                action_type="ERROR",
                action_detail="CREATE_FRIENDSHIP",
                **self.normalize_tweet_data(tweet),
            )
            return False
        else:
            self.log.info(f"Friended user (id: {tweet.id}, user_id: {tweet.user.id})")
            self.events.log(
                action_type="CREATE_FRIENDSHIP",
                action_detail="PROMOTION",
                **self.normalize_tweet_data(tweet),
            )
        return True

    def send_encouragement(self, tweet):
        status = self.generate_promotion_tweet()

        try:
            self.api.update_status(
                status=f"@{tweet.user.screen_name} {status}",
                in_reply_to_status_id=tweet.id_str,
            )
        except:
            self.log.exception(
                f"Failed to send encouragement to user (id: {tweet.id}, user_id: {tweet.user.id})"
            )
            self.events.log(
                action_type="ERROR",
                action_detail="SEND_TWEET",
                **self.normalize_tweet_data(tweet),
            )
            return False
        else:
            self.log.info(f"Tweeted @ user (id: {tweet.id}, user_id: {tweet.user.id})")
            self.events.log(
                action_type="SEND_TWEET",
                action_detail="PROMOTION",
                **self.normalize_tweet_data(tweet),
            )
        return True

    def on_status(self, tweet):
        self.log.info(f"Processing tweet (id: {tweet.id})")

        # Skip tweets outside of the locations we care about
        if not self.is_in_right_location(tweet):
            self.log.info(
                f"Skipping tweet outside of locations of interest (id: {tweet.id})"
            )
            self.events.log(
                action_type="SKIP",
                action_detail="LOCATION",
                **self.normalize_tweet_data(tweet),
            )
            return True  # Early Return

        # Skip replies
        if tweet.in_reply_to_status_id is not None or tweet.user.id == self.me.id:
            self.log.info(f"Skipping tweet in response to me (id: {tweet.id})")
            self.events.log(
                action_type="SKIP",
                action_detail="REPLY",
                **self.normalize_tweet_data(tweet),
            )
            return True  # Early Return

        # If we are already following this user, then we can
        if self.already_following_author(tweet):
            self.log.info(f"Skipping tweet from my followers (id: {tweet.id})")
            self.events.log(
                action_type="SKIP",
                action_detail="ALREADY_FOLLOWING_USER",
                **self.normalize_tweet_data(tweet),
            )
            return True  # Early Return

        # Should we skip this tweet based on the content?
        if self.should_skip_tweet_on_content(tweet):
            self.log.info(f"Skipping tweet based on the content (id: {tweet.id})")
            self.events.log(
                action_type="SKIP",
                action_detail="BAD_CONTENT",
                **self.normalize_tweet_data(tweet),
            )
            return True  # Early Return

        # Skip RTs
        if tweet.text.startswith("RT"):
            self.log.info(f"Skipping RT (id: {tweet.id})")
            self.events.log(
                action_type="SKIP",
                action_detail="RT",
                **self.normalize_tweet_data(tweet),
            )
            return True  # Early Return

        # Otherwise, we're going to follow this person and encourage them to
        # make a plan to vote
        if not self.friend(tweet):
            return True  # Early Return
        return self.send_encouragement(tweet)


def run_promote(events_filepath, states, **kwargs):
    events = EventLog(events_filepath)
    client = get_client()
    listener = PromotionListener(client, events, states)
    stream = tweepy.Stream(client.auth, listener)
    stream.filter(**kwargs)
