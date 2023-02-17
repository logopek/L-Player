import re
import ast
from PyQt5 import QtWidgets, QtSvg
from PyQt5.QtCore import QUrl, QRect
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QMediaPlaylist
import setproctitle
from PyQt5.QtWidgets import QInputDialog, QMenuBar, QMenu, QAction, QMessageBox, QDialog

import settings
#import ui
import playlists
import test_ui
import os
import database_rq
import requests

"""Changelog: Code reviewed"""


class MainApp(test_ui.Ui_MainWindow):
    version = "1.5"

    def __init__(self, MainWindow: QtWidgets.QMainWindow) -> None:
        super().__init__()
        self.MainWindow = MainWindow
        self.MainWindow.setWindowIcon(QIcon("src/music-note-beamed.svg"))
        self.MainWindow.setWindowTitle(f"L Player. Version: {self.version}")
        setproctitle.setproctitle(f"L Player")

        self.setupUi(MainWindow)
        #self._createBindMenuBar()

        self.player = QMediaPlayer()

        self.items = []
        self.selected = False
        self.paused = True
        self.now_pos = 0
        self.confirm = False

        self.playlist = QMediaPlaylist()
        self.player.setPlaylist(self.playlist)
        self.player.setVolume(30)
        self.database = database_rq.Database()
        self.playlistDB = playlists.ConnectDBandPlaylists(self.database)
        self.addMusicFromDatabase()

        self.setupButtons()
        self.load_custom_theme()
        self.loadPlaylists(clear = True)
        self.setGlobalPlaylist()


    def setupButtons(self) -> None:
        """Setup buttons"""
        self.addMusic.clicked.connect(self.addMusicToList)
        self.buttonPlay.clicked.connect(self.playNow)
        self.nextTrack.clicked.connect(self.toNextTrack)
        self.previousTrack.clicked.connect(self.toPreviousTrack)
        self.timeMusic.sliderReleased.connect(self.changeTime)
        self.player.durationChanged.connect(self.setDuration)
        self.player.positionChanged.connect(self.updateSlider)
        self.repeat_btn.clicked.connect(self.repeatMusic)
        self.listMusic.itemSelectionChanged.connect(self.dropAll)
        self.volume.sliderMoved.connect(self.changeVolume)
        self.playlist.currentMediaChanged.connect(self.playlistMediaChanged)
        self.downloadFromWeb.clicked.connect(self.addFromWeb)
        self.settings.clicked.connect(self.openSettings)
        self.add_music_to_playlist.clicked.connect(self.addMusicToPlaylist)
        self.create_new_playlist.clicked.connect(self.createPlaylist)
        self.addMusic.setShortcut("Ctrl+O")
        self.buttonPlay.setShortcut("Space")
        self.nextTrack.setShortcut("D")
        self.previousTrack.setShortcut("A")
        self.playlist_it.itemSelectionChanged.connect(self.changePlaylist)

    def addFromWeb(self):
        dialog = QInputDialog().getText(self.centralwidget, "Url", "Enter your url:")
        temp = dialog[0]
        if temp.find("?") != -1:
            temp = temp[:temp.index("?")]
        if "http://" not in temp or "https://" not in temp:
            temp = "http://" + temp
        if temp:
            if temp.split(".")[-1] == "mp3" or temp.split(".")[-1] == "ogg" or temp.split(".")[-1] == "wav":
                r = requests.get(dialog[0])
                x = QtWidgets.QFileDialog.getExistingDirectory(self, "Select a directory",
                                                               directory=os.environ["USERPROFILE"] + "/Downloads")
                x += "/"
                x += temp.rsplit('/', 1)[-1]
                open(x, "wb").write(r.content)
                if os.path.exists(x):
                    self.listMusic.addItem(x)
                    self.playlist.addMedia(QMediaContent(QUrl(x)))
                    if not self.database.request_select(
                            "SELECT * FROM music WHERE path='{}'".format(x)):
                        self.database.add_music(path=x)

            else:
                print("wrong file")

    def playlistMediaChanged(self):
        self.listMusic.setCurrentRow(self.playlist.currentIndex())

    def repeatMusic(self) -> None:
        """Change playlist state to repeat current music or not"""
        if self.repeat_btn.isChecked():
            self.playlist.setPlaybackMode(QMediaPlaylist.CurrentItemInLoop)
        else:
            self.playlist.setPlaybackMode(QMediaPlaylist.CurrentItemOnce)

    def addMusicFromDatabase(self):
        """Read and add music from database"""
        x = self.database.read_music()

        for i in range(len(x)):
            if x[i][0]:
                if os.path.exists(x[i][0]):
                    self.listMusic.addItem(x[i][0])
                    self.playlist.addMedia(QMediaContent(QUrl(x[i][0])))

        for i in range(self.listMusic.count()):
            self.items.append(self.listMusic.item(i).text())

    def addMusicToList(self) -> None:
        """Add user selected music to list and playlist"""

        dialog = QtWidgets.QFileDialog().getOpenFileNames(directory=os.environ["USERPROFILE"] + "/Music",
                                                          filter="mp3 (*.mp3);; ogg (*.ogg);; wav (*.wav)")

        self.listMusic.addItems([dialog[0][i] for i in range(len(dialog[0])) if dialog[0][i] not in self.items])
        [self.playlist.addMedia(QMediaContent(QUrl(dialog[0][i]))) for i in range(len(dialog[0])) if
         dialog[0][i] not in self.items]

        for i in range(self.listMusic.count()):
            if not self.database.request_select(
                    "SELECT * FROM music WHERE path='{}'".format(self.listMusic.item(i).text())):
                self.database.add_music(path=self.listMusic.item(i).text())
        del dialog

    def changeTime(self) -> None:
        """Change music position in accordance with slider"""
        self.player.setPosition(self.timeMusic.value())

    def changeVolume(self) -> None:
        """Change volume"""
        if self.volume.value() <= 0:
            self.volume_icon.load("src/volume-mute-fill.svg")
        elif self.volume.value() <= 50:
            self.volume_icon.load("src/volume-down-fill.svg")
        elif self.volume.value() > 50:
            self.volume_icon.load("src/volume-up-fill.svg")
        self.player.setVolume(self.volume.value())

    def dropAll(self) -> None:
        """Setting all parameters to default"""
        self.now_pos = 0
        self.player.pause()
        self.buttonPlay.setIcon(QIcon("src/play-circle-fill.svg"))
        self.paused = True


    def setMusic(self) -> bool:
        """Set user selected music"""
        if self.listMusic.selectedItems():
            self.timeMusic.setEnabled(True)
            self.playlist.setCurrentIndex(self.listMusic.row(self.listMusic.selectedItems()[0]))
            return True
        else:
            self.timeMusic.setEnabled(False)
            return False

    def toNextTrack(self) -> None:
        """Change current music to next track"""
        if self.listMusic.count():
            x = self.listMusic.selectedItems()
            if self.listMusic.count() == self.listMusic.row(x[0]) + 1:
                self.listMusic.setCurrentRow(0)
            else:
                self.listMusic.setCurrentRow(self.listMusic.row(x[0]) + 1)
            del x
        self.dropAll()
        self.playNow()

    def toPreviousTrack(self) -> None:
        """Change current music to previous track"""
        if self.listMusic.count():
            x = self.listMusic.selectedItems()
            if self.listMusic.row(x[0]) == 0:
                self.listMusic.setCurrentRow(self.listMusic.count() - 1)
            else:
                self.listMusic.setCurrentRow(self.listMusic.row(x[0]) - 1)
        self.dropAll()
        self.playNow()

    def setDuration(self) -> None:
        """Music duration in minutes and seconds"""
        self.timeMusic.setMaximum(self.player.duration())
        seconds = int((self.player.duration() / 1000) % 60)
        minutes = int((self.player.duration() / (1000 * 60)) % 60)
        self.all_time_music.setText(f"{0 if minutes < 10 else ''}{minutes}:{0 if seconds < 10 else ''}{seconds}")
        del seconds, minutes

    def updateSlider(self) -> None:
        """Change slider position in accordance with music position"""
        self.timeMusic.setValue(self.player.position())
        seconds = int((self.player.position() / 1000) % 60)
        minutes = int((self.player.position() / (1000 * 60)) % 60)
        self.now_time_music.setText(f"{0 if minutes < 10 else ''}{minutes}:{0 if seconds < 10 else ''}{seconds}")
        del seconds, minutes

    def playNow(self) -> None:
        """Playing selected music"""
        x = self.listMusic.selectedItems()[0].text()
        if self.paused:
            self.setMusic()
            self.player.play()
            self.player.setPosition(self.now_pos)

            if self.player.mediaStatus() != 1 and self.player.mediaStatus() != 8:
                self.timeMusic.setEnabled(True)
                self.buttonPlay.setIcon(QIcon("src/pause-circle-fill.svg"))
                self.paused = False
            print(self.player.currentMedia())

        else:
            self.now_pos = self.player.position()
            self.player.pause()
            self.buttonPlay.setIcon(QIcon("src/play-circle-fill.svg"))
            self.paused = True
        self.confirm = False
        self.add_music_to_playlist.setText("Add music to playlist")

    def helpWindow(self):
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Help")
        dialog.setText(
            "How to use \"From web\".\nGet link end with file extension like \".mp3\", \".ogg\", \".wav\" and put it "
            "into input label" "\n Media isn`t playing? Install K-Lite Codec Pack")
        dialog.exec()

    def openSettings(self):
        self.setting_s = settings.Settings()
        self.setting_s.colorDialog(self)
        print(settings.ColorPicker(self))

    def load_custom_theme(self):
        if os.path.exists("theme_path.txt"):
            self.MainWindow.setStyleSheet(open(open("theme_path.txt", "r").read(), "r").read())

    def setGlobalPlaylist(self):
        self.playlist_it.addItem("Global")

    def loadPlaylists(self, clear):
        if clear:
            self.playlist_it.clear()
        playlists = self.playlistDB.getPlaylists()
        print(playlists)
        for i in range(len(playlists)):
                self.playlist_it.addItem(playlists[i][0])

    def changePlaylist(self):
        if self.playlist_it.selectedItems()[0].text() == "Global":
            self.playlist.clear()
            self.listMusic.clear()
            self.addMusicFromDatabase()
        else:
            self.playlist.clear()
            self.listMusic.clear()
            x = self.playlistDB.getPlaylistNamed(self.playlist_it.selectedItems()[0].text())
            x = [n.strip() for n in ast.literal_eval(x[1])]
            print(x)
            for i in x:
                print(i)
                self.playlist.addMedia(QMediaContent(QUrl(i)))
                self.listMusic.addItem(i)

            for i in range(self.listMusic.count()):
                self.items.append(self.listMusic.item(i).text())
    def addTempMusic(self):
        self.playlist.clear()
        self.listMusic.clear()
        self.addMusicFromDatabase()

    def addMusicToPlaylist(self):
        if not self.confirm:
            self.addTempMusic()
            self.listMusic.setCurrentRow(0)
            self.info = {'name': self.playlist_it.selectedItems()[0].text()}
            self.confirm = True
            self.add_music_to_playlist.setText("Press to confirm")
        else:
            self.info["musics"] = self.listMusic.selectedItems()[0].text()
            self.playlistDB.addMusicToPlaylist(self.info)
            self.listMusic.clear()
            self.changePlaylist()
            self.confirm = False
            self.add_music_to_playlist.setText("Add music to playlist")

    def createPlaylist(self):
        dialog = QInputDialog().getText(self.centralwidget, "New playlist", "Name of your new playlist:")
        temp = dialog[0]
        self.playlistDB.addNewPlaylist(temp)
        self.loadPlaylists(clear=True)
        self.setGlobalPlaylist()

def _except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)



if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    exe = MainApp(MainWindow)
    MainWindow.show()
    sys.excepthook = _except_hook
    sys.exit(app.exec_())
