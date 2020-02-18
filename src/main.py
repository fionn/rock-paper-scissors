#!/usr/bin/env python3
"""Play rock paper scissors on Twitter"""

import os
import enum
import logging
from typing import Set, Any

import tweepy

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

@enum.unique
class Weapon(enum.Enum):
    """Enum of weapons"""
    ROCK = 0
    PAPER = 1
    SCISSORS = 2

    @property
    def defeated_by(self) -> "Weapon":
        """Creates a new weapon that will defeat itself"""
        return self.__class__((self.value + 1) % 3)

    @property
    def defeats(self) -> "Weapon":
        """Creates a new weapon that it will defeat"""
        return self.__class__((self.value - 1) % 3)

class RockPaperScissors:
    """Wrapper for the Twitter interface"""

    MAX_COUNT = 1  # Will increase this in production

    def __init__(self) -> None:
        auth = tweepy.OAuthHandler(os.environ["API_KEY"],
                                   os.environ["API_SECRET"])
        auth.set_access_token(os.environ["ACCESS_TOKEN"],
                              os.environ["ACCESS_TOKEN_SECRET"])
        self.api = tweepy.API(auth, wait_on_rate_limit=True,
                              wait_on_rate_limit_notify=True)
        self.me = self.api.me()  # pylint: disable=invalid-name
        self.timeline = self.api.user_timeline(count=self.MAX_COUNT)

    def _already_replied_to(self, tweet: tweepy.models.Status) -> bool:
        return tweet.id in set(tweet.in_reply_to_status_id
                               for tweet in self.timeline)

    @staticmethod
    def _weapons(tweet: tweepy.models.Status) -> Set[Weapon]:
        return set(weapon for weapon in Weapon
                   if weapon.name in tweet.text.upper())

    def _filter(self, tweet: tweepy.models.Status) -> bool:
        if self._already_replied_to(tweet):
            return False
        if len(self._weapons(tweet)) != 1:
            return False
        return tweet.in_reply_to_user_id == self.me.id

    @staticmethod
    def _compose(tweet: tweepy.models.Status) -> dict:
        weapon = RockPaperScissors._weapons(tweet).pop()
        text = f"@{tweet.author.screen_name} {weapon.defeated_by.name.title()}."
        return {"status": text, "in_reply_to_status_id": tweet.id}

    def mentions(self) -> list:
        """Get mentions"""
        tweets = self.api.mentions_timeline(since_id=self.timeline.since_id,
                                            count=self.MAX_COUNT)
        tweets = [tweet for tweet in tweets if self._filter(tweet)]
        return tweets

    def reply(self, tweet: tweepy.models.Status) -> tweepy.models.Status:
        """Win the game"""
        composition = self._compose(tweet)
        LOG.info("Replying to \"%s\" with \"%s\"",
                 tweet.text, composition["status"])
        status = self.api.update_status(**composition)
        self.timeline.append(status)
        return status

def lambda_parameters() -> dict:
    """Get parameters from SSM parameter store"""
    # pylint: disable=import-outside-toplevel
    import boto3  # type: ignore
    ssm = boto3.client("ssm")
    prefix = "rockpaperscissors-"
    names = ["api-key", "api-secret", "access-token", "access-token-secret"]
    names = [prefix + name for name in names]
    parameters = [ssm.get_parameter(Name=name, WithDecryption=True)["Parameter"]
                  for name in names]
    return {p["Name"].split(prefix)[1].upper().replace("-", "_"): p["Value"]
            for p in parameters}


# pylint: disable=unused-argument
def lambda_handler(event: dict, context: Any) -> dict:
    """Lambda entry point"""
    # type(context) = bootstrap.LambdaContext
    os.environ.update(lambda_parameters())
    try:
        main()
        return {"ok": True, "message": "ok"}
    # pylint: disable=broad-except
    except Exception as ex:
        return {"ok": False, "message": str(ex)}

def main() -> None:
    """Entry point"""
    rps = RockPaperScissors()
    mentions = rps.mentions()
    for mention in mentions:
        rps.reply(mention)

if __name__ == "__main__":
    main()
