import praw
import urllib.request
import requests
import shutil
import tweepy
import config
import os.path

client = tweepy.Client(config.consumer_key,
                       config.consumer_secret, config.access_token,
                       config.access_token_secret)


auth = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)

auth.set_access_token(config.access_token, config.access_token_secret)

api = tweepy.API(auth)


class RedditFetcher:
    def __init__(self, sub, rtype="top", time_span="week", limit=10):
        self.time_span = time_span
        self.limit = limit
        self.sub = sub
        self.rtype = rtype
        self.reddit_key = config.reddit_key
        self.reddit_secret = config.reddit_secret
        self.user_agent = "politwit"
        self.reddit = praw.Reddit(
            client_id=self.reddit_key, client_secret=self.reddit_secret, user_agent=self.user_agent)

    def get_urls(self):
        urls_list = []
        for submission in self.reddit.subreddit(self.sub).top(time_filter=self.time_span, limit=self.limit):
            print(submission.url)
            url = submission.url
            try:
                if url.endswith(("jpg", ".png", "gif")):
                    urllib.request.urlretrieve(url)
                    r = requests.get(url, stream=True)
                    filename = url.split("/")[-1]
                    print(submission.id)
                    print("hi")

                    # Check if the image was retrieved successfully
                    if r.status_code == 200:
                        # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
                        r.raw.decode_content = True

                        # Open a local file with wb ( write binary ) permission.
                        with open(filename, 'wb') as f:
                            shutil.copyfileobj(r.raw, f)

                        print('Image sucessfully Downloaded: ', filename)
                    with open("urls.txt", "a") as f:
                        f.write(
                            f"{submission.id}, {filename}, {submission.title}\n")
                else:
                    print("Image Couldn't be retreived")
            except:
                print("imagecorrupt")

    def tweet_data(self):
        with open("urls.txt", "r") as f:
            lines = f.readlines()
            for line in lines:
                line = line.split(", ")
                break
        f = open("urls.txt", "r+")
        lines = f.readlines()
        tweet = lines[0]

        f.seek(0)
        # truncate the file
        f.truncate()

        # start writing lines except the first line
        # lines[1:] from line 2 to last line
        f.writelines(lines[1:])
        f.close()
        # print(len('tweet'))
        mylist = tweet.split(',')

        tweet = f"Interesting Quote: {mylist[2]} #quoteporn #quotes #quote"
        filename = mylist[1].strip()

        media = api.media_upload(filename)

        # Post tweet with image

        api.update_status(status=tweet, media_ids=[media.media_id])

        return


r = RedditFetcher('quoteporn', rtype="top", time_span="all", limit=365)
# r.get_urls() # use this to fetch initial images
r.tweet_data()  # use this to tweet images once fetched
