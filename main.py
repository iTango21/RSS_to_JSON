import feedparser
import json


feed = feedparser.parse('http://feeds.bbci.co.uk/news/rss.xml#')

urls = ['http://feeds.bbci.co.uk/news/rss.xml#',
        'http://feeds.nature.com/nmat/rss/current',
        'https://rss.nytimes.com/services/xml/rss/nyt/Sports.xml',
        'http://feeds.bbci.co.uk/news/rss.xml#',
        'https://news.google.com/rss/search?q=weird+AND+OR+hundred+OR+thousand+OR+million+OR+billion&num=100&newwindow=1&safe=off&client=safari&rls=en&biw=1415&bih=1086&um=1&ie=UTF-8&hl=en-US&gl=US&ceid=US:en',
        'http://feeds.bbci.co.uk/news/world/africa/rss.xml',
        'https://news.google.com/rss/search?q=Elon%20Musk&ceid=US:en&hl=en-US&gl=US',

    ]

feeds = [feedparser.parse(url)['entries'] for url in urls]
#print(feeds[1][0].keys())

#feedparser.parse('https://dev.to/feed')[0].keys()

feed = [item for feed in feeds for item in feed]
print(feed)

with open('out.json', 'w', encoding='utf-8') as file:
        json.dump(feed, file, indent=4, ensure_ascii=False)


