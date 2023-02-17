import sqlite3
import os




class Database(object):
    def __init__(self, database="media_db.db"):
        if not os.path.exists(os.path.dirname(__file__) +"\\data\\" + database):
            try:
                os.mkdir("data")
            except:
                pass
            open("data/" + database, "w").close()
            tempcon = sqlite3.connect('data/' + database)
            tempcon.cursor().execute("CREATE TABLE 'music' (path string(32767))")
            tempcon.cursor().execute("CREATE TABLE 'playlists' (name string(256), music string(9223372036854775807))")
            tempcon.commit()
            tempcon.close()
        self.con = sqlite3.connect('data/' + database)
        self.cur = self.con.cursor()

    def add_music(self, path):
        try:
            self.cur.execute("INSERT INTO 'music' VALUES ('{}')".format(path))
            self.con.commit()
        except Exception as e:
            print(e)
            return ""

    def read_music(self):
        try:
            return self.cur.execute("SELECT * FROM 'music'").fetchall()
        except Exception as e:
            print(str(e))
            return ""


    def request_select(self, sql_request):
        try:
            return self.cur.execute(sql_request).fetchall()
        except Exception as e:
            print(e)
            return ""

    def add_playlist(self, playlist):
        print(playlist['name'], playlist['musics'])
        self.cur.execute(f'UPDATE playlists SET music="{str(playlist["musics"])}" WHERE name LIKE "{playlist["name"]}"')
        self.con.commit()

    def get_playlists(self):
        return self.cur.execute("SELECT * FROM 'playlists'").fetchall()

    def get_playlist_named(self, name: str):
        return self.cur.execute(f"SELECT * FROM 'playlists' WHERE name LIKE '{name}'").fetchone()

    def create_playlist(self, name):
        self.cur.execute(f'INSERT INTO playlists (`name`, `music`) VALUES ("{name}", "")')
        self.con.commit()