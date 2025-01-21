import requests
import json

THREAD_ID = "222373"
BASE_URL = f"https://www.elektronauts.com/t/{THREAD_ID}.json"


def get_post_ids():
    """Fetch post IDs directly from the URL."""
    response = requests.get(BASE_URL)
    if response.status_code == 200:
        data = response.json()
        return data.get("post_stream", {}).get("stream", [])
    else:
        print(f"Failed to fetch initial data: {response.status_code}")
        return []


post_ids = get_post_ids()


def fetch_posts_in_batches(post_ids, batch_size=20):
    """Fetch posts in batches and return their 'cooked' content."""
    cooked_contents = []
    posts_url = f"https://www.elektronauts.com/t/{THREAD_ID}/posts.json"

    for i in range(0, len(post_ids), batch_size):
        batch = post_ids[i : i + batch_size]
        response = requests.get(posts_url, params={"post_ids[]": batch})
        if response.status_code == 200:
            posts = response.json().get("post_stream", {}).get("posts", [])
            for post in posts:
                cooked_contents.append(
                    {"id": post.get("id"), "content": post.get("cooked", "")}
                )
        else:
            print(f"Failed to fetch batch {i//batch_size + 1}: {response.status_code}")
    return cooked_contents


all_cooked_contents = fetch_posts_in_batches(post_ids)

output_file = "thread_cooked_content_222278.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(all_cooked_contents, f, ensure_ascii=False, indent=4)

print(f"Thread content saved to {output_file}")
