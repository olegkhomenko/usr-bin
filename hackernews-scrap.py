#!/Users/ko/miniconda3/bin/python3
# modify shebang with your python executable
import argparse
from typing import Optional

import requests
from bs4 import BeautifulSoup


def hackernews_scrap(date: Optional[str] = None):
    if date is not None:
        resp = requests.get(
            "https://news.ycombinator.com/front",
            params={"day": f"20{date[:2]}-{date[2:4]}-{date[4:6]}"},
        )
    else:
        resp = requests.get("https://news.ycombinator.com")

    if not resp.ok:
        print(f"Something went wrong. Response status code: {resp.status_code}")
        return

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


def date_t(inp: str):
    if len(inp) != 6 or not inp.isdigit():
        raise ValueError("Date format should be: YYMMDD")
    return inp


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--date",
        default=None,
        type=date_t,
        help="Date to scrap in format: YYMMDD",
    )
    args = parser.parse_args()
    hackernews_scrap(date=args.date)
