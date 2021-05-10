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
from address_to_birds_eye import address_to_birds_eye

BOT_HELP_MESSAGE = "Please provide an address that you would like a satellite image of."

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


@app.get("/webhook")
def twitter_challenge_response_check(crc_token):
    validation = hmac.new(
        key=bytes(TWITTER_CONSUMER_SECRET, 'utf-8'),
        msg=bytes(crc_token, 'utf-8'),
        digestmod=hashlib.sha256
    )
    digested = base64.b64encode(validation.digest())
    response = {
        'response_token': 'sha256=' + format(str(digested)[2:-1])
    }
    print('responding to CRC call')

    return json.dumps(response)


@app.get("/address")
def direct_address_request(address_request: AddressRequest):
    address = address_request.address
    image_path = address_to_birds_eye(address)
    response = FileResponse(image_path)
    return response


@app.post("/webhook")
def on_twitter_event(request: Request):
    json_request = request.json()

    # iterate over all mention events
    if "tweet_create_events" in json_request:
        tweet_create_events = json_request["tweet_create_events"]
        for tweet in tweet_create_events:
            # parse request
            text = tweet["text"]
            if text.lower() == "help": # show help message
                twitter_bot.update_status(status=BOT_HELP_MESSAGE, in_reply_to_status_id=tweet.id)
            else: # interpret as address
                text_parts = text.split("@" + TWITTER_HANDLE)
                if len(text_parts) < 2:
                    continue
                address = text_parts[1]
                # get satellite image
                image_path = address_to_birds_eye(address)
                if image_path is None:
                    print("Error: Could not get image_path")
                    continue
                # reply with image
                twitter_bot.media_upload(image_path, status=address, in_reply_to_status_id=tweet.id)