import multiprocessing
from joblib import Parallel, delayed
import random
import timeit
import logging

import numpy as np

from exceptions import *
from utils import *
from hand import Hand
from ranker import *

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class Table:

    def __init__(self, num_players, hand_limit, deck_type='full'):

        self.deck_arr = self.generate_deck(deck_type)
        self.player_hands = {player_num: Hand(hand_limit) for player_num in range(1, num_players + 1)}
        self.num_players = num_players
        self.community_arr = np.zeros(shape=(0, 2), dtype=np.int)

    def generate_deck(self, deck_type):

        if deck_type == "full":
            num = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
        elif deck_type == "short":
            num = ["6", "7", "8", "9", "T", "J", "Q", "K", "A"]
        else:
            raise DeckException("Invalid Deck Type. Valid options are: Full/Short ")

        suit = ["d", "c", "s", "h"]
        return card_str_to_arr([n + s for n in num for s in suit])

    def add_to_hand(self, player_num, cards):

        cards = format_cards(cards)
        for card in cards:
            self.player_hands[player_num].add_cards(card)
            self.deck_arr = remove_card(card, self.deck_arr)

    def add_to_community(self, cards):
        cards = format_cards(cards)

        for card in cards:
            self.community_arr = add_card(card, self.community_arr)
            self.deck_arr = remove_card(card, self.deck_arr)

    def simulation_preparation(self, num_scenarios):

        for player in self.player_hands:
            if len(self.player_hands[player].card_arr) < self.player_hands[player].hand_limit:
                raise HandException(f"Please Deal a Starting Hand to Player {player}")

        total_idx = comb_index(len(self.deck_arr), 5 - len(self.community_arr))
        undrawn_combos = self.deck_arr[total_idx]
        if num_scenarios != 'all':
            if len(undrawn_combos) > num_scenarios:
                undrawn_combos = undrawn_combos[np.array(random.sample(range(len(undrawn_combos)), num_scenarios))]

        if len(self.community_arr) > 0:
            community_cards = np.repeat([self.community_arr], len(undrawn_combos), axis=0)
        else:
            community_cards = None
        return community_cards, undrawn_combos

    def simulate(self, num_scenarios=150000, odds_type="tie_win", final_hand=False):
        raise NotImplementedError

    def simulate_calculation(self, community_cards, undrawn_combos):
        raise NotImplementedError

    def gen_single_hand(self, community_cards, player, undrawn_combos, res_arr):
        raise NotImplementedError

    def hand_strength_analysis(self, res_arr):
        final_hand_dict = {}
        for player in range(self.num_players):
            hand_type, hand_freq = np.unique((res_arr // 16 ** 5)[:, player], return_counts=True)
            final_hand_dict[player + 1] = dict(
                zip(np.vectorize(hand_type_dict.get)(hand_type), np.round(hand_freq / hand_freq.sum() * 100, 2)))
        return final_hand_dict

    def simulation_analysis(self, odds_type, res_arr):
        # Result Analysis
        outcome_arr = (res_arr == np.expand_dims(np.max(res_arr, axis=1), axis=1))
        num_outcomes = len(outcome_arr)
        outcome_dict = {}
        # Any Tied Win counts as a Win
        if odds_type == "win_any":
            tie_indices = np.all(outcome_arr, axis=1)  # multi-way tie
            outcome_dict['Tie'] = np.round(np.mean(tie_indices) * 100, 2)

            for player in range(self.num_players):
                outcome_dict["Player " + str(player + 1)] = np.round(
                    np.sum(outcome_arr[~tie_indices, player]) / num_outcomes * 100, 2)
        # Any Multi-way Tie/Tied Win counts as a Tie, Win must be exclusive
        elif odds_type == "tie_win":
            for player in range(self.num_players):
                tie_win_scenarios = outcome_arr[outcome_arr[:, player] == 1].sum(axis=1)
                outcome_dict["Player " + str(player + 1) + " Win"] = np.round(
                    np.sum(tie_win_scenarios == 1) / num_outcomes * 100, 2)
                outcome_dict["Player " + str(player + 1) + " Tie"] = np.round(
                    np.sum(tie_win_scenarios > 1) / num_outcomes * 100, 2)
        elif odds_type == "precise":

            for num_player in range(1, self.num_players + 1):
                for player_arr in comb_index(self.num_players, num_player):
                    temp_arr = np.ones(shape=(outcome_arr.shape[0]), dtype=bool)
                    for player in player_arr:
                        temp_arr = (temp_arr & (outcome_arr[:, player] == 1))
                    for non_player in [player for player in range(self.num_players) if player not in player_arr]:
                        temp_arr = (temp_arr & (outcome_arr[:, non_player] == 0))

                    if len(player_arr) == 1:
                        outcome_key = f"Player {player_arr[0] + 1} Win"
                    else:
                        outcome_key = f"Player {','.join([str(player + 1) for player in player_arr])} Tie"

                    outcome_dict[outcome_key] = np.round(temp_arr.sum() / num_outcomes * 100, 2)
        return outcome_dict

    def next_round(self, verbose=True):

        hand_player_cards = True
        for player in self.player_hands:
            if len(self.player_hands[player].card_arr) == 0:
                hand_player_cards = False
                added_card = self.random_card(self.player_hands[player].hand_limit)
                self.add_to_hand(player, added_card)
                logging.info(f"Giving Player {player} {' '.join(card_arr_to_str(added_card))}")

        if hand_player_cards:
            if len(self.community_arr) == 0:
                added_card = self.random_card(3)
            else:
                added_card = self.random_card(1)

            if verbose:
                logging.info(f"{'Flop' if len(self.community_arr) == 0 else 'Turn' if len(self.community_arr) == 3 else 'River'} card:  {' '.join(card_arr_to_str(added_card))}")
            self.add_to_community(added_card)


    def random_card(self, num_cards):
        rand_indices = np.array(random.sample(range(len(self.deck_arr)), num_cards))
        return self.deck_arr[rand_indices]

    def view_table(self):
        res_dict = {"Player " + str(player): str(self.player_hands[player]) for player in self.player_hands}
        res_dict["Community Cards"] = ' '.join(card_arr_to_str(self.community_arr))
        return res_dict

    def view_deck(self):
        return " ".join(card_arr_to_str(self.deck_arr))

    def view_hand(self):
        output_dict = {}
        if len(self.community_arr) < 3:
            raise HandException("Please Flop to form a valid hand")

        for player in range(self.num_players):
            output_dict[f"Player {player + 1} Current Hand"] = self.player_hands[player + 1].hand_evaluation(
                self.community_arr)
        return output_dict

    def view_result(self):
        player_rank = np.zeros(self.num_players, dtype=np.int)
        player_hand_type = np.zeros(self.num_players, dtype=np.int)

        for player in range(self.num_players):
            player_combos, player_res_arr = self.player_hands[player + 1].hand_value(self.community_arr)
            player_rank[player] = np.max(player_res_arr)
            player_hand_type[player] = np.max(player_res_arr) // 16 ** 5

        if (np.max(player_rank) == player_rank).sum() == 1:
            return f"Player {np.argmax(player_rank) + 1} wins with a {hand_type_dict[player_hand_type[np.argmax(player_rank)]]}"
        else:
            winners, = np.where(np.max(player_rank) == player_rank)
            return f"Player {', '.join((winners + 1).astype(str))} ties with a {hand_type_dict[player_hand_type[winners[0]]]}"



class HoldemTable(Table):

    def __init__(self, num_players, deck_type='full'):
        super(HoldemTable, self).__init__(num_players=num_players,
                                          hand_limit=2,
                                          deck_type=deck_type)

    def simulate(self, num_scenarios=150000, odds_type="tie_win", final_hand=False):

        start = timeit.default_timer()
        community_cards, undrawn_combos = self.simulation_preparation(num_scenarios)
        # end = timeit.default_timer()
        # logging.info(f"Generate Hand Combinations Time Cost: {end - start}s")

        # start = timeit.default_timer()
        res_arr = self.simulate_calculation(community_cards, undrawn_combos)
        # end = timeit.default_timer()
        # logging.info(f"Calculation Time Cost: {end - start}s")
        outcome_dict = self.simulation_analysis(odds_type, res_arr)

        if final_hand:
            final_hand_dict = self.hand_strength_analysis(res_arr)
            logging.info(f"{min([len(undrawn_combos), num_scenarios]) * 21 * self.num_players} Simulations in {np.round(timeit.default_timer() - start, 2)}s")
            return outcome_dict, final_hand_dict

        logging.info(f"{min([len(undrawn_combos), num_scenarios]) * 21 * self.num_players} Simulations in {np.round(timeit.default_timer() - start, 2)}s")
        return outcome_dict

    def simulate_calculation(self, community_cards, undrawn_combos):
        res_arr = np.zeros(shape=(len(undrawn_combos), self.num_players), dtype=np.int)
        if self.num_players >= 2:
            Parallel(n_jobs=multiprocessing.cpu_count(), backend="threading") \
                (delayed(self.gen_single_hand)(community_cards, player, undrawn_combos, res_arr) for player in range(self.num_players))
        else:
            for player in range(self.num_players):
                self.gen_single_hand(community_cards, player, undrawn_combos, res_arr)
        return res_arr

    def gen_single_hand(self, community_cards, player, undrawn_combos, res_arr):
        if community_cards is None:
            cur_player_cards = np.concatenate(
                [np.repeat([self.player_hands[player + 1].card_arr], len(undrawn_combos), axis=0),
                 undrawn_combos], axis=1)
        else:
            cur_player_cards = np.concatenate(
                [np.repeat([self.player_hands[player + 1].card_arr], len(undrawn_combos), axis=0),
                 community_cards,
                 undrawn_combos], axis=1)
        res_arr[:, player] =  Ranker.rank_all_hands(cur_player_cards[:, comb_index(7, 5), :])



class OmahaTable(Table):

    def __init__(self, num_players, deck_type='full'):
        super(OmahaTable, self).__init__(num_players=num_players,
                                          hand_limit=4,
                                          deck_type=deck_type)

    def simulate(self, num_scenarios=25000, odds_type="tie_win", final_hand=False):

        start = timeit.default_timer()
        community_cards, undrawn_combos = self.simulation_preparation(num_scenarios)
        res_arr = self.simulate_calculation(community_cards, undrawn_combos)
        outcome_dict = self.simulation_analysis(odds_type, res_arr)

        if final_hand:
            final_hand_dict = self.hand_strength_analysis(res_arr)
            logging.info(f"{min([len(undrawn_combos), num_scenarios]) * 60 * self.num_players} Simulations in {np.round(timeit.default_timer() - start, 2)}s")
            return outcome_dict, final_hand_dict
        logging.info(f"{min([len(undrawn_combos), num_scenarios]) * 60 * self.num_players} Simulations in {np.round(timeit.default_timer() - start, 2)}s")
        return outcome_dict

    def simulate_calculation(self, community_cards, undrawn_combos):
        res_arr = np.zeros(shape=(len(undrawn_combos), self.num_players), dtype=np.int)

        if self.num_players >= 2:
            Parallel(n_jobs=multiprocessing.cpu_count(), backend="threading") \
                (delayed(self.gen_single_hand)(community_cards, player, undrawn_combos, res_arr) for player in
                 range(self.num_players))
        else:
            for player in range(self.num_players):
                self.gen_single_hand(community_cards, player, undrawn_combos, res_arr)
        return res_arr

    def gen_single_hand(self, community_cards, player, undrawn_combos, res_arr):


        if community_cards is None:
            community_combos = undrawn_combos[:, comb_index(5, 3), :]
        else:
            community_combos = np.concatenate(
                [np.repeat([self.community_arr], len(undrawn_combos), axis=0),
                 undrawn_combos], axis=1)[:, comb_index(5, 3), :]

        hand_combos = np.repeat([self.player_hands[player + 1].card_arr], len(undrawn_combos), axis=0)[:,
                      comb_index(4, 2), :]

        cur_player_cards = np.concatenate(
            [np.repeat(hand_combos, repeats=10, axis=1), np.concatenate(6 * [community_combos], axis=1)], axis=2)

        # cur_player_cards = np.zeros(shape=(len(undrawn_combos), 60, 5, 2), dtype=np.int)
        # for scenario in range(len(undrawn_combos)):
        #     for i, comm in enumerate(community_combos[scenario, :, :, :]):
        #         for j, hand in enumerate(hand_combos[scenario, :, :, :]):
        #             cur_player_cards[scenario, i * 6 + j, :, :] = np.concatenate([comm, hand])

        res_arr[:, player] = Ranker.rank_all_hands(cur_player_cards)



### Consider Input Error and Prevent Them - Card Removal, Same Input
    ### Delete Player, Remove Card from Hand
    ### Add Randomized Flop/River/.....