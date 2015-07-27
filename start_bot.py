#!/usr/bin/env python3

from easy_tweepy import EasyTweepy
import time
from random import choice

wait=10

with EasyTweepy() as ez:
	ez.log('wait time is', wait, 'seconds')
	while(True):
		tweets=ez.mentions()
		for tweet in tweets:
			if 'rock' in tweet.text.lower(): response_file='paper.txt'
			elif 'paper' in tweet.text.lower(): response_file='scissors.txt'
			elif 'scissors' in tweet.text.lower(): response_file='rock.txt'
			else: continue
		
			with open(response_file) as responses:
				response=choice(responses.read().splitlines())
				ez.reply(tweet,response)
		time.sleep(wait)
