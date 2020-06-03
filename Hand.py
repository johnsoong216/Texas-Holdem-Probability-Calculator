import numpy as np
from itertools import combinations
from Exception import *


class Hand(np.ndarray):
    """
    A class that identifies the Hand Type

    10: Royal Flush
    9: Straight Flush
    8: Four of A Kind    4, 1, 2
    7. Full House        3, 2, 2
    6: Flush
    5: Straight
    4: Three of a Kind   3, 1, 3
    3: Two Pair          2, 1, 3
    2: One Pair          2, 1, 4
    1: High Card         1, 1, 5

    Properties:

    hand_candidates:
    hand:
    in_rank_values
    rank:

    """


    def __new__(cls, input_array):
        # Input array is an already formed ndarray instance
        # We first cast to be our class type
        obj = np.asarray(input_array).view(cls)
        # add the new attribute to the created instance
        # Finally, we must return the newly created object:
        return obj


    def __init__(self, cards) -> None:
        self.hand_candidates = self.create_hand(cards)

        if len(cards) <= 5:
            self.hand = self.create_hand(cards, sort=True)

            if len(self.hand) == 5:
                # Assign rank and in rank values of the current hand
                self.rank, self.in_rank_values = self.assign_rank(self.hand)
            else:
                # Not a hand of 5 yet
                self.rank, self.in_rank_values = 0, []


    def create_hand(self, cards, sort=False):
        cardlist = np.empty((len(cards),), dtype=object)
        if sort:
            cardlist[:] = sorted(cards)
        else:
            cardlist[:] = cards
        return cardlist

    # @staticmethod
    # @np.vectorize
    # def concatenate(hand_1, hand_2):
    #     """
    #     Want to vectorize two hands，typically 2 + 5
    #     """
    #     if isinstance(hand_1, Hand) and isinstance(hand_2, Hand):
    #         return Hand(np.append(hand_1.hand_candidates, hand_2.hand_candidates))
    #     elif isinstance(hand_1, Hand):
    #         return Hand(np.append(hand_1.hand_candidates, hand_2))
    #     elif isinstance(hand_2, Hand):
    #         return Hand(np.append(hand_1, hand_2.hand_candidates))
    #     return Hand(np.append(hand_1, hand_2))

    @staticmethod
    @np.vectorize
    def find_max(hand):
        if isinstance(hand, Hand):
            if len(hand.hand_candidates) > 5:
                return Hand(max(list(map(Hand, combinations(hand.hand_candidates, 5)))).hand_candidates)
            return hand
        else:
            # wrong
            if len(hand.hand_candidates) > 5:
                return Hand(max(list(map(Hand, combinations(hand.hand_candidates, 5)))).hand_candidates)
            return Hand(hand)

    def __add__(self, other):
        if isinstance(other, Hand):
            return Hand(np.append(self.hand_candidates, other.hand_candidates))
        else:
            return Hand(np.append(self.hand_candidates, other))

    def __radd__(self, other):
        if isinstance(other, Hand):
            return Hand(np.append(self.hand_candidates, other.hand_candidates))
        else:
            return Hand(np.append(self.hand_candidates, other))

    def _valid_hand(self, hand):
        pass

    def _hand_values(self, hand):
        """
        Helper functions to get hand values
        """

        return sorted([card[0] for card in hand])

    def _hand_suits(self, hand):
        """
        Helper functions to get hand's suits
        """
        return sorted([card[1] for card in hand])

    def suit_check(self, hand):
        """
        Checks if all five cards are of the same suit
        True: 5 cards are of the same suit
        False: 5 cards are of different suits
        """
        if len(np.unique(self._hand_suits(hand))) == 1:
            return True
        return False

    def straight_check(self, hand):
        """
        Checks if the five cards form a straight
        True: 5 cards form a straight
        False: 5 cards do not form a straight
        """
        hand_values = self._hand_values(hand)
        if hand_values == list(np.arange(hand_values[0], hand_values[0] + 5, 1)) or \
                (hand_values == [2, 3, 4, 5, 14]):
            return True
        return False

    def assign_rank(self, hand):
        """
        Assigns the rank of the hand
        """
        suit_check = self.suit_check(hand)
        straight_check = self.straight_check(hand)
        hand_values = self._hand_values(hand)

        # We could use straight check and suit check to quickly determine certain card types
        if suit_check and straight_check and hand_values[0] == 10:
            return 10, hand_values
        elif suit_check and straight_check:
            return 9, hand_values
        elif suit_check:
            return 6, hand_values
        elif straight_check:
            return 5, hand_values

        # Assign all other categories
        val, count = np.unique(hand_values, return_counts=True)
        return self._rank_dict((max(count), min(count), len(count))), list(val[count.argsort()])

    def _rank_dict(self, max_min_len):
        rank_params_dict = {(4, 1, 2): 8, (3, 2, 2): 7, (3, 1, 3): 4, (2, 1, 3): 3, (2, 1, 4): 2, (1, 1, 5): 1}
        return rank_params_dict[max_min_len]

    # Overwriting Comparison Operators
    def __eq__(self, other) -> bool:
        if isinstance(other, Hand):
            if self.rank != other.rank:
                return False
            elif Hand.in_rank_comparison(self.in_rank_values, other.in_rank_values) == 0:
                return True
            return False
        return False

    def __gt__(self, other) -> bool:
        if isinstance(other, Hand):
            if self.rank > other.rank:
                return True
            elif self.rank < other.rank:
                return False
            elif Hand.in_rank_comparison(self.in_rank_values, other.in_rank_values) == 1:
                return True
            return False
        return False

    def __lt__(self, other) -> bool:
        if isinstance(other, Hand):
            if self.rank < other.rank:
                return True
            elif self.rank > other.rank:
                return False
            elif Hand.in_rank_comparison(self.in_rank_values, other.in_rank_values) == -1:
                return True
            return False
        return False

    def __ge__(self, other) -> bool:
        if isinstance(other, Hand):
            if self.rank > other.rank:
                return True
            elif self.rank < other.rank:
                return False
            elif Hand.in_rank_comparison(self.in_rank_values, other.in_rank_values) in [0, 1]:
                return True
            return False
        return False

    def __le__(self, other) -> bool:
        if isinstance(other, Hand):
            if self.rank < other.rank:
                return True
            elif self.rank > other.rank:
                return False
            elif Hand.in_rank_comparison(self.in_rank_values, other.in_rank_values) in [0, -1]:
                return True
            return False
        return False

    def __ne__(self, other) -> bool:
        if isinstance(other, Hand):
            if self.rank != other.rank:
                return False
            elif Hand.in_rank_comparison(self.in_rank_values, other.in_rank_values) == 0:
                return True
            return False
        return False

    @staticmethod
    def in_rank_comparison(hand_value_1, hand_value_2):

        if hand_value_1 == [2, 3, 4, 5, 14]:
            hand_value_1 = [1, 2, 3, 4, 5]
        if hand_value_2 == [2, 3, 4, 5, 14]:
            hand_value_2 = [1, 2, 3, 4, 5]

        # Tied
        if hand_value_1 == hand_value_2:
            return 0

        # 1 denotes hand_1 wins
        # -1 denotes hand_2 wins
        for i in range(-1, -len(hand_value_1) - 1, -1):
            if hand_value_1[i] > hand_value_2[i]:
                return 1
            elif hand_value_1[i] < hand_value_2[i]:
                return -1

    @staticmethod
    @np.vectorize
    def compare(hand_1, hand_2) -> int:
        """
        Compare hand type. Otherwise, compare with rank values
        """
        if hand_1.rank > hand_2.rank:
            return 1
        elif hand_1.rank < hand_2.rank:
            return -1
        return Hand.in_rank_comparison(hand_1.in_rank_values, hand_2.in_rank_values)

    @staticmethod
    @np.vectorize
    def multi_compare() -> int:
        pass

    # Overwriting String Operation
    def __str__(self) -> str:
        category_strings = {10: 'Royal Flush', 9: 'Straight Flush', 8: 'Four of a Kind',
                            7: 'Full House', 6: 'Flush', 5: 'Straight', 4: 'Three of a Kind', 3: 'Two Pairs',
                            2: 'One Pair', 1: 'High Card'}
        if len(self.hand_candidates) == 5:
            return category_strings.get(self.rank) + " " + str([card.__str__() for card in self.hand_candidates])
        return str([card.__str__() for card in self.hand_candidates])
