import feedparser
import hashlib
import sqlite3
import os
import json
from tkinter import Tk, Label, Button
from pathlib import Path    # checking the existence of program files

scriptDir = os.path.dirname(os.path.realpath(__file__))
db_connection = sqlite3.connect(scriptDir + r'/rss.sqlite')
db = db_connection.cursor()

# =====================================================================================================================

timer_running = True

# Timer :
mm = 0   # minutes
ss = 15  # seconds

default_seconds = mm * 60 + ss
timer_seconds = default_seconds


def timer_start_pause():
    global timer_running
    timer_running = not timer_running  # work | pause
    print('Timer running!..')
    if timer_running:  # work
        timer_tick()


def timer_reset():
    global timer_running, timer_seconds
    timer_running = False  # stop
    timer_seconds = default_seconds  # start position
    show_timer()


def timer_tick():
    global timer_seconds
    if timer_running and timer_seconds:
        label.after(1000, timer_tick)  # restart after 1 sec
        # decrease the timer

        timer_seconds -= 1

        if timer_seconds == 0:
            timer_seconds = default_seconds
            print(f'')
            main()
        show_timer()


def show_timer():
    m = timer_seconds//60
    s = timer_seconds-m*60
    label['text'] = '%02d:%02d' % (m, s)

# =====================================================================================================================


db.execute("""CREATE TABLE IF NOT EXISTS feeds(     
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    feed_link_sha TEXT(64), 
    feed_link TEXT,
    feed_sha TEXT(64)
   );
""")
db_connection.commit()

db.execute("""CREATE TABLE IF NOT EXISTS items(
   item_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
   item_title TEXT,
   item_published TEXT,
   feed_id INTEGER,
   FOREIGN KEY (feed_id)  REFERENCES feeds (id) ON DELETE CASCADE);
""")
db_connection.commit()


def feed_is_not_db(fls):
    db.execute("SELECT * FROM feeds WHERE feed_link_sha = ?", (fls,))
    if not db.fetchall():
        return True
    else:
        return False


def add_feed_to_db(fls, fl, fs):
    db.execute("INSERT INTO feeds VALUES (?, ?, ?, ?);", (None, fls, fl, fs))
    db_connection.commit()


def item_is_not_db(fid, t, p):
    db.execute("SELECT * FROM items WHERE feed_id = ? AND item_title = ? AND item_published = ?", (fid, t, p))
    if not db.fetchall():
        return True
    else:
        return False

def add_items_to_db(item_title, item_published, feed_id):
    db.execute("INSERT INTO items VALUES (?, ?, ?, ?)", (None, item_title, item_published, feed_id))
    db_connection.commit()


items_new = []
items = []
item_new_my = []


def add_items_to_feed_(url, feed_link_sha, key):


    global items_new
    global item_new_my
    items_new_count = 0

    for item in items['entries']:

        db.execute("SELECT id FROM feeds WHERE feed_link_sha = ?", (feed_link_sha,))
        feed_id_ = db.fetchone()
        feed_id = feed_id_[0]

        tit = item['title']
        try:
            pub = item['published']

            if item_is_not_db(feed_id, tit, pub):
                add_items_to_db(item['title'], item['published'], feed_id)
                #print('New item found: ' + item['title'] + ',' + item['link'])
                items_new.append(item)
                items_new_count += 1

                pp_ = []
                for pp in item['published_parsed']:
                    pp_.append(pp)

                item_s_hash = hashlib.sha256(str(item['summary']).encode('utf-8'))
                item_hash = item_s_hash.hexdigest()

                try_bool = True
                source_title = ''
                source_href = ''

                try:
                    source = item['source']
                    source_title = item['source']['title']
                    source_href = item['source']['href']
                    try_bool = False
                except:
                    pass
                item_new_my.append(
                    {
                        'feedname': key,
                        'itemID': item_hash,
                        'dateYear': pp_[0],  # from “published parsed”
                        'date month': pp_[1],
                        'dateDay': pp_[2],
                        'dateHour': pp_[3],
                        'dateMinute': pp_[4],
                        'dateSecond': pp_[5],
                        'dateDayofWeek': pp_[6],
                        'dateDayofYear': pp_[7],
                        'dateTimezone': pp_[8],
                        'title': item['title'],  # as is “title”
                        'link': 'http:www.cnn.com/fullilinktothearticleofthe-item',  # as is “link”
                        'sourceName': source_title,
                        'sourceURL': source_href  # from “source” — “href” and “title”
                    }
                )

                if try_bool:
                    print(f"New item found:  {item['title']}  {item['link']}  ------------>  Name: {source_title}  URL: {source_href}")
                else:
                    print('New item found: ' + item['title'] + ',' + item['link'] + ', ------------> ' 'SOURCE is NONE!!!')
        except:
            print(f'FEED: {url} has an invalid post date format!')

def main():
    global item_new_my

    # with open('in/links.txt') as file:
    #     urls = [line.strip() for line in file.readlines()]
    with open('./in/links.json', 'r', encoding='utf-8') as set_:
        set_data = json.load(set_)

    global items, items_new

    # for url in urls:
    for key in set_data:
        url = set_data[key]
        if url:
            feed_link = url

            f_link_hash = hashlib.sha256(str(feed_link).encode('utf-8'))
            feed_link_sha = f_link_hash.hexdigest()

            items = feedparser.parse(url)

            # I using entries, because in testing it gave me the same hash.
            items_updated = items.entries

            hash_object = hashlib.sha256(str(items_updated).encode('utf-8'))
            feed_sha = hash_object.hexdigest()

            if feed_is_not_db(feed_link_sha):
                #print(f'{feed_link} - feed is NOT db! ADD...')
                add_feed_to_db( feed_link_sha, feed_link, feed_sha)
                #print(f'New feed found:  {feed_link_sha} - {feed_link} feedSHA: {feed_sha}')

                ### ADD items to feed
                ###
                add_items_to_feed_(url, feed_link_sha, key)
            else:
                #print(f'feed: {feed_link} IN db ')
                db.execute("SELECT feed_sha FROM feeds WHERE feed_link_sha = ?", (feed_link_sha,))
                ttt = db.fetchone()
                if ttt[0] == feed_sha:
                    pass
                    #print(f'EQUAL! {ttt[0]} = {feed_sha}')
                else:
                    #print(f'!!! NOT EQUAL !!! {ttt[0]} != {feed_sha}')
                    add_items_to_feed_(url, feed_link_sha, key)
            #print(f'---------------------------------')

    # clear file...

    with open('feedsImported.json', 'w', encoding='utf-8') as file:
        json.dump(item_new_my, file, indent=4, ensure_ascii=False)
    item_new_my = []

    # NEW items to file
    if items_new:
        with open('feedsImported_new_items.json', 'w', encoding='utf-8') as file:
            json.dump(items_new, file, indent=4, ensure_ascii=False)
        items_new = []

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    # ALL items to file
    merged = []
    out_files = ('feedsImported_new_items.json', 'feedsImported_all_items.json')

    fle = Path('feedsImported_all_items.json')
    if fle.touch():
        pass
    else:
        fle.touch(exist_ok=True)
        with open('feedsImported_all_items.json', 'w', encoding='utf-8') as file:
            file.write('[]')

    # clear file...
    with open('urls.txt', 'w+', encoding='utf-8') as file:
        file.write('')

    for infile in out_files:
        with open(infile, 'r', encoding='utf-8') as infp:
            data = json.load(infp)
            merged.extend(data)

    with open('feedsImported_all_items.json', 'w', encoding="utf-8") as outfp:
        json.dump(merged, outfp)
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


main()


if __name__ == '__main__':
    #main()
    root = Tk()
    label = Label(root)
    label.pack()
    Button(root, text='start/pause', command=timer_start_pause).pack()  # запуск/пауза отсчета
    Button(root, text='reset', command=timer_reset).pack()  # сброс
    timer_reset()
    root.mainloop()
