from PyQt5 import QtWidgets
import database_rq
import ast

class ConnectDBandPlaylists():
    def __init__(self, database: database_rq.Database = None):
        self.database = database

    def addMusicToPlaylist(self, playlist: dict):
        tmp = self.database.get_playlist_named(playlist['name'])
        print(tmp[0][1])
        if tmp[1]:
            x = [i.strip() for i in ast.literal_eval(tmp[1])]
            x.append(playlist['musics'])
        else:
            x = [playlist["musics"]]

        self.database.add_playlist({'name': playlist['name'], 'musics': x})

    def addNewPlaylist(self, name):
        self.database.create_playlist(name)


    def getPlaylists(self):
        return self.database.get_playlists()

    def getPlaylistNamed(self, name: str):
        print(name)
        return self.database.get_playlist_named(name)