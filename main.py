import re
import sqlite3
import glob


def db_connect():
    path = glob.glob('/*/*/.mozilla/firefox/*.default/places.sqlite')[0]
    conn = sqlite3.connect(path)
    c = conn.cursor()
    return c, conn


def downloads():
    download_result = open('downloads.txt', 'w')
    
    cursor.execute("SELECT datetime(moz_historyvisits.visit_date/1000000,'unixepoch'), moz_places.url "
                   "FROM moz_historyvisits, moz_places WHERE moz_places.id = moz_historyvisits.place_id "
                   "AND visit_type=7 ORDER BY visit_date")
    for row in cursor:
        date = str(row[0])
        url = str(row[1])    
        if re.search(r'(.pdf$|.jpg$|.jpeg$|.png$|.zip$|.mp3$)', url):
            line = ' '.join((date, url))
            download_result.write(line + '\n')

    download_result.close()
    

def google_search():
    search_result = open('google_search_all.txt', 'w')
    search_word = open('google_search_word.txt', 'w')
    cursor.execute("SELECT datetime(moz_historyvisits.visit_date/1000000,'unixepoch'), moz_places.url "
                   "FROM moz_historyvisits, moz_places WHERE visit_count>0 "
                   "AND moz_places.id == moz_historyvisits.place_id ORDER BY visit_date")
    
    for row in cursor:
        date = str(row[0])
        url = str(row[1])   

        if 'google' in url.lower():
            r = re.findall(r'q=.*\&', url)
            if r:
                search = r[0].split('&')[0]
                search = search.replace('q=', '').replace('+', ' ')
                line = ' '.join((date, search))
                search_result.write(line + '\n')
                if 'python' in search:
                    line = ' '.join((date, search))
                    search_word.write(line + '\n')

    search_result.close()
    search_word.close()


if __name__ == '__main__':
    cursor, conn = db_connect()
    downloads()
    google_search()
    conn.close()
