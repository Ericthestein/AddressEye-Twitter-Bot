# AddressEye

AddressEye is a [Twitter bot](https://twitter.com/AddressEye) that can convert a property address into a satellite image representing a birds-eye view. Internally, it uses the [MapQuest Geocoding API](https://developer.mapquest.com/documentation/geocoding-api/) to convert addresses into latitude and longitude coordinate pairs. Then, it passes these pairs through the [MapBox Satellite Imagery API](https://docs.mapbox.com/help/getting-started/satellite-imagery/) to obtain satellite imagery.

## Try it out

To try out [AddressEye](https://twitter.com/AddressEye), send a tweet to @AddressEye with an address. For example: `@AddressEye 1815 Stadium Rd, Charlottesville, VA 22903`. For usage instructions, send `@AddressEye help`.

## Sample output

![output](sample_output.PNG "AddressEye Sample Output")

## Building With Docker

To build a Docker image of AddressEye, run `docker build -t address_eye .` after cloning this repository and `cd`ing into the directory.
Alternatively, you could pull the [docker image from dockerhub](https://hub.docker.com/r/ericthestein/address_eye) by running `docker pull ericthestein/address_eye`

## Running With Docker

To run the previously-built Docker image, run the following, adding in your keys as necessary:
```
docker run -d -p 8080:80 \
  -e TWITTER_CONSUMER_KEY= \
  -e TWITTER_CONSUMER_SECRET= \
  -e TWITTER_ACCESS_TOKEN= \
  -e TWITTER_ACCESS_TOKEN_SECRET= \
  -e TWITTER_ENV_NAME= \
  -e WEBHOOK_ENDPOINT= \
  -e TWITTER_HANDLE= \
  -e MAPQUEST_KEY= \
  -e MAPBOX_KEY= \
  -e RUN_MODE= \
ericthestein/address_eye
```

The `RUN_MODE`s available are:
1) API: Runs AddressEye as a REST API. This contains numerous methods, including one that directly returns a satellite image from an address passed in through JSON, one that processes mentions sent via Twitter's Account Activity API webhook, and one that properly replies to Twitter's Challenge Response Check (CRC). @AddressEye's API is running on LightSail at https://address-eye.0mg5o04lbriga.us-east-1.cs.amazonlightsail.com/. If you choose this `RUN_MODE`, you can test the /address GET endpoint using Postman by sending the following raw body as JSON to `localhost:8080/address/`:
```
{
    "address": "YOUR ADDRESS HERE"
}
```
Requires the following environment variables: `TWITTER_CONSUMER_KEY`, `TWITTER_CONSUMER_SECRET`, `TWITTER_ACCESS_TOKEN`, `TWITTER_ACCESS_TOKEN_SECRET`, `TWITTER_HANDLE`, `MAPQUEST_KEY`, `MAPBOX_KEY`, `RUN_MODE`. If you're only using the /address endpoint, none of the Twitter environment variables are required.

2) REGISTER: Registers for and subscribes to Twitter's Account Activity API webhook.

Requires the following environment variables: `TWITTER_CONSUMER_KEY`, `TWITTER_CONSUMER_SECRET`, `TWITTER_ACCESS_TOKEN`, `TWITTER_ACCESS_TOKEN_SECRET`, `TWITTER_ENV_NAME`, `WEBHOOK_ENDPOINT`, `RUN_MODE`

3) INTERVAL: At a set interval, collects and processes all mentions of @AddressEye.

Requires the following environment variables: `TWITTER_CONSUMER_KEY`, `TWITTER_CONSUMER_SECRET`, `TWITTER_ACCESS_TOKEN`, `TWITTER_ACCESS_TOKEN_SECRET`, `TWITTER_HANDLE`, `MAPQUEST_KEY`, `MAPBOX_KEY`, `RUN_MODE`

## Challenges

The most challenging aspect of developing AddressEye was subscribing to Twitter's Account Activity API webhook for instantaneous mention alerts and replies. Although the bot was functional when run from the `INTERVAL` mode, a maximum delay of 60 seconds between being mentioned and replying was possible. To avoid this, the API running the bot would have to be alerted immediately after the bot was mentioned. However, setting up such alerts was not entirely straightforward at first. The following realizations helped me along the way:
1) an [Account Activity API Dev Environment](https://developer.twitter.com/en/account/environments) is necessary to use this feature. When setting it up, take note of the Dev environment label you provide. This corresponds with the `TWITTER_ENV_NAME` environment variable in the `docker run` command above.
2) after giving your Twitter bot Read, Write, and Direct Messages permissions, you must regenerate your authentication tokens for the change to take effect
3) a CRC GET endpoint must be set up for Twitter to authorize access to the Account Activity API for your bot. For an example of this with FastAPI, see [the twitter_challenge_response_check function of this file](app/main.py).
4) after setting up the CRC GET endpoint and the POST endpoint that consumes Twitter's alerts [(on_twitter_event in this case)](app/main.py), which should have the same path (/webhook in this case), you must send a POST request to Twitter to initiate the CRC check and subsequent alerts. In this repository, the REGISTER `RUN_MODE` handles this process in [entry.py](app/entry.py).

## Built With

AddressEye was developed using:
1) [Twitter Account Activity API](https://developer.twitter.com/en/docs/twitter-api/enterprise/account-activity-api/overview)
2) [MapQuest Geocoding API](https://developer.mapquest.com/documentation/geocoding-api/)
3) [MapBox Satellite Imagery API](https://docs.mapbox.com/help/getting-started/satellite-imagery/)
4) [Amazon Lightsail](https://lightsail.aws.amazon.com/)
5) [FastAPI](https://fastapi.tiangolo.com/)
6) [Docker](https://www.docker.com/)
7) [Python](https://www.python.org/)
