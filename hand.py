from utils import *
from exceptions import *
from ranker import *



class Hand:

    def __init__(self, hand_limit=2):

        self.hand_limit = hand_limit
        self.card_arr = np.zeros(shape=(0, hand_limit), dtype=np.int)

    def add_cards(self, cards):

        cards = format_cards(cards)

        for card in cards:
            self.card_arr = add_card(card, self.card_arr)

        if len(self.card_arr) > self.hand_limit:
            raise HandException(f"Cannot Have more than {self.hand_limit} cards in hand")

    def remove_cards(self, cards):

        cards = format_cards(cards)

        for card in cards:
            self.card_arr = remove_card(card, self.card_arr)

    def hand_evaluation(self, community_arr):

        all_combos, res_arr = self.hand_value(community_arr)
        return hand_type_dict[np.max(res_arr) // 16 ** 5] + ' ' + ' '.join(
            card_arr_to_str(all_combos[0, np.argmax(res_arr), :, :]))

    def hand_value(self, community_arr):

        if len(community_arr) < 3:
            raise HandException("No valid hand has formed.")
        if self.hand_limit == 2:
            player_valid_hand = np.concatenate([self.card_arr, community_arr], axis=0)
            all_combos = np.expand_dims(player_valid_hand, axis=0)[:, comb_index(len(player_valid_hand), 5), :]
        else:
            community_combos = np.expand_dims(community_arr, axis=0)[:, comb_index(len(community_arr), 3), :]
            hand_combos = np.expand_dims(self.card_arr, axis=0)[:, comb_index(4, 2), :]
            all_combos = np.concatenate(
                [np.repeat(hand_combos, repeats=num_combinations(len(community_arr), 3), axis=1),
                 np.concatenate(6 * [community_combos], axis=1)], axis=2)
        res_arr = Ranker.rank_all_hands(all_combos, return_all=True)
        return all_combos, res_arr

    def __str__(self):
        return " ".join(card_arr_to_str(self.card_arr))