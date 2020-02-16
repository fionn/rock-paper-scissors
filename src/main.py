#!/usr/bin/env python3
"""Play rock paper scissors on Twitter"""

import os
import enum
import logging

import tweepy  # type: ignore

def configure_logger(module_name: str) -> logging.Logger:
    """Configure the logger"""
    logger = logging.getLogger(module_name)
    formatter = logging.Formatter(fmt="%(levelname)s: %(message)s")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger

LOG = configure_logger(__name__)

class Weapon(enum.IntEnum):
    """Enum of weapons"""
    ROCK = 0
    PAPER = 1
    SCISSORS = 2

    @property
    def beaten_by(self) -> "Weapon":
        """Creates a new weapon that will beat itself"""
        return self.__class__((self.value + 1) % 3)

    @property
    def beats(self) -> "Weapon":
        """Creates a new weapon that it will beat"""
        return self.__class__((self.value - 1) % 3)

class RockPaperScissors:
    """Wrapper for the Twitter interface"""

    MAX_COUNT = 1

    def __init__(self) -> None:
        auth = tweepy.OAuthHandler(os.environ["API_KEY"],
                                   os.environ["API_SECRET"])
        auth.set_access_token(os.environ["ACCESS_TOKEN"],
                              os.environ["ACCESS_TOKEN_SECRET"])
        self.api = tweepy.API(auth, wait_on_rate_limit=True,
                              wait_on_rate_limit_notify=True)
        self.me = self.api.me()  # pylint: disable=invalid-name
        self.timeline = self.api.user_timeline(count=self.MAX_COUNT)

    def _filter(self, tweet: tweepy.models.Status) -> bool:
        if tweet.in_reply_to_user_id != self.me.id:
            return False
        if tweet.id in set(tweet.in_reply_to_status_id
                           for tweet in self.timeline):
            return False
        weapons_in_tweet = set(weapon for weapon in Weapon
                               if weapon.name in tweet.text.upper())
        return len(weapons_in_tweet) == 1

    @staticmethod
    def _compose(tweet: tweepy.models.Status) -> dict:
        weapon = set(weapon for weapon in Weapon
                     if weapon.name in tweet.text.upper()).pop()
        text = f"@{tweet.author.screen_name} {weapon.beaten_by.name.title()}."
        return {"status": text, "in_reply_to_status_id": tweet.id}

    def mentions(self) -> list:
        """Get mentions"""
        since_id = self.timeline[0].id
        tweets = self.api.mentions_timeline(since_id=since_id,
                                            count=self.MAX_COUNT)
        tweets = [tweet for tweet in tweets if self._filter(tweet)]
        return tweets

    def reply(self, tweet: tweepy.models.Status) -> tweepy.models.Status:
        """Win the game"""
        composition = self._compose(tweet)
        LOG.info("Replying to \"%s\" with \"%s\"",
                 tweet.text, composition["status"])
        return self.api.update_status(**composition)

def main() -> None:
    """Entry point"""
    rps = RockPaperScissors()
    mentions = rps.mentions()
    for mention in mentions:
        rps.reply(mention)

if __name__ == "__main__":
    main()
