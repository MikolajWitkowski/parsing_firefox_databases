import glob
import optparse
import re
import sqlite3
from contextlib import contextmanager


def main(download, all_words, word):
    try:
        path = glob.glob('/*/*/.mozilla/firefox/*.default/places.sqlite')[0]
        if download:
            downloads(path)
        if all_words:
            search_all(path)
        if word:
            search_word(path, word)

        return
        
    except (NameError, IndexError):
        print('Error Establishing a Database Connection')
        return   
        

@contextmanager
def db_connect(conn, q, params=()):
    c = conn.cursor()
    c.execute(q, params)
    conn.commit()
    yield c
    c.close()

@contextmanager
def open_file(path, mode):
    file = open(path, mode)
    yield file
    file.close()


def downloads(path):
    with sqlite3.connect(path) as db:
        with db_connect(db, "SELECT datetime(moz_historyvisits.visit_date/1000000,'unixepoch'), moz_places.url "
                   "FROM moz_historyvisits, moz_places WHERE moz_places.id = moz_historyvisits.place_id "
                   "AND visit_type=7 ORDER BY visit_date") as r:
            with open_file('downloads.txt', 'w') as download_result:
                for row in r:
                    date = str(row[0])
                    url = str(row[1])    
                    if re.search(r'(.pdf$|.jpg$|.jpeg$|.png$|.zip$|.mp3$)', url):
                        line = ' '.join((date, url))                    
                        download_result.write(line + '\n')
         

def google_search(path, file, word=None):
    with sqlite3.connect(path) as db:
        with db_connect(db, "SELECT datetime(moz_historyvisits.visit_date/1000000,'unixepoch'), moz_places.url "
                   "FROM moz_historyvisits, moz_places WHERE visit_count>0 "
                   "AND moz_places.id == moz_historyvisits.place_id ORDER BY visit_date") as r:
                    for row in r:
                        date = str(row[0])
                        url = str(row[1])   

                        if 'google' in url.lower():
                            r = re.findall(r'q=.*\&', url)
                            if r:
                                search = r[0].split('&')[0]
                                search = search.replace('q=', '').replace('+', ' ')
                               
                                if word is None:
                                    line = ' '.join((date, search))
                                    file.write(line + '\n')
                                elif word in search:
                                    line = ' '.join((date, search))
                                    file.write(line + '\n')

def search_all(path):
    with open_file('google_search_all.txt', 'w') as google_search_all:
        google_search(path, google_search_all)

def search_word(path, word):
    with open_file('google_search_word.txt', 'w') as google_search_word:
        google_search(path, google_search_word, word)



if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('-d', '--download', action="store_true", help='info about downloaded content')
    parser.add_option('-a', '--all', action="store_true", dest='all', help='searched word on google')
    parser.add_option('-w', '--word', action="store", dest='word', help='checking if the word was searched in google')
    option, arg = parser.parse_args()
    main(download=option.download, all_words=option.all, word=option.word)