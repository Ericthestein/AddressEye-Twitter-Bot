import os

from address_to_birds_eye import address_to_birds_eye

BOT_HELP_MESSAGE = "Please provide an address that you would like a satellite image of"

TWITTER_HANDLE = os.getenv("TWITTER_HANDLE")

# Process a mention by either providing help info or replying with an image of a property address
def process_tweet(bot, tweet):
    # parse request
    text = tweet.text
    print("handling tweet with text: " + text)
    text_parts = text.split("@" + TWITTER_HANDLE + " ")
    if len(text_parts) < 2:
        print("Could not find twitter handle")
        return
    message = text_parts[1]
    print("message: " + message)
    if len(message) < 2:
        print("message too short")
        status = "@" + tweet.user.screen_name + " " + "I couldn't understand you; no address provided. " + BOT_HELP_MESSAGE
        bot.update_status(status=status, in_reply_to_status_id=tweet.id)
        return
    if message.lower() == "help":  # show help message
        print("Replying with help message")
        status = "@" + tweet.user.screen_name + " " + BOT_HELP_MESSAGE
        bot.update_status(status=status, in_reply_to_status_id=tweet.id)
        return
    else:  # interpret as address
        print("Replying with satellite image")
        address = message
        # get satellite image
        try:
            image_path = address_to_birds_eye(address)
            print("Sending image " + image_path)
            # reply with image
            status = "@" + tweet.user.screen_name + " Here is a bird's-eye view of " + address
            update_status = bot.update_with_media(image_path, status=status, in_reply_to_status_id=tweet.id)
        except Exception as e:
            print("Error: Could not get image_path")
            # Attempt to send error message as tweet
            status = "@" + tweet.user.screen_name + " " + str(e)
            bot.update_status(status=status, in_reply_to_status_id=tweet.id)