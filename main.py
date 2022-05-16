import feedparser
# import hashlib
import sqlite3
import os
import json
import requests

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
}


#feed = feedparser.parse('http://feeds.bbci.co.uk/news/rss.xml#')


# read LINKS from previously created file
# !!! CUTTING THE LINE BREAK !!!
with open('in/links.txt') as file:
    urls = [line.strip() for line in file.readlines()]

my_feeds = []

with requests.Session() as session:
    for url in urls:
        print(url)
        try:
            response = session.get(url=url, headers=headers)
            my_feeds.append(url)
            # if response.status_code == 200:
            #     print('Success!')
            # elif response.status_code == 404:
            #     print('Not Found.')
        except:
            print(f'Not Found: {url} !_!_!_!_!')


# feeds = [feedparser.parse(url)['entries'] for url in urls]
#
#
#
# #print(feeds[1][0].keys())
# #feedparser.parse('https://dev.to/feed')[0].keys()
#
# feed = [item for feed in feeds for item in feed]
#
#
# with open('out.json', 'w', encoding='utf-8') as file:
#         json.dump(feed, file, indent=4, ensure_ascii=False)


scriptDir = os.path.dirname(os.path.realpath(__file__))
db_connection = sqlite3.connect(scriptDir + '/rss.sqlite')
db = db_connection.cursor()
db.execute('CREATE TABLE IF NOT EXISTS myrss (title TEXT, date TEXT)')


def article_is_not_db(article_title, article_date):
    db.execute("SELECT * from myrss WHERE title=? AND date=?", (article_title, article_date))
    if not db.fetchall():
        return True
    else:
        return False


def add_article_to_db(article_title, article_date):
    db.execute("INSERT INTO myrss VALUES (?,?)", (article_title, article_date))
    db_connection.commit()


# We write the procedure for obtaining a feed, checking its presence in the database:
def read_article_feed(feed):
    feed = feedparser.parse(feed)
    print(feed)

    # feeds = [feedparser.parse(url)['entries'] for url in urls]
    # feed = [item for feed in feeds for item in feed]

    for article in feed['entries']:
        if article_is_not_db(article['title'], article['published']):
            add_article_to_db(article['title'], article['published'])
            print('New feed found ' + article['title'] +',' + article['link'])


# Checking each feed from the list:
def spin_feds():
    for x in my_feeds:
        read_article_feed(x)


if __name__ == '__main__':
    spin_feds()
    db_connection.close()
