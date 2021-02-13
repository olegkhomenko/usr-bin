#!/Users/ko/miniconda3/bin/python3
# modify shebang with your python executable 
import requests
from bs4 import BeautifulSoup


def hackernews_scrap():
    resp = requests.get("https://news.ycombinator.com")
    if not resp.ok:
        print(f"Something went wrong. Response status code: {resp.status_code}")

    html_text = resp.text
    soup = BeautifulSoup(html_text, "html.parser")
    posts = soup.find_all("a", "storylink")
    scores = soup.find_all("span", "score")

    def sort_by(tup):
        return int(tup[1].text.split(" ")[0])

    for i, (post, score) in enumerate(sorted(zip(posts, scores), key=sort_by)):
        print(post.text)
        print(score.text)
        print(post.attrs.get("href") + "\n")


if __name__ == "__main__":
    hackernews_scrap()
