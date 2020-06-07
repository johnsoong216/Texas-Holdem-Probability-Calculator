# PokerOddsCalc

<p align="left">
    <a href="https://www.python.org/">
        <img src="https://ForTheBadge.com/images/badges/made-with-python.svg"
            alt="python"></a> &nbsp;
    <a href="https://opensource.org/licenses/MIT">
        <img src="https://img.shields.io/badge/License-MIT-brightgreen.svg?style=flat-square"
            alt="MIT license"></a> &nbsp;
</p>

---

**PokerOddsCalc** is a simple poker hand evaluator that can simulate Texas Hold'em or Omaha poker variants. 
Most pure poker odds calculators written in Python currently either use a hashtable to store *Card information* as bits to enhance performance or use a strong OOP design, which sacrifices performance. The **development goal** of this project is to achieve relatively high simulation efficiency without the use of a hashtable.

Check out **demo.ipynb** to look at all the functions the tool supports or continue below for some brief examples.

---

## Table of Contents


- [Installation](#installation)
- [Design](#design)
- [Example](#example)
- [License](#license)

---

## Installation

### Setup

> install directly using pip

```shell
$ pip install pokeroddscalc
```

> install from github

```shell
$ pip install git+https://github.com/johnsoong216/PokerOddsCalc.git
```

---

## Design

In order to process data at a fast speed, all Card information are converted into numpy arrays to improve speed.

Card inputs are taken in the format of number: 23456789TJQKA followed by suit: dcsh. 

To rank cards, we use a hexidecimal system to assign strength to the card from the most most significant card to the least significant card. There are 7462 distinct poker hands so we created an algorithm that transforms a hand into an integer value.

Firstly, we determine if the 5 card combination is suited/straight. This can quickly identify the type of several hands.

Then we work with numerical values of the cards where 2 to A are represented by integers from 2 to 14. 

We sort the cards to quickly identify the card type.

> First Step
   - Four of A Kind can exist in two formats after sorted: AAAAB or BAAAA
   - Then we move the values in terms of the most valuable digit, so AAAAB -> BAAAA
   - Similarly for Three of a Kind there are three formats: AAABC, ABBBC, ABCCC and we can move the values
> Second Step
    - We can identify all the card types and we assign an integer value from 1 - 8 to each hand TYPE(1 being High Card and 8 being Straight Flush)
    - The integer value is calculated as $D_1 * 1, D_2 * 16, D_3 * 16^2, D_4 * 16^3, D_5 * 16^4, TYPE * 16^5$ where $D_i$ is the $i^{th}$ most significant numerical value of the hand. Since the maximum value of any digit is 14, we know that using a hexidecimal system can avoid coalition and successfully assign a unique value to each hand.
> Third Step
    - Assigning a value to a hand can allow for quick comparisons between hand strength, which makes simulation more efficient.
    
> Conclusion
    - Implementing this design, we can achieve a speed of 5M simulations per second for Hold'em and 1.5M/s for Omaha.
    - Although this is not as fast as certain bitwise methods/hashtable methods, which can achieve a speed north of 10M/s, it is a great improvement over certain OOP designs which are not functionally usable when the flop is not drawn.

## Example

> Import Game

```python
from PokerOddsCalc import HoldemTable, OmahaTable
```
> Create a game, specify the number of players and the deck type (full deck or short deck)

```python

ht = HoldemTable(num_players=5, deck_type='full') # Will Create Three Players: Player 1 - 5

```
> Randomly Hand Out Cards by calling the next_round() function any step in the game, or Assign Manually

```python

ht.add_to_hand(1, ['Td, 'Ad']) # Assign Player 1
ht.next_round() # Assign all other players randomly

```
> Simulate to generate outcome, specify the number of scenarios and the odds calculation type (For more details please check **demo.ipynb**)

```python

ht.simulate()
#
{'Player 1 Win': 50.31,
 'Player 1 Tie': 3.84,
 'Player 2 Win': 12.09,
 'Player 2 Tie': 0.41,
 'Player 3 Win': 11.4,
 'Player 3 Tie': 3.84,
 'Player 4 Win': 11.05,
 'Player 4 Tie': 0.41,
 'Player 5 Win': 11.31,
 'Player 5 Tie': 0.41}
```

> View Current Table, Current Hand or Current Result (if Game Ended)

```python

ht.view_table()
ht.view_hand()
ht.view_result()

```

## Contributors
John Song [![GithubLink](https://github.com/johnsoong216)]
Kent Wu [![GithubLink](https://github.com/Kentwhf)]

---

## License

[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](http://badges.mit-license.org)

- **[MIT license](http://opensource.org/licenses/mit-license.php)**
- Copyright 2020 ©
