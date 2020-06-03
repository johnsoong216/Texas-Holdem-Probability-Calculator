from Card import *
from Hand import *
import itertools

"""
This class compares all possible hands and finds the best hand using the Model Class
"""


class Sorter:
    def __init__(self, starting_hand: list, flop: list) -> None:
        self.starting_hand = starting_hand
        self.flop = flop
        

    def besthand_solver(self) -> list:
        all_cards = self.starting_hand + self.flop
        all_hands = itertools.combinations(all_cards, 5)
        best = all_cards[0:5]
        for hand in all_hands:
            best = self.hand_compare(hand, best, False)
        return best
    

    def hand_compare(self, p1: list, p2: list, direct: bool) -> list:
        
    
        p1C = Categorizer(p1)
        p2C = Categorizer(p2)
        if p1C.category < p2C.category:
            return p1
        elif p1C.category == p2C.category:
            better = self.rank_under_same_category(p1C, p2C)
            if len(better) == 1:
                if better[0] == p1C:
                    return p1
                else:
                    return p2
            elif direct == False:
                return p1
            else:
                return [Card(14,1) * 5]
        else:
            return p2
        
    
    
    def rank_under_same_category(self, obj1: "Categorizer", obj2: "Categorizer") -> list:
        # print(obj1.assign_table())
        # print(obj2.assign_table())
        for i in range(5):
            if obj1.assign_table()[i] > obj2.assign_table()[i]:
                return [obj1]
            elif obj1.assign_table()[i] < obj2.assign_table()[i]:
                return [obj2]
        return [obj1, obj2]


if __name__ == '__main__':
    b = [Card(10, 1), Card(10, 2), Card(10, 3), Card(11, 4), Card(14, 1)]
    a = [Card(14, 2), Card(14, 3)]
    new = Sorter(a, b)
