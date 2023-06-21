import os
import dotenv
from PIL import Image
from instagrapi import Client
import praw
import sys
import urllib.request

dotenv.load_dotenv()
cred_path = os.environ.get("CRED_PATH")
bot = Client()

reddit = praw.Reddit(
        client_id=os.environ.get('RED_ID'),
        client_secret=os.environ.get('RED_SECRET'),
        user_agent="Some random reddit bot"
)

# If credential file exists then:
if os.path.exists(cred_path):
    #load the file
    bot.load_settings(cred_path)
    pass
else:
    #otherwise Login In and Dump settings to credential file 
    bot.login(os.environ.get('USERNAME'), os.environ.get('PASSWORD'))
    bot.dump_settings(cred_path)
print("Logged In!")

def check_if_past(meme):
    with open("past_memes","a+") as f:
        f.seek(0)
        if meme.id in f.read().splitlines():
            return True
        else:
            f.write(meme.id+"\n")
            return False

def post_meme(meme):
    print(meme.url)
    urllib.request.urlretrieve(meme.url,"tmp.jpg")
    img = Image.open("tmp.jpg")
    if meme.url.endswith(".png"):
        img = img.convert("RGB")
    img.save("tmp.jpg")
    print("Received Image")

    uploaded = False
    times_failed = 0
    while True: 
        try:
            bot.photo_upload(
                    "tmp.jpg",
                    f"""
                    {meme.title}
                
                    Credit goes to /u/{meme.author.name}!
                    https://redd.it/{meme.id}/

                    (this is an Automated Post, if your ape like brain coudnt tell already)
                    github.com/OpenSaned/CapriSunPikachu
                    """
            )
        except Exception as e:
            if times_failed == 10:
                print("It failed :(")
                post_successful = False
            else:
                times_failed += 1
                print(f"Retried {times_failed} time(s)")
        else:
            print("Uploaded Post")
            post_successful = True
            break
        if not post_successful:
            break
    return post_successful


subreddit = reddit.subreddit("memes")
for meme in subreddit.top(time_filter="day"):
    if (
            (not meme.over_18)
            and (not meme.is_self) 
            and (meme.url.endswith(".jpg") or meme.url.endswith(".png"))
    ):
        print("found")
        if not check_if_past(meme):
            retries = 0
            while retries != 10:
                if post_meme(meme):
                    break
                else:
                    retries += 1
            break

