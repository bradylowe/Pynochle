import os.path as osp
from PyQt5.QtGui import QPixmap
from GameLogic.cards import Card


here = osp.abspath(osp.dirname(__file__))
icons_path = osp.join(here, 'icons')


class QtPlayingCard(Card):

    card_back_pixmap = None
    card_front_pixmap = {}
    Card.values = ['A', '10', 'K', 'Q', 'J', '9']
    card_back_name = 'card-back'

    def __init__(self, suit, value):
        super().__init__(suit, value)
        if QtPlayingCard.card_back_pixmap is None:
            QtPlayingCard.build_pixmaps()

        self.visible = False
        self.face_up = False
        self.x, self.y = 0, 0

    @staticmethod
    def random():
        return QtPlayingCard(Card.random_suit(), Card.random_value())

    @staticmethod
    def build_pixmaps():
        QtPlayingCard.card_back_pixmap = QPixmap(osp.join(icons_path, QtPlayingCard.card_back_name), 'png')
        QtPlayingCard.card_front_pixmap = {hash(card): QPixmap(osp.join(icons_path, card.suit + card.value), 'png')
                                           for card in Card.unique_cards()}

    @property
    def pixmap(self):
        return QtPlayingCard.card_front_pixmap[hash(self)] if self.face_up else QtPlayingCard.card_back_pixmap

    @property
    def width(self):
        return self.pixmap.width()

    @property
    def height(self):
        return self.pixmap.height()
