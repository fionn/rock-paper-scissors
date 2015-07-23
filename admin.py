#!/usr/bin/env python3
# Connect to the Twitter API please

### TODO: write latest_id to file on close


import tweepy
import time
import os.path
consumer = open('consumer.txt', 'r').read().splitlines()[:2]
access= open('access.txt', 'r').read().splitlines()[:2]
auth = tweepy.OAuthHandler(*consumer)
auth.set_access_token(*access)
api = tweepy.API(auth,wait_on_rate_limit=True,wait_on_rate_limit_notify=True)

#https://github.com/tweepy/tweepy/issues/554
try:
	user = api.me()
	print('Starting',user.screen_name)
except Exception as e:
	print(e)
	exit(1)

def get_mentions(latest_id):
	last_tweet_id=0
	for tweet in api.search(to=user.screen_name, since_id=latest_id):
		last_tweet_id=max(tweet.id,last_tweet_id)
		tweet_info = [tweet.id, tweet.text, tweet.user.id]
		print(*tweet_info)
		try:
			api.update_status(status="@"+tweet.user.screen_name+" ha lol", in_reply_to_status_id=tweet.id)
		except tweepy.error.TweepError as e:
			if '403' in e.args[0]: pass
			else: raise
	return last_tweet_id or latest_id

if __name__ == '__main__':
	latest_id=int(open('latest_id', 'r').read()) if os.path.isfile('latest_id') else None
	try:
		while(True):
			latest_id=get_mentions(latest_id)
			time.sleep(10)
	except KeyboardInterrupt:
		exit(1)
	except:
		raise
	finally:
		with open('latest_id','w') as f:
			f.write(str(latest_id))
