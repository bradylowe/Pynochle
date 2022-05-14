from GameLogic.cards import Card, Hand


class SuitEncoding:
    """Create one-hot encodings for suits AND mappings to/from these encodings"""

    n = len(Card.suits)
    # Build a dictionary for getting the corresponding suit from a given index position
    suit = {idx: suit for idx, suit in enumerate(Card.suits)}
    # Build a dictionary for getting the index associated with a given suit
    idx = {this_suit: this_idx for this_idx, this_suit in suit.items()}

    # Build a dictionary for getting the one-hot encoding from a given suit
    one_hot = {suit: [0] * len(Card.suits) for suit in Card.suits}
    for idx, suit in enumerate(Card.suits):
        one_hot[suit][idx] = 1


class CardEncoding:
    """Create one-hot encodings for cards AND mappings to/from these encodings"""

    unique = Hand()
    n = 0

    idx = {}  # Get the index (into the one-hot array) for a given card
    card = {}  # Get the card associated with a given index (integer)
    one_hot = {}  # Get the one-hot encoding of a given card

    @staticmethod
    def build():
        """Create one-hot encodings for cards and mappings to/from these encodings"""

        # Set the possible values, generate a hand with one of each possible card
        CardEncoding.unique = Hand(Card.unique_cards())
        CardEncoding.n = len(CardEncoding.unique)

        # Build a dictionary for getting the corresponding card from a given index position
        CardEncoding.card = {this_idx: this_card for this_idx, this_card in enumerate(CardEncoding.unique)}

        # Build a dictionary for getting the index associated with a given card
        CardEncoding.idx = {this_card: this_idx for this_idx, this_card in CardEncoding.card.items()}

        # Build a dictionary for getting the one-hot encoding from a given card
        CardEncoding.one_hot = {this_card: [0] * CardEncoding.n for this_card in CardEncoding.unique}
        for this_idx, this_card in CardEncoding.card.items():
            CardEncoding.one_hot[this_card][this_idx] = 1

        # Build a null one-hot array (all zeros) for a null card
        CardEncoding.one_hot[None] = [0] * CardEncoding.n
