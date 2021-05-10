import time
import os
import tweepy

from process_tweet import process_tweet

# Set up Twitter API Connection

TWITTER_CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY")
TWITTER_CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
TWITTER_ENV_NAME = os.getenv("TWITTER_ENV_NAME")
WEBHOOK_ENDPOINT = os.getenv("WEBHOOK_ENDPOINT")


def create_bot():
    auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
    auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
    twitter_bot = tweepy.API(auth)
    return twitter_bot


def check_mentions(bot, since_id):
    print("Checking all mentions")
    for tweet in tweepy.Cursor(bot.mentions_timeline, since_id=since_id).items():
        print("Found mention")

        since_id = max(tweet.id, since_id)

        # Check if this is a new tweet (not part of an existing thread)
        if tweet.in_reply_to_status_id is not None:
            continue

        # Follow user
        if not tweet.user.following:
            print("Followed user " + tweet.user.name)
            tweet.user.follow()

        try:
            process_tweet(bot, tweet)
        except Exception as e:
            print(e)


    return since_id


def get_latest_id(bot):
    latest_id = 1
    for tweet in tweepy.Cursor(bot.mentions_timeline, since_id=latest_id).items():
        latest_id = max(tweet.id, latest_id)
    return latest_id

def check_mentions_at_interval(interval_in_seconds):
    bot = create_bot()
    since_id = get_latest_id(bot)
    while True:
        since_id = check_mentions(bot, since_id)
        time.sleep(interval_in_seconds)