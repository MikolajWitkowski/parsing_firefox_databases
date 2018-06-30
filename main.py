import glob
import re
import sqlite3
from contextlib import contextmanager

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

def main():
    try:
        path = glob.glob('/*/*/.mozilla/firefox/*.default/places.sqlite')[0]
        downloads(path)
        google_search(path)
        return
        
    except (NameError, IndexError):
        print('Error Establishing a Database Connection')
        return   

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
         

def google_search(path):
    with sqlite3.connect(path) as db:
        with db_connect(db, "SELECT datetime(moz_historyvisits.visit_date/1000000,'unixepoch'), moz_places.url "
                   "FROM moz_historyvisits, moz_places WHERE visit_count>0 "
                   "AND moz_places.id == moz_historyvisits.place_id ORDER BY visit_date") as r:
            with open_file('google_search_all.txt', 'w') as google_search_all:
                with open_file('search_word.txt', 'w') as search_word:
                    for row in r:
                        date = str(row[0])
                        url = str(row[1])   

                        if 'google' in url.lower():
                            r = re.findall(r'q=.*\&', url)
                            if r:
                                search = r[0].split('&')[0]
                                search = search.replace('q=', '').replace('+', ' ')
                                line = ' '.join((date, search))
                                google_search_all.write(line + '\n')
                                if 'python' in search:
                                    line = ' '.join((date, search))
                                    search_word.write(line + '\n')


if __name__ == '__main__':
    main()
