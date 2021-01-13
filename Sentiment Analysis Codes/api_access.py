import tweepy
from tweepy import OAuthHandler
import config

try:

    # Creating the authentification object
    auth = OAuthHandler(config.consumer_key, config.consumer_secret)

    # Setting access token and secret
    auth.set_access_token(config.access_token, config.access_secret)

    # Creating the Tweepy API object to fetch tweets
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    
except tweepy.TweepError as e:
    
    print(f"Error: Twitter Authentification Failed - \n{str(e)}")