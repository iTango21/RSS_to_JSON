import feedparser
import json
import requests

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
}


#feed = feedparser.parse('http://feeds.bbci.co.uk/news/rss.xml#')


# читаю ССЫЛКИ из ранее созданного файла
# !!! ОБРЕЗАЮ СИМВОЛ ПЕРЕНОСА СТРОКИ !!!
with open('in/links.txt') as file:
    urls = [line.strip() for line in file.readlines()]

with requests.Session() as session:
    for url in urls:
        print(url)
        try:
            response = session.get(url=url, headers=headers)
            # if response.status_code == 200:
            #     print('Success!')
            # elif response.status_code == 404:
            #     print('Not Found.')
        except:
            print('Not Found!!!')

# feeds = [feedparser.parse(url)['entries'] for url in urls]
# #print(feeds[1][0].keys())
#
# #feedparser.parse('https://dev.to/feed')[0].keys()
#
# feed = [item for feed in feeds for item in feed]
# #print(feed)
#
# with open('out.json', 'w', encoding='utf-8') as file:
#         json.dump(feed, file, indent=4, ensure_ascii=False)


