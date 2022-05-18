import feedparser
import hashlib
import sqlite3
import os
import json
import requests

# =====================================================================================================================
#
from tkinter import Tk, Label, Button

timer_running = True
with open('config.json', 'r', encoding='utf-8') as infp:
    data = json.load(infp)
mm = int(data['time_to_update_min'])
ss = int(data['time_to_update_sec'])

default_seconds = mm * 60 + ss
timer_seconds = default_seconds


def timer_start_pause():
    global timer_running
    timer_running = not timer_running  # work | pause
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
            timer_seconds = 10
            _my_()
        show_timer()


def show_timer():
    m = timer_seconds//60
    s = timer_seconds-m*60
    label['text'] = '%02d:%02d' % (m, s)
#
# =====================================================================================================================


headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
}

scriptDir = os.path.dirname(os.path.realpath(__file__))
db_connection = sqlite3.connect(scriptDir + r'/rss.sqlite')
db = db_connection.cursor()

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

def read_items_from_feed(feed):
    pass
    # feed = feedparser.parse(feed)
    #
    # print(len(feed))
    #
    # feeds_new = []
    # feeds_new_count = 0
    # for item in feed['entries']:
    #     #print(item)
    #
    #     if item_is_not_db(item['title'], item['published']):
    #         add_items_to_db(item['title'], item['published'])
    #         print('New item found: ' + item['title'] +',' + item['link'])
    #         feeds_new.append(item)
    #         feeds_new_count += 1
    #
    # # if feeds_new_count:
    # #     with open('feedsImported.json', 'w', encoding='utf-8') as file:
    # #         json.dump(feeds_new, file, indent=4, ensure_ascii=False)

#=====================================================================================

items_new = []
items = []

### ADD items to feed
###
def add_items_to_feed_(url, feed_link_sha):
    print(len(url))

    global items_new
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
                print('New item found: ' + item['title'] + ',' + item['link'])
                items_new.append(item)
                items_new_count += 1
        except:
            print(f'FEED: {url} has an invalid post date format!')

def _my_():
    # read LINKS from previously created file
    # !!! CUTTING THE LINE BREAK !!!
    with open('in/links.txt') as file:
        urls = [line.strip() for line in file.readlines()]

    my_feeds = []
    global items, items_new

    with requests.Session() as session:
        for url in urls:
            if url:
                response = session.get(url=url, headers=headers)
                feed_link = url

                f_link_hash = hashlib.sha256(str(feed_link).encode('utf-8'))
                feed_link_sha = f_link_hash.hexdigest()

                #my_feeds.append(url)
                # if response.status_code == 200:
                #     print('Success!')
                print(f'status code 200')

                items = feedparser.parse(url)

                # I using entries, because in testing it gave me the same hash.
                items_updated = items.entries

                hash_object = hashlib.sha256(str(items_updated).encode('utf-8'))
                feed_sha = hash_object.hexdigest()

                if feed_is_not_db(feed_link_sha):
                    print(f'{feed_link} - feed is NOT db! ADD...')
                    add_feed_to_db( feed_link_sha, feed_link, feed_sha)
                    print(f'New feed found:  {feed_link_sha} - {feed_link} feedSHA: {feed_sha}')

                    ### ADD items to feed
                    ###
                    add_items_to_feed_(url, feed_link_sha)


                else:
                    print(f'feed: {feed_link} IN db ')
                    db.execute("SELECT feed_sha FROM feeds WHERE feed_link_sha = ?", (feed_link_sha,))
                    ttt = db.fetchone()
                    if ttt[0] == feed_sha:
                        print(f'EQUAL! {ttt[0]} = {feed_sha}')
                    else:
                        print(f'!!! NOT EQUAL !!! {ttt[0]} != {feed_sha}')
                        add_items_to_feed_(url, feed_link_sha)
                print(f'---------------------------------')

    # NEW items to file
    if items_new:
        with open('feedsImported_new_items.json', 'w', encoding='utf-8') as file:
            json.dump(items_new, file, indent=4, ensure_ascii=False)
        items_new = []
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    # ALL items to file
    merged = []
    out_files = ('feedsImported_new_items.json', 'feedsImported_all_items.json')
    """
    !!!
        At the first start, at least one line must exist in the 'feedsImported_all_items.json' file! 
    !!!
    """
    for infile in out_files:
        with open(infile, 'r', encoding='utf-8') as infp:
            data = json.load(infp)
            merged.extend(data)

    with open('feedsImported_all_items.json', 'w', encoding="utf-8") as outfp:
        json.dump(merged, outfp)
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


# # Checking each feed from the list:
# def spin_feds():
#     for x in my_feeds:
#         read_items_from_feed(x)


if __name__ == '__main__':
    root = Tk()
    label = Label(root)
    label.pack()
    Button(root, text='start/pause', command=timer_start_pause).pack()  # запуск/пауза отсчета
    Button(root, text='reset', command=timer_reset).pack()  # сброс

    timer_reset()
    root.mainloop()
    #spin_feds()
    #db_connection.close()
