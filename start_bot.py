#!/usr/bin/env python3

from easy_tweepy import EasyTweepy
import time

wait=10

with EasyTweepy() as ez:
	ez.log('wait time is', wait, 'seconds')
	while(True):
		tweets=ez.mentions()
		for tweet in tweets:
			ez.log('i saw a tweet')
      #ez.reply(tweet,'oh lol')
		time.sleep(wait)
