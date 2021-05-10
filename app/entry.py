import os
import requests
from requests_oauthlib import OAuth1Session
import urllib
import time
from check_at_interval import check_mentions_at_interval

CHECK_INTERVAL = 60 # For RUN_MODE=INTERVAL (in seconds)

# Links for registering for and subscribing to Twitter webhook alerts
TWITTER_ACCOUNT_ACTIVITY_ENDPOINT = "https://api.twitter.com/1.1/account_activity/all/"
TWITTER_WEBHOOK_REGISTRATION_PATH = "webhooks.json"
TWITTER_WEBHOOK_SUBSCRIPTION_PATH = "subscriptions.json"

# Authentication
TWITTER_CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY")
TWITTER_CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
TWITTER_ENV_NAME = os.getenv("TWITTER_ENV_NAME")
WEBHOOK_ENDPOINT = os.getenv("WEBHOOK_ENDPOINT")

RUN_MODE = os.getenv("RUN_MODE")

# Start API

def start_api():
    print("Starting API")
    os.system("../start.sh")

# Subscribe to Twitter events

# Code adapted from https://medium.com/@nragusa/getting-started-with-the-twitter-account-activity-api-beta-395e9498af81
def register_and_subscribe_webhook():
    print("Registering and subscribing webhook")
    print(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
    twitter = OAuth1Session(TWITTER_CONSUMER_KEY,
                client_secret=TWITTER_CONSUMER_SECRET,
                resource_owner_key=TWITTER_ACCESS_TOKEN,
                resource_owner_secret=TWITTER_ACCESS_TOKEN_SECRET)
    print("Created OAUTH Session")
    print("Endpoint: " + WEBHOOK_ENDPOINT)
    webhook_endpoint = urllib.parse.quote_plus(WEBHOOK_ENDPOINT)
    reg_url = TWITTER_ACCOUNT_ACTIVITY_ENDPOINT + TWITTER_ENV_NAME + "/" + TWITTER_WEBHOOK_REGISTRATION_PATH + "?url={}".format(webhook_endpoint)
    reg_res = twitter.post(reg_url)
    print(reg_res.json())
    sub_url = TWITTER_ACCOUNT_ACTIVITY_ENDPOINT + TWITTER_ENV_NAME + "/" + TWITTER_WEBHOOK_SUBSCRIPTION_PATH
    sub_res = twitter.post(sub_url)
    print(sub_res)
    print("Registered and subscribed webhook")


# Check run mode

if RUN_MODE is None:
    start_api()
elif RUN_MODE == "REGISTER":
    try:
        register_and_subscribe_webhook()
    except Exception as e:
        print(e)
elif RUN_MODE == "API":
    start_api()
elif RUN_MODE == "INTERVAL":
    check_mentions_at_interval(CHECK_INTERVAL)