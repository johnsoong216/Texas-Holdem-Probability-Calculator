from Exception import CardException

suitStrings = {1: 'd', 2: 'c', 3: 'h', 4: 's'}
numStrings = {2: '2', 3: '3', 4: '4', 5:'5', 6:'6', 7:'7', 8:'8', 9:'9',
                      10: 'T', 11: 'J', 12: 'Q', 13:'K', 14:'A'}


class Card(tuple):
    """
    A standard poker card with value and suit
    Suit:
    - Diamond 1
    - Club 2
    - Heart 3
    - Spade 4

    Value:
    - Two 2
    ....s
    - King 13
    - Ace 14
    """

    def __init__(self, value: int, suit: int) -> None:
        
        if (value < 2) or (value > 14) or (suit < 1) or (suit > 4):
            raise CardException("Card is not valid")
            
        self.value = value
        self.suit = suit

    def __new__(self, value: int, suit: int) -> tuple:
        return tuple.__new__(self, (value, suit))
    
    def __duplicate__(self, other) -> bool:
        if isinstance(other, tuple):
            return (self[0] == other[0]) & (self[1] == other[1])
        return False
    
    # Overwrite Comparison Operators
    
    def __eq__(self, other) -> bool:
        if isinstance(other, tuple):
            return self[0] == other[0]
        return False

    def __gt__(self, other) -> bool:
        if isinstance(other, tuple):
            return self[0] > other[0]
        return False
    
    def __lt__(self, other) -> bool:
        if isinstance(other, tuple):
            return self[0] < other[0]
        return False
   
    def __ge__(self, other) -> bool:
        if isinstance(other, tuple):
            return self[0] >= other[0]
        return False
    
    def __le__(self, other) -> bool:
        if isinstance(other, tuple):
            return self[0] <= other[0]
        return False
    
    def __ne__(self, other) -> bool:
        if isinstance(other, tuple):
            return self[0] != other[0]
        return False
    
    
    def __str__(self) -> str:
        return numStrings.get(self[0]) + suitStrings.get(self[1])


if __name__ == '__main__':
    a = Card(7, 3)
    b = Card(7, 4)
    print(a < b)
    print(a[1])
    print(a)
    print(a.value)
    print(a.suit)
