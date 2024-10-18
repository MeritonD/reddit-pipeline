# Importing necessary libraries
import praw
import pandas as pd
from dotenv import load_dotenv
import os
import time
import json

load_dotenv()

# Initialize Reddit instance
reddit = praw.Reddit(
    client_id=os.environ.get("client_id"),
    client_secret=os.environ.get("client_password"),
    user_agent='User-Agent": "Ubuntu/v1',
)


# Subreddit to scrape
subreddit = reddit.subreddit("sidehustle")


# Define lists to store data
data = []

i = 0
comm_count = 0

# Scraping posts & Comments
for post in subreddit.top(limit=10):
    data.append(
        {
            "Type": "Post",
            "Post_id": post.id,
            "Title": post.title,
            "Author": post.author.name if post.author else "Unknown",
            "Timestamp": post.created_utc,
            "Text": post.selftext,
            "Score": post.score,
            "Total_comments": post.num_comments,
            "Post_URL": post.url,
        }
    )

    print(f"Scraping post {i + 1} of 10")

    # Check if the post has comments
    if post.num_comments > 0:

        # Scraping comments for each post
        post.comments.replace_more(limit=None)
        for comment in post.comments.list():
            print(f"Scraping comment {comm_count} for post {i + 1} of 10")
            data.append(
                {
                    "Type": "Comment",
                    "Post_id": post.id,
                    "Title": post.title,
                    "Author": comment.author.name if comment.author else "Unknown",
                    "Timestamp": pd.to_datetime(
                        comment.created_utc, unit="s"
                    ).isoformat(),
                    "Text": comment.body,
                    "Score": comment.score,
                    "Total_comments": 0,  # Comments don't have this attribute
                    "Post_URL": None,  # Comments don't have this attribute
                }
            )
            comm_count += 1
            # time.sleep(0.001)
    i += 1


# Create json file
with open("reddit_data_v2.json", "w") as f:
    json.dump(data, f)
