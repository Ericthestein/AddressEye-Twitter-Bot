import os
import requests
from requests_oauthlib import OAuth1Session
import urllib

TWITTER_WEBHOOK_REGISTRATION_ENDPOINT = "https://api.twitter.com/1.1/account_activity/all/env-beta/webhooks.json"
TWITTER_WEBHOOK_SUBSCRIPTION_ENDPOINT = "https://api.twitter.com/1.1/account_activity/all/env-beta/subscriptions.json"

TWITTER_CONSUMER_KEY = os.getenv("CONSUMER_KEY")
TWITTER_CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
TWITTER_ENV_NAME = os.getenv("ENV_NAME")
WEBHOOK_ENDPOINT = os.getenv("WEBHOOK_ENDPOINT")


# Start API

def start_api():
    os.system("../start.sh")


start_api()


# Subscribe to Twitter events

# Code adapted from https://medium.com/@nragusa/getting-started-with-the-twitter-account-activity-api-beta-395e9498af81
def register_and_subscribe_webhook():
    twitter = OAuth1Session(TWITTER_CONSUMER_KEY,
                client_secret=TWITTER_CONSUMER_SECRET,
                resource_owner_key=TWITTER_ACCESS_TOKEN,
                resource_owner_secret=TWITTER_ACCESS_TOKEN_SECRET)
    webhook_endpoint = urllib.parse.quote_plus(WEBHOOK_ENDPOINT)
    reg_url = TWITTER_WEBHOOK_REGISTRATION_ENDPOINT + "?url={}".format(webhook_endpoint)
    reg_res = twitter.post(reg_url)
    sub_url = 'https://api.twitter.com/1.1/account_activity/all/env-beta/subscriptions.json'
    sub_res = twitter.post(sub_url)


try:
    register_and_subscribe_webhook()
except Exception as e:
    print(e)