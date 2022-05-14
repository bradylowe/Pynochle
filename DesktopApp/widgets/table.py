from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QFrame

from DesktopApp.qcards import QtPlayingCard


class CardTable(QFrame):

    msg_to_status_bar = pyqtSignal(str)

    displacement = 10

    def __init__(self, parent):
        super().__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)

        self.setStyleSheet("QFrame { background-color:green; }")
        QtPlayingCard.values = ['A', '10', 'K', 'Q', 'J']

        self.card = QtPlayingCard.random()
        self.card.visible = True

    def clearTable(self):
        pass

    def resetDeck(self):
        pass

    def shuffle(self):
        pass

    def deal(self):
        pass

    def hoverCard(self):
        pass

    def playCard(self):
        pass

    def showKitty(self):
        pass

    def start(self):
        """starts game"""
        self.clearTable()
        self.resetDeck()
        self.msg_to_status_bar.emit('Hello, Pynochle!')

    def paintEvent(self, event):
        """paints all shapes of the game"""

        painter = QPainter(self)

        if self.card.visible:
            painter.drawPixmap(self.card.x, self.card.y, self.card.pixmap)

    def keyPressEvent(self, event):
        """processes key press events"""

        key = event.key()

        if key == Qt.Key_V:
            self.card.visible = not self.card.visible

        elif key == Qt.Key_Space:
            self.card.face_up = not self.card.face_up
            if self.card.face_up:
                self.card.suit = QtPlayingCard.random_suit()
                self.card.value = QtPlayingCard.random_value()

        elif key == Qt.Key_Right:
            self.card.x = min(self.card.x + self.displacement, self.width() - self.card.width)
        elif key == Qt.Key_Left:
            self.card.x = max(0, self.card.x - self.displacement)

        elif key == Qt.Key_Up:
            self.card.y = max(0, self.card.y - self.displacement)
        elif key == Qt.Key_Down:
            self.card.y = min(self.card.y + self.displacement, self.height() - self.card.height)

        elif key == Qt.Key_P:
            if 'pretty' in QtPlayingCard.card_back_name:
                QtPlayingCard.card_back_name = 'card-back'
            else:
                QtPlayingCard.card_back_name = 'card-back-pretty'
            QtPlayingCard.build_pixmaps()

        else:
            super(Table, self).keyPressEvent(event)
            return

        self.update()
