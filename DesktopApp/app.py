# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QMainWindow, QDesktopWidget

from DesktopApp import __appname__
from DesktopApp.widgets.table import CardTable


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.status_bar = self.statusBar()

        # Set up the card table
        self.card_table = CardTable(self)
        self.setCentralWidget(self.card_table)
        self.card_table.msg_to_status_bar[str].connect(self.status_bar.showMessage)

        # Set up geometry
        self.resize(1000, 800)
        self.center()
        self.setWindowTitle(__appname__)
        self.show()

        # Start game
        self.card_table.start()

    def center(self):
        """centers the window on the screen"""
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(int((screen.width() - size.width()) / 2),
                  int((screen.height() - size.height()) / 2))


