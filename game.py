"""
This class is the game interface
"""
from deck import Deck
from Card import Card
from besthand_sorter import Sorter
from collections import Counter
import itertools
import time
from matplotlib import pyplot as plt
import pandas as pd


class Game:
    
    def __init__(self) -> None:
        self.deck = Deck()
        self.p1 = []
        self.p2 = []
        
        
    def start(self, p1c1: "Card", p1c2: "Card", p2c1: "Card", p2c2: "Card") -> None:
        
        self.p1.append(p1c1)
        self.p1.append(p1c2)
        self.p2.append(p2c1)
        self.p2.append(p2c2)
        
        self.deck.removeByCard(p1c1)
        self.deck.removeByCard(p1c2)
        self.deck.removeByCard(p2c1)
        self.deck.removeByCard(p2c2)
        
        self.p1Outcome = []
        self.p2Outcome = []
        self.wld = []
    
    
    def flip(self, _next: "Card") -> None:
        self.deck.removeByCard(_next)
        self.p1.append(_next)
        self.p2.append(_next)
        
        print(self.p1)
        print(self.p2)
        self.p1Outcome = []
        self.p2Outcome = []
        self.wld = []
        
    def model(self):
        all_hands = itertools.combinations(self.deck, 7 - len(self.p1))
        for hand in all_hands:
            self.comparison(self.p1, self.p2, list(hand))
            
        df1 = pd.DataFrame.from_dict(Counter(self.p1Outcome), orient='index')
        df1.plot(kind='bar')
        D = {1: 'Royal Flush', 2: 'Straight Flush', 3: 'Four of A Kind', 4: 'Full House', 5: 'Flush', 6: 'Straight', 7: 'Three of a Kind', 
                   8: 'Two Pair', 9: 'One Pair', 10: 'High Card'}        
        plt.bar(range(len(D)), D.values(), align = 'center')
        plt.xticks(range(len(D)), list(D.keys()))
        plt.show()
        df2 = pd.DataFrame.from_dict(Counter(self.p2Outcome), orient='index')
        df2.plot(kind='bar')
        plt.bar(range(len(D)), D.values(), align = 'center')
        plt.xticks(range(len(D)), list(D.keys()))
        plt.show()
        df3 = pd.DataFrame.from_dict(Counter(self.wld), orient='index')
        df3.plot(kind='bar')
        D = {1: "WIN", 0: "TIE", -1: "LOSS"}
        plt.bar(range(len(D)), D.values(), align = 'center')
        plt.xticks(range(len(D)), list(D.keys()))
        plt.show() 
            

            
    def comparison(self, p1:list, p2:list, hand:list) -> None:
        p1 = Sorter(p1, hand)
        p2 = Sorter(p2, hand)
        platform = Sorter([],[])
        p1 = p1.besthand_solver()
        p2 = p2.besthand_solver()
        
        
    
        p1C = Categorizer(p1)
        p2C = Categorizer(p2)
        
        self.p1Outcome.append(p1C.category)
        self.p2Outcome.append(p2C.category)
        
        outcome = platform.hand_compare(p1, p2, True)
        if outcome == p1:
            self.wld.append(1)
        elif outcome == p2:
            self.wld.append(-1)
        else:
            self.wld.append(0)
            
        
def replace(card:list, dictionary:dict):
    new_list = []
    for i in card:
        result = dictionary.get(i)
        new_list.append(result)
    return new_list   
            
        
if __name__ == '__main__':
    firstHand = input("Input Your Current Hand")
    secondHand = input("Input Your Opponent's Hand")
    fH = str.split(firstHand)
    sH = str.split(secondHand)
    fH = list("".join(fH))
    sH = list("".join(sH))
    print(fH)
    print(sH)
    game = Game()
    conversion = {'d': 1, 'c': 2, 'h': 3, 's': 4, '2': 2, '3': 3, '4': 4, '5':5, '6':6, '7':7, '8':8, '9':9,
                  'T': 10, 'J': 11, 'Q': 12, 'K':13, 'A':14}    
    fH = replace(fH, conversion)
    sH = replace(sH, conversion)
    game.start(Card(fH[0], fH[1]), Card(fH[2], fH[3]), Card(sH[0], sH[1]), Card(sH[2], sH[3]))
    while len(game.p1) < 7:
        calculation = input("Do you want to calculate odds now? Enter True or False")
        if calculation == 'True':
            game.model()
        else:
            nextHand = input("Flip the Next Card")
            nH = str.split(nextHand)
            nH = list("".join(nH))
            nH = replace(nH, conversion)
            game.flip(Card(nH[0], nH[1]))
                  
    
    
    
    
    
    
