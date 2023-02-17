from PyQt5 import QtWidgets, QtGui, QtCore

import colors_ui
import main

class ColorPicker(QtWidgets.QWidget, colors_ui.Ui_Settings):
    def __init__(self, main: main.MainApp):
        super().__init__()
        self.main = main
        self.setupUi(self)
        self.text_color.clicked.connect(self.text_color_S)
        self.buttons_color.clicked.connect(self.button_color_S)
        self.background_color.clicked.connect(self.background_color_S)
        self.slider_handle_color.clicked.connect(self.slider_handle_S)
        self.slider_groove_color.clicked.connect(self.slider_groove_S)
        self.load_theme.clicked.connect(self.load_theme_S)
        self.export_theme.clicked.connect(self.export_theme_S)
        self.default.clicked.connect(self.default_S)

    def __str__(self) -> str:
        return self.main.MainWindow.styleSheet()

    def text_color_S(self) -> None:
        v = QtWidgets.QColorDialog().getColor()
        tmp = v.name()
        self.main.MainWindow.setStyleSheet(self.main.MainWindow.styleSheet() + "QLabel {color: %s } QPushButton {color: %s} QListWidget{color: %s} QStatusBar{color: %s} QMenuBar{background-color: %s}" % (tmp, tmp, tmp, tmp, tmp))
        print(tmp)
    def button_color_S(self) -> None:
        v = QtWidgets.QColorDialog().getColor()
        tmp = v.name()

        self.main.MainWindow.setStyleSheet(self.main.MainWindow.styleSheet() + "QPushButton {background-color: %s}" % tmp)
        print(tmp)
    def background_color_S(self) -> None:
        v = QtWidgets.QColorDialog().getColor()
        tmp = v.name()
        self.main.MainWindow.setStyleSheet(self.main.MainWindow.styleSheet() + "QWidget {background-color: %s}" % tmp)
        print(tmp)

    def slider_handle_S(self) -> None:
        v = QtWidgets.QColorDialog().getColor()
        tmp = v.name()
        self.main.MainWindow.setStyleSheet(
            self.main.MainWindow.styleSheet() + "QSlider::handle:horizontal {background-color: %s}" % tmp)
        print(tmp)
    def slider_groove_S(self) -> None:
        v = QtWidgets.QColorDialog().getColor()
        tmp = v.name()
        self.main.MainWindow.setStyleSheet(
            self.main.MainWindow.styleSheet() + "QSlider::groove:horizontal {background-color: %s}" % tmp)
        print(tmp)

    def default_S(self) -> None:
        self.main.MainWindow.setStyleSheet(open("data/css/main.css", "r").read())

    def load_theme_S(self) -> bool:
        x = QtWidgets.QFileDialog().getOpenFileName(directory=__file__, filter="css (*.css)")
        file = open(x[0], "r")
        rl = file.readlines()
        self.main.MainWindow.setStyleSheet(''.join(rl))
        return True


    def export_theme_S(self) -> str:
        x = self.main.MainWindow.styleSheet()
        diag = QtWidgets.QFileDialog().getExistingDirectory()
        open(diag + '/style.css', "w").write(x)
        open("theme_path.txt", "w").write(diag + "/style.css")


class Settings:
    def __init__(self):
        pass
    def colorDialog(self, main):
        self.colorpicker = ColorPicker(main)
        self.colorpicker.show()


