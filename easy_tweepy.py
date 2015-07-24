import tweepy
import datetime
import os.path
import traceback

class EasyTweepy:
	def __enter__(self): return self
	def __exit__(self,type,value,tb):
		if type is None:
			pass
		elif isinstance(value,KeyboardInterrupt):
			self.log('[WARNING]','received user interrupt, exiting...')
		else:
			self.log('[ERROR]','encountered unexpected exception...')
			self.log('[ERROR] Exception Type:',str(value))
			self.log('\n[ERROR] Traceback:\n ','  '.join(traceback.format_tb(tb)))
			self.log('exiting...')

		with open('latest_id','w') as f: f.write(str(self.latest_id))
		self.__logfile.close()
		return True

	def __init__(self,debug=False):
		self.__logfile=open('log','a')

		consumer = open('consumer.txt', 'r').read().splitlines()[:2]
		access= open('access.txt', 'r').read().splitlines()[:2]

		auth = tweepy.OAuthHandler(*consumer)
		auth.set_access_token(*access)

		if not debug:
			self.api=tweepy.API(auth,wait_on_rate_limit=True,wait_on_rate_limit_notify=True)
			self.me=self.api.me().screen_name
		else:
			self.me='DEBUG MODE'

		try: 
			self.latest_id=int(open('latest_id', 'r').read())
		except:
			self.latest_id=0
		self.log('Starting',self.me)

	def log(self,*msg):
		logtime=datetime.datetime.now().strftime('[%d/%m/%y %H:%M:%S]')
		print(logtime,*msg)
		self.__logfile.write(logtime+' '+' '.join([str(m) for m in msg])+'\n')

	def mentions(self):
		tweets=self.api.search(to=self.me, since_id=self.latest_id)
		if tweets:
			self.log('found',len(tweets),'new mention(s)')
			self.latest_id=max([tweet.id for tweet in tweets])
		return tweets

	def reply(tweet,msg):
		self.log('sending a reply to tweet#'+tweet.id)
		pre_reply='@'+tweet.user.screen_name+' '
		allowed_length=140-len(pre_reply)
		if msg > allowed_length:
			self.log('[WARNING] message too long (',len(pre_reply+msg),'characters )')
			self.log('[WARNING] msg: '+pre_reply+msg)
			return
		self.api.update_status(status=pre_reply+msg, in_reply_to=tweet.id)


