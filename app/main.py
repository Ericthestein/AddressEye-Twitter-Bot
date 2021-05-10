#!/usr/bin/env python3

import os
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel
import hashlib
import hmac
import base64
import json
from typing import Optional
import tweepy
from process_tweet import process_tweet

from address_to_birds_eye import address_to_birds_eye

# Set up Twitter API Connection

TWITTER_CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY")
TWITTER_CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
TWITTER_ENV_NAME = os.getenv("TWITTER_ENV_NAME")
WEBHOOK_ENDPOINT = os.getenv("WEBHOOK_ENDPOINT")
TWITTER_HANDLE = os.getenv("TWITTER_HANDLE")

auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
twitter_bot = tweepy.API(auth)

# Set up API

app = FastAPI()


class AddressRequest(BaseModel):
    address: str


@app.get("/")  # zone apex
def read_root():
    return {"Error": "Please see /docs"}

# The code below has been adapted from https://developer.twitter.com/en/docs/twitter-api/enterprise/account-activity-api/guides/securing-webhooks
# Properly reply to Twitter's Challenge Response Check after registering for webhook alerts
@app.get("/webhook")
def twitter_challenge_response_check(crc_token):
    print("Received CRC with token " + str(crc_token))
    # creates HMAC SHA-256 hash from incoming token and your consumer secret
    consumer_secret_binary = TWITTER_CONSUMER_SECRET.encode(encoding="utf-8")
    crc_token_binary = crc_token.encode(encoding="utf-8")
    sha256_hash_digest = hmac.new(consumer_secret_binary, msg=crc_token_binary,
                                  digestmod=hashlib.sha256).digest()
    # sha256_hash_digest_str = sha256_hash_digest.decode('UTF-8')
    # construct response data with base64 encoded hash
    response = {
        "response_token": "sha256=" + base64.b64encode(sha256_hash_digest).decode("UTF-8")
    }

    return response

# Directly return an address image
@app.get("/address")
def direct_address_request(address_request: AddressRequest):
    print("Received direct address request")
    address = address_request.address
    image_path = address_to_birds_eye(address)
    response = FileResponse(image_path)
    return response

# Process incoming Twitter data
@app.post("/webhook")
async def on_twitter_event(request: Request):
    print("Received twitter event!")
    json_request = await request.json()
    print(json_request)

    # iterate over all mention events
    if "tweet_create_events" in json_request:
        tweet_create_events = json_request["tweet_create_events"]
        for tweet in tweet_create_events:
            tweet = tweepy.Status().parse(None, tweet) # Convert into Tweet object
            process_tweet(twitter_bot, tweet)