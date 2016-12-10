#!/usr/bin/python3

import sys
from easy_tweepy import EasyTweepy
from tweepy.error import TweepError
import time
from random import choice, randrange
import re
wait=10
response_file='responses.txt'
weapons=['scissors','paper','rock',]
with EasyTweepy() as ez:
	ez.log('wait time is', wait, 'seconds')
	while(True):
		try:
			tweets=ez.mentions()
		except:
			ez.log('Error: couldn\'t retrieve tweets')
			raise
		for tweet in tweets:
			weapon=re.findall('('+'|'.join(weapons)+')',tweet.text.lower())
			if len(weapon) == 0:
				continue
			if len(weapon) > 1:
				ez.reply(tweet,'Ow, my logics.')
				continue
			weapon=weapon[0]
			win_weapon=weapons[weapons.index(weapon)-1]
			lose_weapon=weapons[weapons.index(weapon)-2]
			with open(response_file) as responses:
				blank_response=choice([r for r in responses.read().splitlines() if r ])
				response=blank_response.format(Win=win_weapon.title(), 
				                               win=win_weapon, 
				                               Draw=weapon.title(),
				                               draw=weapon, 
				                               Lose=lose_weapon.title(),
				                               lose=lose_weapon,
				                               percentage=randrange(100))
				try:
					ez.reply(tweet,response)
				except TweepError as e:
					if e.args[0]=='Twitter error response: status code = 403':
						pass
					else:
						raise
				except:
					ez.log('Error: couldn\'t send message "'+response+'"')
					raise
			sys.stdout.flush()
		time.sleep(wait)
