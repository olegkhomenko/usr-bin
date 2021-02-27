#!/Users/ko/miniconda3/bin/python3
# modify shebang with your python executable
import argparse
import datetime
import time
from typing import Optional

import requests
from bs4 import BeautifulSoup
from sqlalchemy import Column, Date, Integer, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy.exc import IntegrityError


SLEEP_TIME = 0.5

Base = declarative_base()


class Post(Base):
    __tablename__ = "hn_posts"
    post_name = Column(Text, primary_key=True, nullable=False)
    post_date = Column(Date, primary_key=True, nullable=False)
    post_score = Column(Integer, nullable=False)
    post_link = Column(Text, nullable=False)
    post_access_date = Column(Date, nullable=False)


def hackernews_scrap(date: Optional[str] = None, session: Optional[Session] = None):
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

    if date is None:
        post_date = datetime.datetime.now()
    else:
        post_date = datetime.datetime.strptime(date, "%y%m%d")

    processed_data = []
    for i, (post, score) in enumerate(sorted(zip(posts, scores), key=sort_by)):
        post_name = post.text
        post_score = score.text
        post_link = post.attrs.get("href")
        if session is not None:
            processed_data += [
                Post(
                    post_name=post.text,
                    post_date=post_date,
                    post_score=int(score.text.split(" ")[0]),
                    post_link=post_link,
                    post_access_date=datetime.datetime.now(),
                )
            ]

        print(post_name)
        print(post_score)
        print(post_link + "\n")

    if session is not None and len(processed_data):
        try:
            session.add_all(processed_data)
            session.commit()
        except IntegrityError as e:  # UNIQUE constraint failed: -> Values are already added
            pass

    return


def date_t(inp: str):
    if len(inp) != 6 or not inp.isdigit():
        raise ValueError("Date format should be: YYMMDD")
    return inp


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--date", default=None, type=date_t, help="Date to scrap in format: YYMMDD")
    parser.add_argument("--date_from", default=None, type=date_t)
    parser.add_argument("--date_to", default=None, type=date_t)
    parser.add_argument("--db", action="store_true")
    args = parser.parse_args()
    if args.date_from or args.date_to:
        assert args.date_from and args.date_to

    hackernews_scrap_kwargs = {}
    if args.db:
        engine = create_engine("sqlite:///hn.db")
        session = sessionmaker(bind=engine)()
        hackernews_scrap_kwargs["session"] = session
        Base.metadata.create_all(engine)

    if args.date_from:
        import numpy as np

        d_from = datetime.datetime.strptime(args.date_from, "%y%m%d")
        d_to = datetime.datetime.strptime(args.date_to, "%y%m%d")
        assert d_to > d_from, "Check dates"
        days = np.arange(d_from, d_to, datetime.timedelta(days=1)).astype(datetime.datetime)
        days = [d.strftime("%y%m%d") for d in days]
        for d in days:
            print(f"DATE: {d}")
            hackernews_scrap(date=d, **hackernews_scrap_kwargs)
            time.sleep(SLEEP_TIME)
    else:
        hackernews_scrap(date=args.date, **hackernews_scrap_kwargs)
