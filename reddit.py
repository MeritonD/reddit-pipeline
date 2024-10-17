import praw
from dotenv import load_dotenv
import os
import requests
import time
import json

load_dotenv()

auth = requests.auth.HTTPBasicAuth(
    os.environ.get("client_id"), os.environ.get("client_password")
)

data = {
    "grant_type": "password",
    "username": os.environ.get("username"),
    "password": os.environ.get("user_password"),
}

headers = {"User-Agent": "Ubuntu/v1"}
res = requests.post(
    "https://www.reddit.com/api/v1/access_token", auth=auth, data=data, headers=headers
)

access_token = res.json()["access_token"]

headers.update({"Authorization": f"bearer {access_token}"})

posts = []
after = None

posts_with_comments = []

# Retry configuration
max_retries = 10
sleep_time = 10

for i in range(10):
    params = {"limit": 100, "after": after}
    for attempt in range(max_retries):
        try:
            res = requests.get(
                "https://oauth.reddit.com/r/sidehustle/top",
                headers=headers,
                params=params,
            )

            data_posts = res.json()
            posts.extend(data_posts["data"]["children"])
            break
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error on attempy {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                time.sleep(sleep_time)
            else:
                raise

    for post in posts:
        post_data = post["data"]
        post_id = post_data["id"]
        post_title = post_data["title"]
        permalink = post_data["permalink"]

        comments_url = f"https://oauth.reddit.com{permalink}.json"

        for attempt in range(max_retries):
            try:
                res_comments = requests.get(comments_url, headers=headers)

                if res_comments.status_code == 200:
                    post_comments_data = res_comments.json()

                    if len(post_comments_data) > 1:
                        comments = post_comments_data[1]["data"]["children"]
                        post_data["comments"] = comments
                    else:
                        post_data["comments"] = []
                else:
                    post_data["comments"] = []
                break
            except requests.exceptions.ConnectionError as e:
                print(f"Connection error on attempy {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(sleep_time)
                else:
                    raise

    posts_with_comments.append(post_data)

    after = data_posts["data"]["after"]

    print(f"Successful Iteration number {i} is done")

with open("reddit_posts.json", "w") as json_file:
    json.dump(posts_with_comments, json_file, indent=4)
